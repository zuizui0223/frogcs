"""Fixed generality grid: recipient x response x stage; all failures retained."""
import itertools,json,hashlib
import numpy as np
import pandas as pd
from nee_context_robustness import ROOT
from refuge_response_20261029 import FAMILIES
from refuge_annual_summary_20261029 import summarize_years
from run_literature_extension import CONTEXTS
from multiyear_stage_network import DEMOGRAPHY
OUT=ROOT/'research/results/refuge_generality_20261029'
ROLES=['no_direct_function','F_from_S','F_from_D','F_both','S_from_D','D_from_S','D_attack_support','D_emergence_support','F_and_S_refuge']

def computation_provenance(dt):
 names=['run_refuge_generality.py','refuge_response_20261029.py','stage_refuge_generality_20261029.py','refuge_annual_summary_20261029.py','multiyear_stage_network.py','run_literature_extension.py']
 return dict(dt=dt,years=80,window=20,conversion=4.,demography=DEMOGRAPHY,numpy=np.__version__,pandas=pd.__version__,source_hashes={n:hashlib.sha256((ROOT/'research/scripts'/n).read_bytes()).hexdigest() for n in names})

def design(secondary=False):
 rows=[]
 settings=[(ctx,fam,role,k,r) for ctx,fam,role in itertools.product(CONTEXTS,FAMILIES,ROLES) for k,r in [(1.,.25)]] if not secondary else [(CONTEXTS[0],fam,'F_from_S',k,r) for fam,k,r in itertools.product(FAMILIES,[.5,1.,2.],[.25,.5,.75])]
 for (ctx,fam,role,k,r),arm,edge,v,s,d in itertools.product(settings,['1000','1111'],[0,1],[0.,1.],[.25,2.] if secondary else [0.,.25,2.],[.25,2.]):
  rows.append(dict(**ctx,family=fam,role=role,K=k,refuge_strength=r,arm=arm,DS_edge=edge,V=v,S_source=s,D_source=d))
 return pd.DataFrame(rows)

