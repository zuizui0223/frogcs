#!/usr/bin/env python3
"""Response-blind longitudinal exposure contrasts at repeated NAAMP physical sites.

Matches same verified route × physical site × survey round in EXACT adjacent
calendar years within 21 day-of-year positions. Does not read frog outcomes,
assume occupancy, impute missing water, or interpret acoustic changes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

DAY_OF_YEAR_MAX_DIFFERENCE=21
KEYS=['run_id','route_id','site_id','survey_date']
METADATA={*KEYS,'survey_round'}
CLIMATE={*KEYS,'tmean_anomaly_30d_c','climate_shift_5y_tmean_c','climate_shift_5y_precip_ratio'}
SATELLITE={*KEYS,'coordinate_qc_status',
 'b250_water_detected_fraction_observed_12m','b250_water_detection_lower_bound_12m',
 'b250_water_detection_upper_bound_12m','b250_forest_frac_prior_year',
 'b250_developed_frac_prior_year','b250_water_months_observed_12m'}
FEATURES=[
  'tmean_anomaly_30d_c','climate_shift_5y_tmean_c','climate_shift_5y_precip_ratio',
  'b250_water_detected_fraction_observed_12m',
  'b250_water_detection_lower_bound_12m','b250_water_detection_upper_bound_12m',
  'b250_forest_frac_prior_year','b250_developed_frac_prior_year']


def _date(df,where):
    out=df.copy()
    out['survey_date']=pd.to_datetime(out.survey_date,errors='raise').dt.normalize()
    if out.survey_date.isna().any():raise ValueError(f'{where} has blank survey dates')
    for key in ('run_id','route_id','site_id'):
        out[key]=out[key].astype('string').str.strip()
        if out[key].isna().any() or out[key].eq('').any():
            raise ValueError(f'{where} has blank {key}')
    if out.duplicated(KEYS).any():raise ValueError(f'{where} duplicate survey-site events')
    return out


def make(meta, climate, satellite):
    for name,src,cols in [('metadata',meta,METADATA),('climate',climate,CLIMATE),('satellite',satellite,SATELLITE)]:
        missing=cols-set(src.columns)
        if missing:raise ValueError(f'{name} missing {sorted(missing)}')
    m=_date(meta[sorted(METADATA)],'metadata')
    c=_date(climate[sorted(CLIMATE)],'climate')
    s=_date(satellite[sorted(SATELLITE)],'satellite')
    if not s.coordinate_qc_status.eq('verified_external').all():
        raise ValueError('unverified physical site in exposure panel')
    # Only rows with BOTH feature families are considered. Preserve measured
    # NA values in the matched table: missing observations are NOT dry.
    x=m.merge(c,on=KEYS,how='left',validate='one_to_one',indicator='climate_join')
    x=x.merge(s,on=KEYS,how='left',validate='one_to_one',indicator='satellite_join')
    if not (x.climate_join.eq('both').all() and x.satellite_join.eq('both').all()):
        raise ValueError('environmental exposure row missing for surveyed event')
    x=x.drop(columns=['climate_join','satellite_join'])
    x['survey_round']=pd.to_numeric(x.survey_round,errors='raise').astype(int)
    if not x.survey_round.isin([1,2,3,4]).all():raise ValueError('invalid NAAMP run/round')
    for f in FEATURES:
        x[f]=pd.to_numeric(x[f],errors='coerce')
    x['survey_year']=x.survey_date.dt.year
    x['doy']=x.survey_date.dt.dayofyear
    if x.duplicated(['route_id','site_id','survey_round','survey_year']).any():
        raise ValueError('multiple visits to one site/round/year: pairing ambiguous')
    out=[];excluded_gap=0;excluded_doy=0
    # Only exact one-calendar-year pairs, matched before frog outcomes.
    for key,g in x.groupby(['route_id','site_id','survey_round'],sort=True):
        g=g.sort_values(['survey_year','run_id'])
        for a,b in zip(g.iloc[:-1].itertuples(index=False),g.iloc[1:].itertuples(index=False)):
            if b.survey_year-a.survey_year!=1:
                excluded_gap+=1
                continue
            # Leap-aware month/day indexing on a nonleap template so two
            # surveys on same calendar date align despite Feb 29.
            def season_ix(date):
                ts=pd.Timestamp(date)
                return (pd.Timestamp(2001,ts.month,ts.day)-pd.Timestamp(2001,1,1)).days if not (ts.month==2 and ts.day==29) else 59
            day_diff=abs(season_ix(b.survey_date)-season_ix(a.survey_date))
            if day_diff>DAY_OF_YEAR_MAX_DIFFERENCE:
                excluded_doy+=1
                continue
            record={'route_id':str(a.route_id),'site_id':str(a.site_id),
                    'survey_round':int(a.survey_round),
                    'from_run_id':str(a.run_id),'to_run_id':str(b.run_id),
                    'from_date':a.survey_date.date().isoformat(),
                    'to_date':b.survey_date.date().isoformat(),
                    'from_year':int(a.survey_year),'to_year':int(b.survey_year),
                    'season_day_difference':int(day_diff)}
            for f in FEATURES:
                aa=getattr(a,f);bb=getattr(b,f)
                record['delta_'+f]=(float(bb-aa) if np.isfinite(aa) and np.isfinite(bb) else np.nan)
            for side,row in [('from',a),('to',b)]:
                record[side+'_water_detection_bound_width_12m']=(
                  float(row.b250_water_detection_upper_bound_12m-row.b250_water_detection_lower_bound_12m)
                  if np.isfinite(row.b250_water_detection_upper_bound_12m)
                  and np.isfinite(row.b250_water_detection_lower_bound_12m) else np.nan)
                record[side+'_observed_water_months_12m']=float(row.b250_water_months_observed_12m)
            record['water_contrast_eligible']=(
                np.isfinite(record['delta_b250_water_detected_fraction_observed_12m'])
                and record['from_observed_water_months_12m']>=9
                and record['to_observed_water_months_12m']>=9)
            out.append(record)
    t=pd.DataFrame(out)
    receipt={'study':'independent environmental site-history contrasts',
         'n_input_event_rows':len(x),
         'n_site_round_strata':int(x[['route_id','site_id','survey_round']].drop_duplicates().shape[0]),
         'n_consecutive_same_season_site_pairs':len(t),
         'n_water_comparable_pairs':int(t.water_contrast_eligible.sum()) if len(t) else 0,
         'excluded_due_to_nonconsecutive_year':excluded_gap,
         'excluded_due_to_season_day_shift_over_21':excluded_doy,
         'exact_calendar_year_gap_required':1,
         'max_season_day_difference':DAY_OF_YEAR_MAX_DIFFERENCE,
         'reads_species_or_count_data':False,
         'effect_on_frog_reproduction_estimated':False}
    return t,receipt


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--metadata',required=True)
    p.add_argument('--climate',required=True)
    p.add_argument('--satellite',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--receipt',required=True)
    a=p.parse_args()
    args={key:getattr(a,key) for key in ['metadata','climate','satellite']}
    d={key:pd.read_csv(path,dtype={'run_id':str,'route_id':str,'site_id':str}) for key,path in args.items()}
    t,rec=make(d['metadata'],d['climate'],d['satellite'])
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);t.to_csv(out,index=False)
    rec['input_sha256']={k:sha(p) for k,p in args.items()}
    rec['output_sha256']=sha(out)
    dest=Path(a.receipt);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(rec,sort_keys=True,indent=2)+"\n",encoding='utf-8')
    print(json.dumps(rec,sort_keys=True,indent=2))
if __name__=='__main__':main()
