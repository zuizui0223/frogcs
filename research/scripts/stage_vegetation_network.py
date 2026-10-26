"""Synthetic one-season stage network; no empirical fit or calling prediction."""
import argparse
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd

DEFAULT = dict(community='FSD',roles=15,refuge_order='S',vegetation=0.,
               f_arrival=10.,s_arrival=0.,d_arrival=35.,attack_scale=1.,cue=3.,
               water=120.,reverse=True,reciprocal=True,intraguild=True)
ENDPOINTS=['F_completed','S_completed','D_completed']


def simulate(parameters,dt=.25):
    if not np.isfinite(dt) or dt<=0 or abs(120/dt-round(120/dt))>1e-8:
        raise ValueError('dt must divide the 120-day observation period')
    for row in parameters:
        if set(row)-set(DEFAULT):raise ValueError('Unknown parameter')
    p=pd.DataFrame([{**DEFAULT,**row} for row in parameters])
    if p.empty:raise ValueError('No scenarios')
    numeric=['vegetation','f_arrival','s_arrival','d_arrival','attack_scale','cue','water','roles']
    if not np.isfinite(p[numeric].to_numpy(float)).all():raise ValueError('Non-finite input')
    if not p.community.isin(['F','FS','FD','FSD']).all() or not p.refuge_order.isin(['S','equal','D']).all():
        raise ValueError('Unknown community or refuge ordering')
    if ((p[numeric]<0).any().any() or (p.vegetation>1).any() or (p.water>120).any()
            or (p.roles>15).any() or (p.roles%1!=0).any()):raise ValueError('Out-of-range parameter')
    events=np.column_stack([p.f_arrival,p.s_arrival,p.d_arrival,p.water,
                            p.f_arrival+45,p.s_arrival+70,p.d_arrival+60,p.d_arrival+65])
    if not np.allclose(events/dt,np.round(events/dt),rtol=0,atol=1e-8):
        raise ValueError('Event times must align with integration grid')
    if (p[['f_arrival','s_arrival','d_arrival']]>120).any().any():raise ValueError('Arrival outside season')
    n=len(p);zero=lambda:np.zeros(n)
    f,s,d,fp,sp,de,da=[zero() for _ in range(7)]
    death={k:zero() for k in ['F_by_S','F_by_D','S_by_D','D_by_S','D_by_F','D_failure','F_dry','S_dry','D_dry']}
    v=p.vegetation.to_numpy(float);roles=p.roles.to_numpy(int)
    refuge=((roles&1)>0)*v;support=((roles&2)>0)*v;sref=((roles&4)>0)*v;stem=((roles&8)>0)*v
    r_s=np.select([p.refuge_order=='S',p.refuge_order=='D'],[1.25,.25],default=.75)
    r_d=1.5-r_s
    sf_cover=np.exp(-r_s*refuge);df_cover=np.exp(-r_d*refuge+.8*support)
    ds_cover=np.exp(-.8*sref+.8*support)
    scale=p.attack_scale.to_numpy(float);cue=p.cue.to_numpy(float)
    fa=p.f_arrival.to_numpy(float);sa=p.s_arrival.to_numpy(float);dd=p.d_arrival.to_numpy(float)
    sinit=p.community.isin(['FS','FSD']).to_numpy(float);dinit=p.community.isin(['FD','FSD']).to_numpy(float)
    water=p.water.to_numpy(float)
    sigmoid=lambda z:1/(1+np.exp(-np.clip(z,-60,60)))
    for step in range(round(120/dt)+1):
        t=step*dt
        f+=np.isclose(t,fa,rtol=0,atol=1e-9)
        s+=np.isclose(t,sa,rtol=0,atol=1e-9)*sinit
        d+=np.isclose(t,dd,rtol=0,atol=1e-9)*dinit
        # Transitions at the boundary precede drying at the same time.
        m=t>=fa+45;fp+=np.where(m,f,0);f=np.where(m,0,f)
        m=t>=sa+70;sp+=np.where(m,s,0);s=np.where(m,0,s)
        m=t>=dd+60;de+=np.where(m,d,0);d=np.where(m,0,d)
        m=t>=dd+65;da+=np.where(m,de,0);de=np.where(m,0,de)
        dry=t>=water
        for key,a in [('F_dry',f),('S_dry',s),('D_dry',d)]:death[key]+=np.where(dry,a,0)
        f=np.where(dry,0,f);s=np.where(dry,0,s);d=np.where(dry,0,d)
        if step==round(120/dt):break
        fs=.15+.020*np.maximum(t-fa,0);ss=.15+.014*np.maximum(t-sa,0);ds=.15+.015*np.maximum(t-dd,0)
        # All hazards use the same start-of-step cohort state.
        suppressed=1/(1+cue*d)
        hsf=.035*scale*s*sigmoid(8*(ss-fs))*sf_cover*suppressed
        hdf=.025*scale*d*sigmoid(3*(ds-.5*fs))*df_cover
        hds=.025*scale*d*sigmoid(8*(ds-ss))*ds_cover*p.intraguild.to_numpy(bool)
        hsd=.020*scale*s*sigmoid(8*(ss-ds))*suppressed*p.reciprocal.to_numpy(bool)*p.intraguild.to_numpy(bool)
        hfe=.060*scale*fp*np.exp(.4*stem)*p.reverse.to_numpy(bool)
        hfail=.100*np.exp(-.8*stem)
        hf=hsf+hdf;loss=f*(-np.expm1(-hf*dt))
        bys=loss*np.divide(hsf,hf,out=zero(),where=hf>0)
        death['F_by_S']+=bys;death['F_by_D']+=loss-bys;f-=loss
        loss=s*(-np.expm1(-hds*dt));death['S_by_D']+=loss;s-=loss
        loss=d*(-np.expm1(-hsd*dt));death['D_by_S']+=loss;d-=loss
        he=hfe+hfail;loss=de*(-np.expm1(-he*dt));byf=loss*hfe/he
        death['D_by_F']+=byf;death['D_failure']+=loss-byf;de-=loss
    out=p.copy()
    for key,val in [('F_completed',fp),('S_completed',sp),('D_completed',da),
                    ('F_survived',f+fp),('S_survived',s+sp),('D_survived',d+de+da)]:out[key]=val
    for key,val in death.items():out[key.replace('_by_','_killed_by_')]=val
    for g,initial in [('F',np.ones(n)),('S',sinit),('D',dinit)]:
        out[g+'_dead']=sum(val for key,val in death.items() if key.startswith(g+'_'))
        if not np.allclose(out[g+'_dead']+out[g+'_survived'],initial,rtol=0,atol=1e-11):
            raise AssertionError('Cohort accounting failed: '+g)
        if (out[g+'_survived']<0).any():raise AssertionError('Negative cohort')
    return out


