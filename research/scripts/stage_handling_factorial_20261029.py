"""Four directed handling ablations; previous kernels remain unchanged.
Partial budgets are diagnostic interventions, not independently fitted feeding laws.
"""
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


def handling_denominators(qf,qd,matrix):
    # Columns: F handling -> F capture, D handling -> F capture,
    # F handling -> D capture, D handling -> D capture.
    return 1+matrix[:,0]*qf+matrix[:,1]*qd,1+matrix[:,2]*qf+matrix[:,3]*qd


def simulate(parameters,dt=.25,initial_cohorts=None,stage_durations=(45,70,60),size_gate=None,
             pathway_controls=None,diagnostics=False,functional_response=None,
             behavioral_refuge=False,emergence_delay=0,handling_s=0.,handling_d=0.,
             sd_size_mode="dynamic",s_growth=.014,d_growth=.015,extension_diagnostics=False,s_handling_matrix=None):
    if sd_size_mode not in ("dynamic","frozen"):
        raise ValueError("Unknown size mode")
    extension=[np.asarray(x,float) for x in [handling_s,handling_d,s_growth,d_growth]]
    if any(x.shape not in ((),(len(parameters),)) or not np.isfinite(x).all() or (x<0).any() for x in extension):
        raise ValueError("Finite nonnegative scalar or scenario handling and growth required")
    handling_s,handling_d,s_growth,d_growth=extension
    if s_handling_matrix is None:
        matrix=np.repeat(np.broadcast_to(handling_s,(len(parameters),))[:,None],4,axis=1)
    else:
        matrix=np.asarray(s_handling_matrix,float)
        if matrix.shape==(4,):matrix=np.broadcast_to(matrix,(len(parameters),4))
        if matrix.shape!=(len(parameters),4) or not np.isfinite(matrix).all() or (matrix<0).any() or np.any(handling_s!=0):
            raise ValueError('Four finite nonnegative controls required; do not combine with handling_s')
    durations=np.asarray(stage_durations,dtype=float)
    if durations.shape not in ((3,),(len(parameters),3)) or not np.isfinite(durations).all() or (durations<=0).any():
        raise ValueError('Three finite positive aquatic durations required')
    if size_gate is not None and (not np.isfinite(size_gate) or not 0<=size_gate<=1):
        raise ValueError('Constant size gate must lie in [0,1]')
    ft,st,dt_aquatic=durations if durations.ndim==1 else durations.T
    if not np.isfinite(dt) or dt<=0 or abs(120/dt-round(120/dt))>1e-8:
        raise ValueError('dt must divide the 120-day observation period')
    for row in parameters:
        if set(row)-set(DEFAULT):raise ValueError('Unknown parameter')
    p=pd.DataFrame([{**DEFAULT,**row} for row in parameters])
    if p.empty:raise ValueError('No scenarios')
    if functional_response not in (None,'litter'):raise ValueError('Unknown functional response')
    delay=np.asarray(emergence_delay,float)
    if delay.shape not in ((),(len(p),)) or not np.isfinite(delay).all() or (delay<0).any():
        raise ValueError('Emergence delay must be nonnegative scalar or scenario vector')
    dt_aquatic=dt_aquatic+delay
    numeric=['vegetation','f_arrival','s_arrival','d_arrival','attack_scale','cue','water','roles']
    if not np.isfinite(p[numeric].to_numpy(float)).all():raise ValueError('Non-finite input')
    if not p.community.isin(['F','FS','FD','FSD']).all() or not p.refuge_order.isin(['S','equal','D']).all():
        raise ValueError('Unknown community or refuge ordering')
    if ((p[numeric]<0).any().any() or (p.vegetation>1).any() or (p.water>120).any()
            or (p.roles>15).any() or (p.roles%1!=0).any()):raise ValueError('Out-of-range parameter')
    events=np.column_stack([p.f_arrival,p.s_arrival,p.d_arrival,p.water,
                            p.f_arrival+ft,p.s_arrival+st,p.d_arrival+dt_aquatic,p.d_arrival+dt_aquatic+5])
    if not np.allclose(events/dt,np.round(events/dt),rtol=0,atol=1e-8):
        raise ValueError('Event times must align with integration grid')
    if (p[['f_arrival','s_arrival','d_arrival']]>120).any().any():raise ValueError('Arrival outside season')
    n=len(p);zero=lambda:np.zeros(n)
    # Optional interventions: multiplier 1 retains the original mechanism;
    # 0 removes only this directed pathway. Arrays allow matched batched runs.
    names=['edge_SF','edge_DF','edge_DS','edge_SD','edge_FE','cue_SF','cue_SD',
           'cover_SF','cover_DF','cover_DS','support_DF','support_DS',
           'emerge_survival','emerge_exposure','cover_SD']
    controls=pathway_controls or {}
    if set(controls)-set(names):raise ValueError('Unknown pathway control')
    c={}
    for name in names:
        a=np.asarray(controls.get(name,0. if name=='cover_SD' else 1.),float)
        if a.shape not in ((),(n,)) or not np.isfinite(a).all() or (a<0).any() or (a>1).any():
            raise ValueError('Pathway controls must be scalar or n-vector in [0,1]')
        c[name]=a
    audit={k:zero() for k in ['H_SF','H_DF','H_DS','H_SD','S_days_Fwindow',
                             'S_active_Fwindow','D_days_Fwindow','S_days_Dwindow',
                             'S_active_Dwindow','H_FE','H_failure']}
    if extension_diagnostics:
        audit.update({k:zero() for k in ['DS_dominant_days','SD_dominant_days','both_alive_days']})
    f,s,d,fp,sp,de,da=[zero() for _ in range(7)]
    death={k:zero() for k in ['F_by_S','F_by_D','S_by_D','D_by_S','D_by_F','D_failure','F_dry','S_dry','D_dry']}
    v=p.vegetation.to_numpy(float);roles=p.roles.to_numpy(int)
    refuge=((roles&1)>0)*v;support=((roles&2)>0)*v;sref=((roles&4)>0)*v;stem=((roles&8)>0)*v
    r_s=np.select([p.refuge_order=='S',p.refuge_order=='D'],[1.25,.25],default=.75)
    r_d=1.5-r_s
    sf_cover=np.exp(-r_s*refuge*c['cover_SF'])
    df_cover=np.exp(-r_d*refuge*c['cover_DF']+.8*support*c['support_DF'])
    ds_cover=np.exp(-.8*sref*c['cover_DS']+.8*support*c['support_DS'])
    scale=p.attack_scale.to_numpy(float);cue=p.cue.to_numpy(float)
    fa=p.f_arrival.to_numpy(float);sa=p.s_arrival.to_numpy(float);dd=p.d_arrival.to_numpy(float)
    sinit=p.community.isin(['FS','FSD']).to_numpy(float);dinit=p.community.isin(['FD','FSD']).to_numpy(float)
    present=np.column_stack([np.ones(n),sinit,dinit])
    initial=present if initial_cohorts is None else np.asarray(initial_cohorts,dtype=float)
    if initial.shape!=(n,3) or not np.isfinite(initial).all() or (initial<0).any():
        raise ValueError('Initial cohorts must be finite nonnegative n-by-3 F/S/D densities')
    if ((present==0)&(initial!=0)).any():raise ValueError('Density supplied for absent guild')
    finit,sinit,dinit=initial.T
    intraguild=p.intraguild.to_numpy(bool);reciprocal=p.reciprocal.to_numpy(bool);reverse=p.reverse.to_numpy(bool)
    water=p.water.to_numpy(float)
    sigmoid=lambda z:1/(1+np.exp(-np.clip(z,-60,60)))
    for step in range(round(120/dt)+1):
        t=step*dt
        f+=np.isclose(t,fa,rtol=0,atol=1e-9)*finit
        s+=np.isclose(t,sa,rtol=0,atol=1e-9)*sinit
        d+=np.isclose(t,dd,rtol=0,atol=1e-9)*dinit
        # Transitions at the boundary precede drying at the same time.
        m=t>=fa+ft;fp+=np.where(m,f,0);f=np.where(m,0,f)
        m=t>=sa+st;sp+=np.where(m,s,0);s=np.where(m,0,s)
        m=t>=dd+dt_aquatic;de+=np.where(m,d,0);d=np.where(m,0,d)
        m=t>=dd+dt_aquatic+5;da+=np.where(m,de,0);de=np.where(m,0,de)
        dry=t>=water
        for key,a in [('F_dry',f),('S_dry',s),('D_dry',d)]:death[key]+=np.where(dry,a,0)
        f=np.where(dry,0,f);s=np.where(dry,0,s);d=np.where(dry,0,d)
        if step==round(120/dt):break
        fs=.15+.020*np.maximum(t-fa,0);ss=.15+s_growth*np.maximum(t-sa,0);ds=.15+d_growth*np.maximum(t-dd,0)
        # All hazards use the same start-of-step cohort state.
        suppressed_sf=1/(1+cue*d*c['cue_SF'])
        suppressed_sd=1/(1+cue*d*c['cue_SD'])
        gsf=sigmoid(8*(ss-fs)) if size_gate is None else size_gate
        gdf=sigmoid(3*(ds-.5*fs)) if size_gate is None else size_gate
        gds=sigmoid(8*(ds-ss)) if size_gate is None else size_gate
        gsd=sigmoid(8*(ss-ds)) if size_gate is None else size_gate
        if sd_size_mode=='frozen':
            overlap=np.maximum(sa,dd)
            ss0=.15+s_growth*(overlap-sa);ds0=.15+d_growth*(overlap-dd)
            gds=sigmoid(8*(ds0-ss0));gsd=1-gds
        # Risk-induced F refuge: evidence for a D-triggered reduction of newt
        # feeding; this response shape/strength is synthetic, not fitted.
        current_sf_cover=(np.exp(-r_s*refuge*c['cover_SF']*d/(1+d))
                          if behavioral_refuge else sf_cover)
        hsf=.035*scale*s*gsf*current_sf_cover*suppressed_sf*c['edge_SF']
        hdf=.025*scale*d*gdf*df_cover*c['edge_DF']
        if functional_response=='litter':
            # Per-prey hazards yield type II (no cover) and type III (cover)
            # total consumption at infinitesimal dt. Both normalized at F=1.
            # Response family is evidence-informed; density scale is synthetic.
            hdf*=((1-v)*2/(1+f)+v*2*f/(1+f*f))
        hds=.025*scale*d*gds*ds_cover*intraguild*c['edge_DS']
        # Optional D refuge from S; default zero preserves previous models.
        hsd=.020*scale*s*gsd*suppressed_sd*reciprocal*intraguild*c['edge_SD']*np.exp(-.8*refuge*c['cover_SD'])
        # Shared handling is a structural hypothesis, not a fitted feeding rate.
        # S shares its time between F and D. D's existing F response is kept,
        # but feeding on S occupies the same budget; S capture is also
        # constrained by F processing. Zero strengths exactly replay baseline.
        if np.any(matrix>0):
            demand_f=gsf*current_sf_cover*suppressed_sf*c['edge_SF']*f
            demand_d=gsd*suppressed_sd*c['edge_SD']*np.exp(-.8*refuge*c['cover_SD'])*d*reciprocal*intraguild
            denom_sf,denom_sd=handling_denominators(demand_f,demand_d,matrix)
            hsf/=denom_sf;hsd/=denom_sd
        if np.any(handling_d>0):
            base_d=(1+(1-v)*f+v*f*f) if functional_response=='litter' else np.ones(n)
            demand_ds=gds*ds_cover*intraguild*c['edge_DS']*s
            denom_d=base_d+handling_d*demand_ds
            hdf*=np.where(handling_d>0,base_d/denom_d,1.)
            hds/=np.where(handling_d>0,denom_d,1.)
        hfe=.060*scale*fp*np.exp(.4*stem*c['emerge_exposure'])*reverse*c['edge_FE']
        hfail=.100*np.exp(-.8*stem*c['emerge_survival'])
        if extension_diagnostics:
            both=(s>1e-12)&(d>1e-12)
            audit['DS_dominant_days']+=dt*both*(hds*s>hsd*d+1e-12)
            audit['SD_dominant_days']+=dt*both*(hsd*d>hds*s+1e-12)
            audit['both_alive_days']+=dt*both
        if diagnostics:
            fw=(t>=fa)&(t<fa+ft)&(t<water)
            sw=(t>=sa)&(t<sa+st)&(t<water)
            dw=(t>=dd)&(t<dd+dt_aquatic)&(t<water)
            ew=(t>=dd+dt_aquatic)&(t<dd+dt_aquatic+5)
            vals={'H_SF':hsf*fw,'H_DF':hdf*fw,'H_DS':hds*sw,'H_SD':hsd*dw,
                  'S_days_Fwindow':s*fw,'S_active_Fwindow':s*suppressed_sf*fw,
                  'D_days_Fwindow':d*fw,'S_days_Dwindow':s*dw,
                  'S_active_Dwindow':s*suppressed_sd*dw,'H_FE':hfe*ew,'H_failure':hfail*ew}
            for key,val in vals.items():audit[key]+=val*dt
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
    if diagnostics:
        for key,val in audit.items():out['audit_'+key]=val
    for g,start in [('F',finit),('S',sinit),('D',dinit)]:
        out[g+'_dead']=sum(val for key,val in death.items() if key.startswith(g+'_'))
        if not np.allclose(out[g+'_dead']+out[g+'_survived'],start,rtol=0,atol=1e-11):
            raise AssertionError('Cohort accounting failed: '+g)
        if (out[g+'_survived']<0).any():raise AssertionError('Negative cohort')
    return out
