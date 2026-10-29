"""Fixed rank estimand: mechanism interventions and observed calling components."""
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from common_scale_comparison import ROOT, weighted_core, features, effects
from nee_context_robustness import SITE, VISITS, SURVEY, ENV, load, zrank, block_stats
from confront_mechanism_sites import fit_setup

OUT=ROOT/'research/results/mechanism_observation_20261029'
SOURCE=ROOT/'research/results/model_failure_diagnosis_20261029'


def components(strong,any_call):
    strong=np.asarray(strong,float);any_call=np.asarray(any_call,float)
    if np.any(strong>any_call+1e-12) or np.any(any_call<=0):
        raise ValueError('Components require positive any-call probability and nested events')
    conditional=strong/any_call
    np.testing.assert_allclose(strong,any_call*conditional,atol=1e-12)
    return np.column_stack([strong,any_call,conditional])


def empirical_weights(d,bg,levels):
    n=len(d)
    di=np.rint((rankdata(d['mean_suitability_Odonata_'+bg])-.5)/n*(levels-1)).astype(int)
    si=np.rint((rankdata(d['mean_suitability_pond_breeding_Caudata_'+bg])-.5)/n*(levels-1)).astype(int)
    vi=(d.flooded_3000m_mean.to_numpy()>0).astype(int)
    return np.bincount(vi*levels*levels+si*levels+di,minlength=2*levels*levels).astype(float)


def mechanisms(d):
    records=[];paths=[]
    sources=[('local',SOURCE/'counterfactual_None_cells.csv.gz'),
             ('local',SOURCE/'counterfactual_0.5_cells.csv.gz'),
             ('half_step',SOURCE/'counterfactual_half_step_cells.csv.gz'),
             ('long_run',SOURCE/'counterfactual_long_run_cells.csv.gz')]
    for check,path in sources:
        paths.append(path);cells=pd.read_csv(path)
        for (mid,bid),g in cells.groupby(['model_id','block_id']):
            g=g.sort_values(['vegetation','S_source','D_source']);assert len(g)==18
            for bg in ['uniform','target_group']:
                w=empirical_weights(d,bg,3)
                result=weighted_core(g.D_source.to_numpy(),g.S_source.to_numpy(),g.vegetation.to_numpy(),g.F_B.to_numpy(),w,'rank','rank')
                records.append(dict(check=check,model_id=mid,block_id=bid,background=bg,
                    simultaneous_signs=bool(result['OS']<0 and result['OV']<0 and result['SV']>0),**result))
    r=pd.DataFrame(records)
    aliases=json.loads((SOURCE/'counterfactual_design.json').read_text())['aliases']
    labels=pd.DataFrame(aliases).groupby('block_id').label.agg(' | '.join)
    r['intervention']=r.block_id.map(labels)
    macro=pd.read_csv(ROOT/'research/results/scale_comparison_20261029/macro_common_estimators.csv')
    for bg in ['uniform','target_group']:
        q=macro[(macro.background==bg)&(macro.vegetation=='binary')&(macro.x_transform=='rank')&(macro.y_transform=='rank')&(macro.adjustment=='space')&(macro['mode']=='pooled')].set_index('term')
        mask=r.background==bg
        for term in ['OS','OV','SV']:
            r.loc[mask,term+'_within_macro_interval']=r.loc[mask,term].between(q.loc[term,'low'],q.loc[term,'high'])
    r['all_three_marginal_intervals']=r[[t+'_within_macro_interval' for t in ['OS','OV','SV']]].all(axis=1)
    r.to_csv(OUT/'fixed_scale_interventions.csv',index=False)
    return paths


def calling(d):
    v=pd.read_csv(VISITS);v=v[(v.timeout==0)&v.site.isin(d.site)]
    assert not v.duplicated(['site','run']).any()
    assert (v.strong<=v['any']).all()
    means=v.groupby('site')[['strong','any']].mean()
    np.testing.assert_allclose(d.strong_rate,d.site.map(means.strong))
    np.testing.assert_allclose(d.any_rate,d.site.map(means['any']))
    d=d[d.any_rate>0].copy();assert len(d)==4182
    ys=components(d.strong_rate,d.any_rate)
    names=['strong_rate','any_call_rate','strong_given_call']
    pd.DataFrame(dict(site=d.site,route=d.route,strong_rate=ys[:,0],any_call_rate=ys[:,1],strong_given_call=ys[:,2])).to_csv(OUT/'calling_component_cohort.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    ys=zrank(ys)
    ll=zrank(d[['lat','lon']].to_numpy())
    cov=np.column_stack([zrank(d[SURVEY].to_numpy()),zrank(d[ENV].to_numpy()),ll,ll[:,0]**2,ll[:,0]*ll[:,1],ll[:,1]**2])
    ids=pd.factorize(d.spatial_block,sort=True)[0];k=ids.max()+1
    draws=np.random.default_rng(20261029).multinomial(k,np.full(k,1/k),size=999)
    results=[];contrasts=[]
    for bg in ['uniform','target_group']:
        o=zrank(d['mean_suitability_Odonata_'+bg]);s=zrank(d['mean_suitability_pond_breeding_Caudata_'+bg]);vv=zrank((d.flooded_3000m_mean>0).to_numpy(float))
        x=features(o,s,vv)
        for mode in ['pooled','within']:
            yy=[]
            for j in range(3):
                z,y,condition=fit_setup(x,cov,ys[:,j],d.route,mode);yy.append(y)
            yy=np.column_stack(yy);beta=np.linalg.lstsq(z,yy,rcond=1e-10)[0]
            xx,xy=block_stats(z,yy[:,0],ids)
            xys=np.stack([block_stats(z,yy[:,j],ids)[1] for j in range(3)],axis=-1)
            aa=np.einsum('bg,gij->bij',draws,xx);bb=np.einsum('bg,gij->bij',draws,xys)
            boot=[]
            for a,b in zip(aa,bb):
                coef,_,rank,_=np.linalg.lstsq(a,b,rcond=1e-12)
                if rank==z.shape[1]:boot.append(coef[:7])
            boot=np.asarray(boot)
            for i,term in enumerate(['O','S','V','OS','OV','SV','OSV']):
                for j,name in enumerate(names):
                    lo,hi=np.quantile(boot[:,i,j],[.025,.975])
                    results.append(dict(background=bg,mode=mode,outcome=name,term=term,beta=beta[i,j],low=lo,high=hi,sites=len(d),blocks=k,valid_bootstraps=len(boot)))
                delta=boot[:,i,2]-boot[:,i,1];lo,hi=np.quantile(delta,[.025,.975])
                contrasts.append(dict(background=bg,mode=mode,term=term,contrast='conditional_minus_any_rank_coefficients',beta=beta[i,2]-beta[i,1],low=lo,high=hi))
    pd.DataFrame(results).to_csv(OUT/'calling_component_coefficients.csv',index=False)
    pd.DataFrame(contrasts).to_csv(OUT/'paired_component_contrasts.csv',index=False)


def main():
    OUT.mkdir(parents=True,exist_ok=True);d=load()
    paths=mechanisms(d);calling(d)
    (OUT/'receipt.json').write_text(json.dumps(dict(
        fixed_estimator='rank O/S/Y, binary V, seven-term OLS; no scale selection',
        mechanism_primary='predictor-only empirical rank-bin weights, all 54 local contexts',
        macro_reference_sites=4248,component_sites=4182,excluded_zero_any=66,
        model_refit=False,observation_calibration=False,seed=20261029,
        input_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [SITE,VISITS,*paths]}),indent=2)+'\n')


if __name__=='__main__':main()
