"""Inspectable selection summary and descriptive (not likelihood) comparison."""
import json
import numpy as np
import pandas as pd
from final_mechanism_common import OUT
def main():
 screen=pd.read_csv(OUT/'screen_scores.csv');validation=pd.read_csv(OUT/'validation_scores.csv');fresh=validation[validation.block_id>=0]
 reduced=pd.read_csv(OUT/'reduced_validation_scores.csv');factor=pd.read_csv(OUT/'winner_factorial_scores.csv')
 macro=pd.read_csv(OUT.parent/'naamp_remote_vegetation_20261026/network_rank_coefficients.csv')
 macro=macro[(macro.group=='pond_breeding_Caudata')&(macro.vegetation_metric=='mean')&(macro.radius_m==3000)&(~macro.within_route)]
 macro.to_csv(OUT/'macro_targets.csv',index=False)
 # Different observables/sample distributions: distances are descriptive only.
 terms=['Odonata:Caudata','Odonata:vegetation','Caudata:vegetation'];comparisons=[]
 for label,coeffs in [('leader_3',fresh[fresh.joint_pass][['rank_DS','rank_DV','rank_SV']].iloc[0].to_numpy()),('reduced_3',reduced[reduced.joint_pass][['rank_DS','rank_DV','rank_SV']].iloc[0].to_numpy())]:
  for bg,g in macro.groupby('background'):
   target=g.set_index('term').loc[terms,'beta'].to_numpy();comparisons.append(dict(candidate=label,background=bg,DS=coeffs[0],DV=coeffs[1],SV=coeffs[2],descriptive_l2=float(np.linalg.norm(coeffs-target)),interpretation='NOT_FIT_NOT_LIKELIHOOD'))
 pd.DataFrame(comparisons).to_csv(OUT/'descriptive_effect_comparison.csv',index=False)
 q=pd.read_csv(OUT/'winner_base_1_cells.csv.gz');q=q[q.model_id==200015];paths=[]
 for v in [0.,1.]:
  for s in [.25,1.,2.]:
   a=q[(q.vegetation==v)&(q.S_source==s)].set_index('D_source')
   sf=a.loc[2.,'audit_H_SF']-a.loc[.25,'audit_H_SF'];df=a.loc[2.,'audit_H_DF']-a.loc[.25,'audit_H_DF']
   paths.append(dict(vegetation=v,S_source=s,D_increase=.25,D_to=2.,change_H_SF=sf,change_H_DF=df,change_total_H=sf+df))
 pd.DataFrame(paths).to_csv(OUT/'leader_hazard_decomposition.csv',index=False)
 summary=dict(catalog_models=3600,screen_scenario_evaluations=194400,screen_model_contexts=len(screen),screen_joint=int(screen.joint_pass.sum()),screen_floor_avoiding=int(screen.floor_avoiding_pass.sum()),finalists=20,validation_blocks=24,validation_scenario_evaluations=len(validation)*18,validation_joint=int(fresh.joint_pass.sum()),validation_floor_avoiding=int(fresh.floor_avoiding_pass.sum()),leader=1479,reduced_candidate=1455,reduced_joint=int(reduced.joint_pass.sum()),factorial_successes=factor[factor.joint_pass][['model_id','check']].to_dict('records'),total_scenario_evaluations=213336,conclusion='Conditional leading family; no robust field cause identified',fixed_criterion_not_changed=True,post_selection_diagnostics=['rank resolution','factorial reduction','reduced replay of same 24 nuisance blocks'])
 assert len(screen)==10800 and len(validation)==540 and len(reduced)==24
 assert fresh.joint_pass.sum()==1 and factor.joint_pass.sum()==6
 assert set(factor[factor.joint_pass].model_id)=={200007,200015}
 assert fresh[fresh.joint_pass].min_F.min()>.37
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
