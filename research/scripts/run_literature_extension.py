"""Prespecified additions, paired stage ablations; no observation-link fitting."""
import argparse
import hashlib
import itertools
import json
import numpy as np
import pandas as pd
from extension_annual_summary_20261029 import summarize_years
from common_scale_comparison import weighted_core
from separate_mechanism_observation import empirical_weights
from nee_context_robustness import ROOT,load

OUT=ROOT/'research/results/literature_extension_20261029'
CONTEXTS=[dict(context='original',sa=20,da=0,dduration=40,sg=.014,dg=.015),
          dict(context='D_first_S_overtakes',sa=20,da=0,dduration=60,sg=.030,dg=.015),
          dict(context='S_first_D_overtakes',sa=0,da=20,dduration=60,sg=.014,dg=.030)]


def design():
    cases=[]
    for ctx,(family,hs,hd),risk,edge in itertools.product(CONTEXTS,[('baseline',0.,0.),('shared_S',1.,0.),('shared_D',0.,1.),('shared_both',1.,1.)],[False,True],['dynamic','frozen','no_DS','no_SD','frog_reverse']):
        cases.append(dict(**ctx,family=family,hs=hs,hd=hd,risk=risk,edge=edge))
    for ctx,risk,h in itertools.product(CONTEXTS,[False,True],[.5,2.]):
        cases.append(dict(**ctx,family='shared_both_sensitivity',hs=h,hd=h,risk=risk,edge='dynamic'))
    for i,c in enumerate(cases):c['case']=i
    return pd.DataFrame(cases)


def evaluate(cases,tag,dt,levels=9):
    rows=[]
    for c in cases.to_dict('records'):
        for v,s,d in itertools.product([0.,1.],np.linspace(.25,2.,levels),np.linspace(.25,2.,levels)):
            rows.append(dict(**c,vegetation=v,S_source=s,D_source=d))
    de=pd.DataFrame(rows);frames=[]
    de['size_mode']=np.where(de.edge=='frozen','frozen','dynamic')
    for (risk,mode),g in de.groupby(['risk','size_mode']):
        g=g.reset_index(drop=True);path=OUT/f'{tag}_{int(risk)}_{mode}_cells.csv.gz'
        if path.exists():
            su=pd.read_csv(path)
            np.testing.assert_array_equal(su[['case','vegetation','S_source','D_source']],g[['case','vegetation','S_source','D_source']])
        else:
            params=[dict(community='FSD',roles=15,refuge_order='D',vegetation=r.vegetation,f_arrival=20.,s_arrival=float(r.sa),d_arrival=float(r.da),attack_scale=.5,cue=0.,reverse=r.edge=='frog_reverse',rho=.75) for r in g.itertuples()]
            controls=dict(cover_SF=1.,cover_DF=0.,cover_DS=0.,cover_SD=0.,support_DF=0.,support_DS=0.,emerge_survival=0.,emerge_exposure=0.,cue_SD=0.,edge_SD=(g.edge!='no_SD').to_numpy(float),edge_DS=(g.edge!='no_DS').to_numpy(float))
            opts=dict(pathway_controls=controls,stage_durations=np.column_stack([np.full(len(g),45.),np.full(len(g),80.),g.dduration]),functional_response='litter',behavioral_refuge=bool(risk),handling_s=g.hs.to_numpy(),handling_d=g.hd.to_numpy(),s_growth=g.sg.to_numpy(),d_growth=g.dg.to_numpy(),sd_size_mode=mode)
            su=summarize_years(params,years=80,window=20,dt=dt,source_cohorts=np.column_stack([np.ones(len(g)),g.S_source,g.D_source]),seasonal_options=opts,conversion=4.)
            su=pd.concat([g,su],axis=1);su.to_csv(path,index=False,compression={'method':'gzip','mtime':0})
        frames.append(su);print('Finished',tag,risk,mode,len(g),flush=True)
    return pd.concat(frames,ignore_index=True)


