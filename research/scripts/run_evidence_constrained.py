"""Unfitted evidence-constrained alternatives: no inhibition of S eating D.

Qualitative mechanisms have primary literature support. Rates, functional
forms, stage durations and annual return remain explicit synthetic assumptions.
Design is saved before execution; all source rectangles are reported.
"""
import argparse
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from multiyear_stage_network import simulate_years
from run_stage_timing import CONTEXTS

OUT=Path(__file__).resolve().parents[1]/'results/evidence_constrained_20261027'
TIMINGS={**CONTEXTS,'D_first':((50,35,0),(45,70,60)),'F_first':((10,30,35),(45,70,60))}
PROFILES=['refuge_only','litter_response','risk_refuge','timing_shift','combined']
KEYS=['profile','timing','refuge_order','attack_scale','cue','reverse']
METRICS=[g+s for g in 'FSD' for s in ('_B','_C','_fraction','_local')]+[
    'F_killed_by_S','F_killed_by_D','D_killed_by_S','S_killed_by_D','D_killed_by_F']


def options(profile,vegetation,durations):
    controls=dict(cue_SD=0.,support_DF=0.,support_DS=0.,cover_DS=0.,
                  emerge_survival=0.,emerge_exposure=0.)
    # The functional response itself represents D-specific refuge; do not
    # stack an exponential D-refuge reduction on top of it.
    litter=profile in ('litter_response','combined')
    if litter:controls['cover_DF']=0.
    return dict(pathway_controls=controls,stage_durations=durations,
                functional_response='litter' if litter else None,
                behavioral_refuge=profile in ('risk_refuge','combined'),
                emergence_delay=5*np.asarray(vegetation) if profile in ('timing_shift','combined') else 0)


def grid(profile,durations):
    rows=[]
    for name,(arr,dur) in TIMINGS.items():
        if tuple(dur)!=tuple(durations):continue
        for order,attack,cue,reverse,v,s,d in itertools.product(
                ['S','equal','D'],[.5,1.5,3.],[0.,3.],[False,True],[0.,1.],[.25,1.,2.],[.25,1.,2.]):
            rows.append(dict(profile=profile,timing=name,refuge_order=order,attack_scale=attack,
                cue=cue,reverse=reverse,vegetation=v,S_source=s,D_source=d,
                f_arrival=arr[0],s_arrival=arr[1],d_arrival=arr[2],roles=15,rho=.5))
    return pd.DataFrame(rows)


def simulate_design(des,durations,**kwargs):
    profile=des.profile.iloc[0]
    kernel=des.drop(columns=['profile','timing','S_source','D_source']).to_dict('records')
    sources=np.column_stack([np.ones(len(des)),des.S_source,des.D_source])
    tr=simulate_years(kernel,source_cohorts=sources,
        seasonal_options=options(profile,des.vegetation.to_numpy(),durations),**kwargs)
    tail=tr[tr.year>tr.year.max()-20]
    su=tail.groupby('scenario_id')[METRICS].mean().join(des.reset_index(drop=True)).reset_index()
    su['F_B_sd']=tail.groupby('scenario_id').F_B.std(ddof=0).to_numpy()
    return su


