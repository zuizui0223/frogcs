"""Fixed-cohort seasonal/taxon/common-environment support sensitivity."""
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
from nee_context_robustness import ROOT,load,zrank,SURVEY,ENV,VISITS,prepare,block_stats
from nee_shared_environment_crossfit import folds_for
from common_scale_comparison import features
from naamp_site_use_associations import POND
OUT=ROOT/'research/results/nee_boundaries_20261029'

def seasonal_outcomes(visits,season):
 q=visits[visits.season==season].groupby('site').agg(rate=('strong','mean'),n=('strong','size'),years=('year','nunique'))
 return q.loc[(q.n>=3)&(q.years>=2),'rate']

def covariates(d):
 ll=zrank(d[['lat','lon']].to_numpy())
 return np.column_stack([zrank(d[SURVEY].to_numpy()),zrank(d[ENV].to_numpy()),ll,ll[:,0]**2,ll[:,0]*ll[:,1],ll[:,1]**2])

def seasonal_controls(d,visits,mask):
 q=visits.groupby('site').agg(n_visits=('strong','size'),n_years=('year','nunique'),mean_air=('air','mean'),mean_noise=('noise','mean'),mean_doy=('doy','mean'))
 for season in [2,3,4]:q['season_'+str(season)]=visits.assign(p=visits.season==season).groupby('site').p.mean()
 raw=q.reindex(d.site)[SURVEY].to_numpy();valid=mask & np.isfinite(raw).all(axis=1);c=covariates(d);c[:,:len(SURVEY)]=0
 if valid.any():c[valid,:len(SURVEY)]=zrank(raw[valid])
 return c,valid

def estimate(d,x,c,y,mask,meta):
 sub=d.loc[mask];n=len(sub);k=sub.spatial_block.nunique()
 if n<200 or sub.route.nunique()<20 or k<10:return [],dict(**meta,sites=n,blocks=k,status='insufficient_support')
 rows=[]
 for mode in ['pooled','within']:
  try:z,yy,_,info=prepare(x[mask],c[mask],y[mask],sub.route,mode)
  except ValueError as e:return [],dict(**meta,sites=n,blocks=k,status=str(e))
  ids=pd.factorize(sub.spatial_block,sort=True)[0];xx,xy=block_stats(z,yy,ids)
  beta=np.linalg.lstsq(z,yy,rcond=1e-10)[0][:7];draw=np.random.default_rng(20261029).multinomial(k,np.full(k,1/k),size=999)
  boot=[]
  for a,b in zip(np.einsum('bg,gij->bij',draw,xx),draw@xy):
   q,_,rank,_=np.linalg.lstsq(a,b,rcond=1e-12)
   if rank==z.shape[1]:boot.append(q[:7])
  if len(boot)<800:return [],dict(**meta,sites=n,blocks=k,status='low_bootstrap_support')
  low,high=np.quantile(boot,[.025,.975],axis=0)
  for j,t in enumerate(['O','S','V','OS','OV','SV','OSV']):rows.append(dict(**meta,mode=mode,term=t,beta=beta[j],low=low[j],high=high[j],sites=n,blocks=k,valid=len(boot)))
 return rows,dict(**meta,sites=n,blocks=k,status='OK')

def main():
 OUT.mkdir(parents=True,exist_ok=True);d=load();c=covariates(d);v=zrank(d.flooded_3000m_mean.to_numpy());y=zrank(d.strong_rate.to_numpy())
 visits=pd.read_csv(VISITS);visits=visits[(visits.timeout==0)&visits.site.isin(d.site)]
 pred=pd.read_csv(ROOT/'research/results/interaction_species_sdm_20261026/naamp_species_suitability.csv.gz');pred=pred[pred.site.isin(d.site)]
 rows=[];diags=[];supports=[]
 for bg in ['uniform','target_group']:
  o=zrank(d['mean_suitability_Odonata_'+bg].to_numpy());s=zrank(d['mean_suitability_pond_breeding_Caudata_'+bg].to_numpy());x=features(o,s,v)
  tasks=[('baseline','all',x,y,np.ones(len(d),bool))]
  for season in [1,2,3,4]:
   q=d.site.map(seasonal_outcomes(visits,season)).to_numpy();mask=np.isfinite(q);yy=np.zeros(len(d));yy[mask]=zrank(q[mask]);tasks.append(('season',str(season),x,yy,mask))
  for quarter in [1,2,3,4]:
   calendar=visits.assign(season=((visits.month-1)//3+1));q=d.site.map(seasonal_outcomes(calendar,quarter)).to_numpy();mask=np.isfinite(q);yy=np.zeros(len(d));yy[mask]=zrank(q[mask]);tasks.append(('calendar_quarter',str(quarter),x,yy,mask))
  for guild in ['Odonata','pond_Caudata']:
   pp=pred[(pred.background==bg)&((pred.guild=='Odonata') if guild=='Odonata' else pred.species.isin(POND))]
   for sp in sorted(pp.species.unique()):
    means=pp[pp.species!=sp].groupby('site').suitability_percentile.mean();new=zrank(d.site.map(means).to_numpy());assert np.isfinite(new).all()
    tasks.append(('omit_'+guild,sp,features(new,s,v) if guild=='Odonata' else features(o,new,v),y,np.ones(len(d),bool)))
  # Outcome-blind support of extreme S thirds, not treatment propensity identification.
  low,high=np.quantile(s,[1/3,2/3]);extreme=(s<=low)|(s>=high);label=(s[extreme]>=high).astype(int)
  ce=np.column_stack([c,v])[extreme];fold=folds_for(d.loc[extreme,'spatial_block'].to_numpy());prob=np.zeros(len(ce))
  for f in range(5):
   train=fold!=f;test=~train;m=ExtraTreesClassifier(n_estimators=300,min_samples_leaf=20,random_state=20261029,n_jobs=2)
   m.fit(ce[train],label[train]);prob[test]=m.predict_proba(ce[test])[:,1]
  keep=(prob>=.1)&(prob<=.9);mask=np.zeros(len(d),bool);mask[np.flatnonzero(extreme)[keep]]=True
  supports.append(pd.DataFrame(dict(site=d.loc[extreme,'site'],background=bg,high_S=label,probability=prob,retained=keep)))
  tasks.extend([('support','extreme_thirds',x,y,extreme),('support','overlap_01_09',x,y,mask)])
  for family,name,xx,yy,mask in tasks:
   cc=c
   if family in ['season','calendar_quarter']:
    vv=visits[visits.season==int(name)] if family=='season' else visits[((visits.month-1)//3+1)==int(name)]
    cc,mask=seasonal_controls(d,vv,mask);yy=yy.copy();yy[mask]=zrank(yy[mask])
   r,dg=estimate(d,xx,cc,yy,mask,dict(background=bg,family=family,name=name));rows.extend(r);diags.append(dg)
  print('strata done',bg,len(tasks),flush=True)
 pd.DataFrame(rows).to_csv(OUT/'strata_coefficients.csv',index=False);pd.DataFrame(diags).to_csv(OUT/'strata_diagnostics.csv',index=False)
 pd.concat(supports).to_csv(OUT/'support_membership.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 (OUT/'strata_receipt.json').write_text(json.dumps(dict(bootstrap=999,source_cohort=4248,rank_reference='full cohort predictors; available seasonal outcome',inference='exploratory sensitivity; no multiplicity-adjusted significance claim',species_scope='leave-one-predator-species-out; not frog-specific calling',season_scope='season field is survey round, separate fixed calendar quarters added',support='outcome-blind diagnostic; not causally identified'),indent=2)+'\n')
if __name__=='__main__':main()
