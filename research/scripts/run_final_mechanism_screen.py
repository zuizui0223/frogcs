"""Exhaustive canonical structural screen at three frozen contexts."""
import json
import pandas as pd
from final_mechanism_common import OUT,catalog,design,evaluate,score,CONTEXTS

def main():
 OUT.mkdir(parents=True,exist_ok=True);models=catalog();models.to_csv(OUT/'catalog.csv',index=False)
 (OUT/'screen_design.json').write_text(json.dumps(dict(raw_logical_combinations=12288,canonical_models=len(models),contexts=CONTEXTS,years=40,window=10,dt=.5,scope='Exhaustive canonical existing catalog at three contexts; coarse screen not impossibility proof',exclusions=['cue_SD unsupported inhibition','explicit egg stage','emergence exposure boost','abiotic confounding','species-specific toxicity','explicit size distributions']),indent=2)+'\n')
 allscores=[];jobs=0
 for (behavior,litter),g in models.groupby(['behavior','litter'],sort=True):
  for start in range(0,len(g),96):
   chunk=g.iloc[start:start+96];tag=f'{behavior}_{litter}_{start:04d}'
   path=OUT/(tag+'_screen.csv')
   if path.exists():cs=pd.read_csv(path)
   else:
    su=evaluate(design(chunk,CONTEXTS));cs=score(su);cs.to_csv(path,index=False)
    su[['model_id','block_id','vegetation','S_source','D_source','F_B','F_fraction','S_B','S_fraction','D_B','audit_H_SF','audit_H_DF','audit_H_DS','audit_H_SD']].to_csv(OUT/(tag+'_cells.csv.gz'),index=False,compression={'method':'gzip','mtime':0})
   allscores.append(cs);jobs+=1
   print('Screen',tag,'models',len(chunk),'joint matches',int(cs.joint_pass.sum()),flush=True)
 scores=pd.concat(allscores,ignore_index=True);scores.to_csv(OUT/'screen_scores.csv',index=False)
 rank=scores.groupby('model_id')[['floor_avoiding_pass','joint_pass','conditional_pass','macro_form_pass']].sum().join(models.set_index('model_id')).sort_values(['floor_avoiding_pass','joint_pass','conditional_pass','extrapolation_flags','assumptions'],ascending=[False,False,False,True,True]);rank.to_csv(OUT/'screen_ranking.csv')
 print('Screen finished',len(models),len(scores)*18,'scenarios',flush=True);print(rank.head(15).to_string(),flush=True)
if __name__=='__main__':main()
