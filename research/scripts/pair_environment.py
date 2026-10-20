#!/usr/bin/env python3
"""Cached fixed-margin species-pair structure versus ERA5/MODIS, exploratory.
No network, no new null draws, no original source or main manuscript changes.
Protocol: PAIR_SEGREGATION_ENVIRONMENT_CONTRACT_2026-10-20.md.
"""
from __future__ import annotations
import argparse, ast, hashlib, io, json, platform
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import pandas as pd
import scipy
from scipy.linalg import qr
from scipy.stats import norm
import statsmodels
import statsmodels.api as sm

SOURCES={
 'pair':('NAAMP_2026-10-19_species_pair_checkerboard_fixed_margins.zip','0690c24e72172a0d6a5a4a0144bac9bda9c78bacee9651b69b49e2cbb2275e19'),
 'soil':('NAAMP_environment_state_response_2026-10-19.zip','e182e0e30a7a5f1a7f1b8683d0024155b06f44b03205faa5df4beb02895d97a0'),
 'joint':('NAAMP_soil_and_MODIS_joint_2026-10-19.zip','ee72dd9b436b5d036fbd43a8c9220038f046aa57dc8f097ec76a08e88a48b366')}
PRIMARY=[('ERA5','layer_common'),('ERA5_MODIS','layer_common'),('ERA5_MODIS','surface_current_delta')]
KEYS=['wet_RunID','dry_RunID']
BASE=['rain_contrast','rain72','temp_difference','doy_difference','year_gap',
      'vpd_relief','vpd_mid','air_mid','soil_mid','layer_common','surface_excess']
WATER=['surface_current_delta','surface_current_mid','surface_prior_delta','surface_prior_mid']
OUTCOMES=['delta_excess','strong_new_count']
MIN_PAIRS,MIN_ROUTES=200,80


def verified_zip(path:Path,expected:str)->dict[str,bytes]:
 raw=path.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('outer SHA mismatch '+path.name)
 with ZipFile(io.BytesIO(raw)) as z:
  names=z.namelist()
  if len(names)!=len(set(names)) or any(n.startswith('/') or '..' in Path(n).parts for n in names):raise ValueError('unsafe archive')
  mf='SHA256SUMS.json' if 'SHA256SUMS.json' in names else 'SHA256.json'
  h=json.loads(z.read(mf))
  if set(names)!=set(h)|{mf}:raise ValueError('unlisted archive members')
  data={n:z.read(n) for n in h}
  if any(hashlib.sha256(data[n]).hexdigest()!=v for n,v in h.items()):raise ValueError('inner SHA mismatch')
  return data


def csv(data:bytes)->pd.DataFrame:
 return pd.read_csv(io.BytesIO(data),compression='gzip',dtype={
      'RunID':str,'wet_RunID':str,'dry_RunID':str,'RouteNumber':str,'RunNumber':str})


def correct_residuals(p:pd.DataFrame)->pd.DataFrame:
 p=p.copy()
 for side in ['wet','dry']:
  p[side+'_excess']=p[side+'_observed_cscore']-p[side+'_null_mean_cscore']
 if not np.allclose(p.wet_excess-p.dry_excess,p.delta_excess,atol=1e-10,rtol=0):
  raise ValueError('old paired residual identity fails')
 return p


