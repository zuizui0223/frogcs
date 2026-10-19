#!/usr/bin/env python3
"""Exploratory cached NAAMP environment analysis. No network; no main edits.

Protocol: research/ENVIRONMENT_WITHIN_ROUTE_CONTRACT_2026-10-19.md.
Absorbed route effects are estimated by exact within transformation. CR1
covariance retains the full fixed-effect parameter count. Wet/dry is a
rain-recency contrast, not a before/after experiment. Counts measure calling,
not abundance, occupancy, breeding success, or original JAE concentration C.
"""
from __future__ import annotations
import argparse, hashlib, io, json, platform
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import pandas as pd
import scipy
from scipy.linalg import qr
from scipy.stats import norm
import statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf

SOURCE_SHA='e182e0e30a7a5f1a7f1b8683d0024155b06f44b03205faa5df4beb02895d97a0'
BASE='rain_contrast + rain72_z + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber) + vpd_relief_z + vpd_mid_z + air_mid_z'
FORMS={'base_no_soil':'strong_new_score ~ '+BASE,
       'soil_additive':'strong_new_score ~ '+BASE+' + soil_delta_z + soil_mid_z',
       'soil_context':'strong_new_score ~ '+BASE+' + soil_delta_z + soil_mid_z + soil_delta_z:soil_mid_z + soil_delta_z:vpd_mid_z',
       'layer_partition':'strong_new_score ~ '+BASE+' + soil_mid_z + layer_common_z + surface_excess_z'}
ENV_NAMES=['soil_delta','soil_mid','vpd_mid','vpd_relief','rain72','layer_common','surface_excess','air_mid']
NUMERIC=['rain_contrast','rain72','temp_difference','doy_difference','year_gap',
         'vpd_relief','vpd_mid','air_mid','soil_mid','layer_common','surface_excess']
RESPONSES=['strong_new_count','richness_gain','strong_new_score','new_ci3_count','wet_only','dry_only']
PRIMARY=[('strong_new_count','layer_common'),('strong_new_count','surface_excess'),('richness_gain','layer_common')]

def raw_features(d: pd.DataFrame) -> pd.DataFrame:
    a=d.copy()
    a['soil_delta']=d.soil1_w-d.soil1_d
    a['soil_mid']=(d.soil1_w+d.soil1_d)/2
    a['vpd_mid']=(d.vpd_w+d.vpd_d)/2
    a['vpd_relief']=d.vpd_d-d.vpd_w
    a['rain72']=np.log1p(d.rain72_w)-np.log1p(d.rain72_d)
    a['layer_common']=((d.soil1_w-d.soil1_d)+(d.soil2_w-d.soil2_d))/2
    a['surface_excess']=(d.soil1_w-d.soil1_d)-(d.soil2_w-d.soil2_d)
    a['air_mid']=(d.air_w+d.air_d)/2
    if not np.isfinite(a[ENV_NAMES].to_numpy(dtype=float)).all():
        raise ValueError('Missing environmental values are not zero')
    return a

def validate_outcome_identities(d: pd.DataFrame) -> bool:
    equalities=[(d.strong_new_score,2*d.strong_new_count+d.new_ci3_count),
                (d.richness_gain,d.wet_only-d.dry_only),
                (d.richness_gain,d.wet_richness-d.dry_richness)]
    if not all(np.allclose(x,y,rtol=0,atol=1e-12) for x,y in equalities):
        raise ValueError('Cached acoustic count/score identities changed')
    return True

def holm(p):
    p=np.asarray(p,float)
    if not np.isfinite(p).all() or ((p<0)|(p>1)).any():raise ValueError('invalid p-values')
    order=np.argsort(p);v=np.maximum.accumulate((len(p)-np.arange(len(p)))*p[order])
    out=np.empty_like(p);out[order]=np.minimum(1,v);return out

def term(b,se):
    if not np.isfinite([b,se]).all() or se<=0:raise ValueError('undefined coefficient uncertainty')
    z=norm.ppf(.975)
    return {'beta':float(b),'se':float(se),'ci95':[float(b-z*se),float(b+z*se)],
            'p':float(2*norm.sf(abs(b/se))),'beta_per_0_01':float(.01*b),
            'ci95_per_0_01':[float(.01*(b-z*se)),float(.01*(b+z*se))]}

