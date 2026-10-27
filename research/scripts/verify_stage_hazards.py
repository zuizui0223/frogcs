"""Numerical verification of every dynamically-sized successful stage context."""
import numpy as np
import pandas as pd
from stage_vegetation_network import DEFAULT
from multiyear_stage_network import simulate_years
from run_evidence_constrained import options
from audit_response_scales import compare,transform
from audit_stage_hazards import OUT
c=pd.read_csv(OUT/'dynamic_contrasts.csv');c=c[(c.D_low==.25)&c.metric.isin(['F_B','log_F_B','log_F_fraction','negative_H'])]
passed=c.groupby('timing').all_three.all();names=passed[passed].index
base=pd.read_csv(OUT/'dynamic_summary.csv');base=base[base.timing.isin(names)].reset_index(drop=True)
opt=options('refuge_only',base.vegetation.to_numpy(),base[['F_duration','S_duration','D_duration']].to_numpy());opt['pathway_controls']['cover_DF']=0.;opt['diagnostics']=True
kernel=base[[k for k in DEFAULT if k in base]+['rho']].to_dict('records');source=np.column_stack([np.ones(len(base)),base.S_source,base.D_source])
rows=[]
for label,kwargs in {'half_step':{'dt':.125},'horizon160':{'years':160}}.items():
 tr=simulate_years(kernel,source_cohorts=source,seasonal_options=opt,**kwargs);tail=tr[tr.year>tr.year.max()-20].copy();tail['negative_H']=-tail.audit_H_SF-tail.audit_H_DF
 assert np.max(abs(np.log(tail.F_fraction)-tail.negative_H))<1e-9
 su=transform(tail.groupby('scenario_id')[['F_B','F_fraction','negative_H']].mean().join(base[['timing','vegetation','S_source','D_source']]))
 su.to_csv(OUT/('verified_'+label+'_summary.csv'),index=False)
 for name,g in su.groupby('timing'):rows+=compare(g,dict(check=label,timing=name))
 print(label,'complete',len(names),flush=True)
r=pd.DataFrame(rows);r.to_csv(OUT/'numerical_checks.csv',index=False)
x=r[(r.D_low==.25)&r.metric.isin(['F_B','log_F_B','log_F_fraction','negative_H'])].groupby(['check','timing']).all_three.all()
print(x.groupby('check').agg(['sum','count']).to_string(),flush=True)
