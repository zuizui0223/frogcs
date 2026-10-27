"""Frozen finite structural catalog and scale/macro-form scoring."""
import itertools,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from stage_vegetation_network import DEFAULT
from final_network_summary import summarize_years
OUT=Path(__file__).resolve().parents[1]/'results/final_mechanism_20261027'
CELLS=list(itertools.product([0.,1.],[.25,1.,2.],[.25,1.,2.]))
CONTEXTS=[dict(f_arrival=20,s_arrival=40,d_arrival=20,F_duration=45,S_duration=40,D_duration=40),dict(f_arrival=20,s_arrival=40,d_arrival=20,F_duration=45,S_duration=40,D_duration=60),dict(f_arrival=20,s_arrival=0,d_arrival=20,F_duration=45,S_duration=60,D_duration=60)]
FEATURES=['cover_SF','cover_DF','cover_DS','cover_SD','survival','timing','support_DF','support_DS','edge_SD','edge_DS','reverse','behavior','litter']
def catalog():
 rows=[]
 for covers,edges,emerge,support,rev,behavior,litter in itertools.product(itertools.product([0,1],repeat=4),itertools.product([0,1],repeat=2),itertools.product([0,1],repeat=2),itertools.product([0,1],repeat=2),[0,1],['none','cue_SF','risk_refuge'],[0,1]):
  a=dict(zip(FEATURES,list(covers)+list(emerge)+list(support)+list(edges)+[rev,behavior,litter]))
  if litter:a['cover_DF']=0
  if not a['cover_SF'] and behavior=='risk_refuge':a['behavior']='none'
  if not a['edge_SD']:a['cover_SD']=0
  if not a['edge_DS']:a['cover_DS']=0;a['support_DS']=0
  rows.append(a)
 c=pd.DataFrame(rows).drop_duplicates().sort_values(FEATURES).reset_index(drop=True)
 c.insert(0,'model_id',np.arange(len(c)))
 c['assumptions']=c[[k for k in FEATURES if k!='behavior']].sum(axis=1)+(c.behavior!='none')
 c['extrapolation_flags']=c.cover_DS+c.cover_SD+c.support_DF+c.support_DS+c.survival
 return c

def design(models,contexts,blockids=None):
 rows=[]
 for m in models.to_dict('records'):
  for ci,ctx in enumerate(contexts):
   for v,s,d in CELLS:rows.append({**m,**ctx,'block_id':ci if blockids is None else blockids[ci],'vegetation':v,'S_source':s,'D_source':d})
 return pd.DataFrame(rows)

def evaluate(des,years=40,window=10,dt=.5,strength=1.,conversion=4.,rho=.5,attack=3.,size_gate=None,refuge_order='S'):
 des=des.copy();des['attack_scale']=attack;des['rho']=rho;des['refuge_order']=refuge_order;des['cue']=np.where(des.behavior=='cue_SF',3.,0.);des['roles']=15
 if des.behavior.nunique()!=1 or des.litter.nunique()!=1:raise ValueError('Group by behavioral/functional response')
 controls={k:des[k].to_numpy(float)*strength for k in ['cover_SF','cover_DF','cover_DS','cover_SD','support_DF','support_DS']}
 controls.update(edge_SD=des.edge_SD.to_numpy(),edge_DS=des.edge_DS.to_numpy(),cue_SD=0.,emerge_survival=des.survival.to_numpy()*strength,emerge_exposure=0.)
 opt=dict(pathway_controls=controls,stage_durations=des[['F_duration','S_duration','D_duration']].to_numpy(),emergence_delay=5*des.vegetation.to_numpy()*des.timing.to_numpy(),size_gate=size_gate,functional_response='litter' if des.litter.iloc[0] else None,behavioral_refuge=des.behavior.iloc[0]=='risk_refuge')
 kernel=des[[k for k in DEFAULT if k in des]+['rho']].to_dict('records')
 src=np.column_stack([np.ones(len(des)),des.S_source,des.D_source])
 conv=np.asarray(conversion)
 conv=(conversion,)*3 if conv.ndim==0 else np.column_stack([conv]*3)
 su=summarize_years(kernel,years=years,window=window,dt=dt,source_cohorts=src,seasonal_options=opt,conversion=conv)
 return pd.concat([des.reset_index(drop=True),su],axis=1)

def score(su):
 # Design construction guarantees 18 consecutive cells per model/context.
 n=len(su)//18
 assert len(su)==n*18
 expected=np.tile(np.array(CELLS),(n,1));assert np.array_equal(su[['vegetation','S_source','D_source']].to_numpy(),expected)
 result=su.iloc[::18][['model_id','block_id']].reset_index(drop=True)
 responses=dict(F_B=su.F_B.to_numpy(),log_F_B=np.log(su.F_B.to_numpy()),log_F_survival=np.log(su.F_fraction.to_numpy()),negative_H=-su.audit_H_SF.to_numpy()-su.audit_H_DF.to_numpy())
 passed=[]
 for name,val in responses.items():
  a=val.reshape(n,2,3,3);ds=(a[:,:,:,2]-a[:,:,:,0])/1.75;ss=(a[:,:,2,1]-a[:,:,0,1])/1.75
  dv=ds[:,1,1]-ds[:,0,1];sv=ss[:,1]-ss[:,0];sd=ds[:,1,2]-ds[:,1,0]
  result[name+'_DV']=dv;result[name+'_SV']=sv;result[name+'_SD']=sd
  good=(dv< -1e-6)&(sv>1e-6)&(sd< -1e-6)&(ds[:,1,2]< -1e-6);result[name+'_pass']=good;passed.append(good)
 result['conditional_pass']=np.logical_and.reduce(passed)
 cell=np.array(CELLS);v=cell[:,0];v=(v-v.mean())/v.std();s=rankdata(cell[:,1]);s=(s-s.mean())/s.std();d=rankdata(cell[:,2]);d=(d-d.mean())/d.std()
 X=np.column_stack([np.ones(18),d,s,v,d*s,d*v,s*v,d*s*v]);pinv=np.linalg.pinv(X)
 y=rankdata(responses['F_B'].reshape(n,18),axis=1);y-=y.mean(axis=1,keepdims=True);std=y.std(axis=1,keepdims=True);y=np.divide(y,std,out=np.zeros_like(y),where=std>1e-14)
 coef=y@pinv.T
 for idx,key in [(4,'DS'),(5,'DV'),(6,'SV'),(7,'DSV')]:result['rank_'+key]=coef[:,idx]
 result['macro_form_pass']=(coef[:,4]<-1e-6)&(coef[:,5]<-1e-6)&(coef[:,6]>1e-6)
 result['joint_pass']=result.conditional_pass&result.macro_form_pass
 result['min_F']=su.minimum_F_survival.to_numpy().reshape(n,18).min(axis=1);result['min_S']=su.minimum_S_survival.to_numpy().reshape(n,18).min(axis=1)
 result['floor_avoiding']=(result.min_F>=.05)&(result.min_S>=.05)
 result['floor_avoiding_pass']=result.joint_pass&result.floor_avoiding
 result['max_F_cv']=(su.F_B_sd/su.F_B).to_numpy().reshape(n,18).max(axis=1)
 return result
