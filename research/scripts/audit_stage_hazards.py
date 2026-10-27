"""Fixed-candidate timing/size audit using hazard and relative survival criteria."""
import itertools,json
from pathlib import Path
import numpy as np
import pandas as pd
from stage_vegetation_network import DEFAULT
from multiyear_stage_network import simulate_years
from run_evidence_constrained import options
from audit_response_scales import compare,transform
OUT=Path(__file__).resolve().parents[1]/'results/stage_hazard_audit_20261027'

def mean_gates(des):
    arr=des[['f_arrival','s_arrival','d_arrival']].to_numpy(float)
    dur=des[['F_duration','S_duration','D_duration']].to_numpy(float)
    sums={k:np.zeros(len(des)) for k in ['SF','DF','DS','SD']};counts={k:np.zeros(len(des)) for k in sums}
    for t in np.arange(0,120,.25):
        fs,ss,ds=(.15+np.maximum(t-arr,0)*np.array([.020,.014,.015])).T
        live=(t>=arr)&(t<arr+dur)
        masks={'SF':live[:,0]&live[:,1],'DF':live[:,0]&live[:,2],'DS':live[:,1]&live[:,2],'SD':live[:,1]&live[:,2]}
        for k,z in {'SF':8*(ss-fs),'DF':3*(ds-.5*fs),'DS':8*(ds-ss),'SD':8*(ss-ds)}.items():
            sums[k]+=masks[k]/(1+np.exp(-np.clip(z,-60,60)));counts[k]+=masks[k]
    return {k:np.divide(sums[k],counts[k],out=np.zeros(len(des)),where=counts[k]>0) for k in sums}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    design=dict(candidate='111110',F_arrival=20,F_duration=45,S_arrival=[0,20,40],D_arrival=[0,20,40],S_duration=[40,60,80],D_duration=[40,60,70],modes=['dynamic','mean_matched','D_disadvantage','balanced','D_advantage'],fixed_attack=3,years=80,rho=.5,cue=0,reverse=False,criterion='F_B, log_F_B, log_F_fraction and negative_H all pass full supply .25 to 2; threshold 1e-6',size_control='Mean-matched removes time variation preserving unweighted overlap gate separately per edge. Directional controls fix DS/SD at .2/.8, .5/.5 or .8/.2, holding SF/DF at mean matched. Synthetic susceptibility, not measured lengths.',scope='81 timing-duration settings; fixed frog development; no density-linked timing; settings fixed before run')
    (OUT/'design.json').write_text(json.dumps(design,indent=2)+'\n')
    rows=[]
    for sa,da,sd,dd in itertools.product([0,20,40],[0,20,40],[40,60,80],[40,60,70]):
        for v,s,d in itertools.product([0.,1.],[.25,1.,2.],[.25,1.,2.]):
            rows.append(dict(timing=f'S{sa}_D{da}_dur45_{sd}_{dd}',f_arrival=20,s_arrival=sa,d_arrival=da,F_duration=45,S_duration=sd,D_duration=dd,vegetation=v,S_source=s,D_source=d,refuge_order='S',attack_scale=3.,cue=0.,reverse=False,roles=15,rho=.5))
    base=pd.DataFrame(rows);means=mean_gates(base);allcs=[]
    modes=design['modes']+['no_DS','no_SD']
    for mode in modes:
        des=base.copy()
        if mode.startswith('no_'):
            des=des[(des.S_duration==40)&(des.D_duration==40)].reset_index(drop=True)
        opt=options('refuge_only',des.vegetation.to_numpy(),des[['F_duration','S_duration','D_duration']].to_numpy())
        opt['pathway_controls'].update(cover_DF=0.)
        opt['diagnostics']=True
        if mode in ['mean_matched','D_disadvantage','balanced','D_advantage']:
            opt['size_gate']=1.
            for k,a in means.items():opt['pathway_controls']['edge_'+k]=a
            if mode!='mean_matched':
                ds={'D_disadvantage':.2,'balanced':.5,'D_advantage':.8}[mode]
                opt['pathway_controls'].update(edge_DS=ds,edge_SD=1-ds)
        if mode.startswith('no_'):opt['pathway_controls']['edge_'+mode[3:]]=0.
        kernel=des[[k for k in DEFAULT if k in des]+['rho']].to_dict('records')
        source=np.column_stack([np.ones(len(des)),des.S_source,des.D_source])
        tr=simulate_years(kernel,source_cohorts=source,seasonal_options=opt)
        tail=tr[tr.year>=60].copy();tail['negative_H']=-tail.audit_H_SF-tail.audit_H_DF
        err=float(np.max(abs(np.log(tail.F_fraction)-tail.negative_H)))
        if err>1e-9:raise AssertionError('Hazard identity')
        cols=['F_B','F_fraction','negative_H','S_B','D_B','audit_H_SF','audit_H_DF','audit_H_DS','audit_H_SD']
        su=transform(tail.groupby('scenario_id')[cols].mean().join(des))
        su['F_B_sd']=tail.groupby('scenario_id').F_B.std(ddof=0)
        su.to_csv(OUT/(mode+'_summary.csv'),index=False)
        cc=[]
        for timing,g in su.groupby('timing'):cc+=compare(g,dict(mode=mode,timing=timing))
        cc=pd.DataFrame(cc);allcs.append(cc);cc.to_csv(OUT/(mode+'_contrasts.csv'),index=False)
        print(mode,'complete',len(des),'hazard identity error',err,flush=True)
        del tr,tail
    c=pd.concat(allcs,ignore_index=True);c.to_csv(OUT/'all_contrasts.csv',index=False)
    full=c[c.D_low==.25]
    full.groupby(['mode','metric']).all_three.agg(['sum','count']).to_csv(OUT/'counts.csv')
    both=full[full.metric.isin(['F_B','log_F_B','log_F_fraction','negative_H'])].groupby(['mode','timing']).all_three.all().rename('all_scales').reset_index()
    meta=base[['timing','s_arrival','d_arrival','S_duration','D_duration']].drop_duplicates()
    both=both.merge(meta,on='timing',validate='many_to_one');both['arrival_order']=np.where(both.s_arrival<both.d_arrival,'S_first',np.where(both.s_arrival>both.d_arrival,'D_first','same'))
    both['overlap']=np.maximum(0,np.minimum(both.s_arrival+both.S_duration,both.d_arrival+both.D_duration)-np.maximum(both.s_arrival,both.d_arrival))
    both.to_csv(OUT/'joint_success.csv',index=False)
    print(both.groupby(['mode','arrival_order']).all_scales.agg(['sum','count']).to_string(),flush=True)

if __name__=='__main__':main()