def strict_join(p:pd.DataFrame,e:pd.DataFrame):
 if p.duplicated(KEYS).any() or e.duplicated(KEYS).any():raise ValueError('duplicate pair key')
 if p[KEYS].isna().any().any() or e[KEYS].isna().any().any():raise ValueError('missing key')
 p=p.copy();e=e.copy()
 for k in KEYS:p[k]=p[k].astype(str);e[k]=e[k].astype(str)
 common=sorted(set(p)&set(e)-set(KEYS))
 d=p.merge(e,on=KEYS,how='inner',suffixes=('','__e'),validate='one_to_one',sort=False)
 for c in common:
  left,right=d[c],d[c+'__e']
  if pd.api.types.is_numeric_dtype(left) and pd.api.types.is_numeric_dtype(right):
   ok=np.allclose(left.to_numpy(float),right.to_numpy(float),rtol=0,atol=1e-9,equal_nan=True)
  else:ok=np.all(left.fillna('<NA>').astype(str).to_numpy()==right.fillna('<NA>').astype(str).to_numpy())
  if not ok:raise ValueError('cross-source metadata mismatch '+c)
 d=d.drop(columns=[c+'__e' for c in common])
 if not pd.api.types.is_bool_dtype(d.stable_sites) or not pd.api.types.is_bool_dtype(d.stable_physical_siteids):
  raise ValueError('ambiguous source stability flag')
 stable=d.stable_sites & d.stable_physical_siteids
 audit={'pair_source_n':len(p),'environment_source_n':len(e),'joined_before_stability':len(d),
        'missing_pairs':len(p)-len(d),'unstable_pairs':int((~stable).sum()),
        'matched':int(stable.sum()),'route_count':int(d.loc[stable,'route_cluster'].nunique()),
        'state_count':int(d.loc[stable,'State'].nunique()),'verified_common_columns':common}
 return d[stable].copy().reset_index(drop=True),audit


def route_summary(d:pd.DataFrame,var:str,seed:int=20261020):
 x=d.groupby('route_cluster',sort=True)[var].mean().to_numpy(float)
 if not len(x) or not np.isfinite(x).all():raise ValueError('invalid route summary')
 rng=np.random.default_rng(seed);means=x[rng.integers(0,len(x),(2000,len(x)))].mean(axis=1)
 avg=float(x.mean());ci=np.quantile(means,[.025,.975])
 return {'pairs_or_runs':len(d),'routes':len(x),'mean':avg,'ci95':ci.tolist(),
         'positive_route_fraction':float((x>0).mean()),
         'p_centered_bootstrap':float((1+(abs(means-avg)>=abs(avg)).sum())/2001),
         'bootstrap_n':2000,'conditional_on_cached_null':True}


def holm(p):
 p=np.asarray(p,float)
 if not np.isfinite(p).all():raise ValueError('nonfinite p')
 order=np.argsort(p);v=np.minimum(1,np.maximum.accumulate((len(p)-np.arange(len(p)))*p[order]))
 out=np.empty_like(p);out[order]=v;return out


def term(b,se):
 if not np.isfinite([b,se]).all() or se<=0:raise ValueError('non-estimable coefficient')
 z=norm.ppf(.975)
 return {'beta':float(b),'se':float(se),'ci95':[float(b-z*se),float(b+z*se)],
         'p':float(2*norm.sf(abs(b/se)))}


def fit_within(d:pd.DataFrame,cols:list[str],ys:list[str],strata='route_cluster'):
 if len(cols)!=len(set(cols)) or not d.columns.is_unique:raise ValueError('duplicate design columns')
 if set(cols)&set(ys):raise ValueError('response also in design')
 a=d[cols+ys].astype(float)
 if not np.isfinite(a.to_numpy()).all():raise ValueError('missing design; not zero')
 w=a-a.groupby(d[strata],sort=False).transform('mean')
 X0=w[cols].to_numpy();Y=w[ys].to_numpy();n=len(d)
 _,R,piv=qr(X0,mode='economic',pivoting=True);di=np.abs(np.diag(R))
 tol=di.max(initial=0)*max(X0.shape)*np.finfo(float).eps
 rank=int((di>tol).sum());keep=sorted(piv[:rank]);names=[cols[i] for i in keep]
 G=d.route_cluster.nunique();S=d[strata].nunique()
 if rank==0 or G<2 or n<=S+rank:raise ValueError('no within-stratum degrees of freedom')
 X=X0[:,keep];B=np.linalg.lstsq(X,Y,rcond=None)[0];err=Y-X@B
 bread=np.linalg.inv(X.T@X);code=pd.factorize(d.route_cluster,sort=True)[0]
 factor=G/(G-1)*(n-1)/(n-S-rank);out={}
 for j,y in enumerate(ys):
  score=np.zeros((G,rank));np.add.at(score,code,X*err[:,j,None])
  cov=bread@(score.T@score)@bread*factor
  se=np.sqrt(np.maximum(0,np.diag(cov)))
  out[y]={'n':n,'routes':int(G),'strata':int(S),'rank':rank,'df_resid':int(n-S-rank),
          'columns_used':names,'dropped':[c for c in cols if c not in names],
          'terms':{k:term(B[i,j],se[i]) for i,k in enumerate(names)},
          'rmse_within':float(np.sqrt(np.mean(err[:,j]**2))),
          'cr1_factor':float(factor)}
 return out


