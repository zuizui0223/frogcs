"""Independent stage-order/duration and size-gate controls for two candidates."""
import itertools
import json
import numpy as np
import pandas as pd
from run_evidence_constrained import OUT,options,contrasts,METRICS
from multiyear_stage_network import simulate_years


def main():
    design=dict(F_arrival=20,S_arrival=[0,20,40],D_arrival=[0,20,40],
        F_duration=[45,60,75],S_duration=[40,60,80],D_duration=[40,60,70],
        size_gates=['dynamic',.25,.5,.75],profiles={'refuge_only':3.,'litter_response':1.5},
        cue=0,reverse=False,refuge_order='S',rho=.5,years=80,dt=.25,
        scope='Independent exploratory grid; no density-linked development. Constants change mean attacks as well as remove size dependence.',
        fixed_before_run=True)
    (OUT/'stage_grid_design.json').write_text(json.dumps(design,indent=2)+'\n',encoding='utf-8')
    summaries=[];compares=[]
    for profile,attack in design['profiles'].items():
        for gate in (None,.25,.5,.75):
            rows=[]
            for sa,da,fd,sd,dd in itertools.product([0,20,40],[0,20,40],[45,60,75],[40,60,80],[40,60,70]):
                name=f'S{sa}_D{da}_dur{fd}_{sd}_{dd}_gate{gate}'
                for v,s,d in itertools.product([0.,1.],[.25,1.,2.],[.25,1.,2.]):
                    rows.append(dict(profile=profile,timing=name,f_arrival=20,s_arrival=sa,d_arrival=da,
                        F_duration=fd,S_duration=sd,D_duration=dd,size_gate='dynamic' if gate is None else str(gate),
                        refuge_order='S',attack_scale=attack,cue=0.,reverse=False,roles=15,rho=.5,
                        vegetation=v,S_source=s,D_source=d))
            des=pd.DataFrame(rows)
            durations=des[['F_duration','S_duration','D_duration']].to_numpy(float)
            kernel=des.drop(columns=['profile','timing','F_duration','S_duration','D_duration','size_gate','S_source','D_source']).to_dict('records')
            opt=options(profile,des.vegetation.to_numpy(),durations);opt['size_gate']=gate
            source=np.column_stack([np.ones(len(des)),des.S_source,des.D_source])
            tr=simulate_years(kernel,source_cohorts=source,seasonal_options=opt)
            tail=tr[tr.year>=60]
            su=tail.groupby('scenario_id')[METRICS].mean().join(des).reset_index()
            su['F_B_sd']=tail.groupby('scenario_id').F_B.std(ddof=0).to_numpy()
            label=profile+'_'+str(gate)
            su.to_csv(OUT/('stage_'+label+'_summary.csv'),index=False)
            cc=contrasts(su)
            meta=des[['timing','F_duration','S_duration','D_duration','s_arrival','d_arrival','size_gate']].drop_duplicates()
            cc=cc.merge(meta,on='timing',validate='many_to_one')
            compares.append(cc);summaries.append(su)
            q=cc[(cc.metric=='F_B')&(cc.D_low==1)&(cc.D_high==2)&(cc.S_low==.25)&(cc.S_high==2)]
            print('Stage grid',label,len(su),'local matches',int(q.all_three.sum()),flush=True)
    pd.concat(summaries,ignore_index=True).to_csv(OUT/'stage_grid_summary.csv',index=False)
    cc=pd.concat(compares,ignore_index=True);cc.to_csv(OUT/'stage_grid_contrasts.csv',index=False)
    q=cc[(cc.metric=='F_B')&(cc.D_high==2)&cc.D_low.isin([.25,1.])&(cc.S_low==.25)&(cc.S_high==2)]
    q.groupby(['profile','size_gate','D_low']).all_three.agg(['size','sum']).to_csv(OUT/'stage_grid_counts.csv')


if __name__=='__main__':main()
