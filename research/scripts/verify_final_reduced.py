"""Post-selection reduction: replay all nuisance blocks, not a new holdout."""
import json
import numpy as np
import pandas as pd
from final_mechanism_common import OUT,design,evaluate,score,catalog,FEATURES
def main():
 c=catalog();base=c[c.model_id==1479].iloc[0].to_dict();base['edge_SD']=0
 mask=np.ones(len(c),bool)
 for k in FEATURES:mask &= c[k].to_numpy()==base[k]
 m=c[mask];assert len(m)==1
 blocks=json.loads((OUT/'validation_design.json').read_text())['blocks'];scores=[]
 for gate in [None,.5]:
  parts=[]
  for b in blocks:
   if b['size_gate']!=gate or b['block_id']<0:continue
   ctx={k:b[k] for k in ['f_arrival','s_arrival','d_arrival','F_duration','S_duration','D_duration']}
   q=design(m,[ctx],[b['block_id']])
   for k in ['attack','rho','conversion','strength','refuge_order']:q['batch_'+k]=b[k]
   parts.append(q)
  de=pd.concat(parts,ignore_index=True)
  su=evaluate(de,years=80,window=20,dt=.25,size_gate=gate,**{k:de['batch_'+k].to_numpy() for k in ['attack','rho','conversion','strength','refuge_order']})
  sc=score(su);scores.append(sc);su.to_csv(OUT/f'reduced_{gate}_cells.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 pd.concat(scores,ignore_index=True).to_csv(OUT/'reduced_validation_scores.csv',index=False)
 m.to_csv(OUT/'reduced_candidate.csv',index=False)
 print('Reduced matched validation complete',int(m.iloc[0].model_id),flush=True)
if __name__=='__main__':main()
