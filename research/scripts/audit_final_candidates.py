"""Predeclared screen leaders/anchors: convergence and single-path removal."""
import json
import pandas as pd
from final_mechanism_common import OUT,CONTEXTS,design,evaluate,score

def main():
 catalog=pd.read_csv(OUT/'catalog.csv')
 rank=pd.read_csv(OUT/'screen_ranking.csv')
 anchors=pd.read_csv(OUT/'finalists.csv')
 ids=set(rank.loc[rank.joint_pass>0,'model_id'])|set(anchors.loc[anchors.selection_reason.isin(['mandatory_frog_refuge','mandatory_salamander_refuge']),'model_id'])
 models=catalog[catalog.model_id.isin(ids)]
 results=[]
 for check,years,dt in [('half_step',80,.125),('long_run',160,.25)]:
  for (behavior,litter),group in models.groupby(['behavior','litter']):
   tag=f'audit_{check}_{behavior}_{litter}'
   path=OUT/(tag+'_scores.csv')
   if path.exists():sc=pd.read_csv(path)
   else:
    su=evaluate(design(group,[CONTEXTS[0]],[-1]),years=years,window=20,dt=dt)
    sc=score(su);sc['check']=check;sc.to_csv(path,index=False)
    su.to_csv(OUT/(tag+'_cells.csv.gz'),index=False,compression={'method':'gzip','mtime':0})
   results.append(sc)
   print('Numerical audit',check,behavior,len(group),flush=True)
 pd.concat(results,ignore_index=True).to_csv(OUT/'numerical_audit.csv',index=False)
 rows=[]
 # Interpret the two cue-free screen matches; every active removable path
 # is switched off individually. These are synthetic interventions.
 for base in models[(models.behavior=='none') & models.model_id.isin(rank.loc[rank.joint_pass>0,'model_id'])].to_dict('records'):
  for path in ['baseline','edge_SD','edge_DS','cover_SF','cover_DS','survival','timing','reverse']:
   if path!='baseline' and not base[path]:continue
   row={**base,'parent_id':base['model_id'],'removed':path,'model_id':100000+len(rows)}
   if path!='baseline':row[path]=0
   rows.append(row)
 variants=pd.DataFrame(rows);variants.to_csv(OUT/'ablation_design.csv',index=False)
 su=evaluate(design(variants,[CONTEXTS[0]],[-1]),years=80,window=20,dt=.25)
 sc=score(su).merge(variants[['model_id','parent_id','removed']],on='model_id',validate='one_to_one')
 sc.to_csv(OUT/'ablation_scores.csv',index=False)
 su.to_csv(OUT/'ablation_cells.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 print('Ablation finished',len(variants),flush=True)
if __name__=='__main__':main()
