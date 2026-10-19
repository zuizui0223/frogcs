#!/usr/bin/env python3
"""Transparent source-coverage amendment; preserves the stopped fixed-2008 test.

Select cutoff from Runs/Stops only before loading Counts in this source pass.
No sample threshold, lag, endpoint or scoring rule is changed after performance.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import numpy as np
import recent_site_history_forecast as core


def select_cutoff(targets):
    def count(rows):
        return {'surveys':len(rows), 'routes':len({r['route'] for r in rows})}
    candidates=[]
    for c in range(2008,2013):
        train=count([r for r in targets if r['year']<=c])
        test=count([r for r in targets if r['year']>c])
        passed=all(d['surveys']>=100 and d['routes']>=50 for d in (train,test))
        candidates.append({'cutoff':c,'training':train,'testing':test,'passes':passed})
    chosen=next((d['cutoff'] for d in candidates if d['passes']),None)
    return chosen,candidates


def metadata_plan():
    old,_=core.load_archived()
    item=old.base.get_json(old.base.ITEM_URL)
    raw={'Counts.csv':[]}
    for name in ('Runs.csv','Stops.csv'):
        data=old.base.get_bytes(old.base.find_file(item,name))
        if hashlib.sha256(data).hexdigest()!=old.base.PINS[name]:
            raise ValueError('metadata SHA256 drift')
        raw[name]=list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
    runs,_=old.base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=old.spatial.stop_matrix(raw,eligible)
    site=old.site_map(raw,eligible)
    targets=[]
    for key,g in runs.groupby(['State','RouteNumber','RunNumber'],sort=True):
        g=g.loc[~g.SurveyYear.duplicated(keep=False)]
        byyear={}
        for row in g.itertuples(index=False):
            rid=str(row.RunID); stops=sampled.get(rid,set())
            if len(stops)!=10 or any((rid,s) not in site for s in stops):continue
            ids=frozenset(site[(rid,s)] for s in stops)
            if len(ids)==10:byyear[int(row.SurveyYear)]=ids
        for year,ids in byyear.items():
            if byyear.get(year-1)!=ids or byyear.get(year-2)!=ids:continue
            if sum(y<=year-3 and s==ids for y,s in byyear.items())<3:continue
            targets.append({'year':year,'route':str(key[0])+':'+str(key[1])})
    if len(runs)!=7848 or len(targets)!=497:
        raise ValueError('metadata-only cohort does not reproduce first attempt')
    chosen,candidates=select_cutoff(targets)
    return chosen,{'counts_opened_during_cutoff_selection':False,
                   'source_eligible_surveys':len(runs),'structural_target_surveys':len(targets),
                   'candidates':candidates,'selected_cutoff':chosen}


def self_test():
    a=[{'year':y,'route':str(r)} for y in (2009,2010,2013,2014) for r in range(50)]
    chosen,audit=select_cutoff(a)
    assert chosen==2010 and len(audit)==5
    assert select_cutoff([{**r,'ignored_frog_outcome':9999} for r in a])==(chosen,audit)
    b=[{'year':y,'route':str(r)} for y in range(2006,2016) for r in range(49)]
    assert select_cutoff(b)[0] is None
    print('PASS: earliest metadata-only cutoff; ignored outcomes; unchanged source feasibility thresholds')


def run(output):
    cut,plan=metadata_plan()
    # This is printed BEFORE core.assemble downloads/reads Counts.csv.
    print('METADATA_PLAN_BEFORE_COUNTS',json.dumps(plan,sort_keys=True),flush=True)
    out={'analysis':'recent_site_history_source_coverage_amendment_2026_10_19',
         'original_2008_attempt':'STOPPED_WITHOUT_COEFFICIENTS',
         'amended_exploratory_not_original_frozen_design':True,'metadata_only_plan':plan,
         'no_frozen_main_changes':True,'not_cognitive_or_intergenerational_memory_test':True,
         'not_JAE_concentration_C_test':True,'current_k_conditioned_not_unconditional_forecast':True}
    if cut is None:
        out['status']='NO_SOURCE_SUPPORTED_SPLIT_STOP'
    else:
        frames,source=core.assemble()
        if source['selection_counts']['source_eligible_target_surveys']!=plan['structural_target_surveys']:
            raise ValueError('Counts-dependent structural gate: stop')
        train=[f for f in frames if f['year']<=cut]
        test=[f for f in frames if f['year']>cut]
        out.update({'source':source,'training_coverage':core.coverage(train),'test_coverage':core.coverage(test)})
        if any(len(p)<200 or core.coverage(p)['routes']<50 for p in (train,test)):
            out['status']='INFORMATIVE_SAMPLE_GATE_FAILED_DO_NOT_SELECT_ANOTHER_CUTOFF'
        else:
            models={};pred={}
            for name,extra in [('M0',None),('MR','recent'),('MO','older')]:
                models[name]=core.fit(train,extra)
                pred[name]=core.scores(np.asarray(models[name]['coefficients']),core.design(test,extra))
            out.update({'status':'EXECUTED_AMENDED_POST_HOC_FORECAST','models':models,
                        'heldout_test':core.summarize(test,pred),'by_test_year':{}})
            for year in sorted({f['year'] for f in test}):
                ix=np.array([f['year']==year for f in test])
                out['by_test_year'][str(year)]=core.summarize([f for f,b in zip(test,ix) if b],
                                                           {k:v[ix] for k,v in pred.items()},False)
            ix=np.array([f['same_observer'] for f in test])
            out['same_observer_three_visits_no_refit']=core.summarize([f for f,b in zip(test,ix) if b],
                                                                   {k:v[ix] for k,v in pred.items()})
            out['interpretation']='Temporal recency prediction, not complete habitat adjustment, detection correction, demographic or cognitive mechanism identification.'
            out['uncertainty_boundary']='Route bootstrap conditions on trained coefficients; training uncertainty and between-route spatial dependence excluded.'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('AMENDED_RESULT_JSON_BEGIN',flush=True)
    print(json.dumps(out,indent=2,sort_keys=True),flush=True)
    print('AMENDED_RESULT_JSON_END',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--output',type=Path,default=core.ROOT/'research/output/RECENT_HISTORY_AMENDED_2026-10-19.json')
    a=p.parse_args()
    if a.self_test:self_test()
    else:run(a.output)