def absorb_fit(d: pd.DataFrame, outcomes: list[str], columns: list[str],
               strata: str='route_cluster') -> dict:
    """Within OLS and route-cluster CR1, including absorbed parameter df."""
    vals=d[columns+outcomes].astype(float)
    if not np.isfinite(vals.to_numpy()).all():raise ValueError('nonfinite design or outcome')
    within=vals-vals.groupby(d[strata],sort=False).transform('mean')
    X0=within[columns].to_numpy();Y=within[outcomes].to_numpy()
    n=len(d);G=int(d.route_cluster.nunique());S=int(d[strata].nunique())
    if G<2:raise ValueError('cluster inference requires multiple routes')
    _,R,piv=qr(X0,mode='economic',pivoting=True)
    diag=np.abs(np.diag(R));tol=diag.max(initial=0)*max(X0.shape)*np.finfo(float).eps
    rank=int(np.sum(diag>tol));keep=sorted(piv[:rank]);names=[columns[i] for i in keep]
    if rank==0 or n<=S+rank:raise ValueError('no within-stratum support or residual df')
    X=X0[:,keep];B=np.linalg.lstsq(X,Y,rcond=None)[0];E=Y-X@B
    bread=np.linalg.inv(X.T@X)
    routes=pd.factorize(d.route_cluster,sort=True)[0]
    correction=G/(G-1)*(n-1)/(n-S-rank)
    result={}
    for j,outcome in enumerate(outcomes):
        scores=np.zeros((G,rank));np.add.at(scores,routes,X*E[:,j,None])
        covariance=bread@(scores.T@scores)@bread*correction
        sd=np.sqrt(np.maximum(np.diag(covariance),0))
        terms={name:term(B[i,j],sd[i]) for i,name in enumerate(names)}
        result[outcome]={'pairs':n,'routes':G,'absorbed_strata':S,'states':int(d.State.nunique()) if 'State' in d else None,
           'residual_df':n-S-rank,'cr1_correction':float(correction),'rank':rank,
           'dropped_columns':[x for x in columns if x not in names],
           'terms':terms,'within_residual_rmse':float(np.sqrt(np.mean(E[:,j]**2)))}
    return result

def error_decomposition(y,pred,routes) -> dict:
    y=np.asarray(y,float);p=np.asarray(pred,float);r=np.asarray(routes)
    if not (len(y)==len(p)==len(r)) or not len(y) or not np.isfinite([y,p]).all():
        raise ValueError('invalid error decomposition input')
    codes,groups=pd.factorize(r,sort=True);counts=np.bincount(codes)
    w=1/(len(groups)*counts[codes]);err=y-p
    bias=float(w@err);mse=float(w@(err**2));centered=float(w@((err-bias)**2))
    if not np.isclose(mse,bias**2+centered,atol=1e-10):raise RuntimeError('MSE identity failed')
    return {'pairs':len(y),'routes':len(groups),'mse':mse,'bias_squared':bias**2,'centered_mse':centered,
            'mean_error_y_minus_prediction':bias,'mean_observed':float(w@y),
            'mean_predicted':float(w@p),'negative_prediction_weight':float(w@(p<0)),
            'test_response_centering_is_diagnostic_not_a_forecast':True}

def design(d,year_effects=False):
    a=raw_features(d).reset_index(drop=True);cols=NUMERIC.copy()
    runs=pd.get_dummies(a.RunNumber.astype(str),prefix='run',drop_first=True,dtype=float)
    a=pd.concat([a,runs],axis=1);cols+=runs.columns.tolist()
    a['route_season']=a.route_cluster.astype(str)+'|'+a.RunNumber.astype(str)
    if year_effects:
        # year_gap is exactly year_later - year_earlier: do not duplicate it.
        cols.remove('year_gap')
        for name in ('year_earlier','year_later'):
            yy=pd.get_dummies(a[name].astype(str),prefix=name,drop_first=True,dtype=float)
            a=pd.concat([a,yy],axis=1);cols+=yy.columns.tolist()
    return a,cols

