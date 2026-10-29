"""Annual summary with directed handling ablations and the unchanged recurrence."""
import numpy as np
import pandas as pd
from stage_refuge_generality_20261029 import DEFAULT,simulate
from multiyear_stage_network import DEMOGRAPHY

def summarize_years(scenarios,years=80,window=20,dt=.25,source_cohorts=None,seasonal_options=None,**demography):
 cfg={**DEMOGRAPHY,**demography}
 if set(demography)-set(DEMOGRAPHY):raise ValueError('Unknown demography')
 if not 1<=window<=years:raise ValueError('Invalid window')
 n=len(scenarios);rho=np.array([r.get('rho',.5) for r in scenarios])[:,None]
 kernel=[{k:v for k,v in r.items() if k!='rho'} for r in scenarios]
 params=[{**DEFAULT,**r} for r in kernel]
 present=np.array([[1,int(r['community'] in ('FS','FSD')),int(r['community'] in ('FD','FSD'))] for r in params],float)
 B=present*cfg['initial_scale'];source=present if source_cohorts is None else np.asarray(source_cohorts,float)
 s=np.array(cfg['survival']);b=np.array(cfg['conversion']);j=np.array(cfg['juvenile']);m=np.array(cfg['delays'],int);K=cfg['capacity']
 immigrant=(1-rho)*(1-s)*source;upper=np.maximum(B,(rho*b*K+immigrant)/(1-s));ring={};sums={};squares=np.zeros(n);minimum_F=np.ones(n);minimum_S=np.ones(n)
 options={**(seasonal_options or {}),'diagnostics':True}
 for year in range(years):
  out=simulate(kernel,dt=dt,initial_cohorts=B,**options)
  C=out[[g+'_completed' for g in 'FSD']].to_numpy();ring[year]=C
  due=np.zeros_like(B)
  for k in range(3):
   origin=year+1-m[k]
   if origin>=0:due[:,k]=ring[origin][:,k]
  local=rho*b*j**(m-1)*due/(1+due/K);nextB=s*B+local+immigrant
  if not np.isfinite(nextB).all() or (nextB<0).any() or (nextB>upper+1e-10).any():raise AssertionError('Annual bounds')
  for k in list(ring):
   if k<year+1-int(max(m)):del ring[k]
  if year>=years-window:
   values={}
   for k,g in enumerate('FSD'):
    values[g+'_B']=B[:,k];values[g+'_fraction']=np.divide(C[:,k],B[:,k],out=np.ones(n),where=B[:,k]>0)
   for col in ['F_killed_by_S','F_killed_by_D','S_killed_by_D','D_killed_by_S','D_killed_by_F','audit_H_SF','audit_H_DF','audit_H_DS','audit_H_SD','audit_H_FE','audit_H_failure']:values[col]=out[col].to_numpy()
   minimum_F=np.minimum(minimum_F,values['F_fraction']);minimum_S=np.minimum(minimum_S,values['S_fraction'])
   if not np.allclose(np.log(values['F_fraction']),-values['audit_H_SF']-values['audit_H_DF'],atol=1e-9,rtol=0):raise AssertionError('Hazard identity')
   for col,val in values.items():sums[col]=sums.get(col,np.zeros(n))+val
   squares+=B[:,0]**2
  B=nextB
 frame=pd.DataFrame({k:v/window for k,v in sums.items()})
 frame['F_B_sd']=np.sqrt(np.maximum(0,squares/window-frame.F_B.to_numpy()**2));frame['minimum_F_survival']=minimum_F;frame['minimum_S_survival']=minimum_S
 return frame
