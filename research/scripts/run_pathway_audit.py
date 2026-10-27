"""Directed causal interventions in the selected synthetic model, not a field fit.

Replays the complete 3x3 source grid and both vegetation levels; primary
interpretation stays on the previously selected D=1..2, S=.25..2 rectangle.
All mortality is in normalized cohort units, never animal counts in NAAMP.
"""
import argparse
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from stage_vegetation_network import simulate
from multiyear_stage_network import simulate_years

OUT=Path(__file__).resolve().parents[1]/'results/pathway_audit_20261027'
EDGES=['edge_SF','edge_DF','edge_DS','edge_SD','edge_FE','cue_SF','cue_SD']
VEG=['cover_SF','cover_DF','cover_DS','support_DF','support_DS','emerge_survival','emerge_exposure']


def variants():
    v={'full':{}}
    for key in EDGES+VEG:v['no_'+key]={key:0.}
    for key,keys in {'frog_refuge':['cover_SF','cover_DF'],
                     'D_support':['support_DF','support_DS'],
                     'emergence':['emerge_survival','emerge_exposure']}.items():
        v['no_'+key]=dict.fromkeys(keys,0.)
    # Factorial predator pathways: which combinations support the pattern?
    keys=['edge_DS','edge_SD','cue_SF','cue_SD']
    for values in itertools.product([0.,1.],repeat=4):
        v['pred_'+''.join(str(int(x)) for x in values)]=dict(zip(keys,values))
    # Separate the two emergence mechanisms and their interactions with refuge/support.
    groups=[['cover_SF','cover_DF'],['support_DF','support_DS'],
            ['cover_DS'],['emerge_survival'],['emerge_exposure']]
    for values in itertools.product([0.,1.],repeat=5):
        v['veg_'+''.join(str(int(x)) for x in values)]={k:x for group,x in zip(groups,values) for k in group}
    return v


def design(labels):
    rows=[];controls=[];kernels=[];sources=[]
    for label,c in labels.items():
        for v,s,d in itertools.product([0.,1.],[.25,1.,2.],[.25,1.,2.]):
            rows.append(dict(variant=label,vegetation=v,S_source=s,D_source=d))
            controls.append(c)
            kernels.append(dict(roles=15,vegetation=v,refuge_order='S',f_arrival=50.,
                                attack_scale=1.5,cue=3.,rho=.5))
            sources.append([1.,s,d])
    return pd.DataFrame(rows),kernels,np.array(sources),{
        k:np.array([c.get(k,1.) for c in controls]) for k in EDGES+VEG}


def summarize(tr,des):
    tr=tr.copy()
    # Death fractions always use the start of the corresponding cohort.
    for col,g in [('F_killed_by_S','F'),('F_killed_by_D','F'),('S_killed_by_D','S'),
                  ('D_killed_by_S','D'),('D_killed_by_F','D'),('D_failure','D')]:
        tr[col+'_fraction']=tr[col]/tr[g+'_B']
    metrics=[x for x in tr if x.startswith(('F_','S_','D_','audit_')) and x not in ('F_source','S_source','D_source')]
    tail=tr[tr.year>tr.year.max()-20]
    su=tail.groupby('scenario_id')[metrics].mean().join(des).reset_index()
    for g in 'FSD':su[g+'_B_sd']=tail.groupby('scenario_id')[g+'_B'].std(ddof=0).to_numpy()
    return su


def contrasts(su):
    rows=[]
    for label,q in su.groupby('variant'):
        ix=q.set_index(['vegetation','S_source','D_source'])
        for dlo,dhi in [(.25,2.),(1.,2.)]:
            ds=lambda v,s:(ix.loc[(v,s,dhi),'F_B']-ix.loc[(v,s,dlo),'F_B'])/(dhi-dlo)
            ss=lambda v:(ix.loc[(v,2.,1.),'F_B']-ix.loc[(v,.25,1.),'F_B'])/1.75
            dv=ds(1.,1.)-ds(0.,1.);sv=ss(1.)-ss(0.)
            sd=ds(1.,2.)-ds(1.,.25)
            rows.append(dict(variant=label,D_low=dlo,D_high=dhi,DV=dv,SV=sv,SD=sd,
                             D_highS=ds(1.,2.),all_three=bool(dv<-1e-6 and sv>1e-6 and sd<-1e-6 and ds(1.,2.)<-1e-6)))
    return pd.DataFrame(rows)