def scenario_grid():
    names=['roles','refuge_order','f_arrival','s_arrival','d_arrival','attack_scale','cue','vegetation','community']
    values=[range(16),['S','equal','D'],[10.,30.,50.],[0.,20.],[10.,35.],[.5,1.5],[0.,3.],[0.,1.],['F','FS','FD','FSD']]
    return [dict(zip(names,x)) for x in itertools.product(*values)]


def contrasts(frame):
    keys=list(DEFAULT);keys.remove('community')
    wide=frame.pivot(index=keys,columns='community',values='F_completed').reset_index()
    wide['D_effect_without_S']=wide.FD-wide.F
    wide['D_effect_with_S']=wide.FSD-wide.FS
    wide['S_effect_with_D']=wide.FSD-wide.FD
    wide['nonadditivity']=wide.FSD-wide.FS-wide.FD+wide.F
    # Raw survival differences can be positive even with independent hazards.
    # The multiplicative-survival null removes that scale artifact.
    wide['log_survival_interaction']=np.log(wide.FSD)+np.log(wide.F)-np.log(wide.FS)-np.log(wide.FD)
    return wide


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    grid=scenario_grid();base=simulate(grid);fine=simulate(grid,dt=.125)
    error=float(np.max(abs(base[ENDPOINTS].to_numpy()-fine[ENDPOINTS].to_numpy())))
    if error>.005:raise AssertionError('Half-step difference exceeds 0.005: '+str(error))
    base.insert(0,'scenario_id',np.arange(len(base)))
    base.to_csv(args.out/'all_scenarios.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    paired=contrasts(base);paired.to_csv(args.out/'paired_community_contrasts.csv',index=False)
    keys=[c for c in DEFAULT if c not in ['community','vegetation']]
    cols=['D_effect_without_S','D_effect_with_S','S_effect_with_D','nonadditivity','log_survival_interaction']
    lo=paired[paired.vegetation==0].set_index(keys);hi=paired[paired.vegetation==1].set_index(keys)
    modification=(hi[cols]-lo[cols]).add_prefix('vegetation_change_').reset_index()
    modification.to_csv(args.out/'vegetation_modification.csv',index=False)
    audits=[]
    for label,changes in [('no_reverse',{'reverse':False}),('no_reciprocal',{'reciprocal':False}),
                          ('independent_predators',{'intraguild':False,'cue':0.}),('dry60',{'water':60.})]:
        alt=simulate([{**r,**changes} for r in grid])
        data=alt[ENDPOINTS+['D_killed_by_F','D_killed_by_S','S_killed_by_D']].copy()
        data.insert(0,'scenario_id',np.arange(len(data)))
        data.to_csv(args.out/(label+'.csv.gz'),index=False,compression={'method':'gzip','mtime':0})
        audits.append(dict(variant=label,max_abs_completion_change={g:float(abs(alt[g]-base[g]).max()) for g in ENDPOINTS}))
        if label=='independent_predators':
            # Setting both original cue levels to zero creates identical scenarios.
            # Remove exact duplicate rows only, never average conflicting outputs.
            null=contrasts(alt.drop_duplicates())
            err=float(null.log_survival_interaction.abs().max())
            if err>1e-10:raise AssertionError('Independent-hazard null failed')
            audits[-1]['max_abs_log_survival_interaction']=err
    counts={c:{'negative':int((paired[c]<-.002).sum()),'near_zero':int((paired[c].abs()<=.002).sum()),
               'positive':int((paired[c]>.002).sum())} for c in cols}
    report=dict(classification='SYNTHETIC_NOT_EMPIRICAL',scenarios=len(base),paired_contexts=len(paired),
                dt=.25,half_step_dt=.125,half_step_max_abs_completion_difference=error,
                contrast_sign_threshold=.002,contrast_counts=counts,ablation_audits=audits,
                scope='One-season normalized cohort completion; no calling prediction, fit, reproduction, or coexistence claim',
                nonadditivity_null='Raw difference-of-differences includes survival-scale nonlinearity; use log_survival_interaction for multiplicative-hazard null',
                design='research/manuscript/STAGE_VEGETATION_MODEL_DESIGN_2026-10-26.md',
                emergence_only_causality='Emergence benefits cannot affect earlier same-season larval F survival; no recruitment feedback')
    (args.out/'synthetic_results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
