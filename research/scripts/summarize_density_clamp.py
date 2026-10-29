"""Finite-grid signs and mediator predictions; neither calibration nor field proof."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'research/results/density_clamp_20261029'

def main():
 validation={}
 for name,keys in [('season',['context','family','role','arm','F0','mode','DS_edge','path','contrast','at']),('bridge',['context','arm','initial_policy','clamp','path','contrast','at'])]:
  prefix='' if name=='season' else 'bridge_'
  a=pd.read_csv(P/f'{prefix}dt025_contrasts.csv',dtype={'arm':str});b=pd.read_csv(P/f'{prefix}dt0125_contrasts.csv',dtype={'arm':str})
  z=a.merge(b,on=keys,suffixes=('_025','_0125'),validate='one_to_one');assert len(z)==len(a)==len(b)
  z['stable']=np.sign(z.value_025.where(abs(z.value_025)>1e-9,0))==np.sign(z.value_0125.where(abs(z.value_0125)>1e-9,0));z['difference']=z.value_025-z.value_0125
  z.to_csv(P/f'{name}_timestep.csv',index=False)
  h=z[z.path=='H_total'].copy()
  for tag in ['025','0125']:h['pass_'+tag]=np.where(h.contrast=='SV',-h['value_'+tag],h['value_'+tag])>1e-9
  group=[x for x in keys if x not in ['path','contrast','at']]
  joint=h.groupby(group).agg(pass025=('pass_025','all'),pass0125=('pass_0125','all')).reset_index();joint['both']=joint.pass025 & joint.pass0125;joint.to_csv(P/f'{name}_joint.csv',index=False)
  validation[name]=dict(contrasts=len(z),sign_changes=int((~z.stable).sum()),hazard_sign_changes=int((~h.stable).sum()),max_absolute_difference=float(abs(z.difference).max()),joint_count=int(joint.both.sum()))
 # Direct effects at fixed F/S/D expose which mediator would distinguish roles.
 for tag in ['dt025','dt0125']:
  a=pd.read_csv(P/f'{tag}_cells.csv.gz',dtype={'arm':str});a=a[(a['mode']=='FSD_clamped')&(a.DS_edge==1)]
  rows=[]
  for key,g in a.groupby(['context','family','role','arm','F0','S0','D0']):
   g=g.set_index('V');meta=dict(zip(['context','family','role','arm','F0','S0','D0'],key))
   for path in ['audit_H_SF','audit_H_DF','audit_H_DS','audit_H_SD']:
    rows.append(dict(**meta,path=path,lowV=g.loc[0.,path],highV=g.loc[1.,path],ratio=g.loc[1.,path]/g.loc[0.,path] if g.loc[0.,path]>0 else np.nan))
  pd.DataFrame(rows).to_csv(P/f'{tag}_direct_mediator_predictions.csv',index=False)
 e=pd.read_csv(P/'dt025_edge_effects.csv');f=pd.read_csv(P/'dt0125_edge_effects.csv')
 keys=['context','family','role','arm','F0','mode','path','contrast','at']
 e=e.merge(f,on=keys,suffixes=('_025','_0125'),validate='one_to_one')
 q=e[(e.role=='F_from_S')&(e['mode']=='F_clamped')&(e.path=='H_total')&(e.contrast=='OV')]
 validation['F_clamp_rescue_loss']=dict(contrasts=len(q),positive_both=int(((q.edge_difference_025>1e-9)&(q.edge_difference_0125>1e-9)).sum()),min025=float(q.edge_difference_025.min()),max025=float(q.edge_difference_025.max()))
 (P/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
 print(json.dumps(validation,indent=2))

if __name__=='__main__':main()