def run(label,labels,years=80,dt=.25):
    des,kernel,source,controls=design(labels)
    tr=simulate_years(kernel,years=years,dt=dt,source_cohorts=source,
                      seasonal_options={'diagnostics':True,'pathway_controls':controls})
    su=summarize(tr,des)
    su.to_csv(OUT/(label+'_summary.csv'),index=False)
    contrasts(su).to_csv(OUT/(label+'_contrasts.csv'),index=False)
    tr.to_csv(OUT/(label+'_trajectories.csv.gz'),index=False,compression={'method':'gzip','mtime':0})
    des.to_csv(OUT/(label+'_design.csv'),index=False)
    # Fixed-input seasonal replay: identical starting cohorts for all interventions.
    # Distinguishes the within-season effects from accumulated annual feedback.
    reference=su[su.variant=='full'].set_index(['vegetation','S_source','D_source'])
    init=np.array([reference.loc[(r.vegetation,r.S_source,r.D_source),['F_B','S_B','D_B']].to_numpy(float)
                   for r in des.itertuples()])
    season=simulate([{k:v for k,v in p.items() if k!='rho'} for p in kernel],dt=dt,
                    initial_cohorts=init,pathway_controls=controls,diagnostics=True)
    season=season[[x for x in season if x.startswith(('F_','S_','D_','audit_'))]].join(des)
    season.to_csv(OUT/(label+'_fixed_cohort_replay.csv'),index=False)
    print('Completed',label,len(des),flush=True)
    return su


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sensitivity',action='store_true');a=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    all_variants=variants()
    if a.sensitivity:
        small={k:v for k,v in all_variants.items() if k=='full' or k.startswith('no_')}
        for label,kw in [('half_step',dict(dt=.125)),('horizon160',dict(years=160))]:run(label,small,**kw)
        return
    su=run('primary',all_variants)
    old=pd.read_csv(OUT.parent/'source_gradient_20261026/primary_summary.csv')
    old=old[(old.roles==15)&(old.refuge_order=='S')&(old.f_arrival==50)&(old.variant=='full')]
    keys=['vegetation','S_source','D_source'];cols=['F_B','F_C','S_B','D_B','F_killed_by_S','F_killed_by_D','D_killed_by_F']
    x=old.set_index(keys)[cols].sort_index();y=su[su.variant=='full'].set_index(keys)[cols].sort_index()
    error=float(np.abs(x-y).max().max())
    if error>1e-11:raise AssertionError('Baseline drift '+str(error))
    report=dict(classification='MODEL_INTERNAL_PATHWAY_AUDIT_NOT_FIELD_CAUSAL_IDENTIFICATION',
                scenarios=len(su),years=80,window=20,baseline_max_abs_error=error,
                selected_context=dict(roles=15,refuge_order='S',f_arrival=50,attack_scale=1.5,rho=.5),
                source_values=[.25,1,2],vegetation=[0,1],variants=all_variants,
                predator_factorial_order=['edge_DS','edge_SD','cue_SF','cue_SD'],
                vegetation_factorial_order=['frog_refuge','D_support','S_refuge','emerge_survival','emerge_exposure'],
                hazard_convention='SF means S eats F; cues separately suppress S feeding on F or D',
                fixed_cohort_replay='Mean baseline last20 cohorts, kept identical across interventions within each source/vegetation cell',
                no_empirical_fit=True)
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Baseline replay error:',error,flush=True)


if __name__=='__main__':main()