def between_fit(d,cols):
    means=d.groupby('route_cluster')[cols+RESPONSES].mean()
    states=d.groupby('route_cluster').State.first()
    dummy=pd.get_dummies(states,prefix='state',drop_first=True,dtype=float)
    X=pd.concat([means[cols],dummy],axis=1)
    X=sm.add_constant(X,has_constant='add')
    fits={}
    for y in RESPONSES:
        f=sm.OLS(means[y],X).fit(cov_type='HC1')
        fits[y]={'routes':len(means),'route_equal_weight':True,'covariance':'HC1',
                 'terms':{v:term(f.params[v],f.bse[v]) for v in ('layer_common','surface_excess')}}
    return fits

def old_features(d,scaler=None):
    a=raw_features(d)
    if scaler is None:scaler={n:[float(a[n].mean()),float(a[n].std(ddof=0)) or 1.] for n in ENV_NAMES}
    for n in ENV_NAMES:a[n+'_z']=(a[n]-scaler[n][0])/scaler[n][1]
    return a,scaler

def temporal(d,reference):
    train=d[d.year_later<=2008].copy();candidate=d[d.year_earlier>=2009].copy()
    train,sc=old_features(train);test,_=old_features(candidate,sc)
    known=test.State.isin(train.State.unique())&test.RunNumber.isin(train.RunNumber.unique())
    test=test[known].copy();y=test.strong_new_score.to_numpy()
    if len(train)!=1403 or len(test)!=1519:raise ValueError('original temporal sample drift')
    models={};preds={}
    for name,formula in FORMS.items():
        fit=smf.ols(formula,train).fit();p=np.asarray(fit.predict(test));preds[name]=p
        models[name]=error_decomposition(y,p,test.route_cluster)
    compares={}
    for name,base in [('soil_additive','base_no_soil'),('soil_context','soil_additive'),('layer_partition','soil_additive')]:
        key=name+'_over_'+base
        gain=models[base]['mse']-models[name]['mse']
        old=reference['temporal_transfer']['comparisons'][key]['route_equal_mse_reduction']
        if not np.isclose(gain,old,atol=1e-8,rtol=0):raise RuntimeError('prior temporal result not reproduced')
        compares[key]={'mse_reduction':float(gain),
         'squared_bias_reduction':models[base]['bias_squared']-models[name]['bias_squared'],
         'centered_error_reduction':models[base]['centered_mse']-models[name]['centered_mse'],
         'original_point_estimate_reproduced':True}
    seen=test.route_cluster.isin(train.route_cluster.unique());by_route={}
    for label,mask in [('seen_training_routes',seen),('unseen_training_routes',~seen)]:
        sub=test[mask];ps={name:error_decomposition(sub.strong_new_score,p[mask],sub.route_cluster)
                          for name,p in preds.items()} if len(sub) else {}
        by_route[label]=ps
    distribution={}
    for label,data in [('train',train),('test',test)]:
        distribution[label]={'pairs':len(data),'routes':int(data.route_cluster.nunique()),'states':int(data.State.nunique()),
          'strong_score_route_equal_mean':float(data.groupby('route_cluster').strong_new_score.mean().mean()),
          'strong_score_zero_fraction':float((data.strong_new_score==0).mean()),
          'feature_pair_quantiles':{n:np.quantile(data[n],[.1,.5,.9]).tolist() for n in ('layer_common','surface_excess','soil_mid')}}
    return {'original_cutoff_retained':True,'no_refit_on_test':True,'unknown_category_excluded_pairs':int((~known).sum()),
            'models':models,'comparisons':compares,'distribution':distribution,'by_seen_route':by_route}

