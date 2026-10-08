#!/usr/bin/env python3
"""Outcome-blind Daymet route-scale climate pilot using PINNED NAAMP metadata.

A sampled route-centroid is an approximate 1-km regional exposure location,
never an independently field-verified 30-m station coordinate. No Counts.csv,
calling index, frog taxon, or retrospective land cover outcomes are read.

This is a fixed-source feasibility diagnostic, NOT an estimate of anthropogenic
climate-change effects on frogs, nor a station-level hydroperiod measurement.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta
import hashlib
import io
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from scipy.stats import theilslopes

from audit_coordinates import audit as geometry_audit
from build_naamp_observation_panel import make as make_panel, SOURCE_PINS
from run_public_naamp_feasibility import COORD_SHA

FIRST_YEAR, LAST_YEAR = 1981, 2015
BASE_YEARS = tuple(range(1981, 2001))
YEARS = tuple(range(FIRST_YEAR, LAST_YEAR + 1))
MAX_ROUTES = 12
SELECTION_SEED = 'frogcs-daymet-route-pilot-fixed-2026-10-08-v0.1'
MIN_SURVEY_YEARS = 5
MIN_SURVEY_SPAN = 8
BASE_URL = 'https://daymet.ornl.gov/single-pixel/api/data'
REQUIRED = ('prcp', 'tmax', 'tmin')


def _sha(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def select_routes(runs:pd.DataFrame, stops:pd.DataFrame, coords:pd.DataFrame,
                  max_routes:int=MAX_ROUTES)->tuple[list[dict],dict]:
    """Select once per state based on metadata/geometry, never frog responses."""
    if not isinstance(max_routes,int) or max_routes<1:
        raise ValueError('Bad route pilot sample size')
    panel,_=make_panel(runs,stops)
    loc,_=geometry_audit(coords)
    loc=loc.loc[loc.geometry_qc_status.eq('pass_unverified')].copy()
    if panel.empty or loc.empty:
        raise ValueError('No eligible NAAMP metadata / route geometry')
    # The source geometry alone is not an external site validation.
    loc=loc.rename(columns={'route_id':'route_number'})
    uniq=panel[['state','route_number','route_id','site_id']].drop_duplicates()
    joined=uniq.merge(loc[['route_number','site_id','latitude','longitude']],
                      how='inner',on=['route_number','site_id'],validate='many_to_one')
    route_geoms=(joined.groupby(['state','route_number','route_id'],as_index=False)
                 .agg(n_geometry_pass_sites=('site_id','nunique'),
                      latitude=('latitude','median'),longitude=('longitude','median')))
    years=panel.groupby('route_id',as_index=False).agg(
        n_survey_years=('survey_year','nunique'),
        first_survey_year=('survey_year','min'),last_survey_year=('survey_year','max'),
        n_site_visits=('site_id','size'))
    candidates=route_geoms.merge(years,on='route_id',validate='one_to_one')
    candidates['survey_span']=candidates.last_survey_year-candidates.first_survey_year
    eligible=candidates.loc[(candidates.n_geometry_pass_sites>=8)&
        (candidates.n_survey_years>=MIN_SURVEY_YEARS)&
        (candidates.survey_span>=MIN_SURVEY_SPAN)].copy()
    if eligible.empty:
        raise ValueError('No routes meet fixed repeat-time and geometry eligibility')
    eligible['selection_hash']=eligible.apply(lambda r:hashlib.sha256(
        f'{SELECTION_SEED}:{r.route_id}'.encode()).hexdigest(),axis=1)
    # One route per state; deterministically hashed rather than choosing endpoints
    # or the highest apparent climate trend. Then deterministic state selection.
    eligible=eligible.sort_values(['state','selection_hash'])
    one=eligible.drop_duplicates('state',keep='first').copy()
    one['state_order']=one.state.map(lambda s:hashlib.sha256(
        f'{SELECTION_SEED}:state:{s}'.encode()).hexdigest())
    chosen=one.sort_values('state_order').head(max_routes).sort_values('state')
    payload=[]
    for row in chosen.itertuples(index=False):
        payload.append({
            'state':str(row.state), 'route_id':str(row.route_id),
            'latitude_route_median':round(float(row.latitude),6),
            'longitude_route_median':round(float(row.longitude),6),
            'n_geometry_pass_sites':int(row.n_geometry_pass_sites),
            'n_survey_years':int(row.n_survey_years),
            'first_survey_year':int(row.first_survey_year),
            'last_survey_year':int(row.last_survey_year),
            'survey_year_span':int(row.survey_span),
            'n_site_visits':int(row.n_site_visits),
            'coordinate_status':'route_median_geometry_pass_unverified',
            'does_not_verify_physical_station':True,
        })
    summary={
        'n_full_metadata_routes':int(panel.route_id.nunique()),
        'n_longitudinal_geometry_eligible_routes':int(len(eligible)),
        'n_states_with_eligible_routes':int(one.state.nunique()),
        'n_sampled_routes':len(payload), 'n_sampled_states':len(payload),
        'site_level_externally_verified':False,
        'route_median_is_1km_gridded_weather_screen_only':True,
        'sample_rule':'fixed hash one route per state among >=5 years, span>=8y, >=8 geometry-pass sites',
        'seed':SELECTION_SEED,
        'input_uses_count_data':False,
    }
    return payload,summary


def daymet_url(lat:float,lon:float,years=YEARS):
    if not 14.5 <= lat <= 52.0 or not -131.0<=lon<=-53.0:
        raise ValueError('Outside published North American Daymet single-pixel domain')
    query=urlencode({'lat':f'{lat:.6f}','lon':f'{lon:.6f}',
                     'vars':','.join(REQUIRED),'years':','.join(map(str,years))})
    return BASE_URL+'?'+query


def fetch_daymet(url:str)->bytes:
    if not url.startswith(BASE_URL+'?'):
        raise ValueError('Only official HTTPS Daymet endpoint is authorized')
    for attempt in range(3):
        try:
            req=Request(url,headers={'User-Agent':'frogcs-landscape-daymet-v0.7/0.1',
                                     'Accept':'text/csv, text/plain'})
            with urlopen(req, timeout=115) as stream:
                return stream.read()
        except (HTTPError,URLError,TimeoutError) as e:
            if attempt==2 or (isinstance(e,HTTPError) and e.code not in (408,429,500,502,503,504)):
                raise
            time.sleep(3*(attempt+1))
    raise RuntimeError('Daymet download failed')


def parse_daymet_csv(raw:bytes,years=YEARS)->pd.DataFrame:
    text=raw.decode('utf-8-sig')
    lines=text.splitlines()
    header=next((i for i,v in enumerate(lines) if v.strip().lower().startswith('year,yday,')),None)
    if header is None:
        raise ValueError('Daymet response has no year,yday header; API may have returned error')
    table=list(csv.DictReader(io.StringIO('\n'.join(lines[header:]))))
    if not table:raise ValueError('Empty Daymet CSV')
    def colnames(keys):
        labels=list(table[0].keys())
        match=[key for key in labels if key.split('(',1)[0].strip().lower()==keys]
        if len(match)!=1:raise ValueError(f'Daymet column {keys} absent or duplicated')
        return match[0]
    name={k:colnames(k) for k in REQUIRED}
    records=[]
    seen=set()
    for record in table:
        year,yday=int(record['year']),int(record['yday'])
        if year not in years or not 1<=yday<=365:
            raise ValueError('Daymet calendar year/day is invalid or outside expected years')
        if (year,yday) in seen:raise ValueError('Duplicate Daymet calendar record')
        seen.add((year,yday))
        p,tmax,tmin=(float(record[name[k]]) for k in ('prcp','tmax','tmin'))
        if not np.isfinite([p,tmax,tmin]).all() or p<0 or tmax<tmin:
            raise ValueError('Nonphysical or missing daily Daymet climate record')
        d=date(year,1,1)+timedelta(days=yday-1)
        # Daymet includes Feb 29 in leap years and drops Dec 31 of leap years.
        if d.year!=year or (d.month==12 and d.day==31 and (year%4==0 and
          (year%100!=0 or year%400==0))):
            raise ValueError('Daymet leap calendar inconsistency')
        records.append({'year':year,'yday':yday,'date':d.isoformat(),
                        'precip_mm':p,'tmean_c':(tmax+tmin)/2})
    expected={(y,k) for y in years for k in range(1,366)}
    if seen != expected:raise ValueError('Incomplete annual Daymet daily record coverage')
    return pd.DataFrame(records).sort_values(['year','yday']).reset_index(drop=True)


def climate_summary(daily:pd.DataFrame)->dict:
    annual=daily.groupby('year',sort=True).agg(tmean_c=('tmean_c','mean'),
                                               precip_mm=('precip_mm','sum'),
                                               days=('yday','nunique'))
    if list(annual.index)!=list(YEARS) or not annual.days.eq(365).all():
        raise ValueError('Not all baseline/followup years are complete')
    baseline=annual.loc[list(BASE_YEARS)]
    yrs=annual.index.to_numpy(dtype=float)
    slope_t=float(theilslopes(annual.tmean_c.to_numpy(),yrs)[0])*10
    slope_p=float(theilslopes(annual.precip_mm.to_numpy(),yrs)[0])*10
    btemp=float(baseline.tmean_c.mean())
    bprecip=float(baseline.precip_mm.mean())
    if bprecip<=0:raise ValueError('Undefined baseline precipitation ratio')
    # Five COMPLETE previous years; never mix survey-year outcomes with weather.
    past={}
    for target in range(2001,2016):
        before=annual.loc[list(range(target-5,target))]
        past[str(target)]={
            'prior5_tmean_anomaly_c':round(float(before.tmean_c.mean()-btemp),6),
            'prior5_precip_ratio_to_1981_2000':round(float(before.precip_mm.mean()/bprecip),6),
        }
    return {
        'baseline_years':'1981-2000',
        'annual_observations':len(annual),
        'baseline_mean_temp_c':round(btemp,6),
        'baseline_precip_mm_year':round(bprecip,6),
        'descriptive_1981_2015_temp_slope_c_decade':round(slope_t,6),
        'descriptive_1981_2015_precip_slope_mm_decade':round(slope_p,6),
        'retrospective_trend_is_not_an_early_year_predictor':True,
        'climate_state_by_survey_year':past,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--runs',required=True)
    p.add_argument('--stops',required=True)
    p.add_argument('--coords',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--sample-out',required=True)
    args=p.parse_args()
    hashes={'Runs.csv':_sha(args.runs),'Stops.csv':_sha(args.stops),
            'Coordinates.csv':_sha(args.coords)}
    if hashes != {**SOURCE_PINS,'Coordinates.csv':COORD_SHA}:
        raise ValueError('Official USGS NAAMP source hashes did not match frozen values')
    run=pd.read_csv(args.runs,dtype=str,keep_default_na=False)
    stop=pd.read_csv(args.stops,dtype=str,keep_default_na=False)
    coords=pd.read_csv(args.coords,dtype={'RouteNumber':str,'SiteID':str})
    chosen,selection=select_routes(run,stop,coords)
    path=Path(args.sample_out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({'routes':chosen,'selection':selection,
             'source_sha256':hashes},sort_keys=True,indent=2)+'\n',encoding='utf-8')
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    receipt={'analysis':'daymet_route_level_pilot_v0_1',
             'status':'source_only_not_frog_climate_effect',
             'site_coordinate_verification': 'geometry_pass_unverified',
             'authoritative_daymet_api':'daymet.ornl.gov/single-pixel/api/data',
             'sample_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
             'n_requested':len(chosen),'selection':selection,'routes':[],
             'reads_frog_calling_data':False,'reads_landcover_pixel_values':False}
    for idx,r in enumerate(chosen,1):
        url=daymet_url(r['latitude_route_median'],r['longitude_route_median'])
        try:
            raw=fetch_daymet(url)
            parsed=parse_daymet_csv(raw)
            summary=climate_summary(parsed)
        except Exception as exc:
            receipt['status']='source_failed_not_inferentially_usable'
            receipt['failed_route_id']=r['route_id']
            receipt['failed_error_type']=type(exc).__name__
            dest.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
            raise
        receipt['routes'].append({'route_id':r['route_id'],'state':r['state'],
          'coordinate_geometry_status':r['coordinate_status'],
          'raw_daymet_response_sha256':hashlib.sha256(raw).hexdigest(),
          'daymet_daily_rows':len(parsed),**summary})
        receipt['status']='partial_source_screening'
        dest.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        print(json.dumps({'route':r['route_id'],'done':idx,'total':len(chosen),
               'n_daily':len(parsed),'slope_temp_c_decade':summary['descriptive_1981_2015_temp_slope_c_decade']}),flush=True)
    receipt['n_complete_routes']=len(receipt['routes'])
    receipt['status']='complete_source_screening'
    dest.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'n_complete_routes':len(chosen),'frog_effect_inferred':False},sort_keys=True))


if __name__=='__main__':
    main()
