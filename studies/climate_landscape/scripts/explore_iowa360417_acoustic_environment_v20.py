#!/usr/bin/env python3
"""Post-hoc descriptive frog/acoustic comparison at one Iowa route, 2010–2015.

This explicitly does NOT estimate a causal habitat-change effect; a pre-selected
single route, old NLCD Collection 1.0 labels, incomplete field-station
verification, observer/rain/season differences and ecological site dependence
prevent confirmatory inference. The one-year lag is enforced for ALL annual
NLCD predictors. Same-year mapped conversion is not a survey-date exposure.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from build_naamp_observation_panel import make as make_panel, SOURCE_PINS

COUNT_SHA='60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086'
ROUTE='360417'; STATE='Iowa'; CHANGEPIVOT=2012
LAND_CODES=('forest_pct','agriculture_pct','developed_pct','wetland_pct','open_water_pct')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare(runs:pd.DataFrame,stops:pd.DataFrame,counts:pd.DataFrame,
            land:pd.DataFrame):
    panel,_=make_panel(runs,stops)
    p=panel.loc[(panel.state.eq(STATE)) & (panel.route_number.astype(str).eq(ROUTE))].copy()
    if p.empty: raise ValueError('Chosen route absent')
    p['stop_number']=pd.to_numeric(p.stop_number,errors='raise').astype(int)
    if sorted(p.stop_number.unique().tolist())!=list(range(1,11)):
        raise ValueError('Stop-number coverage not 1–10')
    if (p.groupby('stop_number').site_id.nunique().ne(1).any() or
        p.groupby('site_id').stop_number.nunique().ne(1).any()):
        raise ValueError('Historic SiteID/stop mapping ambiguous')
    if p.duplicated(['run_id','stop_number']).any() or p.groupby('run_id').size().ne(10).any():
        raise ValueError('Inconsistent non-skipped survey sites')
    required={'RunID','StopNumber','Species','CallingIndex'}
    if not required.issubset(counts.columns):
        raise ValueError(f'Counts missing columns: {sorted(required-set(counts.columns))}')
    count=counts.loc[counts.RunID.isin(set(p.run_id))].copy()
    count['run_id']=count.RunID.astype(str).str.strip()
    count['stop_number']=pd.to_numeric(count.StopNumber,errors='raise').astype(int)
    count['species']=count.Species.astype(str).str.strip()
    count['ci']=pd.to_numeric(count.CallingIndex,errors='raise')
    if (~count.ci.isin([1,2,3])).any() or count.species.eq('').any():
        raise ValueError('Unexpected CI or unidentified Species in source rows')
    allowed=p[['run_id','stop_number']]
    joined=count.merge(allowed,on=['run_id','stop_number'],how='left',indicator=True,validate='many_to_one')
    if not joined._merge.eq('both').all():
        raise ValueError('Positive record for unsurveyed stop')
    # Observations are positive-only. Multiple rows for one taxon×run×stop
    # cannot count as multiple species; strongest index represents it once.
    dup_count=int(joined.duplicated(['run_id','stop_number','species']).sum())
    collapsed=(joined.groupby(['run_id','stop_number','species'],as_index=False)
                .ci.max())
    collapsed['strong']=collapsed.ci.ge(2)
    countstop=collapsed.groupby(['run_id','stop_number']).agg(
        any_species=('species','size'),strong_species=('strong','sum')).reset_index()
    p=p.merge(countstop,on=['run_id','stop_number'],how='left',validate='one_to_one')
    p[['any_species','strong_species']]=p[['any_species','strong_species']].fillna(0).astype(int)
    p['survey_year']=p.survey_year.astype(int)
    p['exposure_year']=p.survey_year-1
    p['era']=np.where(p.survey_year<CHANGEPIVOT,'pre',
              np.where(p.survey_year>CHANGEPIVOT,'post','year_2012_unordered'))
    required_l={'site_id','stop_number','radius_m','year',*LAND_CODES,'historic_field_station_verified'}
    if not required_l.issubset(land.columns):
        raise ValueError('Land-cover table does not match official v1.9 contract')
    l=land[list(required_l)].copy()
    l.site_id=l.site_id.astype(str)
    l.stop_number=pd.to_numeric(l.stop_number,errors='raise').astype(int)
    l.radius_m=pd.to_numeric(l.radius_m,errors='raise').astype(int)
    l.year=pd.to_numeric(l.year,errors='raise').astype(int)
    if l.duplicated(['site_id','stop_number','radius_m','year']).any():
        raise ValueError('Duplicate annual land class record')
    if l.historic_field_station_verified.astype(str).str.lower().eq('true').any():
        raise ValueError('Unjustified historical physical station verification')
    if not set(l.radius_m)=={250,1000}:
        raise ValueError('Both declared scales required')
    results=[]
    for radius in (250,1000):
        sub=l[l.radius_m.eq(radius)].drop(columns=['historic_field_station_verified','radius_m'])
        sub=sub.rename(columns={'year':'exposure_year'})
        rows=p.merge(sub,on=['site_id','stop_number','exposure_year'],
            how='left',validate='many_to_one',indicator=True)
        if not rows._merge.eq('both').all():
            raise ValueError('No strictly antecedent NLCD year available')
        if not rows.exposure_year.lt(rows.survey_year).all():
            raise ValueError('Future or same-year land classification leaked into prior exposure')
        rows=rows.drop(columns='_merge');rows['buffer_m']=radius
        results.append(rows)
    p=pd.concat(results,ignore_index=True)
    return p,collapsed,dup_count

def summarize(panel,collapsed,dup_count,land):
    if panel.groupby(['run_id','buffer_m']).size().ne(10).any():
        raise ValueError('Incorrect 10-stop sampling unit')
    # For an environmental readback-selected breakpoint, show raw acoustic
    # observations without P-value, regression or favorable taxon selection.
    rows=panel[panel.buffer_m.eq(250)].copy()
    run=rows.groupby(['run_id','survey_year','era']).agg(
        active_stops_any=('any_species',lambda s:int((s>0).sum())),
        active_stops_strong=('strong_species',lambda s:int((s>0).sum())),
        n_species_stop_cells_any=('any_species','sum'),
        n_species_stop_cells_strong=('strong_species','sum')).reset_index()
    yearly=run.groupby(['survey_year','era']).agg(
        n_surveys=('run_id','size'),
        mean_strong_stops=('active_stops_strong','mean'),
        mean_strong_species_stop_cells=('n_species_stop_cells_strong','mean'),
        mean_any_species_stop_cells=('n_species_stop_cells_any','mean')).reset_index()
    results=[]
    for radius in (250,1000):
        sub=panel[(panel.buffer_m==radius)&(panel.era.isin(['pre','post']))].copy()
        aggregated=(sub.groupby(['stop_number','site_id','era'],as_index=False)
           .agg(n_surveys=('run_id','nunique'),
                mean_strong_species=('strong_species','mean'),
                n_strong_species_cells=('strong_species','sum'),
                mean_any_species=('any_species','mean')))
        each=aggregated.pivot(index=['stop_number','site_id'],columns='era',
             values=['mean_strong_species','n_strong_species_cells','n_surveys'])
        npre=float(aggregated.loc[aggregated.era.eq('pre'),'n_strong_species_cells'].sum())
        npost=float(aggregated.loc[aggregated.era.eq('post'),'n_strong_species_cells'].sum())
        archived=land.loc[land.radius_m.eq(radius)].copy()
        archived.year=archived.year.astype(int)
        for (stop,site),r in each.iterrows():
            p=float(r.get(('mean_strong_species','pre'),np.nan))
            q=float(r.get(('mean_strong_species','post'),np.nan))
            a=archived[archived.stop_number.eq(stop)].sort_values('year')
            # Time-locked same class labels are a *descriptive nominal-source* series.
            fyear={int(x.year):float(x.forest_pct) for x in a.itertuples(index=False)}
            result={'radius_m':radius,'stop_number':int(stop),'site_id':str(site),
              'pre_mean_strong_species_per_survey':p,'post_mean_strong_species_per_survey':q,
              'post_minus_pre_mean_strong_species':q-p,
              'pre_strong_all_species_share':float(r.get(('n_strong_species_cells','pre'),0))/npre if npre else None,
              'post_strong_all_species_share':float(r.get(('n_strong_species_cells','post'),0))/npost if npost else None,
              'forest_pct_2011_nominal_map':fyear.get(2011),
              'forest_pct_2012_nominal_map':fyear.get(2012),
              'forest_pct_2011_to_2012_change':(fyear[2012]-fyear[2011])
                  if 2011 in fyear and 2012 in fyear else None}
            results.append(result)
    metadata=rows.drop_duplicates('run_id')
    observer=metadata.groupby('era').agg(
          n_survey_runs=('run_id','size'),n_unique_survey_dates=('survey_date','nunique'),
          n_observer_ids=('observer_id','nunique')).reset_index().to_dict(orient='records')
    rounds=metadata.groupby(['era','survey_round']).size().reset_index(name='n_runs').to_dict(orient='records')
    return {'analysis':'single_iowa_route_nlcd_C1V0_posthoc_acoustic_descriptives_v20',
       'status':'DESCRIPTIVE_ONLY_NO_CAUSAL_CLIMATE_OR_HABITAT_EFFECT',
       'route':'360417','n_runs':int(rows.run_id.nunique()),
       'n_surveyed_stops':len(rows),'n_distinct_species_positive':int(collapsed.species.nunique()),
       'n_source_duplicate_run_stop_species_rows_collapsed':dup_count,
       'positive_species_stop_observations':int(len(collapsed)),
       'n_focal_years':int(rows.survey_year.nunique()),
       'era_summary':observer,'rounds_by_era':rounds,
       'run_year_descriptives':yearly.to_dict(orient='records'),
       'all_ten_sites_both_radii':results,
       'mapped_breakpoint_2012_selected_after_environmental_readback':True,
       'no_confirmatory_inference_permitted':True,
       'stop_vs_route_not_independent':True,
       'historical_physical_station_continuity_confirmed':0,
       'forest_source_collection':'Annual NLCD C1V0 NOT C1V2',
       'survey_year_2012_excluded_from_before_after':True,
       '2012_land_class_transition_not_dated_within_calendar_year':True,
       'no_absence_or_breeding_success_inferred_from_acoustic_nondetection':True,
       'no_species_subgroup_was_selected_from_frog_outcomes':True,
       'no_weather_or_observer_adjustment_estimated':True,
       'interpretation':'Display unadjusted site-year acoustic patterns only; environmental classes and survey dates alone cannot identify a habitat conversion effect.'}

def main():
    p=argparse.ArgumentParser()
    for name in ('runs','stops','counts','landcover','out'):
        p.add_argument('--'+name,required=True)
    args=p.parse_args()
    hashes={k:sha(getattr(args,k.split('.')[0].lower())) for k in ('Runs.csv','Stops.csv','Counts.csv')}
    if hashes!={**SOURCE_PINS,'Counts.csv':COUNT_SHA}:
        raise ValueError('Original USGS input source SHA256 mismatch')
    land_sha=sha(args.landcover)
    r=pd.read_csv(args.runs,dtype=str,keep_default_na=False)
    s=pd.read_csv(args.stops,dtype=str,keep_default_na=False)
    c=pd.read_csv(args.counts,dtype=str,keep_default_na=False)
    l=pd.read_csv(args.landcover,dtype={'site_id':str})
    prepared,collapsed,ndups=prepare(r,s,c,l)
    report=summarize(prepared,collapsed,ndups,l)
    report.update({'source_sha256':{**hashes,'annual_nlcd_C1V0_15year_site_fractions_csv':land_sha},
       'strong_CI_definition':'CallingIndex 2 or 3, species-by-survey-stop positive cells',
       'n_same_year_landcover_predictors_used':0,
       'exact_years_2010_2011_pre_2012_excluded_2013_2015_post':True})
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,sort_keys=True,default=int)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('all_ten_sites_both_radii','run_year_descriptives','rounds_by_era')},
        indent=2,sort_keys=True,default=int))

if __name__=='__main__':main()
