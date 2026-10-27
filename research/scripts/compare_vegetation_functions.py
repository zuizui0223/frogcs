"""Factorial vegetation functions on fixed reciprocal-predation model; no fitting."""
import itertools,json
from pathlib import Path
import numpy as np
import pandas as pd
from stage_vegetation_network import DEFAULT
from multiyear_stage_network import simulate_years
from run_evidence_constrained import options
from audit_response_scales import compare,transform
OUT=Path(__file__).resolve().parents[1]/'results/vegetation_functions_20261027'
FUNCTIONS=list(itertools.product([0,1],[0,1],[0,1],['none','survival','timing']))
def label(f,s,d,e):return f'F{f}_S{s}_D{d}_E{e}'
def make_design(functions,wide=True):
 rows=[]
 stages=itertools.product([0,20,40],[0,20,40],[40,60,80] if wide else [40],[40,60,70] if wide else [40])
 for sa,da,sd,dd in stages:
  for f,sp,dp,e in functions:
   for v,s,d in itertools.product([0.,1.],[.25,1.,2.],[.25,1.,2.]):
    rows.append(dict(function=label(f,sp,dp,e),protect_F=f,protect_S=sp,protect_D=dp,emergence=e,timing=f'S{sa}_D{da}_dur45_{sd}_{dd}',f_arrival=20,s_arrival=sa,d_arrival=da,F_duration=45,S_duration=sd,D_duration=dd,vegetation=v,S_source=s,D_source=d,refuge_order='S',attack_scale=3.,cue=0.,reverse=False,roles=15,rho=.5))
 return pd.DataFrame(rows)
def run(des,strength=1.,**kwargs):
 opt=options('refuge_only',des.vegetation.to_numpy(),des[['F_duration','S_duration','D_duration']].to_numpy())
 opt['pathway_controls'].update(cover_DF=0.,cover_SF=strength*des.protect_F.to_numpy(),cover_DS=strength*des.protect_S.to_numpy(),cover_SD=strength*des.protect_D.to_numpy(),emerge_survival=strength*(des.emergence=='survival').to_numpy())
 opt['emergence_delay']=5*des.vegetation.to_numpy()*(des.emergence=='timing').to_numpy()
 opt['diagnostics']=True
 kernel=des[[k for k in DEFAULT if k in des]+['rho']].to_dict('records')
 source=np.column_stack([np.ones(len(des)),des.S_source,des.D_source])
 tr=simulate_years(kernel,source_cohorts=source,seasonal_options=opt,**kwargs)
 tail=tr[tr.year>tr.year.max()-20].copy();tail['negative_H']=-tail.audit_H_SF-tail.audit_H_DF
 error=float(np.max(abs(np.log(tail.F_fraction)-tail.negative_H)));assert error<1e-9
 cols=['F_B','F_fraction','negative_H','S_B','D_B','D_fraction','D_local','audit_H_SF','audit_H_DF','audit_H_DS','audit_H_SD','audit_H_failure']
 su=transform(tail.groupby('scenario_id')[cols].mean().join(des))
 su['F_B_sd']=tail.groupby('scenario_id').F_B.std(ddof=0)
 return su,error

def main():
 OUT.mkdir(exist_ok=True,parents=True)
 design=dict(F_protection=[0,1],S_protection=[0,1],D_protection=[0,1],emergence=['none','survival','timing'],stage_settings=81,cells_per_setting=18,total_scenarios=34992,years=80,dt=.25,source_range=[.25,1,2],rho=.5,attack=3,cue=0,reverse=False,
  coefficients='F hazard reduction exp(-1.25 V); S/D protection exp(-0.8 V); emergence-stage loss hazard 0.1 exp(-0.8 V); timing +5V days aquatic. All strengths synthetic; timing magnitude motivated by one study, not universal.',
  scope='Factorial independent functions, not presumed vegetation tradeoffs. No foraging boost. Emergence survival is generic stage loss proxy, not empirically measured intrinsic molting failure. Predation-size structure fixed to prior audited model.',
  criterion='Full supply range, three directions in F_B/log_F_B/log_F_fraction/negative_H; not fitted macro regression coefficients.',fixed_before_run=True)
 (OUT/'design.json').write_text(json.dumps(design,indent=2)+'\n')
 allcs=[]
 for start in range(0,len(FUNCTIONS),4):
  des=make_design(FUNCTIONS[start:start+4]);su,err=run(des)
  for function,g in su.groupby('function'):
   g.to_csv(OUT/(function+'_summary.csv'),index=False)
   rows=[]
   for timing,q in g.groupby('timing'):rows+=compare(q,dict(function=function,timing=timing))
   cc=pd.DataFrame(rows);cc.to_csv(OUT/(function+'_contrasts.csv'),index=False);allcs.append(cc)
  print('Completed functions',start+4,'of',len(FUNCTIONS),'scenarios',len(des),'identity_error',err,flush=True)
 c=pd.concat(allcs,ignore_index=True);c.to_csv(OUT/'all_contrasts.csv',index=False)
 full=c[c.D_low==.25];full.groupby(['function','metric']).all_three.agg(['sum','count']).to_csv(OUT/'scale_counts.csv')
 joint=full[full.metric.isin(['F_B','log_F_B','log_F_fraction','negative_H'])].groupby(['function','timing']).all_three.all().rename('all_scales').reset_index()
 joint.to_csv(OUT/'joint_success.csv',index=False)
 print(joint.groupby('function').all_scales.agg(['sum','count']).to_string(),flush=True)
if __name__=='__main__':main()