def summarize(cells,d,tag,levels=9):
    macro=pd.read_csv(ROOT/'research/results/scale_comparison_20261029/macro_common_estimators.csv')
    macro=macro[(macro.vegetation=='binary')&(macro.x_transform=='rank')&(macro.y_transform=='rank')&(macro.adjustment=='space')&(macro['mode']=='pooled')]
    rows=[];mortality=[]
    for case,g in cells.groupby('case'):
        g=g.sort_values(['vegetation','S_source','D_source']);meta=g.iloc[0][['case','context','family','hs','hd','risk','edge']].to_dict()
        for bg in ['uniform','target_group']:
            r=weighted_core(g.D_source.to_numpy(),g.S_source.to_numpy(),g.vegetation.to_numpy(),g.F_B.to_numpy(),empirical_weights(d,bg,levels),'rank','rank')
            q=macro[macro.background==bg].set_index('term')
            rows.append(dict(**meta,background=bg,simultaneous_signs=bool(r['OS']<0 and r['OV']<0 and r['SV']>0),all_three_intervals=all(q.loc[t,'low']<=r[t]<=q.loc[t,'high'] for t in ['OS','OV','SV']),conditional_high_OS_within_interval=bool(q.loc['OS_high','low']<=r['OS_high']<=q.loc['OS_high','high']),**r))
        for v in [0.,1.]:
            for s,o in itertools.product([.25,2.],[.25,2.]):
                z=g[(g.vegetation==v)&(g.S_source==s)&(g.D_source==o)].iloc[0]
                mortality.append(dict(**meta,vegetation=v,S_source=s,D_source=o,**{k:z[k] for k in ['F_B','F_fraction','audit_H_DF','audit_H_SF','F_killed_by_S','F_killed_by_D','S_killed_by_D','D_killed_by_S','D_killed_by_F','minimum_F_survival']}))
    pd.DataFrame(rows).to_csv(OUT/f'{tag}_coefficients.csv',index=False)
    pd.DataFrame(mortality).to_csv(OUT/f'{tag}_corner_mortality.csv',index=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--half-step',action='store_true');parser.add_argument('--resolution-audit',action='store_true');a=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);de=design();de.to_csv(OUT/'design.csv',index=False)
    crossover=[]
    for c in CONTEXTS:
        lo=max(c['sa'],c['da']);hi=min(c['sa']+80,c['da']+c['dduration'])
        cross=(c['sg']*c['sa']-c['dg']*c['da'])/(c['sg']-c['dg'])
        crossover.append(dict(**c,overlap_start=lo,overlap_end=hi,crossing_day=cross,actual_crossing=lo<cross<hi))
    assert [r['actual_crossing'] for r in crossover]==[False,True,True]
    pd.DataFrame(crossover).to_csv(OUT/'size_crossovers.csv',index=False)
    if a.resolution_audit:
        # Outcome-triggered numerical audit, never a new selection/fit.
        # Include every uniform marginal-overlap case plus baseline and S-budget anchor.
        scores=pd.read_csv(OUT/'primary_coefficients.csv')
        ids=set(scores.loc[(scores.background=='uniform')&scores.all_three_intervals,'case'])
        anchor=de[(de.context=='original')&de.family.isin(['baseline','shared_S'])&(~de.risk)&(de.edge=='dynamic')]
        ids.update(anchor['case']);selected=de[de['case'].isin(ids)]
        cells=evaluate(selected,'resolution21',.25,levels=21);summarize(cells,load(),'resolution21',levels=21)
        cells=evaluate(selected,'audit_half_step',.125);summarize(cells,load(),'audit_half_step')
    elif a.half_step:
        selected=de[(de.family.isin(['baseline','shared_both']))&(~de.risk)&(de.edge=='dynamic')]
        cells=evaluate(selected,'half_step',.125);summarize(cells,load(),'half_step')
    else:
        cells=evaluate(de,'primary',.25);summarize(cells,load(),'primary')
        # Off extension must reproduce the archived 9x9 anchor.
        old=pd.read_csv(ROOT/'research/results/mechanism_observation_20261029/dense9_None_cells.csv.gz')
        old=old[(old.model_id==1479)&(old.block_id==0)].sort_values(['vegetation','S_source','D_source'])
        new=cells[(cells.context=='original')&(cells.family=='baseline')&(~cells.risk)&(cells.edge=='dynamic')].sort_values(['vegetation','S_source','D_source'])
        np.testing.assert_allclose(new[['F_B','F_fraction','audit_H_DF','audit_H_SF']],old[['F_B','F_fraction','audit_H_DF','audit_H_SF']],atol=1e-12)
        (OUT/'receipt.json').write_text(json.dumps(dict(cases=len(de),cells=len(cells),rank_analysis_fixed=True,calling_link_fitted=False,baseline_replayed=True,parameters_empirically_calibrated=False,
            source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'research/scripts/stage_vegetation_network.py',ROOT/'research/scripts/stage_network_extension_20261029.py',ROOT/'research/scripts/extension_annual_summary_20261029.py']}),indent=2)+'\n')


if __name__=='__main__':main()