def run(source: Path,outdir: Path) -> dict:
    raw=source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('source ZIP digest mismatch')
    with ZipFile(io.BytesIO(raw)) as z:
        manifest=json.loads(z.read('SHA256.json'))
        if set(z.namelist())!={'SHA256.json',*manifest}:raise ValueError('unlisted source member')
        for name,h in manifest.items():
            if hashlib.sha256(z.read(name)).hexdigest()!=h:raise ValueError('inner digest mismatch')
        d=pd.read_csv(io.BytesIO(z.read('paired_environment_and_chorus.csv.gz')),compression='gzip')
        reference=json.loads(z.read('RESULT.json'))
    validate_outcome_identities(d)
    stable=d[d.stable_sites].copy()
    if (len(d),len(stable),stable.route_cluster.nunique())!=(4108,4045,563):raise ValueError('source population drift')
    if d.duplicated(['wet_RunID','dry_RunID']).any():raise ValueError('duplicate matched pair')
    a,cols=design(stable)
    main=absorb_fit(a,RESPONSES,cols)
    primary=[]
    for y,x in PRIMARY:primary.append({'response':y,'exposure':x,**main[y]['terms'][x]})
    for row,p in zip(primary,holm([x['p'] for x in primary])):row['p_holm_three']=float(p)
    sensitivities={'same_observer':absorb_fit(a[a.same_observer],RESPONSES,cols),
                   'route_by_season':absorb_fit(a,RESPONSES,cols,'route_season')}
    ay,cy=design(stable,True);sensitivities['route_and_pair_years']=absorb_fit(ay,RESPONSES,cy)
    # Exact coefficient identities separate acoustic richness components.
    identities={}
    for x in ('layer_common','surface_excess'):
        c=main['strong_new_score']['terms'][x]['beta']
        c2=2*main['strong_new_count']['terms'][x]['beta']+main['new_ci3_count']['terms'][x]['beta']
        r=main['richness_gain']['terms'][x]['beta']
        r2=main['wet_only']['terms'][x]['beta']-main['dry_only']['terms'][x]['beta']
        if not (np.isclose(c,c2,atol=1e-9) and np.isclose(r,r2,atol=1e-9)):
            raise RuntimeError('linear ecological decomposition failed')
        identities[x]={'strong_score_residual':float(c-c2),'richness_gain_residual':float(r-r2)}
    # Reproduce prior within-route score sensitivity, in its standard units.
    sd=float(raw_features(stable).surface_excess.std(ddof=0))
    check_beta=main['strong_new_score']['terms']['surface_excess']['beta']*sd
    ref_beta=reference['route_fixed_effect_sensitivity']['effects'][2]['beta']
    if not np.isclose(check_beta,ref_beta,atol=1e-8):raise RuntimeError('prior route fixed-effect coefficient mismatch')
    result={'analysis':'cached_environment_within_route_ecology_20261019',
       'source_zip_sha256':SOURCE_SHA,'status':'executed_post_hoc','primary_three':primary,
       'within_route':main,'between_route_equal':between_fit(a,cols),'sensitivities':sensitivities,
       'coefficient_identity_checks':identities,'prior_route_score_coefficient_reproduced':float(check_beta),
       'temporal_error_diagnostic':temporal(stable,reference),
       'boundaries':{'no_new_environment_download':True,'not_JAE_concentration_C':True,
          'not_true_occupancy_or_abundance':True,'not_causal_hydric_effect':True,
          'route_effects_do_not_remove_time_varying_habitat_or_taxon_composition':True,
          'prior_boundary_layer_signal_not_overridden':True,'wet_dry_not_chronological':True,
          'main_unchanged':True,'clustering_does_not_model_cross_route_spatial_dependence':True,
          'multiple_testing_family_not_entire_repository':True},
       'runtime':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
                  'scipy':scipy.__version__,'statsmodels':statsmodels.__version__}}
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    rows=[]
    for label,model in [('within_route',main),('between_route',result['between_route_equal']),*sensitivities.items()]:
        for y,f in model.items():
            for x in ('layer_common','surface_excess'):
                if x not in f['terms']:continue
                t=f['terms'][x]
                rows.append({'model':label,'response':y,'exposure':x,'effect_per_0_01':t['beta_per_0_01'],
                  'ci95_low':t['ci95_per_0_01'][0],'ci95_high':t['ci95_per_0_01'][1],'p_unadjusted':t['p'],
                  'n_pairs':f.get('pairs'),'n_routes':f['routes']})
    pd.DataFrame(rows).to_csv(outdir/'effects.csv',index=False)
    print(json.dumps({'primary_three':primary,'temporal_error_diagnostic':result['temporal_error_diagnostic']},indent=2))
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-zip',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.source_zip,args.output)
if __name__=='__main__':main()
