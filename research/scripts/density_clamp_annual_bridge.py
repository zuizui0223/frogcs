"""Replay actual yearly starts, then separate inherited F contrasts and loss."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from stage_density_clamp_20261029 import simulate
ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'research/results/nee_boundaries_20261029'
OUT=ROOT/'research/results/density_clamp_20261029'

def main():
 errors={}
 for dt,tag in [(.25,'dt025'),(.125,'dt0125')]:
  old=pd.read_csv(OLD/f'{tag}_annual.csv.gz',dtype={'arm':str})
  states=np.load(OLD/f'{tag}_annual_states.npy');assert states.shape==(20,120,3)
  cols=['context','sa','da','dduration','sg','dg','arm','vegetation','S_source','D_source']
  de=pd.concat([old[cols].assign(year=i) for i in range(20)],ignore_index=True)
  initial=states.reshape(-1,3)
  de['initial_F']=initial[:,0];de['initial_S']=initial[:,1];de['initial_D']=initial[:,2]
  common=de.groupby(['year','context','arm']).initial_F.transform('mean').to_numpy()
  params=[dict(community='FSD',roles=15,refuge_order='D',vegetation=r.vegetation,f_arrival=20.,s_arrival=r.sa,d_arrival=r.da,attack_scale=.5,cue=0.,reverse=False) for r in de.itertuples()]
  controls=dict(cover_SF=1.,cover_DF=0.,cover_DS=0.,cover_SD=0.,support_DF=0.,support_DS=0.,emerge_survival=0.,emerge_exposure=0.,cue_SD=0.)
  frames=[]
  for shared in [False,True]:
   for clamp in [False,True]:
    start=initial.copy()
    if shared:start[:,0]=common
    a=simulate(params,dt=dt,initial_cohorts=start,stage_durations=np.column_stack([np.full(len(de),45.),np.full(len(de),80.),de.dduration]),pathway_controls=controls,diagnostics=True,s_growth=de.sg.to_numpy(),d_growth=de.dg.to_numpy(),s_handling_matrix=np.array([[int(i) for i in x] for x in de.arm]),response_family='mixed',refuge_strength=.25,clamp_guilds='F' if clamp else '')
    use=['audit_H_SF','audit_H_DF','audit_H_DS','audit_H_SD','F_killed_by_S','F_killed_by_D','S_killed_by_D','D_killed_by_S']
    if not shared and not clamp:
     replay=a[use].to_numpy().reshape(20,120,len(use)).mean(axis=0)
     errors[tag]=float(np.max(abs(replay-old[use].to_numpy())))
     np.testing.assert_allclose(replay,old[use],atol=1e-10)
    q=pd.concat([de,a[use]],axis=1);q['F_start_used']=start[:,0]
    q['initial_policy']='common_F' if shared else 'inherited_F';q['clamp']=clamp
    q['H_total']=q.audit_H_SF+q.audit_H_DF;q['sentinel_survival']=np.exp(-q.H_total)
    frames.append(q)
  full=pd.concat(frames,ignore_index=True);full.to_csv(OUT/f'bridge_{tag}_yearly.csv.gz',index=False,compression={'method':'gzip','mtime':0})
  keys=['context','arm','vegetation','S_source','D_source','initial_policy','clamp']
  means=full.groupby(keys)[use+['H_total','sentinel_survival','F_start_used','initial_S','initial_D']].mean().reset_index();means.to_csv(OUT/f'bridge_{tag}_means.csv',index=False)
  result=[]
  for key,g in means.groupby(['context','arm','initial_policy','clamp']):
   z=g.set_index(['vegetation','S_source','D_source']);meta=dict(zip(['context','arm','initial_policy','clamp'],key))
   for path in ['H_total','audit_H_SF','audit_H_DF']:
    v=z[path]
    for label,ats in [('OS',[0.,1.]),('OV',[.25,2.]),('SV',[.25,2.])]:
     for at in ats:
      if label=='OS':delta=v.loc[at,2.,2.]-v.loc[at,2.,.25]-v.loc[at,.25,2.]+v.loc[at,.25,.25]
      elif label=='OV':delta=v.loc[1.,at,2.]-v.loc[1.,at,.25]-v.loc[0.,at,2.]+v.loc[0.,at,.25]
      else:delta=v.loc[1.,2.,at]-v.loc[1.,.25,at]-v.loc[0.,2.,at]+v.loc[0.,.25,at]
      result.append(dict(**meta,path=path,contrast=label,at=at,value=delta))
  pd.DataFrame(result).to_csv(OUT/f'bridge_{tag}_contrasts.csv',index=False)
 files=[Path(__file__),ROOT/'research/scripts/stage_density_clamp_20261029.py']+[OLD/f'{tag}_{suffix}' for tag in ['dt025','dt0125'] for suffix in ['annual.csv.gz','annual_states.npy']]
 (OUT/'bridge_receipt.json').write_text(json.dumps(dict(replay_error=errors,years=20,original_scenarios=120,initial_F_standardization='mean of eight V/S-source/D-source corners within year/context/handling',re_equilibrated=False,source_hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}),indent=2)+'\n')
 print(errors)

if __name__=='__main__':main()