def contrasts(su):
    rows=[]
    ranges=[(.25,2.),(.25,1.),(1.,2.)]
    for key,q in su.groupby(KEYS,sort=True):
        x=q.set_index(['vegetation','S_source','D_source'])
        if not x.index.is_unique or len(x)!=18:raise ValueError('Need complete matched 2x3x3 cells')
        for dl,dh in ranges:
            for sl,sh in ranges:
                for metric in ('F_B','F_C'):
                    ds=lambda v,s:(x.loc[(v,s,dh),metric]-x.loc[(v,s,dl),metric])/(dh-dl)
                    ss=lambda v:(x.loc[(v,sh,1.),metric]-x.loc[(v,sl,1.),metric])/(sh-sl)
                    dv=ds(1.,1.)-ds(0.,1.);sv=ss(1.)-ss(0.)
                    sd=ds(1.,sh)-ds(1.,sl);high=ds(1.,sh)
                    rows.append(dict(zip(KEYS,key))|dict(D_low=dl,D_high=dh,S_low=sl,S_high=sh,
                        metric=metric,DV=dv,SV=sv,SD=sd,D_highS=high,
                        joint_vegetation=bool(dv<-1e-6 and sv>1e-6),
                        all_three=bool(dv<-1e-6 and sv>1e-6 and sd<-1e-6 and high<-1e-6)))
    return pd.DataFrame(rows)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sensitivity',action='store_true');a=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if a.sensitivity:
        base=pd.read_csv(OUT/'summary.csv');cs=pd.read_csv(OUT/'contrasts.csv')
        # Deterministic selection, not maximum effect: first full-range success
        # per profile, else first previously-used local-range success.
        candidates=cs[(cs.metric=='F_B')&cs.all_three&(cs.S_low==.25)&(cs.S_high==2)]
        candidates=candidates[candidates.D_low.isin([.25,1.])&(candidates.D_high==2)]
        selected=candidates.sort_values(['D_low']+KEYS).drop_duplicates('profile')
        selected.to_csv(OUT/'sensitivity_selection.csv',index=False)
        outputs=[]
        for r in selected.to_dict('records'):
            mask=np.ones(len(base),bool)
            for k in KEYS:mask&=base[k]==r[k]
            des=base.loc[mask,list(grid(r['profile'],TIMINGS[r['timing']][1]).columns)].reset_index(drop=True)
            for label,kw in [('half_step',{'dt':.125}),('horizon160',{'years':160})]:
                su=simulate_design(des,TIMINGS[r['timing']][1],**kw)
                cc=contrasts(su);cc['check']=label;outputs.append(cc)
                su.to_csv(OUT/(r['profile']+'_'+label+'_summary.csv'),index=False)
                print('Checked',r['profile'],label,flush=True)
        if outputs:pd.concat(outputs,ignore_index=True).to_csv(OUT/'sensitivity_contrasts.csv',index=False)
        return
    report=dict(classification='EVIDENCE_INFORMED_SYNTHETIC_NOT_EMPIRICALLY_PARAMETERIZED',
        profiles=PROFILES,timings=TIMINGS,refuge_orders=['S','equal','D'],attack_scales=[.5,1.5,3.],
        cue_SF=[0,3],cue_SD=0,reverse=[False,True],source_grid=[.25,1,2],vegetation=[0,1],
        years=80,dt=.25,window=20,primary_rectangle=dict(D=[.25,2],S=[.25,2]),
        previous_local_rectangle=dict(D=[1,2],S=[.25,2]),
        literature='research/manuscript/EVIDENCE_CONSTRAINED_MECHANISMS_2026-10-27.md',
        fixed_unverified_functions_removed=['cue_SD','support_DF','support_DS','cover_DS','emerge_survival','emerge_exposure'],
        remaining_assumptions='All numeric rates, exposure functions, size-gate shapes, stage durations, local recruitment, and calling correspondence are unfitted. Qualitative mechanism support is not validation of their combination.',
        new_response='D eats F hazard multiplier: (1-V)*2/(1+F)+V*2F/(1+F^2); arbitrary density scale 1, equal at F=1',
        risk_refuge='S eats F cover exp(-rS*V*D/(1+D)); D-induced F hiding; shape and V scaling synthetic',
        emergence_timing='V adds 5 days to aquatic D period, no survival or exposure multiplier',
        selection='All contexts/ranges reported. First full-range matching context per profile else first prior-local match for numerical sensitivity, ordered by context keys.')
    (OUT/'design.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    summaries=[]
    for profile in PROFILES:
        for durations in [(45,70,60),(60,60,60)]:
            des=grid(profile,durations);su=simulate_design(des,durations)
            su.to_csv(OUT/(profile+'_'+str(durations[0])+'_summary.csv'),index=False)
            summaries.append(su)
            print('Completed',profile,durations,len(des),flush=True)
    su=pd.concat(summaries,ignore_index=True);su.to_csv(OUT/'summary.csv',index=False)
    cs=contrasts(su);cs.to_csv(OUT/'contrasts.csv',index=False)
    primary=cs[(cs.metric=='F_B')&(cs.S_low==.25)&(cs.S_high==2)&(cs.D_high==2)&cs.D_low.isin([.25,1.])]
    counts=primary.groupby(['profile','D_low']).agg(contexts=('all_three','size'),
        joint_vegetation=('joint_vegetation','sum'),all_three=('all_three','sum')).reset_index()
    counts.to_csv(OUT/'counts.csv',index=False)
    print(counts.to_string(index=False),flush=True)


if __name__=='__main__':main()
