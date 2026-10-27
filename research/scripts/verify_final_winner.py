"""Conditional leader: factorial removal, numerical and rank-grid diagnostics."""
import itertools,json
import numpy as np
import pandas as pd
from final_mechanism_common import OUT,design,evaluate,score
from check_final_rank_resolution import rank_coefficients

def main():
 ranking=pd.read_csv(OUT/'validation_ranking.csv');mid=int(ranking.iloc[0].model_id)
 scores=pd.read_csv(OUT/'validation_scores.csv');hits=scores[(scores.model_id==mid)&scores.floor_avoiding_pass]
 if hits.empty:raise RuntimeError('No floor-avoiding leader to verify')
 bid=int(hits.iloc[0].block_id)
 b=next(x for x in json.loads((OUT/'validation_design.json').read_text())['blocks'] if x['block_id']==bid)
 ctx={k:b[k] for k in ['f_arrival','s_arrival','d_arrival','F_duration','S_duration','D_duration']}
 opts={k:b[k] for k in ['attack','rho','conversion','strength','size_gate','refuge_order']}
 base=pd.read_csv(OUT/'catalog.csv').set_index('model_id').loc[mid].to_dict();rows=[]
 for sd,ds,cover,litter in itertools.product([0,1],repeat=4):
  rows.append({**base,'model_id':200000+len(rows),'parent_id':mid,'edge_SD':sd,'edge_DS':ds,'cover_SF':cover,'litter':litter})
 variants=pd.DataFrame(rows);variants.to_csv(OUT/'winner_factorial_design.csv',index=False);allsc=[]
 for check,years,dt in [('base',80,.25),('half_step',80,.125),('long_run',160,.25)]:
  for litter,g in variants.groupby('litter'):
   path=OUT/f'winner_{check}_{litter}_cells.csv.gz'
   if path.exists():su=pd.read_csv(path)
   else:
    su=evaluate(design(g,[ctx],[bid]),years=years,window=20,dt=dt,**opts)
    su.to_csv(path,index=False,compression={'method':'gzip','mtime':0})
   sc=score(su).merge(g[['model_id','edge_SD','edge_DS','cover_SF','litter']],on='model_id');sc['check']=check;allsc.append(sc)
   print('Winner factorial',check,litter,flush=True)
 pd.concat(allsc,ignore_index=True).to_csv(OUT/'winner_factorial_scores.csv',index=False)
 # Post-selection resolution diagnostic, never used to replace the fixed score.
 rows=[]
 for levels in [3,9,21]:
  values=[.25,1.,2.] if levels==3 else np.linspace(.25,2.,levels)
  for v,s,d in itertools.product([0.,1.],values,values):rows.append({**base,**ctx,'model_id':mid,'block_id':bid,'levels':levels,'vegetation':v,'S_source':s,'D_source':d})
 su=evaluate(pd.DataFrame(rows),years=80,window=20,dt=.25,**opts);su.to_csv(OUT/'winner_rank_cells.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 pd.DataFrame([dict(levels=lev,**rank_coefficients(g)) for lev,g in su.groupby('levels')]).to_csv(OUT/'winner_rank_resolution.csv',index=False)
 print('Winner rank resolution complete',flush=True)
if __name__=='__main__':main()
