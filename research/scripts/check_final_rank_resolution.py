"""Post-screen diagnostic: rank quantization; not a new selection rule."""
import itertools
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from final_mechanism_common import OUT,CONTEXTS,evaluate
def rank_coefficients(q):
 z=[]
 for key in ['D_source','S_source','vegetation','F_B']:
  a=rankdata(q[key]);z.append((a-a.mean())/a.std())
 d,s,v,y=z;X=np.column_stack([np.ones(len(q)),d,s,v,d*s,d*v,s*v,d*s*v])
 b=np.linalg.lstsq(X,y,rcond=None)[0]
 return dict(zip(['DS','DV','SV','DSV'],b[4:]))
def main():
 cat=pd.read_csv(OUT/'catalog.csv');fin=pd.read_csv(OUT/'finalists.csv');r=pd.read_csv(OUT/'screen_ranking.csv')
 ids=set(r.loc[r.joint_pass>0,'model_id'])|set(fin.loc[fin.selection_reason.isin(['mandatory_frog_refuge','mandatory_salamander_refuge']),'model_id'])
 rows=[]
 for m in cat[cat.model_id.isin(ids)].to_dict('records'):
  for levels in [3,9,21]:
   values=[.25,1.,2.] if levels==3 else np.linspace(.25,2.,levels)
   for v,s,d in itertools.product([0.,1.],values,values):rows.append({**m,**CONTEXTS[0],'block_id':-1,'levels':levels,'vegetation':v,'S_source':s,'D_source':d})
 de=pd.DataFrame(rows);results=[]
 for (behavior,litter),g in de.groupby(['behavior','litter']):
  path=OUT/f'rank_resolution_{behavior}_{litter}_cells.csv.gz'
  if path.exists():su=pd.read_csv(path)
  else:
   su=evaluate(g.reset_index(drop=True),years=80,window=20,dt=.25);su.to_csv(path,index=False,compression={'method':'gzip','mtime':0})
  for (mid,levels),q in su.groupby(['model_id','levels']):results.append(dict(model_id=mid,levels=levels,**rank_coefficients(q)))
  print('Rank resolution',behavior,len(su),flush=True)
 pd.DataFrame(results).to_csv(OUT/'rank_resolution.csv',index=False)
if __name__=='__main__':main()
