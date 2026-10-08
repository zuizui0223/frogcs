#!/usr/bin/env python3
"""Compare original NAAMP fixed-site coordinates with dated Iowa DNR route PDF waypoints.

This is an external published-map *coordinate agreement* check, not evidence
that 2001–2015 stations remained physically unchanged. No Counts data read.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from build_naamp_observation_panel import SOURCE_PINS, make as panel_make
from run_public_naamp_feasibility import COORD_SHA
from audit_coordinates import audit as geometry_audit, km as haversine_km

PRIMARY_ERROR_METERS=100.0
SECONDARY_ERROR_METERS=250.0
STUDY_LAST_YEAR=2015
REFERENCE_DATE='2020-03-11'
ROUTE_NUMBER='360411'
STATE='Iowa'


def audit(runs: pd.DataFrame, stops: pd.DataFrame, coords: pd.DataFrame, reference: pd.DataFrame)->dict:
    required={'route_number','stop_no','latitude','longitude','reference_date','source_document_url'}
    if required-set(reference.columns): raise ValueError('Reference map CSV missing required columns')
    ref=reference[sorted(required)].copy()
    ref.route_number=ref.route_number.astype(str).str.strip()
    ref.stop_no=pd.to_numeric(ref.stop_no,errors='raise').astype(int)
    ref['latitude']=pd.to_numeric(ref.latitude,errors='raise')
    ref['longitude']=pd.to_numeric(ref.longitude,errors='raise')
    if (len(ref)!=10 or ref.route_number.nunique()!=1 or ref.route_number.iloc[0]!=ROUTE_NUMBER
            or set(ref.stop_no)!={1,2,3,4,5,6,7,8,9,10}):
        raise ValueError('Expected exactly one documented 10-stop route, not arbitrary map selection')
    if not (ref.reference_date.eq(REFERENCE_DATE)).all():
        raise ValueError('Route-map reference date changed; this document has a frozen identifier')
    if not ref.source_document_url.eq('https://www.iowadnr.gov/media/2019/download?inline=').all():
        raise ValueError('Independent official Iowa DNR route PDF provenance mismatch')
    if not np.isfinite(ref[['latitude','longitude']].to_numpy(float)).all():
        raise ValueError('Invalid map coordinates')
    if not (ref.latitude.between(24,50).all() and ref.longitude.between(-125,-66).all()):
        raise ValueError('Reference coordinates outside declared CONUS region')

    panel,cohort=panel_make(runs,stops)
    selected=panel.loc[(panel.state==STATE) & (panel.route_number.astype(str)==ROUTE_NUMBER)].copy()
    raw_geo,geom_summary=geometry_audit(coords)
    loc=raw_geo.loc[raw_geo.route_id.eq(ROUTE_NUMBER)].copy()
    out={'analysis':'naamp_iowa_dnr_2020_map_to_2001_2015_archive_crosscheck_v0_1',
         'reference_route':ROUTE_NUMBER,'state':STATE,
         'reference_creation_date':REFERENCE_DATE,
         'reference_document':'https://www.iowadnr.gov/media/2019/download?inline=',
         'source_date_after_naamp_study_window':True,
         'frog_outcomes_read':False,'nlcd_pixels_read':False,
         'n_map_reference_stops':len(ref),
         'n_eligible_naamp_runs_for_route':int(selected.run_id.nunique()),
         'n_naamp_coordinate_siteids_in_route':int(len(loc)),
         'n_field_verification_of_2001_2015_station_history':0,
         'coordinate_error_threshold_m':PRIMARY_ERROR_METERS,
         'sensitivity_error_threshold_m':SECONDARY_ERROR_METERS,
         'status':'INSUFFICIENT_IDENTITY_JOIN',
         'provenance_limit':'Two maps may share historical source coordinates. Map postdates study; coordinate agreement cannot establish field relocation history.'}
    if selected.empty:
        out['status']='ROUTE_NOT_IN_STANDARDIZED_NAAMP_COHORT'
        return out
    if selected.stop_number.isna().any(): raise ValueError('NAAMP stop position missing')
    selected['stop_no']=pd.to_numeric(selected.stop_number,errors='raise').astype(int)
    # Historical identity may be ambiguous: never select one SiteID after viewing map positions.
    cross=selected.groupby('stop_no').site_id.nunique()
    in_scope=selected.groupby('site_id').stop_no.nunique()
    ambiguous=set(cross[cross.ne(1)].index)
    ambiguous |= set(selected.loc[selected.site_id.isin(in_scope[in_scope.ne(1)].index),'stop_no'])
    out['n_stop_numbers_with_ambiguous_historical_siteid']=len(ambiguous)
    site_by_no=selected.drop_duplicates(['stop_no','site_id'])[['stop_no','site_id']]
    site_by_no=site_by_no.loc[~site_by_no.stop_no.isin(ambiguous)]
    # No route geometry fixes/reassignments after external map readback.
    merged=ref.merge(site_by_no,on='stop_no',how='left',validate='one_to_one')
    geo=loc.rename(columns={'site_id':'site_id','latitude':'naamp_latitude','longitude':'naamp_longitude'})
    merged=merged.merge(geo[['site_id','naamp_latitude','naamp_longitude','geometry_qc_status']],
                         on='site_id',how='left',validate='one_to_one')
    valid=(merged.naamp_latitude.notna() & merged.naamp_longitude.notna() &
           merged.geometry_qc_status.eq('pass_unverified'))
    merged['distance_m']=np.nan
    if valid.any():
        sub=merged.loc[valid]
        merged.loc[valid,'distance_m']=1000.0*haversine_km(
            sub.latitude.to_numpy(float),sub.longitude.to_numpy(float),
            sub.naamp_latitude.to_numpy(float),sub.naamp_longitude.to_numpy(float))
    d=merged.distance_m.dropna().astype(float)
    out.update({'status':'METADATA_COORDINATE_CROSSCHECK_ONLY' if len(d) else 'NO_COMPARABLE_COORDINATE',
       'n_documented_stops_with_unambiguous_naamp_site_identity':int(len(site_by_no)),
       'n_stops_with_comparable_geometry_pass_coordinates':int(len(d)),
       'n_stops_within_100m':int(d.le(PRIMARY_ERROR_METERS).sum()),
       'n_stops_within_250m':int(d.le(SECONDARY_ERROR_METERS).sum()),
       'median_documented_to_naamp_distance_m':float(d.median()) if len(d) else None,
       'max_documented_to_naamp_distance_m':float(d.max()) if len(d) else None,
       'n_map_stops_unresolved':int(len(ref)-len(d)),
       'distance_m_by_stop':[
           {'stop_no':int(r.stop_no),'comparable':bool(pd.notna(r.distance_m)),
            'distance_m':round(float(r.distance_m),3) if pd.notna(r.distance_m) else None}
           for r in merged.itertuples(index=False)]})
    return out


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser()
    for name in ('runs','stops','coords','reference','out'):
        p.add_argument('--'+name,required=True)
    a=p.parse_args()
    pins={'Runs.csv':sha(a.runs),'Stops.csv':sha(a.stops),'Coordinates.csv':sha(a.coords)}
    if pins!={**SOURCE_PINS,'Coordinates.csv':COORD_SHA}:
        raise ValueError('USGS source hash drift')
    document_sha=sha(a.reference)
    result=audit(pd.read_csv(a.runs,dtype=str,keep_default_na=False),
                 pd.read_csv(a.stops,dtype=str,keep_default_na=False),
                 pd.read_csv(a.coords,dtype={'RouteNumber':str,'SiteID':str}),
                 pd.read_csv(a.reference,dtype={'route_number':str}))
    result['source_sha256']={**pins,'iowa_reference_csv':document_sha}
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(list,dict))},indent=2,sort_keys=True))

if __name__=='__main__':main()
