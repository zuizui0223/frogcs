"""Deterministic summaries; no estimator or scenario selection."""
import json,hashlib
import numpy as np
import pandas as pd
from nee_context_robustness import ROOT,load
from nee_existing_strata import covariates
from run_handling_factorial import physical_contrasts
OUT=ROOT/'research/results/nee_boundaries_20261029'

def main():
 receipt=json.loads((OUT/'joint_receipt.json').read_text());expected=receipt['replicates']
 rows=[]
 for kind,path in [('SDM_only','sdm_bootstrap_coefficients.csv'),('joint','joint_refit_coefficients.csv')]:
  if not (OUT/path).exists():raise ValueError('Incomplete uncertainty run: '+path)
  d=pd.read_csv(OUT/path)
  assert d.groupby(['background','term']).replicate.nunique().eq(expected+1).all() and d.replicate.max()==expected
  assert not d.duplicated(['background','term','replicate']).any()
  for (bg,t),g in d[d.replicate>0].groupby(['background','term']):
   rows.append(dict(kind=kind,background=bg,term=t,draws=len(g),minimum=g.beta.min(),q025=g.beta.quantile(.025),median=g.beta.median(),q975=g.beta.quantile(.975),maximum=g.beta.max(),fraction_negative=(g.beta<0).mean(),interval_type='empirical_draw_range_not_confidence_interval'))
 pd.DataFrame(rows).to_csv(OUT/'uncertainty_summary.csv',index=False)
 d=load();c=np.column_stack([covariates(d),d.flooded_3000m_mean]);names=['survey_'+str(i) for i in range(8)]+['bio1','bio4','bio12','bio15','water_3000m','herbaceous_3000m','lat','lon','lat2','lat_lon','lon2','vegetation_3000m']
 membership=pd.read_csv(OUT/'support_membership.csv.gz');balances=[];coverage=[]
 for bg,g in membership.groupby('background'):
  ids=pd.Index(d.site).get_indexer(g.site);assert (ids>=0).all()
  for name,keep in [('extreme_thirds',np.ones(len(g),bool)),('overlap',g.retained.to_numpy(bool))]:
   label=g.high_S.to_numpy();q=c[ids];std=q.std(axis=0)
   smd=np.divide(q[keep&(label==1)].mean(axis=0)-q[keep&(label==0)].mean(axis=0),std,out=np.full(len(std),np.nan),where=std>0)
   for j,col in enumerate(names):balances.append(dict(background=bg,subset=name,covariate=col,standardized_difference=smd[j]))
   sub=d.iloc[ids[keep]];coverage.append(dict(background=bg,subset=name,sites=len(sub),routes=sub.route.nunique(),blocks=sub.spatial_block.nunique(),V_positive=int((sub.flooded_3000m_mean>0).sum()),max_abs_smd=float(np.nanmax(abs(smd)))))
 pd.DataFrame(balances).to_csv(OUT/'support_balance.csv',index=False);pd.DataFrame(coverage).to_csv(OUT/'support_coverage.csv',index=False)
 rows=[]
 for tag in ['dt025','dt0125']:
  for model,file in [('network',tag+'_annual.csv.gz'),('independent_predators',tag+'_independent_predator_cells.csv.gz'),('no_DS',tag+'_no_DS_cells.csv.gz'),('no_SD',tag+'_no_SD_cells.csv.gz')]:
   a=pd.read_csv(OUT/file,dtype={'arm':str});a['H_total']=a.audit_H_DF+a.audit_H_SF
   for (ctx,arm),g in a.groupby(['context','arm']):
    for r in physical_contrasts(g):rows.append(dict(model=model,tag=tag,context=ctx,arm=arm,**r))
 allc=pd.DataFrame(rows);allc.to_csv(OUT/'network_null_all_physical_contrasts.csv',index=False)
 summary=[]
 for key,g in allc[allc.path=='H_total'].groupby(['model','tag','context','arm']):
  summary.append(dict(zip(['model','tag','context','arm'],key),all_physical_directions=bool(np.where(g.contrast=='SV',g.value<0,g.value>0).all())))
 pd.DataFrame(summary).to_csv(OUT/'network_null_direction_summary.csv',index=False)
 source=ROOT/'research/results/nee_context_20261029/coefficients.csv';old=pd.read_csv(source);old[(old.adjustment=='space')&old.subset.ne('all')].to_csv(OUT/'existing_geographic_sensitivity.csv',index=False)
 inputs=[ROOT/'research/scripts'/n for n in ['nee_existing_strata.py','nee_sdm_uncertainty.py','nee_joint_uncertainty.py','nee_boundaries.py','run_nee_boundary_trace.py','nee_independent_predator_null.py','stage_handling_factorial_20261029.py','stage_boundary_trace_20261029.py','boundary_annual_trace_20261029.py']]
 (OUT/'manifest.json').write_text(json.dumps(dict(source_base='451df8efc02961a3184c8d88023b11aae284e1d4',inputs_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},field_mechanism_identified=False,nee_ready=False),indent=2)+'\n')
if __name__=='__main__':main()
