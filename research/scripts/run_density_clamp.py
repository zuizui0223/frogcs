"""Fixed within-season replenishment interventions; no acoustic calibration."""
from pathlib import Path
import itertools,json,hashlib
import numpy as np
import pandas as pd
from stage_density_clamp_20261029 import simulate
from run_literature_extension import CONTEXTS
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/results/density_clamp_20261029'
KEYS=['context','family','role','arm','F0','mode','DS_edge']

def design():
 rows=[]
 for ctx,family,role,arm,f,mode,edge,v,s,d in itertools.product(CONTEXTS,['constant','II','III','mixed'],['none','F_from_S','S_from_D','F_and_S_refuge'],['1000','1111'],[1.,3.,6.],['dynamic','F_clamped','FSD_clamped'],[0,1],[0.,1.],[.25,2.],[.25,2.]):
  rows.append(dict(**ctx,family=family,role=role,arm=arm,F0=f,mode=mode,DS_edge=edge,V=v,S0=s,D0=d))
 return pd.DataFrame(rows)

def run(de,dt):
 frames=[]
 for mode,g in de.groupby('mode',sort=False):
  g=g.reset_index(drop=True);role=g.role
  controls={n:0. for n in ['cover_SF','cover_DF','cover_DS','cover_SD','support_DF','support_DS','emerge_survival','emerge_exposure','cue_SD']}
  controls.update(cover_SF=role.isin(['F_from_S','F_and_S_refuge']).to_numpy(float),cover_DS=role.isin(['S_from_D','F_and_S_refuge']).to_numpy(float)*.25/.8,edge_DS=g.DS_edge.to_numpy(float))
  p=[dict(community='FSD',roles=15,refuge_order='D',vegetation=x.V,f_arrival=20.,s_arrival=x.sa,d_arrival=x.da,attack_scale=.5,cue=0.,reverse=False) for x in g.itertuples()]
  out=simulate(p,dt=dt,initial_cohorts=g[['F0','S0','D0']].to_numpy(),stage_durations=np.column_stack([np.full(len(g),45.),np.full(len(g),80.),g.dduration]),pathway_controls=controls,diagnostics=True,s_growth=g.sg.to_numpy(),d_growth=g.dg.to_numpy(),s_handling_matrix=np.array([[int(x) for x in a] for a in g.arm]),response_family=g.family.to_numpy(),response_scale=1.,refuge_strength=.25,clamp_guilds={'dynamic':'','F_clamped':'F','FSD_clamped':'FSD'}[mode])
  for guild in 'FSD':
   if guild+'_replaced' not in out:out[guild+'_replaced']=0.
  cols=[c for c in out if c.startswith('audit_') or c.endswith(('_completed','_replaced','_survived','_dead')) or '_killed_by_' in c]
  q=pd.concat([g,out[cols]],axis=1);q['H_total']=q.audit_H_SF+q.audit_H_DF;q['sentinel_survival']=np.exp(-q.H_total)
  if mode=='dynamic':np.testing.assert_allclose(q.F_completed/q.F0,q.sentinel_survival,atol=1e-12)
  frames.append(q)
 return pd.concat(frames,ignore_index=True)

def contrasts(a):
 rows=[]
 for key,g in a.groupby(KEYS):
  g=g.set_index(['V','S0','D0']);meta=dict(zip(KEYS,key))
  for path in ['H_total','audit_H_SF','audit_H_DF','audit_H_DS','audit_H_SD','sentinel_survival']:
   z=g[path]
   for label,atlist in [('OV',[.25,2.]),('OS',[0.,1.]),('SV',[.25,2.])]:
    for at in atlist:
     if label=='OV':val=z.loc[1.,at,2.]-z.loc[1.,at,.25]-z.loc[0.,at,2.]+z.loc[0.,at,.25]
     elif label=='OS':val=z.loc[at,2.,2.]-z.loc[at,2.,.25]-z.loc[at,.25,2.]+z.loc[at,.25,.25]
     else:val=z.loc[1.,2.,at]-z.loc[1.,.25,at]-z.loc[0.,2.,at]+z.loc[0.,.25,at]
     rows.append(dict(**meta,path=path,contrast=label,at=at,value=val))
 return pd.DataFrame(rows)

def main():
 OUT.mkdir(parents=True,exist_ok=True);de=design();assert len(de)==13824;de.to_csv(OUT/'design.csv',index=False)
 for dt,tag in [(.25,'dt025'),(.125,'dt0125')]:
  a=run(de,dt);a.to_csv(OUT/f'{tag}_cells.csv.gz',index=False,compression={'method':'gzip','mtime':0})
  q=contrasts(a);q.to_csv(OUT/f'{tag}_contrasts.csv',index=False)
  keys=[k for k in KEYS if k!='DS_edge']+['path','contrast','at']
  e=q.pivot(index=keys,columns='DS_edge',values='value').rename(columns={0:'off',1:'on'}).reset_index();e['edge_difference']=e.on-e.off;e.to_csv(OUT/f'{tag}_edge_effects.csv',index=False)
  null=e[(e['mode']=='FSD_clamped')&e.path.isin(['H_total','audit_H_SF','audit_H_DF','sentinel_survival'])];np.testing.assert_allclose(null.edge_difference,0,atol=1e-12)
  print(tag,len(a),'completed',flush=True)
 files=[Path(__file__),ROOT/'research/scripts/stage_density_clamp_20261029.py',ROOT/'research/scripts/refuge_response_20261029.py',ROOT/'research/scripts/run_literature_extension.py']
 (OUT/'receipt.json').write_text(json.dumps(dict(scope='within-season synthetic intervention; no annual recurrence or field calibration',cells_per_dt=len(de),dt=[.25,.125],F0=[1,3,6],source_hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},numpy=np.__version__,pandas=pd.__version__,cache_reuse=False),indent=2)+'\n')

if __name__=='__main__':main()