def simulate_design(de,dt,path):
 meta=path.with_suffix(path.suffix+'.json')
 provenance=json.loads(json.dumps(computation_provenance(dt)))
 if path.exists():
  if not meta.exists():raise ValueError('Missing computation provenance; move old cache and recompute')
  saved=json.loads(meta.read_text())
  if saved.get('computation')!=provenance or saved.get('output_sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():raise ValueError('Cache provenance mismatch; move old cache and recompute')
  cached=pd.read_csv(path,dtype={'arm':str});pd.testing.assert_frame_equal(cached[de.columns],de.reset_index(drop=True),check_dtype=False);return cached
 role=de.role;r=de.refuge_strength.to_numpy();zero=np.zeros(len(de));controls={k:zero.copy() for k in ['cover_SF','cover_DF','cover_DS','cover_SD','support_DF','support_DS','emerge_survival','emerge_exposure','cue_SD']}
 controls.update(cover_SF=role.isin(['F_from_S','F_both','F_and_S_refuge']).to_numpy(float),cover_DF=role.isin(['F_from_D','F_both']).to_numpy(float),cover_DS=role.isin(['S_from_D','F_and_S_refuge']).to_numpy(float)*r/.8,cover_SD=(role=='D_from_S').to_numpy(float)*r/.8,support_DF=(role=='D_attack_support').to_numpy(float)*r/.8,emerge_survival=(role=='D_emergence_support').to_numpy(float),edge_DS=de.DS_edge.to_numpy(float))
 p=[dict(community='FD' if x.S_source==0 else 'FSD',roles=15,refuge_order='D',vegetation=x.V,f_arrival=20.,s_arrival=float(x.sa),d_arrival=float(x.da),attack_scale=.5,cue=0.,reverse=False,rho=.75) for x in de.itertuples()]
 opts=dict(pathway_controls=controls,stage_durations=np.column_stack([np.full(len(de),45.),np.full(len(de),80.),de.dduration]),s_handling_matrix=np.array([[int(i) for i in a] for a in de.arm]),s_growth=de.sg.to_numpy(),d_growth=de.dg.to_numpy(),response_family=de.family.to_numpy(),response_scale=de.K.to_numpy(),refuge_strength=r)
 su=summarize_years(p,years=80,window=20,dt=dt,source_cohorts=np.column_stack([np.ones(len(de)),de.S_source,de.D_source]),seasonal_options=opts,conversion=4.)
 a=pd.concat([de.reset_index(drop=True),su],axis=1);a.to_csv(path,index=False,compression={'method':'gzip','mtime':0})
 meta.write_text(json.dumps(dict(computation=provenance,output_sha256=hashlib.sha256(path.read_bytes()).hexdigest()),indent=2)+'\n');return a

def summarize(allrows,tag):
 rows=[]
 keys=['context','family','role','K','refuge_strength','arm','DS_edge']
 for key,g in allrows.groupby(keys):
  g=g.set_index(['V','S_source','D_source']);meta=dict(zip(keys,key))
  for path in ['audit_H_SF','audit_H_DF','H_total','F_B']:
   z=g[path] if path!='H_total' else g.audit_H_SF+g.audit_H_DF
   for s in sorted(g.index.get_level_values('S_source').unique()):
    val=z.loc[1.,s,2.]-z.loc[1.,s,.25]-z.loc[0.,s,2.]+z.loc[0.,s,.25]
    rows.append(dict(**meta,path=path,contrast='OV',at=s,value=val))
   for v in [0.,1.]:
    val=z.loc[v,2.,2.]-z.loc[v,2.,.25]-z.loc[v,.25,2.]+z.loc[v,.25,.25]
    rows.append(dict(**meta,path=path,contrast='OS',at=v,value=val))
   for d in [.25,2.]:
    val=z.loc[1.,2.,d]-z.loc[1.,.25,d]-z.loc[0.,2.,d]+z.loc[0.,.25,d]
    rows.append(dict(**meta,path=path,contrast='SV',at=d,value=val))
 q=pd.DataFrame(rows);q.to_csv(OUT/(tag+'_contrasts.csv'),index=False)
 index=[k for k in keys if k!='DS_edge']+['path','contrast','at'];e=q.pivot(index=index,columns='DS_edge',values='value').reset_index();e['edge_contribution']=e[1]-e[0];e=e.rename(columns={0:'edge_off',1:'edge_on'});e.to_csv(OUT/(tag+'_edge_contribution.csv'),index=False)
 if (q['at']==0).any():
  absent=e[(e.contrast=='OV')&(e['at']==0)];np.testing.assert_allclose(absent.edge_contribution,0,atol=1e-12)
 return q

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 for secondary in [False,True]:
  de=design(secondary);label='scale' if secondary else 'primary';de.to_csv(OUT/(label+'_design.csv'),index=False)
  for dt,tag in [(.25,'dt025'),(.125,'dt0125')]:
   frames=[]
   for ctx,g in de.groupby('context',sort=False):
    frames.append(simulate_design(g.reset_index(drop=True),dt,OUT/(label+'_'+tag+'_'+ctx+'_cells.csv.gz')));print('finished',label,tag,ctx,len(g),flush=True)
   summarize(pd.concat(frames,ignore_index=True),label+'_'+tag)
 paths=[ROOT/'research/scripts'/n for n in ['refuge_response_20261029.py','stage_refuge_generality_20261029.py','refuge_annual_summary_20261029.py','run_refuge_generality.py']]
 (OUT/'simulation_receipt.json').write_text(json.dumps(dict(primary_cells=len(design()),secondary_cells=len(design(True)),timesteps=[.25,.125],source_base='0da1d82a966c660f826de13991c5be1676a2b444',scope='finite fixed grid; proportions not ecological probabilities',density_scale_calibrated=False,hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2)+'\n')
if __name__=='__main__':main()
