#!/usr/bin/env python3
"""Response-blind NAAMP physical-stop identity *stability* QC.

Data: original checksum-pinned Runs/Stops and coordinate records.  No Counts.csv.
A consistent SiteID / stop number across years is necessary but NOT sufficient
for externally corroborated historical physical-station continuity.

No filters, spatial-coordinate edits, thresholds or site classification depend
on the frog outcomes. Findings are feasibility information only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
from audit_coordinates import audit as geometry_audit
from build_naamp_observation_panel import make as build_panel, SOURCE_PINS
from run_public_naamp_feasibility import COORD_SHA, yearly_pairs


def audit_metadata(runs:pd.DataFrame,stops:pd.DataFrame,coords:pd.DataFrame) -> dict:
    panel, cohort = build_panel(runs,stops)
    geo, geom_receipt = geometry_audit(coords)
    if panel.empty:
        raise ValueError('No complete standardized runs with physical stop IDs')
    # Normalize stop number; 01 and 1 encode the same numeric stop.
    order=pd.to_numeric(panel.stop_number,errors='coerce')
    if order.isna().any() or not order.between(1,10).all() or (order%1!=0).any():
        raise ValueError('StopNumber is not a standard integer 1-10')
    panel=panel.assign(stop_no=order.astype(int))
    if panel.duplicated(['run_id','stop_no']).any():
        raise ValueError('Duplicated StopNumber in a run')
    # This invariant concerns recorded stop-order identity, not true geolocation.
    bysite=panel.groupby(['route_id','site_id'],sort=True).agg(
        years=('survey_year','nunique'), visits=('run_id','nunique'),
        stop_positions=('stop_no','nunique'),first_year=('survey_year','min'),
        last_year=('survey_year','max')).reset_index()
    bysite['stop_order_stable']=bysite.stop_positions.eq(1)
    geo=geo.rename(columns={'route_id':'route_number'})
    join=bysite.assign(route_number=bysite.route_id.str.split(':',n=1).str[-1])
    join=join.merge(geo[['route_number','site_id','geometry_qc_status']],
                    on=['route_number','site_id'],how='left',validate='many_to_one')
    join['geometry_qc_status']=join.geometry_qc_status.fillna('no_coordinate_match')
    join['provisional_only']=join.stop_order_stable & join.geometry_qc_status.eq('pass_unverified')
    # Strictly descriptive opportunities: fixed metadata stop number across years.
    pairs=yearly_pairs(panel)
    stableids=set(map(tuple,join.loc[join.stop_order_stable,['route_id','site_id']].itertuples(index=False,name=None)))
    geompairs=set(map(tuple,join.loc[join.provisional_only,['route_id','site_id']].itertuples(index=False,name=None)))
    if len(pairs):
        pair_keys=list(zip(pairs.route_id,pairs.site_id))
        pair_stable=sum(key in stableids for key in pair_keys)
        pair_geom=sum(key in geompairs for key in pair_keys)
    else:pair_stable=pair_geom=0
    repeated=bysite.years.ge(2)
    changed=bysite.stop_order_stable.eq(False)
    report={
        'analysis':'naamp_site_identity_temporal_consistency_geometry_only_v0_1',
        'counts_csv_read':False, 'frog_response_read':False,
        'sites_externally_verified':0,
        'coordinate_fix_after_frog_outcome':False,
        'status':'metadata_consistency_only_not_historical_field_site_verification',
        'n_runs':int(panel.run_id.nunique()),
        'n_surveys_stops':int(len(panel)),
        'n_routes':int(panel.route_id.nunique()),
        'n_route_site_keys':int(len(bysite)),
        'n_sites_surveyed_two_or_more_years':int(repeated.sum()),
        'n_route_site_keys_consistent_stop_number':int((~changed).sum()),
        'n_route_site_keys_stop_number_changed':int(changed.sum()),
        'n_repeated_year_sites_stop_number_changed':int((repeated & changed).sum()),
        'n_consistent_site_keys_geometry_pass_unverified':int(join.provisional_only.sum()),
        'n_adjacent_year_same_season_stop_pairs':int(len(pairs)),
        'n_adjacent_year_pairs_consistent_stop_number':int(pair_stable),
        'n_adjacent_year_pairs_consistent_and_geometry_pass_unverified':int(pair_geom),
        'n_adjacent_year_pairs_requiring_independent_site_corroboration':int(pair_geom),
        'n_pairs_true_physical_continuity_independently_confirmed':0,
        'geometry_audit':geom_receipt,
        'cohort_audit':cohort,
        'warning':'Stable recorded SiteID/StopNumber does not prove unchanged physical station or wetland. Satellite 30m site-level inference remains blocked.'
    }
    return report


def sha256(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runs',required=True)
    ap.add_argument('--stops',required=True)
    ap.add_argument('--coords',required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    hashes={'Runs.csv':sha256(args.runs),'Stops.csv':sha256(args.stops),'Coordinates.csv':sha256(args.coords)}
    if hashes!={**SOURCE_PINS,'Coordinates.csv':COORD_SHA}:
        raise ValueError('Unpinned official NAAMP source file')
    d=audit_metadata(pd.read_csv(args.runs,dtype=str,keep_default_na=False),
                     pd.read_csv(args.stops,dtype=str,keep_default_na=False),
                     pd.read_csv(args.coords,dtype={'RouteNumber':str,'SiteID':str}))
    d['source_sha256']=hashes
    path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(d,indent=2,sort_keys=True,default=int)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in d.items() if not isinstance(v,dict)},indent=2,sort_keys=True))

if __name__=='__main__':main()
