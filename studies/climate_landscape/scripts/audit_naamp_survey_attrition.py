#!/usr/bin/env python3
"""Response-blind NAAMP route/stop observation and skip-state transition audit.

Only SHA256-pinned Runs.csv and Stops.csv. This tests whether repeated-site
monitoring exposure is complete before any land-cover × CallingIndex analysis.
A skipped/absent stop is NEVER a zero frog observation or proven retirement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from build_naamp_observation_panel import SOURCE_PINS, _date, _year, make as complete_panel

SURVEY_YEAR_MIN, SURVEY_YEAR_MAX = 2001, 2015
SEASON_WINDOW_DAYS = 21


def same_season_day(d):
    d = pd.Timestamp(d)
    # Stable nonleap-year seasonal index; Feb 29 is assigned to Feb 28.
    if d.month == 2 and d.day == 29:
        return 58
    return int((pd.Timestamp(year=2001, month=d.month, day=d.day) - pd.Timestamp('2001-01-01')).days)


def candidate_runs(runs: pd.DataFrame) -> pd.DataFrame:
    required = {'RunID','SurveyDate','SurveyYear','UnifiedProtocol','RouteNumber',
                'RouteType','State','RunNumber','DaysSinceRain'}
    if required - set(runs.columns):
        raise ValueError(f'Missing source Runs columns: {sorted(required-set(runs.columns))}')
    records = []
    for r in runs.to_dict('records'):
        y = _year(r['SurveyYear']) or _year(r['SurveyDate'])
        d = _date(r['SurveyDate'])
        if y is None or pd.isna(d) or d.year != y or not SURVEY_YEAR_MIN <= y <= SURVEY_YEAR_MAX:
            continue
        rid = str(r['RunID']).strip()
        state = str(r['State']).strip()
        route = str(r['RouteNumber']).strip()
        roundno = str(r['RunNumber']).strip()
        if (str(r['UnifiedProtocol']).strip() != '1' or not rid or not state or
            not route or not str(r['RouteType']).strip() or roundno not in {'1','2','3','4'}):
            continue
        try:
            rain = float(r['DaysSinceRain'])
        except (ValueError, TypeError):
            continue
        if not np.isfinite(rain) or not 0 <= rain <= 180:
            continue
        records.append({'run_id':rid,'route_id':f'{state}:{route}',
                        'state':state,'survey_round':int(roundno),
                        'survey_year':int(y),'survey_date':pd.Timestamp(d)})
    out = pd.DataFrame(records)
    if out.empty: raise ValueError('No candidate surveys')
    if out.run_id.duplicated().any(): raise ValueError('Duplicate RunID in candidate sample')
    return out.sort_values(['route_id','survey_round','survey_year','run_id']).reset_index(drop=True)


def make_stop_records(stops: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    required={'RunID','StopNumber','SiteID','SkippedStop'}
    if required-set(stops.columns):
        raise ValueError(f'Missing Stops columns: {sorted(required-set(stops.columns))}')
    use=stops[stops.RunID.astype(str).isin(set(candidates.run_id))].copy()
    n=pd.to_numeric(use.StopNumber.astype('string').str.strip(),errors='coerce')
    if n.isna().any() or not n.between(1,10).all() or (n%1).ne(0).any():
        raise ValueError('Unexpected StopNumber outside integers 1..10')
    use['stop_no']=n.astype(int)
    use['run_id']=use.RunID.astype(str)
    if use.duplicated(['run_id','stop_no']).any():
        raise ValueError('Duplicate stop order in run')
    use['site_id']=use.SiteID.astype('string').str.strip().fillna('')
    skip=use.SkippedStop.astype('string').str.strip().fillna('')
    use['status']=np.select([skip.eq('0'),skip.eq('1')],['surveyed','skipped'],default='unknown')
    return use[['run_id','stop_no','site_id','status']].sort_values(['run_id','stop_no']).reset_index(drop=True)


def audit(runs: pd.DataFrame,stops: pd.DataFrame) -> dict:
    candidates=candidate_runs(runs)
    sampled, cohort_receipt=complete_panel(runs,stops)
    sr=make_stop_records(stops,candidates)
    counted=sr.groupby(['run_id','status']).size().unstack(fill_value=0)
    for name in ('surveyed','skipped','unknown'):
        if name not in counted: counted[name]=0
    counted['n_rows']=counted[['surveyed','skipped','unknown']].sum(axis=1)
    counted['n_ids']=sr.groupby('run_id').site_id.apply(lambda s:s.ne('').sum())
    cand=candidates.join(counted,on='run_id')
    for name in ('surveyed','skipped','unknown','n_rows','n_ids'):
        cand[name]=cand[name].fillna(0).astype(int)
    cand['complete_field_opportunity']=(cand.n_rows.eq(10)&cand.surveyed.eq(10)&cand.n_ids.eq(10))
    cand['partial_skipped']=(cand.skipped.gt(0))
    cand['unknown_stop_state']=(cand.unknown.gt(0)|cand.n_rows.lt(10))
    accepted=set(sampled.run_id)
    cand['in_complete_analysis_panel']=cand.run_id.isin(accepted)
    if (cand.in_complete_analysis_panel & ~cand.complete_field_opportunity).any():
        raise ValueError('Analysis full sample contains incomplete field opportunities')

    # Derive consecutive-year matched-season pairs without asking about frog calls.
    c=cand.copy()
    grp=['route_id','survey_round','survey_year']
    multi=c.groupby(grp).run_id.transform('size')
    n_nonunique=int(c.loc[multi.gt(1),'run_id'].nunique())
    c=c.loc[multi.eq(1)].copy()
    pairs=[]
    stoprows={str(run):{int(r.stop_no):r for r in g.itertuples(index=False)}
              for run,g in sr.groupby('run_id')}
    for (route,roundno),g in c.groupby(['route_id','survey_round'],sort=False):
        g=g.sort_values(['survey_year','run_id'])
        for a,b in zip(g.iloc[:-1].itertuples(index=False),g.iloc[1:].itertuples(index=False)):
            if int(b.survey_year)-int(a.survey_year)!=1: continue
            if abs(same_season_day(a.survey_date)-same_season_day(b.survey_date))>SEASON_WINDOW_DAYS:
                continue
            summary={'route':route,'before_full':bool(a.complete_field_opportunity),
                     'after_full':bool(b.complete_field_opportunity),
                     'before_skipped':bool(a.partial_skipped),
                     'after_skipped':bool(b.partial_skipped),
                     'before_accepted':bool(a.in_complete_analysis_panel),
                     'after_accepted':bool(b.in_complete_analysis_panel)}
            aa=stoprows.get(a.run_id,{})
            bb=stoprows.get(b.run_id,{})
            sampled_to_skipped=skipped_to_sampled=identity_changed=0
            for no in range(1,11):
                ra=aa.get(no); rb=bb.get(no)
                if ra is None or rb is None: continue
                if not ra.site_id or not rb.site_id or ra.site_id != rb.site_id:
                    if ra.site_id and rb.site_id and ra.site_id != rb.site_id:
                        identity_changed+=1
                    continue
                if ra.status=='surveyed' and rb.status=='skipped': sampled_to_skipped+=1
                elif ra.status=='skipped' and rb.status=='surveyed': skipped_to_sampled+=1
            summary.update({'sampled_to_skipped':sampled_to_skipped,
                            'skipped_to_sampled':skipped_to_sampled,
                            'same_stop_number_different_siteid':identity_changed})
            pairs.append(summary)
    p=pd.DataFrame(pairs)
    def n(cond): return int(cond.sum()) if len(p) else 0
    def prop(a,b): return float(a/b) if b else None
    report={
      'analysis':'naamp_longitudinal_survey_attrition_and_skip_history_v0_1',
      'source_only_no_frog_responses':True,
      'no_automatic_retirement_or_extinction_classification':True,
      'n_pre_stop_qc_candidate_runs':int(len(cand)),
      'n_complete_standardized_runs_after_all_qc':int(len(accepted)),
      'n_complete_field_opportunity_runs_before_temperature_qc':int(cand.complete_field_opportunity.sum()),
      'n_candidate_runs_with_one_or_more_skipped_stops':int(cand.partial_skipped.sum()),
      'n_candidate_runs_with_unknown_stop_state_or_missing_stop_rows':int(cand.unknown_stop_state.sum()),
      'n_candidate_runs_not_in_final_analysis_panel':int((~cand.in_complete_analysis_panel).sum()),
      'n_candidate_runs_field_complete_but_not_final_analysis':int((cand.complete_field_opportunity & ~cand.in_complete_analysis_panel).sum()),
      'n_candidate_stop_records_surveyed':int(sr.status.eq('surveyed').sum()),
      'n_candidate_stop_records_explicitly_skipped':int(sr.status.eq('skipped').sum()),
      'n_candidate_stop_records_unknown_skip_code':int(sr.status.eq('unknown').sum()),
      'n_excluded_ambiguous_duplicate_route_round_year_runids':n_nonunique,
      'n_adjacent_year_same_season_route_round_pairs':int(len(p)),
      'n_pair_both_full_field_opportunity':n(p.before_full & p.after_full) if len(p) else 0,
      'n_pair_before_full_after_partial':n(p.before_full & ~p.after_full) if len(p) else 0,
      'n_pair_before_partial_after_full':n(~p.before_full & p.after_full) if len(p) else 0,
      'n_pair_both_incomplete':n(~p.before_full & ~p.after_full) if len(p) else 0,
      'n_pair_both_in_final_analysis_panel':n(p.before_accepted & p.after_accepted) if len(p) else 0,
      'n_same_id_sampled_to_skipped_stop_transitions':int(p.sampled_to_skipped.sum()) if len(p) else 0,
      'n_same_id_skipped_to_sampled_stop_transitions':int(p.skipped_to_sampled.sum()) if len(p) else 0,
      'n_same_order_siteid_replacement_transitions':int(p.same_stop_number_different_siteid.sum()) if len(p) else 0,
      'complete_pair_fraction_all_matched_rounds':prop(n(p.before_full & p.after_full) if len(p) else 0,len(p)),
      'cohort_receipt':cohort_receipt,
      'interpretation':'Skipped or missing stops are not zero acoustic responses. No documented cause of skipped stops, site retirement, habitat destruction or persistence is recoverable from this audit.'
    }
    return report


def main():
    cli=argparse.ArgumentParser()
    for k in ('runs','stops','out'):cli.add_argument('--'+k,required=True)
    args=cli.parse_args()
    digest={'Runs.csv':hashlib.sha256(Path(args.runs).read_bytes()).hexdigest(),
            'Stops.csv':hashlib.sha256(Path(args.stops).read_bytes()).hexdigest()}
    if digest != SOURCE_PINS:
        raise ValueError('Source SHA256 drift')
    runs=pd.read_csv(args.runs,dtype=str,keep_default_na=False)
    stops=pd.read_csv(args.stops,dtype=str,keep_default_na=False)
    rec=audit(runs,stops)
    rec['source_sha256']=digest
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(rec,indent=2,sort_keys=True,default=int)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in rec.items() if not isinstance(v,dict)},indent=2,sort_keys=True))

if __name__=='__main__':main()
