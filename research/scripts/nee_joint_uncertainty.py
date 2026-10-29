"""Joint SDM/site-block stability with nuisance refitting; limited-replicate diagnostic."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from nee_context_robustness import ROOT,load,zrank
from nee_existing_strata import covariates
from nee_shared_environment_crossfit import folds_for
from common_scale_comparison import features
OUT=ROOT/'research/results/nee_boundaries_20261029'

def main():
 d=load();c=covariates(d);y=zrank(d.strong_rate.to_numpy());v=zrank(d.flooded_3000m_mean.to_numpy());guild=np.load(OUT/'sdm_guild_draws.npy')
 ids=pd.factorize(d.spatial_block,sort=True)[0];k=ids.max()+1;folds=folds_for(ids);R=len(guild)-1
 weights=np.random.default_rng(20261030).multinomial(k,np.full(k,1/k),size=R);rows=[]
 for rep in range(R+1):
  count=np.ones(len(d),int) if rep==0 else weights[rep-1][ids];idx=np.repeat(np.arange(len(d)),count)
  for bi,bg in enumerate(['uniform','target_group']):
   x=features(zrank(guild[rep,bi,:,0]),zrank(guild[rep,bi,:,1]),v);targets=np.column_stack([y,x]);pred=np.zeros_like(targets)
   for f in range(5):
    train=idx[folds[idx]!=f];test=folds==f
    m=ExtraTreesRegressor(n_estimators=300,min_samples_leaf=20,random_state=20261029,n_jobs=2);m.fit(c[train],targets[train]);pred[test]=m.predict(c[test])
   res=targets-pred;z=np.column_stack([res[idx,1:],np.ones(len(idx))]);b=np.linalg.lstsq(z,res[idx,0],rcond=1e-10)[0][:7]
   for j,t in enumerate(['O','S','V','OS','OV','SV','OSV']):rows.append(dict(replicate=rep,background=bg,term=t,beta=b[j]))
  if rep%5==0:print('joint',rep,flush=True);pd.DataFrame(rows).to_csv(OUT/'joint_refit_coefficients.csv',index=False)
 pd.DataFrame(rows).to_csv(OUT/'joint_refit_coefficients.csv',index=False)
 (OUT/'joint_receipt.json').write_text(json.dumps(dict(replicates=R,nuisance='300 ExtraTrees,leaf20,5 spatial folds; every draw refitted',site_bootstrap_seed=20261030,sdm_bootstrap_seed=20261029,independent_resampling_layers=True,rank_reference='fixed cohort; guild ranks recomputed per SDM draw',limits=['49 draws characterize stability, not precise interval tails','One nuisance specification','Missing data bias, structural SDM choices, measurement error and calling-density mapping not covered','Not external validation']),indent=2)+'\n')
if __name__=='__main__':main()