def verify_explicit(d,cols,y,reference,strata='route_cluster'):
 names=reference['columns_used']
 dummy=pd.get_dummies(d[strata].astype(str),drop_first=False,dtype=float).to_numpy()
 X=np.column_stack([dummy,d[names].to_numpy(float)])
 fit=sm.OLS(d[y].to_numpy(float),X).fit(cov_type='cluster',cov_kwds={'groups':d.route_cluster})
 beta=fit.params[-len(names):];se=fit.bse[-len(names):]
 db=max(abs(beta[i]-reference['terms'][k]['beta']) for i,k in enumerate(names))
 ds=max(abs(se[i]-reference['terms'][k]['se']) for i,k in enumerate(names))
 if db>1e-7 or ds>1e-7:raise ValueError('independent explicit route-dummy regression mismatch')
 return {'method':'statsmodels explicit all-route dummies; full CR1',
         'max_beta_error':float(db),'max_se_error':float(ds),'terms_checked':names}


def design(d,water=False):
 a=d.copy()
 for k in [c for c in a if c.startswith('run_') and c[4:].isdigit()]:del a[k]
 a['rain72']=np.log1p(a.rain72_w)-np.log1p(a.rain72_d)
 a['vpd_relief']=a.vpd_d-a.vpd_w;a['vpd_mid']=(a.vpd_w+a.vpd_d)/2
 a['air_mid']=(a.air_w+a.air_d)/2;a['soil_mid']=(a.soil1_w+a.soil1_d)/2
 a['layer_common']=((a.soil1_w-a.soil1_d)+(a.soil2_w-a.soil2_d))/2
 a['surface_excess']=(a.soil1_w-a.soil1_d)-(a.soil2_w-a.soil2_d)
 cols=BASE.copy()
 dum=pd.get_dummies(a.RunNumber.astype(str),drop_first=True,prefix='run',dtype=float)
 for c in dum:a[c]=dum[c];cols.append(c)
 if water:
  for k in ['current','prior']:
   delta=a['surface_'+k+'_w']-a['surface_'+k+'_d']
   mid=(a['surface_'+k+'_w']+a['surface_'+k+'_d'])/2
   if 'surface_'+k+'_delta' in a and not np.allclose(delta,a['surface_'+k+'_delta'],rtol=0,atol=1e-9):raise ValueError('cached surface delta mismatch')
   a['surface_'+k+'_delta']=delta;a['surface_'+k+'_mid']=mid
  cols+=WATER
 a['route_round']=a.route_cluster.astype(str)+'|'+a.RunNumber.astype(str)
 if not np.isfinite(a[cols].to_numpy(float)).all():raise ValueError('nonfinite environmental covariate')
 return a,cols


