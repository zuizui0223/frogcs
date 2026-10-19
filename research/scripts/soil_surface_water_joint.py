#!/usr/bin/env python3
"""Joint cached ERA5 and MODIS DSWEmod associations; post-hoc, not JAE C.
Contract: SOIL_SURFACE_WATER_JOINT_CONTRACT_2026-10-19.md.
Offline only. Exactly matched original RunID/SiteID, fixed r500 M3 completeness,
route FE/CR1, prior source-preserving reparameterization, four primary tests.
"""
from __future__ import annotations
import argparse,hashlib,io,json,platform
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
import numpy as np,pandas as pd,scipy,statsmodels
import statsmodels.formula.api as smf
import environment_within_route as core

SOIL_SHA='e182e0e30a7a5f1a7f1b8683d0024155b06f44b03205faa5df4beb02895d97a0'
WATER_SHA='8db94922a6a4de804b6711b0d2a5ab5e39f18f0a1561deb8392ee13e38100cef'
WATER_CSV_SHA='9d2967923d7c31ace8007cf51f502c1dc56d41ffcf32383dc1b9edd133b94042'
PRIMARY=['layer_common','surface_current_delta','surface_prior_delta','soil_by_water']
WATER_TERMS=['surface_current_delta','surface_current_mid','surface_prior_delta','surface_prior_mid']
OUTCOMES=['strong_new_count','richness_gain','new_ci3_count']

def prior_two(current,recent):
 current=np.asarray(current,float);recent=np.asarray(recent,float)
 if not (np.isfinite(current).all() and np.isfinite(recent).all()):raise ValueError('missing water is not zero')
 prior=(3*recent-current)/2
 for a in (current,recent,prior):
  # Original CSV uses %.8f: max propagated rounding error is 1e-8.
  if (a< -1.01e-8).any() or (a>1+1.01e-8).any():raise ValueError('water fraction outside source bounds')
 if not np.allclose((current+2*prior)/3,recent,rtol=0,atol=1e-12):raise ValueError('historical reconstruction')
 return np.clip(prior,0,1)

def keytext(x):
 s=str(x).strip()
 if s.endswith('.0') and s[:-2].isdigit():s=s[:-2]
 return s

def normalize(d,cols):
 d=d.copy()
 for col in cols:
  if d[col].isna().any():raise ValueError('missing identity '+col)
  d[col]=d[col].map(keytext)
 return d

def join(pairs,water,radius):
 if radius not in (500,250):raise ValueError('unregistered radius')
 pairs=normalize(pairs,['wet_RunID','dry_RunID','RunNumber','RouteNumber'])
 water=normalize(water,['RunID','SiteID','RunNumber','RouteNumber'])
 if pairs.duplicated(['wet_RunID','dry_RunID']).any() or water.duplicated(['RunID','SiteID']).any():raise ValueError('duplicate input keys')
 cols=[f'current_D_r{radius}',f'recent_D_3m_r{radius}',f'DSWE_sd_12m_r{radius}']
 runmap={rid:g for rid,g in water.groupby('RunID',sort=False)}
 fails=Counter();out=[]
 for p in pairs.to_dict('records'):
  if not p['stable_sites']:fails['unstable_sites']+=1;continue
  w,d=runmap.get(p['wet_RunID']),runmap.get(p['dry_RunID'])
  if w is None or d is None:fails['run_missing']+=1;continue
  if len(w)!=10 or len(d)!=10:fails['not_ten_sites']+=1;continue
  if set(w.SiteID)!=set(d.SiteID):fails['siteid_mismatch']+=1;continue
  for g in (w,d):
   for n in ['State','RouteNumber','route_cluster','RunNumber']:
    if g[n].nunique()!=1 or keytext(g[n].iloc[0])!=keytext(p[n]):raise ValueError('cross-source route identity conflict: '+n)
   if g.year.nunique()!=1 or g.month.nunique()!=1:raise ValueError('ambiguous observation month/year')
  years=sorted([int(w.year.iloc[0]),int(d.year.iloc[0])])
  if years!=[int(p['year_earlier']),int(p['year_later'])]:raise ValueError('pair year identity conflict')
  if not (np.isfinite(w[cols]).all().all() and np.isfinite(d[cols]).all().all()):fails['M3_missing']+=1;continue
  r=dict(p)
  for side,g in [('w',w),('d',d)]:
   now=g[cols[0]].to_numpy();recent=g[cols[1]].to_numpy();prior=prior_two(now,recent)
   r['surface_current_'+side]=float(now.mean());r['surface_prior_'+side]=float(prior.mean())
   r['surface_recent3_'+side]=float(recent.mean());r['surface_sd12_'+side]=float(g[cols[2]].mean())
   r['surface_year_'+side]=int(g.year.iloc[0]);r['surface_month_'+side]=int(g.month.iloc[0])
  out.append(r)
 result=pd.DataFrame(out)
 return result,{'input_pairs':len(pairs),'pairs':len(result),'routes':int(result.route_cluster.nunique()) if len(result) else 0,'states':int(result.State.nunique()) if len(result) else 0,'failures':dict(fails),'radius_m':radius,'exact_ten_identical_siteids_in_each_pair':True,'M3_source_gate_retained':True}

