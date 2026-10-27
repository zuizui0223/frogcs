"""Deterministic finalists and matched full-resolution nuisance validation."""
import json
import numpy as np
import pandas as pd
from final_mechanism_common import OUT,FEATURES,CONTEXTS,design,evaluate,score

def selection():
 models=pd.read_csv(OUT/'catalog.csv');ranking=pd.read_csv(OUT/'screen_ranking.csv')
 base={k:0 for k in FEATURES};base.update(edge_SD=1,edge_DS=1,behavior='none')
 specs=[('frog_refuge',{'cover_SF':1}),('salamander_refuge',{'cover_DS':1}),('both_refuge',{'cover_SF':1,'cover_DS':1}),('all_refuges',{'cover_SF':1,'cover_DF':1,'cover_DS':1,'cover_SD':1}),('emergence_survival',{'cover_SF':1,'survival':1}),('emergence_timing',{'cover_SF':1,'timing':1}),('feeding_support',{'cover_SF':1,'support_DF':1,'support_DS':1}),('cue_refuge',{'cover_SF':1,'behavior':'cue_SF'}),('risk_refuge',{'cover_SF':1,'behavior':'risk_refuge'}),('litter_response',{'cover_SF':1,'litter':1}),('reverse_predation',{'cover_SF':1,'reverse':1})]
 reasons={}
 for name,extra in specs:
  a={**base,**extra};mask=np.ones(len(models),bool)
  for k,v in a.items():mask &= models[k].to_numpy()==v
  ids=models.loc[mask,'model_id'].tolist();assert len(ids)==1
  reasons[ids[0]]='mandatory_'+name
 count={}
 for row in ranking.to_dict('records'):
  if len(reasons)>=20:break
  mid=int(row['model_id']);sig=(row['behavior'],row['litter'],row['edge_SD'],row['edge_DS'])
  if mid in reasons or count.get(sig,0)>=2:continue
  reasons[mid]='screen_rank_diversity';count[sig]=count.get(sig,0)+1
 if len(reasons)<20:
  for mid in ranking.model_id:
   if len(reasons)>=20:break
   reasons.setdefault(int(mid),'screen_rank_fill')
 selected=models[models.model_id.isin(reasons)].copy();selected['selection_reason']=selected.model_id.map(reasons);selected.to_csv(OUT/'finalists.csv',index=False)
 rng=np.random.default_rng(20261027);blocks=[]
 axes={k:rng.permutation(np.resize(v,24)) for k,v in dict(attack=[.5,1.5,3],rho=[.25,.5,.75],conversion=[2,4,8],strength=[.5,1.],refuge_order=['S','equal','D']).items()}
 constant_size=set(rng.choice(24,4,replace=False).tolist())
 for i in range(24):
  block=dict(block_id=i,f_arrival=int(rng.choice([0,20,40])),s_arrival=int(rng.choice([0,20,40])),d_arrival=int(rng.choice([0,20,40])),F_duration=int(rng.choice([45,60,75])),S_duration=int(rng.choice([40,60,80])),D_duration=int(rng.choice([40,60,70])),attack=float(axes['attack'][i]),rho=float(axes['rho'][i]),conversion=float(axes['conversion'][i]),strength=float(axes['strength'][i]),size_gate=.5 if i in constant_size else None,refuge_order=str(axes['refuge_order'][i]))
  blocks.append(block)
 # Retain full-resolution confirmation separately; never count it as fresh validation.
 for i,ctx in enumerate(CONTEXTS):blocks.append(dict(block_id=-i-1,**ctx,attack=3.,rho=.5,conversion=4.,strength=1.,size_gate=None,refuge_order='S'))
 (OUT/'validation_design.json').write_text(json.dumps(dict(seed=20261027,blocks=blocks,selection='11 prespecified anchors plus screen ranks with at most two per trophic/behavior family, up to20',sampling='Matched nuisance sensitivity, not independent field validation',floor_diagnostic=.05),indent=2)+'\n')
 return selected,blocks

def main():
 selected,blocks=selection();scores=[]
 # Batch independent contexts with exactly the same seasonal kernel options.
 # Scalar-versus-vector equivalence is checked in test_final_batch.py.
 for (behavior,litter),g in selected.groupby(['behavior','litter']):
  for gate in [None,.5]:
   pending=[];metadata=[]
   for b in blocks:
    if b['size_gate']!=gate:continue
    tag=f"validation_{b['block_id']}_{behavior}_{litter}";path=OUT/(tag+'_scores.csv')
    if path.exists():scores.append(pd.read_csv(path));continue
    ctx={k:b[k] for k in ['f_arrival','s_arrival','d_arrival','F_duration','S_duration','D_duration']}
    de=design(g,[ctx],[b['block_id']])
    for k in ['attack','rho','conversion','strength','refuge_order']:de['batch_'+k]=b[k]
    pending.append(de);metadata.append((b,tag,path))
   if not pending:continue
   de=pd.concat(pending,ignore_index=True)
   su=evaluate(de,years=80,window=20,dt=.25,size_gate=gate,**{k:de['batch_'+k].to_numpy() for k in ['attack','rho','conversion','strength','refuge_order']})
   for b,tag,path in metadata:
    part=su[su.block_id==b['block_id']].reset_index(drop=True);sc=score(part);sc.to_csv(path,index=False);part.to_csv(OUT/(tag+'_cells.csv.gz'),index=False,compression={'method':'gzip','mtime':0});scores.append(sc)
   print('Validated batch',behavior,litter,gate,len(metadata),'contexts',flush=True)
 allscores=pd.concat(scores,ignore_index=True);allscores.to_csv(OUT/'validation_scores.csv',index=False)
 fresh=allscores[allscores.block_id>=0];rank=fresh.groupby('model_id')[['floor_avoiding_pass','joint_pass','conditional_pass','macro_form_pass']].sum().join(selected.set_index('model_id')).sort_values(['floor_avoiding_pass','joint_pass','conditional_pass','extrapolation_flags','assumptions'],ascending=[False,False,False,True,True]);rank.to_csv(OUT/'validation_ranking.csv');print(rank.to_string(),flush=True)
if __name__=='__main__':main()