def run(input_root:Path,out:Path):
 out.mkdir(parents=True,exist_ok=True)
 files={k:verified_zip(input_root/name,h) for k,(name,h) in SOURCES.items()}
 p=correct_residuals(csv(files['pair']['matched_checkerboard_pairs.csv.gz']))
 runs=csv(files['pair']['run_fixed_margin_null.csv.gz']);old=json.loads(files['pair']['RESULT.json'])
 e=csv(files['soil']['paired_environment_and_chorus.csv.gz']);j=csv(files['joint']['output/joined_environment_and_chorus.csv.gz'])
 if (len(p),p.route_cluster.nunique(),len(e),len(j))!=(1440,399,4108,1647):raise ValueError('pinned population changed')
 orig=route_summary(p,'delta_excess')
 if abs(orig['mean']-old['primary']['primary_route_equal']['route_equal_mean'])>1e-12:raise ValueError('original contrast changed')
 np.testing.assert_allclose(orig['ci95'],old['primary']['primary_route_equal']['ci95_route_bootstrap'],rtol=0,atol=1e-12)
 baselines={v:route_summary(p,v) for v in ['wet_excess','dry_excess','delta_excess']}
 # Duplicate each run only once, and verify paired source links to original null cache.
 mapping=pd.concat([p[['wet_RunID','route_cluster']].rename(columns={'wet_RunID':'RunID'}),p[['dry_RunID','route_cluster']].rename(columns={'dry_RunID':'RunID'})])
 if (mapping.groupby('RunID').route_cluster.nunique()>1).any():raise ValueError('RunID multiple routes')
 mapping=mapping.drop_duplicates('RunID');unique=runs.merge(mapping,on='RunID',validate='one_to_one')
 if not unique.informative.all():raise ValueError('uninformative run in analyzed pairs')
 if not np.allclose(unique.excess,unique.observed_cscore-unique.null_mean,rtol=0,atol=1e-10):raise ValueError('run residual inconsistency')
 baselines['unique_runs_in_analyzed_pairs']=route_summary(unique,'excess')
 for ch in [0,1]:
  unique['excess_chain_'+str(ch)]=unique.observed_cscore-unique.chain_means.map(lambda s:ast.literal_eval(s)[ch])
  baselines['unique_chain_'+str(ch)]=route_summary(unique,'excess_chain_'+str(ch))
 result={'study':'NAAMP_fixed_margin_pair_structure_environment_20261020','status':'exploratory_observational',
  'contract':'research/PAIR_SEGREGATION_ENVIRONMENT_CONTRACT_2026-10-20.md',
  'source_sha256':{k:h for k,(name,h) in SOURCES.items()},'baseline_residuals':baselines,
  'old_raw_summary_correction':{'bad_key':'primary.wet_route_equal_excess','actually_summarized':'wet_observed_cscore',
   'old_raw_value':old['primary']['wet_route_equal_excess']['route_equal_mean'],
   'true_excess_value':baselines['wet_excess']['mean'],'old_primary_delta_exactly_reproduced':True},
  'joins':{},'models':{},'sensitivities':{},'verification':{},'primary_tests':[]}
 for label,source,water in [('ERA5',e,False),('ERA5_MODIS',j,True)]:
  joined,audit=strict_join(p,source);result['joins'][label]=audit
  joined.to_csv(out/(label+'_joined.csv.gz'),index=False,compression='gzip')
  audit['states_retained']=sorted(joined.State.unique());sizes=joined.groupby('route_cluster').size()
  audit['singleton_routes']=int((sizes==1).sum());audit['routes_with_repeat_pairs']=int((sizes>1).sum())
  if len(joined)<MIN_PAIRS or joined.route_cluster.nunique()<MIN_ROUTES:
   result['models'][label]={'status':'below_precommitted_support'};continue
  a,cols=design(joined,water)
  fits=fit_within(a,cols,OUTCOMES);result['models'][label]=fits
  result['verification'][label]={y:verify_explicit(a,cols,y,fits[y]) for y in OUTCOMES}
  # Save all uncertainty, plus predictor dispersion for meaningful units.
  within=a[cols]-a[cols].groupby(a.route_cluster).transform('mean')
  result['models'][label]['exposures']={c:{'within_route_sd':float(within[c].std(ddof=0)),
    'quantiles':np.quantile(a[c],[0,.25,.5,.75,1]).tolist()} for c in ['layer_common']+(['surface_current_delta'] if water else [])}
  sens={}
  for name,sub,stratum in [('same_observer',a[a.same_observer],'route_cluster'),
      ('route_by_round',a,'route_round')]:
   if len(sub)>=MIN_PAIRS and sub.route_cluster.nunique()>=MIN_ROUTES:
    sens[name]=fit_within(sub,cols,OUTCOMES,stratum)
   else:sens[name]={'status':'below_precommitted_support','n':len(sub),'routes':int(sub.route_cluster.nunique())}
  sens['null_chains']=fit_within(a,cols,['delta_excess_chain_0','delta_excess_chain_1'])
  result['sensitivities'][label]=sens
  for lab,exposure in PRIMARY:
   if lab!=label:continue
   t=fits['delta_excess']['terms'].get(exposure)
   if t is None:raise ValueError('primary term rank deficient: '+exposure)
   unit=.01 if exposure=='layer_common' else .1
   result['primary_tests'].append({'model':label,'outcome':'delta_excess','term':exposure,**t,
       'report_unit':unit,'reported_beta':unit*t['beta'],'reported_ci95':[unit*x for x in t['ci95']]})
 for row,h in zip(result['primary_tests'],holm([r['p'] for r in result['primary_tests']])):row['p_holm']=float(h)
 result['boundaries']={'not_competition_or_niche_mechanism':True,'not_all_species_pairs_segregate':True,
  'fixed_margin_null_does_not_preserve_taxon_specific_site_preferences':True,
  'environment_response_at_route_not_species_specific_site':True,'monthly_water_may_postdate_day_within_month':True,
  'no_identity_specific_partner_turnover_test':True,'not_independent_new_sample':True,
  'all_inference_conditions_on_cached_null_means':True,'no_main_changes':True,
  'nonsignificance_not_equivalence':True,'different_response_significance_not_effect_difference_test':True}
 result['versions']={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
  'scipy':scipy.__version__,'statsmodels':statsmodels.__version__}
 (out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
 # Corrected mirror only: NEVER overwrite the original checksum-pinned archive.
 corrected=json.loads(json.dumps(old))
 raw_wet=corrected['primary'].pop('wet_route_equal_excess')
 raw_dry=corrected['primary'].pop('dry_route_equal_observed_cscore')
 corrected['primary']['raw_observed_descriptive_only']={
     'wet_mean':raw_wet['route_equal_mean'],'dry_mean':raw_dry['route_equal_mean'],
     'not_compared_to_zero_as_segregation_evidence':True}
 corrected['primary']['wet_null_centered_excess_posthoc']=baselines['wet_excess']
 corrected['primary']['dry_null_centered_excess_posthoc']=baselines['dry_excess']
 corrected['correction']={**result['old_raw_summary_correction'],
     'original_archive_unchanged':True,'old_primary_and_secondary_models_unchanged':True}
 (out/'ORIGINAL_FIXED_MARGIN_RESULT_CORRECTED.json').write_text(
     json.dumps(corrected,indent=2,sort_keys=True,allow_nan=False)+'\n')
 rows=[]
 for label,fit in result['models'].items():
  for y in OUTCOMES:
   if y not in fit:continue
   for x,t in fit[y]['terms'].items():rows.append({'model':label,'outcome':y,'term':x,**{k:v for k,v in t.items() if k!='ci95'},'lower95':t['ci95'][0],'upper95':t['ci95'][1]})
 pd.DataFrame(rows).to_csv(out/'effects.csv',index=False)
 p.to_csv(out/'corrected_original_pair_residuals.csv.gz',index=False,compression='gzip')
 unique.to_csv(out/'unique_run_residuals.csv.gz',index=False,compression='gzip')
 print(json.dumps({k:result[k] for k in ['old_raw_summary_correction','baseline_residuals','joins','primary_tests','verification']},indent=2))
 return result

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--input-root',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
 a=parser.parse_args();run(a.input_root,a.out)