def load_inputs(soil_zip,water_zip):
 for p,h in [(soil_zip,SOIL_SHA),(water_zip,WATER_SHA)]:
  if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h:raise ValueError('source ZIP hash changed')
 with ZipFile(soil_zip) as z:
  m=json.loads(z.read('SHA256.json'))
  if set(z.namelist())!={'SHA256.json',*m}:raise ValueError('soil members changed')
  for n,h in m.items():
   if hashlib.sha256(z.read(n)).hexdigest()!=h:raise ValueError('soil member hash changed')
  pairs=pd.read_csv(io.BytesIO(z.read('paired_environment_and_chorus.csv.gz')),compression='gzip',dtype={'wet_RunID':str,'dry_RunID':str,'RouteNumber':str,'RunNumber':str})
 with ZipFile(water_zip) as z:
  raw=z.read('NAAMP_DSWEMOD_RUN_SITE_METRICS_V0_1.csv')
  if hashlib.sha256(raw).hexdigest()!=WATER_CSV_SHA:raise ValueError('water CSV hash changed')
  water=pd.read_csv(io.BytesIO(raw),dtype={'RunID':str,'SiteID':str,'RouteNumber':str,'RunNumber':str})
 core.validate_outcome_identities(pairs)
 if len(pairs)!=4108 or int(pairs.stable_sites.sum())!=4045 or len(water)!=33260:raise ValueError('source cohort size changed')
 return pairs,water

def design(d,year_effects=False,water_center=None):
 a,base=core.design(d,year_effects)
 for n in ('current','prior'):
  a['surface_'+n+'_delta']=a['surface_'+n+'_w']-a['surface_'+n+'_d']
  a['surface_'+n+'_mid']=(a['surface_'+n+'_w']+a['surface_'+n+'_d'])/2
 if water_center is None:water_center=float(a.surface_prior_mid.mean())
 a['soil_by_water']=a.layer_common*(a.surface_prior_mid-water_center)
 return a,base,water_center

def fit(a,cols,strata='route_cluster'):
 res=core.absorb_fit(a,OUTCOMES,cols,strata)
 needed=[x for x in PRIMARY if x in cols]
 if any(t not in res[OUTCOMES[0]]['terms'] for t in needed):raise ValueError('primary term nonidentifiable')
 return res

def small_terms(fits,model_name):
 return [{'model':model_name,'response':y,'term':t,**v} for y,f in fits.items() for t,v in f['terms'].items() if t in PRIMARY]

def summarize_exposure(a,cols):
 within=a[cols]-a[cols].groupby(a.route_cluster).transform('mean')
 x=['layer_common','surface_excess','surface_current_delta','surface_prior_delta','soil_by_water']
 num=a.groupby('route_cluster').size()
 return {'quantiles':{n:np.quantile(a[n],[0,.25,.5,.75,.9,1]).tolist() for n in x+['surface_current_mid','surface_prior_mid']},
  'within_route_sd':{n:float(within[n].std(ddof=0)) for n in x},
  'within_correlation':within[x].corr().to_dict(),
  'zero_current_both_surveys_pairs':int(((a.surface_current_w==0)&(a.surface_current_d==0)).sum()),
  'zero_prior_both_surveys_pairs':int(((a.surface_prior_w==0)&(a.surface_prior_d==0)).sum()),
  'singleton_routes':int((num==1).sum()),'routes_at_least_two_pairs':int((num>=2).sum()),
  'all_source_years':sorted(set(a.surface_year_w.astype(int))|set(a.surface_year_d.astype(int)))}

