"""Stage control retaining each edge's unweighted mean size susceptibility.

Extension after initial equal-gate controls: avoids conflating removal of
temporal variation with forcing every edge to the same attack susceptibility.
"""
import json
import numpy as np
import pandas as pd
from stage_vegetation_network import DEFAULT
from multiyear_stage_network import simulate_years
from run_evidence_constrained import OUT,options,contrasts,METRICS


def main():
    (OUT/'mean_gate_design.json').write_text(json.dumps(dict(
        rationale='Added after initial stage grid. Constant common gates also change mean susceptibility; this control matches the mean separately for each overlapping predator-prey pair.',
        weighting='Unweighted mean over .25-day active aquatic overlap, independent of realized densities; not an exact density-weighted hazard match.',
        profiles=['refuge_only','litter_response'],size_gate=1,
        pathway_scaling='edge_SF/DF/DS/SD receive their corresponding time-mean logistic gate'),indent=2)+'\n',encoding='utf-8')
    outputs=[]
    for profile in ('refuge_only','litter_response'):
        original=pd.read_csv(OUT/('stage_'+profile+'_None_summary.csv'))
        cols=['profile','timing','refuge_order','attack_scale','cue','reverse','roles','rho',
              'vegetation','S_source','D_source','f_arrival','s_arrival','d_arrival',
              'F_duration','S_duration','D_duration','size_gate']
        des=original[cols].copy();des['timing']=des.timing.str.replace('gateNone','gate_mean',regex=False)
        des['size_gate']='mean_matched'
        arr=des[['f_arrival','s_arrival','d_arrival']].to_numpy(float)
        dur=des[['F_duration','S_duration','D_duration']].to_numpy(float)
        totals={k:np.zeros(len(des)) for k in ('SF','DF','DS','SD')}
        counts={k:np.zeros(len(des)) for k in totals}
        for t in np.arange(0,120,.25):
            size=.15+np.maximum(t-arr,0)*np.array([.020,.014,.015])
            present=(t>=arr)&(t<arr+dur)
            fs,ss,ds=size.T
            z={'SF':8*(ss-fs),'DF':3*(ds-.5*fs),'DS':8*(ds-ss),'SD':8*(ss-ds)}
            masks={'SF':present[:,0]&present[:,1],'DF':present[:,0]&present[:,2],
                   'DS':present[:,1]&present[:,2],'SD':present[:,1]&present[:,2]}
            for k in totals:
                totals[k]+=masks[k]/(1+np.exp(-np.clip(z[k],-60,60)));counts[k]+=masks[k]
        opt=options(profile,des.vegetation.to_numpy(),dur);opt['size_gate']=1.
        for k in totals:
            mean=np.divide(totals[k],counts[k],out=np.zeros(len(des)),where=counts[k]>0)
            opt['pathway_controls']['edge_'+k]=mean;des['mean_gate_'+k]=mean
        kernel=des[[k for k in DEFAULT if k in des]+['rho']].to_dict('records')
        sources=np.column_stack([np.ones(len(des)),des.S_source,des.D_source])
        tr=simulate_years(kernel,source_cohorts=sources,seasonal_options=opt)
        tail=tr[tr.year>=60]
        su=tail.groupby('scenario_id')[METRICS].mean().join(des.reset_index(drop=True)).reset_index()
        su['F_B_sd']=tail.groupby('scenario_id').F_B.std(ddof=0).to_numpy()
        su.to_csv(OUT/('stage_'+profile+'_mean_summary.csv'),index=False)
        cc=contrasts(su);cc['size_gate']='mean_matched';outputs.append(cc)
        print('Mean-matched size control',profile,flush=True)
    cc=pd.concat(outputs,ignore_index=True);cc.to_csv(OUT/'mean_gate_contrasts.csv',index=False)
    q=cc[(cc.metric=='F_B')&(cc.D_high==2)&cc.D_low.isin([.25,1.])&(cc.S_low==.25)&(cc.S_high==2)]
    print(q.groupby(['profile','D_low']).all_three.agg(['size','sum']).to_string(),flush=True)


if __name__=='__main__':main()
