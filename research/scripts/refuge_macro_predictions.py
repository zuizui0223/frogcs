"""Internal conditional OV checks; low suitability is not predator absence."""
import json
import numpy as np
import pandas as pd
from nee_context_robustness import ROOT,load,zrank,prepare,block_stats
from nee_existing_strata import covariates,estimate
from common_scale_comparison import features
OUT=ROOT/'research/results/refuge_generality_20261029'

def main():
 OUT.mkdir(parents=True,exist_ok=True);d=load();c=covariates(d);y=zrank(d.strong_rate.to_numpy());v=zrank(d.flooded_3000m_mean.to_numpy());ids=pd.factorize(d.spatial_block,sort=True)[0];k=ids.max()+1;draw=np.random.default_rng(20261029).multinomial(k,np.full(k,1/k),size=999)
 residual=pd.read_csv(ROOT/'research/results/nee_crossfit_20261029/oof_residuals.csv.gz');rows=[];support=[];strata=[];diagnostics=[]
 for bg in ['uniform','target_group']:
  o=zrank(d['mean_suitability_Odonata_'+bg].to_numpy());s=zrank(d['mean_suitability_pond_breeding_Caudata_'+bg].to_numpy());x=features(o,s,v);lo,hi=np.quantile(s,[.25,.75])
  for name,mask in [('S_low_third',s<=np.quantile(s,1/3)),('S_high_third',s>=np.quantile(s,2/3))]:
   q=d[mask];positive=q[q.flooded_3000m_mean>0];support.append(dict(background=bg,stratum=name,sites=len(q),routes=q.route.nunique(),V_positive=len(positive),V_positive_routes=positive.route.nunique(),O_min=q['mean_suitability_Odonata_'+bg].min(),O_max=q['mean_suitability_Odonata_'+bg].max()))
   rr,dg=estimate(d,x,c,y,mask,dict(background=bg,family='S_support',name=name));strata.extend(rr);diagnostics.append(dg)
  for kind in ['linear','trees20']:
   if kind=='linear':z,yy,_,_=prepare(x,c,y,d.route,'pooled')
   else:
    q=residual[(residual.background==bg)&(residual.nuisance=='trees_20')].set_index('site').loc[d.site];yy=q.Y.to_numpy();z=np.column_stack([q[['O','S','V','OS','OV','SV','OSV']],np.ones(len(d))])
   point=np.linalg.lstsq(z,yy,rcond=1e-10)[0];xx,xy=block_stats(z,yy,ids);boot=[]
   for a,b in zip(np.einsum('bg,gij->bij',draw,xx),draw@xy):
    coef,_,rank,_=np.linalg.lstsq(a,b,rcond=1e-12)
    if rank==z.shape[1]:boot.append(coef)
   boot=np.array(boot)
   for name,weights in [('OV_at_low_S',(1.,lo)),('OV_at_high_S',(1.,hi)),('high_minus_low',(0.,hi-lo))]:
    val=weights[0]*point[4]+weights[1]*point[6];q=weights[0]*boot[:,4]+weights[1]*boot[:,6];low,high=np.quantile(q,[.025,.975]);rows.append(dict(background=bg,adjustment=kind,contrast=name,beta=val,low=low,high=high,S_low=lo,S_high=hi,interval_scope='full_linear' if kind=='linear' else 'conditional_fixed_nuisance'))
 pd.DataFrame(rows).to_csv(OUT/'macro_conditional_OV.csv',index=False);pd.DataFrame(support).to_csv(OUT/'macro_S_support.csv',index=False);pd.DataFrame(strata).to_csv(OUT/'macro_S_strata.csv',index=False);pd.DataFrame(diagnostics).to_csv(OUT/'macro_S_strata_diagnostics.csv',index=False)
 (OUT/'macro_prediction_receipt.json').write_text(json.dumps(dict(independent_test=False,posthoc_to_existing_pattern=True,low_suitability_not_absence=True,contrast='OV+OSV*S with joint coefficient covariance; S25/75rank quantiles',limits=['same observational cohort','landscapeV not pond refuge','SDM not density','no direct predator removal']),indent=2)+'\n')
if __name__=='__main__':main()
