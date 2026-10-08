#!/usr/bin/env python3
"""Outcome-blind roadside traffic/noise history of standardized NAAMP stops.

Runs.csv and Stops.csv only. Quantifies how often repeated route-site annual
pairs contain comparable recorded traffic and listening-impaired measures.
This is NOT a measure of land cover, frog behavior, or traffic causality.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from build_naamp_observation_panel import make as build_panel, SOURCE_PINS
from run_public_naamp_feasibility import yearly_pairs


def numeric(col:pd.Series)->pd.Series:
    return pd.to_numeric(col.astype('string').str.strip(),errors='coerce')


def audit(runs:pd.DataFrame,stops:pd.DataFrame)->dict:
    panel,cohort=build_panel(runs,stops)
    needed={'RunID','SiteID','CarCount','MassNoiseIndex','Noise','TimeOut'}
    if needed-set(stops.columns):
        raise ValueError(f'missing stop fields: {sorted(needed-set(stops.columns))}')
    a=stops[list(needed)].copy()
    a=a.rename(columns={'RunID':'run_id','SiteID':'site_id'})
    a.run_id=a.run_id.astype('string').str.strip()
    a.site_id=a.site_id.astype('string').str.strip()
    if a.duplicated(['run_id','site_id']).any():
        raise ValueError('Duplicate source RunID×SiteID cannot be joined')
    x=panel.merge(a,on=['run_id','site_id'],validate='one_to_one',how='left',indicator=True)
    if not x._merge.eq('both').all():
        raise ValueError('Missing source Stops metadata for eligible panel')
    car=numeric(x.CarCount)
    mass=numeric(x.MassNoiseIndex)
    noise=numeric(x.Noise)
    timeout=numeric(x.TimeOut)
    x['car_valid']=car.where(car.ge(0) & np.isfinite(car))
    x['mass_valid']=mass.where(mass.between(0,4) & (mass%1).eq(0))
    x['noise_valid']=noise.where(noise.isin([0,1]))
    x['timeout_valid']=timeout.where(timeout.isin([0,1]))
    x['impaired']=np.where(x.mass_valid.notna(),(x.mass_valid>=2).astype(float),x.noise_valid)
    x['observer_id']=x.observer_id.fillna('').astype(str).str.strip()
    # Resolve candidate one-year, same-round repeat opportunity with exactly
    # one survey in each year. Multiple surveys per year are excluded, not selected.
    pairs=yearly_pairs(panel)
    y=x[['route_id','site_id','survey_round','survey_year','car_valid','impaired','timeout_valid','observer_id']].copy()
    y=y.rename(columns={'survey_year':'year'})
    counts=y.groupby(['route_id','site_id','survey_round','year']).size().rename('visits')
    y=y.join(counts,on=['route_id','site_id','survey_round','year'])
    y=y[y.visits.eq(1)].drop(columns='visits')
    if y.duplicated(['route_id','site_id','survey_round','year']).any():
        raise ValueError('non-unique annual site-round after eligibility filter')
    l=pairs.merge(y,left_on=['route_id','site_id','survey_round','from_year'],
                  right_on=['route_id','site_id','survey_round','year'],validate='one_to_one')
    l=l.drop(columns='year').rename(columns={c:c+'_before' for c in ('car_valid','impaired','timeout_valid','observer_id')})
    j=l.merge(y,left_on=['route_id','site_id','survey_round','to_year'],
              right_on=['route_id','site_id','survey_round','year'],validate='one_to_one').drop(columns='year')
    car_good=j.car_valid_before.notna() & j.car_valid.notna()
    imp_good=j.impaired_before.notna() & j.impaired.notna()
    time_good=j.timeout_valid_before.notna() & j.timeout_valid.notna()
    observer_good=j.observer_id_before.ne('') & j.observer_id.ne('')
    same=observer_good & j.observer_id.eq(j.observer_id_before)
    delta=(j.loc[car_good,'car_valid']-j.loc[car_good,'car_valid_before']).astype(float)
    record={
        'analysis':'naamp_response_blind_traffic_detection_temporal_covariate_qc_v0_1',
        'frog_outcome_read':False, 'annual_landcover_read':False,
        'n_runs':int(panel.run_id.nunique()), 'n_stops':len(panel),
        'n_adjacent_year_same_season_site_pairs':int(len(pairs)),
        'n_car_count_valid_visits':int(x.car_valid.notna().sum()),
        'n_acoustic_impairment_valid_visits':int(x.impaired.notna().sum()),
        'n_timeout_valid_visits':int(x.timeout_valid.notna().sum()),
        'n_complete_car_count_pairs':int(car_good.sum()),
        'n_complete_acoustic_impairment_pairs':int(imp_good.sum()),
        'n_complete_timeout_pairs':int(time_good.sum()),
        'n_observer_id_complete_pairs':int(observer_good.sum()),
        'n_same_observer_pairs':int(same.sum()),
        'n_complete_car_noise_observer_pairs':int((car_good & imp_good & observer_good).sum()),
        'n_increasing_car_count_pairs':int((delta>0).sum()),
        'n_decreasing_car_count_pairs':int((delta<0).sum()),
        'n_unchanged_car_count_pairs':int((delta==0).sum()),
        'median_car_count_change_in_comparable_pairs':float(delta.median()) if len(delta) else None,
        'data_release_gate':'comparable roadside listening conditions, not verified habitat conversion',
        'cohort_receipt':cohort,
        'interpretation':'Traffic/noise changes may influence detection or behavior. They cannot be ignored when linking land-use change to acoustic site use.'
    }
    return record


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--runs',required=True);p.add_argument('--stops',required=True);p.add_argument('--out',required=True)
    a=p.parse_args()
    dig={'Runs.csv':sha(a.runs),'Stops.csv':sha(a.stops)}
    if dig!=SOURCE_PINS:raise ValueError('Pinned USGS runs/stops hash mismatch')
    runs=pd.read_csv(a.runs,dtype=str,keep_default_na=False)
    stops=pd.read_csv(a.stops,dtype=str,keep_default_na=False)
    rec=audit(runs,stops);rec['input_sha256']=dig
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(rec,indent=2,sort_keys=True,default=int)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in rec.items() if not isinstance(v,dict)},indent=2,sort_keys=True))

if __name__=='__main__':main()