def main():
 p=argparse.ArgumentParser();p.add_argument('--soil-zip',type=Path,required=True);p.add_argument('--water-zip',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--prepare-only',action='store_true');args=p.parse_args()
 pairs,water=load_inputs(args.soil_zip,args.water_zip);d,audit=join(pairs,water,500);d250,audit250=join(pairs,water,250)
 args.out.mkdir(parents=True,exist_ok=True)
 (args.out/'JOIN.json').write_text(json.dumps({'r500':audit,'r250':audit250},indent=2))
 if args.prepare_only:print(json.dumps({'r500':audit,'r250':audit250},indent=2));return
 if len(d)<500 or d.route_cluster.nunique()<100:raise ValueError('insufficient joint within-route sample; no relaxed source gates')
 a,b,center=design(d);cols=b+WATER_TERMS+['soil_by_water']
 fits={'soil_only_same_sample':fit(a,b),'joint_additive':fit(a,b+WATER_TERMS),'joint_interaction':fit(a,cols)}
 mainfit=fits['joint_interaction'];primary=[]
 for name in PRIMARY:
  unit=.01 if name=='layer_common' else (.001 if name=='soil_by_water' else .10)
  t=mainfit['strong_new_count']['terms'][name]
  primary.append({'term':name,**t,'report_scale':unit,'reported_beta':unit*t['beta'],'reported_ci95':[unit*x for x in t['ci95']]})
 for x,h in zip(primary,core.holm([x['p'] for x in primary])):x['p_holm_four']=float(h)
 sens={'same_observer':fit(a[a.same_observer],cols), 'route_by_season':fit(a,cols,'route_season')}
 ay,by,_=design(d,True,center);sens['route_and_pair_years']=fit(ay,by+WATER_TERMS+['soil_by_water'])
 a2,b2,_=design(d250,False,center);sens['radius250']=fit(a2,b2+WATER_TERMS+['soil_by_water'])
 # Independent full-dummy OLS check, including CR1 finite-sample df.
 independent={}
 form='strong_new_count ~ '+' + '.join(cols)+' + C(route_cluster)'
 f=smf.ols(form,a).fit(cov_type='cluster',cov_kwds={'groups':a.route_cluster})
 for name in PRIMARY:
  ref=mainfit['strong_new_count']['terms'][name]
  if not (np.isclose(f.params[name],ref['beta'],rtol=1e-9,atol=1e-9) and np.isclose(f.bse[name],ref['se'],rtol=1e-9,atol=1e-9)):raise RuntimeError('explicit dummy primary verification failed')
  independent[name]={'coefficient_error':float(f.params[name]-ref['beta']),'SE_error':float(f.bse[name]-ref['se'])}
 # Per-route design leverage is descriptive: no influential routes discarded.
 influence=f.get_influence();lev=pd.Series(influence.hat_matrix_diag,index=a.index).groupby(a.route_cluster).sum()
 hdiag=np.asarray(influence.hat_matrix_diag)
 usable_h=hdiag<1-1e-10
 # Singleton FE observations are exactly fitted (h=1), so this
 # diagnostic is undefined there; keep them in every fitted model.
 student=np.abs(np.asarray(f.resid)[usable_h])/np.sqrt(float(f.mse_resid)*(1-hdiag[usable_h]))
 # Rows deliberately carry no coordinates / observer identity.
 a.to_csv(args.out/'joined_environment_and_chorus.csv.gz',index=False,compression='gzip')
 rows=[]
 for name,ff in {**fits,**sens}.items():rows+=small_terms(ff,name)
 pd.DataFrame(rows).to_csv(args.out/'effects.csv',index=False)
 original=pairs[pairs.stable_sites].groupby('State').agg(pairs=('route_cluster','size'),routes=('route_cluster','nunique'))
 retained=d.groupby('State').agg(pairs=('route_cluster','size'),routes=('route_cluster','nunique'))
 state=original.join(retained,lsuffix='_full',rsuffix='_joined').fillna(0).astype(int)
 result={'analysis':'joint_cached_ERA5_MODIS_soil_surface_water_20261019','status':'executed_post_hoc',
  'source_zip_sha256':{'soil':SOIL_SHA,'water':WATER_SHA},'joint_coverage':audit,'radius250_coverage':audit250,
  'primary_four':primary,'models':fits,'sensitivities':sens,'prior_surface_mean_center':center,
  'state_selection':state.to_dict(orient='index'),'exposure_diagnostics':summarize_exposure(a,cols),
  'explicit_dummy_verification':independent,'leverage_diagnostic':{'max_route_leverage_sum':float(lev.max()),'row_internal_studentized_residual_max_where_defined':float(student.max()) if len(student) else None,'undefined_studentized_rows_leverage_one':int((~usable_h).sum()),'diagnostic_exclusion_not_model_exclusion':True,'no_rows_deleted':True},
  'boundaries':{'ERA5_reanalysis_not_satellite_measurement':True,'MODIS_water_actual_cached_satellite_extraction':True,'wet_dry_not_chronological':True,'fixed_route_only_controls_time_invariant_intercepts':True,'monthly_current_can_include_after_survey_images':True,'no_prospective_prediction_claim':True,'prior_two_is_reparameterization_not_new_window_search':True,'not_original_JAE_concentration_C':True,'not_causal_or_memory_test':True,'route_clustering_not_cross_route_spatial_correction':True,'posthoc_four_tests_not_all_repo_multiplicity':True,'main_unchanged':True},
  'runtime':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'statsmodels':statsmodels.__version__}}
 (args.out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'joint':audit,'primary_four':primary,'models':{m:{y:{n:v for n,v in f['terms'].items() if n in PRIMARY} for y,f in ff.items()} for m,ff in fits.items()},'sensitivities':{m:{n:v for n,v in ff['strong_new_count']['terms'].items() if n in PRIMARY} for m,ff in sens.items()},'exposure':result['exposure_diagnostics']},indent=2))

if __name__=='__main__':main()
