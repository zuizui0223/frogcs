"""P1 paired 80-year factorial, changing frog arrival and predator calendars.
The numba kernel skips inactive intervals. Validate all baseline vertices against P1.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from numba import njit, prange, set_num_threads, get_num_threads
from final_mechanism_common import catalog
from abc_pom_main3600 import CORNERS

ROOT=Path(__file__).resolve().parents[2]
FROZEN=ROOT/'research/results/submission_frozen_sources_20261106/P1'
OUT=ROOT/'research/results/frog_arrival_20261109'
# (frog offset from day 20, offset of salamander calendar, offset of odonate calendar)
CALENDARS=[(x,0,0) for x in (0,20,40,60,71,78,84)]+[(78,78,0),(78,0,78),(78,78,78)]

@njit
def vertex(row,v,ssource,dsource,fa,sa,sdur,da,water):
    cs,cd,cds,csd,surv,timing,support,dsupport,esd,eds,reverse,litter,cue,order,gate,attack,rho,conv,strength=row
    dfactor=np.exp(v*strength*(-(1.5-order)*cd+.8*support))
    dsfactor=np.exp(v*strength*.8*(dsupport-cds))
    sfactor=np.exp(-order*v*cs*strength)
    sdfactor=np.exp(-.8*v*csd*strength)
    failure=.1*np.exp(-.8*v*surv*strength)
    dend=da+60+5*v*timing
    # Matrix coefficients include pairwise stage overlap and starting size at each half-day.
    schedule=[]
    for step in range(2*water):
        t=step*.5
        F=fa<=t<fa+45; S=sa<=t<sa+sdur; D=da<=t<dend; E=dend<=t<dend+5
        if not ((F and S) or (F and D) or (S and D) or E):continue
        fs=.15+.02*max(t-fa,0.); sz=.15+.014*max(t-sa,0.); dz=.15+.015*max(t-da,0.)
        sf=.5 if gate else 1/(1+np.exp(-8*(sz-fs)))
        df=.5 if gate else 1/(1+np.exp(-3*(dz-.5*fs)))
        ds=.5 if gate else 1/(1+np.exp(-8*(dz-sz)))
        sg=.5 if gate else 1/(1+np.exp(-8*(sz-dz)))
        schedule.append((.5*.035*attack*sf*sfactor*(F and S),.5*.025*attack*df*dfactor*(F and D),
                         .5*.025*attack*ds*dsfactor*eds*(S and D),.5*.020*attack*sg*sdfactor*esd*(S and D),
                         .5*.06*attack*reverse*(E and t>=fa+45),.5*failure*E,D))
    Bf=Bs=Bd=1.; prevf=prevs=0.; meanf=hsum=dsum=0.
    for year in range(80):
        f,s,d=Bf,Bs,Bd;hs=hd=0.
        for a,b,c,e,rev,fail,D in schedule:
            sf=a*s/(1.+cue*d*D)
            df=b*d
            if litter:df*=((1-v)*2/(1+f)+v*2*f/(1+f*f))
            ds=c*d; sd=e*s
            dh=sd+rev*f+fail
            if sf+df: f*=np.exp(-sf-df)
            if ds:s*=np.exp(-ds)
            if dh:d*=np.exp(-dh)
            hs+=sf;hd+=df
        if year>=60:
            meanf+=Bf/20;hsum+=hs/20;dsum+=hd/20
        if fa+45>water:f=0.
        if sa+sdur>water:s=0.
        Bf=.4*Bf+rho*conv*.8*prevf/(1+prevf)+(1-rho)*.6
        Bs=.5*Bs+rho*conv*.8*prevs/(1+prevs)+(1-rho)*.5*ssource
        Bd=rho*conv*d/(1+d)+(1-rho)*dsource
        prevf,prevs=f,s
    return meanf,hsum,dsum

@njit(parallel=True)
def batch(parameters,stages,corners,f_offset,s_offset,d_offset,water):
    res=np.empty((len(parameters),8,3))
    for i in prange(len(parameters)):
        for j in range(8):
            v,s,d=corners[j]
            res[i,j,:]=vertex(parameters[i],v,s,d,20+f_offset,stages[i,0]+s_offset,stages[i,1],20+d_offset,water)
    return res

def main():
    set_num_threads(min(12,get_num_threads()))
    OUT.mkdir(exist_ok=True)
    saved=pd.read_csv(FROZEN/'P1_original4096_isolated_timing_duration_80year.csv.gz',dtype={'arm':str}).sort_values('draw_id')
    src=saved.merge(catalog(),on='model_id',validate='many_to_one',sort=False)
    assert len(src)==4096 and not src.behavior.eq('risk_refuge').any()
    src['cue']=np.where(src.behavior=='cue_SF',3.,0.)
    src['order']=src.refuge_order.map({'D':.25,'equal':.75,'S':1.25})
    cols='cover_SF cover_DF cover_DS cover_SD survival timing support_DF support_DS edge_SD edge_DS reverse litter cue order gate_code attack rho conversion strength'.split()
    pars=src[cols].to_numpy(float);assert np.isfinite(pars).all()
    stages=src[['s_arrival','S_duration']].to_numpy(int)
    reference=pd.read_csv(FROZEN/'P1_original32768_vegetation_predator_corners.csv.gz').sort_values(['draw_id','vertex'])
    frames=[]
    for fo,so,do in CALENDARS:
        data=batch(pars,stages,np.array(CORNERS),fo,so,do,180)
        if (fo,so,do)==(0,0,0):
            base=data.copy()
            ref=reference[['F_B','audit_H_SF','audit_H_DF']].to_numpy().reshape(data.shape)
            err=np.max(np.abs(data-ref),axis=(0,1));print('replay',err,flush=True)
            np.testing.assert_allclose(data,ref,atol=1e-10,rtol=1e-10)
        if fo==so==do==78:np.testing.assert_allclose(data,base,rtol=0,atol=1e-12)
        df=src[['source_id','stage_design','arm','s_arrival','S_duration']].copy()
        df=df.assign(f_offset=fo,s_offset=so,d_offset=do,mean_log_F=np.log(data[:,:,0]).mean(axis=1),H_SF=data[:,7,1],H_DF=data[:,7,2])
        frames.append(df)
        print('complete',fo,so,do,flush=True)
    # Original drying day isolates habitat truncation for the 78-day shift.
    dry=batch(pars,stages,np.array(CORNERS),78,0,0,120)
    dry_f=src[['source_id','stage_design','arm']].copy()
    dry_f['log_f']=np.log(dry[:,:,0]).mean(axis=1)
    dry_arms=dry_f.pivot(index=['source_id','stage_design'],columns='arm',values='log_f')
    dry_difference=float((dry_arms['11']-dry_arms['00']).abs().max())
    assert dry_difference < 1e-12
    rng=np.random.default_rng(20261109);boot=rng.integers(256,size=(1000,256))
    allrows=pd.concat(frames); allrows.to_csv(OUT/'scenarios.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    rows=[]
    for key,g in allrows.groupby(['f_offset','s_offset','d_offset','stage_design']):
        for metric in ['mean_log_F','H_SF','H_DF']:
            a=g.pivot(index='source_id',columns='arm',values=metric).sort_index()
            for label,x in {'refuge':a['10']-a['00'],'support':a['01']-a['00'],'interaction':a['11']-a['10']-a['01']+a['00'],'net':a['11']-a['00']}.items():
                x=x.to_numpy();low,high=np.quantile(x[boot].mean(axis=1),[.025,.975]);rows.append([*key,metric,label,x.mean(),low,high,sum(x>1e-10),sum(x< -1e-10)])
    pd.DataFrame(rows,columns=['f_offset','s_offset','d_offset','stage','metric','contrast','mean','low','high','positive','negative']).to_csv(OUT/'summary.csv',index=False)
    # Paired late-minus-early contrasts on identical source backgrounds and arms.
    key=['f_offset','s_offset','d_offset','stage_design']
    paired=[]
    for metric in ['mean_log_F','H_SF','H_DF']:
        arms=allrows.pivot(index=key+['source_id'],columns='arm',values=metric)
        effect=(arms['11']-arms['00']).rename('effect').reset_index()
        for cell,g in effect.groupby(key):
            start=effect[(effect.f_offset==0)&(effect.stage_design==cell[-1])].set_index('source_id').effect
            delta=(g.set_index('source_id').effect-start).to_numpy()
            paired.append([*cell,metric,delta.mean(),*np.quantile(delta[boot].mean(axis=1),[.025,.975])])
    pd.DataFrame(paired,columns=key+['metric','mean','low','high']).to_csv(OUT/'paired_change_from_baseline.csv',index=False)
    (OUT/'validation.json').write_text(json.dumps(dict(dry120_day98_max_abs_cohort_contrast=dry_difference,P1_replay_max_errors=err.tolist(),translated_calendar_replay=True,water_days=180,dt=.5,years=80,last_years=20,structures=256,corners=8,scenarios=len(allrows)),indent=2))
if __name__=='__main__':main()
