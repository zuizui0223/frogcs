"""Common estimators across unlike observables; never a biological calibration."""
import json
import hashlib
import platform

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from nee_context_robustness import ROOT, SITE, VISITS, SURVEY, ENV, load, zrank, block_stats
from confront_mechanism_sites import fit_setup

OUT = ROOT/'research/results/scale_comparison_20261029'
MODEL = ROOT/'research/results/final_mechanism_20261027/winner_rank_cells.csv.gz'
TERMS = ['O','S','V','O:S','O:V','S:V','O:S:V']


def weighted_z(a, w):
    a=np.asarray(a,float);w=np.asarray(w,float)
    mean=np.average(a,weights=w);sd=np.sqrt(np.average((a-mean)**2,weights=w))
    if sd <= 1e-14: raise ValueError('Constant variable')
    return (a-mean)/sd


def transform(a, w, kind):
    if kind == 'raw': return weighted_z(a,w)
    if kind != 'rank': raise ValueError(kind)
    _, inverse = np.unique(a,return_inverse=True)
    mass=np.bincount(inverse,weights=w)
    mid=(np.cumsum(mass)-mass/2)/mass.sum()
    return weighted_z(mid[inverse],w)


def features(o,s,v):
    return np.column_stack([o,s,v,o*s,o*v,s*v,o*s*v])


def effects(beta,vlo,vhi):
    return dict(OS=beta[3],OV=beta[4],SV=beta[5],OSV=beta[6],
                OS_low=beta[3]+vlo*beta[6],OS_high=beta[3]+vhi*beta[6],
                OS_high_minus_low=(vhi-vlo)*beta[6])


def weighted_core(o,s,v,y,w,x_transform,y_transform):
    keep=w>0;o=o[keep];s=s[keep];v=v[keep];y=y[keep];w=w[keep]
    zz=transform(v,w,'rank');lo=float(zz[v==0][0]);hi=float(zz[v==1][0])
    x=features(transform(o,w,x_transform),transform(s,w,x_transform),zz)
    yy=transform(y,w,y_transform);z=np.column_stack([x,np.ones(len(w))]);sw=np.sqrt(w)
    beta,_,rank,_=np.linalg.lstsq(z*sw[:,None],yy*sw,rcond=1e-12)
    if rank != 8: raise ValueError('Rank deficient design')
    return dict(**effects(beta,lo,hi),R2=1-np.average((yy-z@beta)**2,weights=w),
                cells_with_positive_weight=len(w),design_condition=np.linalg.cond(z*sw[:,None]))


def main():
    OUT.mkdir(parents=True,exist_ok=True);d=load();n=len(d);w=np.ones(n)
    vraw=d.flooded_3000m_mean.to_numpy();vb=(vraw>0).astype(float)
    obs=zrank(d[SURVEY].to_numpy());env=zrank(d[ENV].to_numpy());ll=zrank(d[['lat','lon']].to_numpy())
    cov=np.column_stack([obs,env,ll,ll[:,0]**2,ll[:,0]*ll[:,1],ll[:,1]**2])
    ids=pd.factorize(d.spatial_block,sort=True)[0];k=ids.max()+1
    weights=np.random.default_rng(20261029).multinomial(k,np.full(k,1/k),size=999)
    results=[]
    for bg in ['uniform','target_group']:
        o=d['mean_suitability_Odonata_'+bg].to_numpy();s=d['mean_suitability_pond_breeding_Caudata_'+bg].to_numpy()
        for vegetation in ['binary','continuous']:
            v=transform(vb if vegetation=='binary' else vraw,w,'rank')
            vlo=float(v[vb==0][0]);vhi=float(v[vb==1][0]) if vegetation=='binary' else float(np.median(v[vb==1]))
            for xt in ['raw','rank']:
                x=features(transform(o,w,xt),transform(s,w,xt),v)
                for adjustment in ['none','space']:
                    for mode in ['pooled','within']:
                        cc=np.empty((n,0)) if adjustment=='none' else cov
                        # Keep exactly the same design for the two outcome transformations.
                        for yt in ['raw','rank']:
                            y=transform(d.strong_rate.to_numpy(),w,yt)
                            z,yy,condition=fit_setup(x,cc,y,d.route,mode)
                            beta=np.linalg.lstsq(z,yy,rcond=1e-10)[0]
                            xx,xy=block_stats(z,yy,ids);aa=np.einsum('bg,gij->bij',weights,xx);bb=weights@xy
                            boot=[]
                            for a,b in zip(aa,bb):
                                coef,_,rank,_=np.linalg.lstsq(a,b,rcond=1e-12)
                                if rank==z.shape[1]:boot.append(effects(coef,vlo,vhi))
                            boot=pd.DataFrame(boot)
                            meta=dict(background=bg,vegetation=vegetation,x_transform=xt,y_transform=yt,
                                adjustment=adjustment,mode=mode,valid_bootstraps=len(boot),focal_condition=condition)
                            for term,value in effects(beta,vlo,vhi).items():
                                lo,hi=boot[term].quantile([.025,.975])
                                results.append({**meta,'term':term,'beta':value,'low':lo,'high':hi})
    macro=pd.DataFrame(results);macro.to_csv(OUT/'macro_common_estimators.csv',index=False)
    # Replay prior rank and original-response sensitivities before interpretation.
    old=pd.read_csv(ROOT/'research/results/mechanism_site_20261029/conditional_OS.csv')
    for bg in ['uniform','target_group']:
        for mode in ['pooled','within']:
            new=macro[(macro.background==bg)&(macro['mode']==mode)&(macro.vegetation=='continuous')&(macro.x_transform=='rank')&(macro.y_transform=='rank')&(macro.adjustment=='space')].set_index('term')
            previous=old[(old.background==bg)&(old['mode']==mode)&(old.group=='all')&(old.cluster=='spatial_block')].set_index('contrast')
            for term,label in [('OS_low','at_zero_detection'),('OS_high','at_positive_median'),('OS_high_minus_low','positive_minus_zero')]:
                np.testing.assert_allclose(new.loc[term,['beta','low','high']].to_numpy(float),previous.loc[label,['beta','low','high']].to_numpy(float),atol=1e-8)
    saved=pd.read_csv(MODEL);model_results=[];weight_rows=[]
    for levels,g in saved.groupby('levels'):
        g=g.sort_values(['vegetation','S_source','D_source']).reset_index(drop=True)
        size=int(levels);assert len(g)==2*size*size
        for bg in ['uniform','target_group']:
            o=d['mean_suitability_Odonata_'+bg].to_numpy();s=d['mean_suitability_pond_breeding_Caudata_'+bg].to_numpy()
            di=np.rint(((rankdata(o)-.5)/n)*(size-1)).astype(int)
            si=np.rint(((rankdata(s)-.5)/n)*(size-1)).astype(int)
            cell=vb.astype(int)*size*size+si*size+di
            joint=np.bincount(cell,minlength=len(g)).astype(float);assert joint.sum()==n
            designs={'balanced':np.ones(len(g)),
                'vegetation_prevalence_only':np.where(g.vegetation==1,vb.mean(),1-vb.mean())*2,
                'empirical_rank_bin_design':joint}
            for name,ww in designs.items():
                for i,r in g.iterrows():weight_rows.append(dict(levels=levels,background=bg,weighting=name,D_source=r.D_source,S_source=r.S_source,vegetation=r.vegetation,weight=ww[i]))
                for xt in ['raw','rank']:
                    for yt in ['raw','rank']:
                        result=weighted_core(g.D_source.to_numpy(),g.S_source.to_numpy(),g.vegetation.to_numpy(),g.F_B.to_numpy(),ww,xt,yt)
                        model_results.append(dict(levels=levels,background=bg,weighting=name,x_transform=xt,y_transform=yt,**result))
    model=pd.DataFrame(model_results);model.to_csv(OUT/'model_common_estimators.csv',index=False)
    pd.DataFrame(weight_rows).to_csv(OUT/'model_design_weights.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    prior=pd.read_csv(ROOT/'research/results/final_mechanism_20261027/winner_rank_resolution.csv').set_index('levels')
    for levels,g in model[(model.weighting=='balanced')&(model.x_transform=='rank')&(model.y_transform=='rank')].groupby('levels'):
        np.testing.assert_allclose(g[['OS','OV','SV','OSV']].iloc[0],prior.loc[levels,['DS','DV','SV','DSV']],atol=1e-10)
    endpoint=[]
    for levels,g in saved.groupby('levels'):
        ranks=rankdata(g.F_B)
        for name,y in [('log_F_B',np.log(g.F_B)),('F_fraction',g.F_fraction),
                       ('negative_H',-g.audit_H_SF-g.audit_H_DF)]:
            delta=float(np.max(abs(ranks-rankdata(y))))
            endpoint.append(dict(levels=levels,endpoint=name,max_rank_difference_from_F_B=delta))
            assert delta==0.
    pd.DataFrame(endpoint).to_csv(OUT/'endpoint_rank_identity.csv',index=False)
    comparisons=[]
    for r in model[model.levels==21].to_dict('records'):
        for adjustment in ['none','space']:
            subset=macro[(macro.background==r['background'])&(macro.vegetation=='binary')
                &(macro.x_transform==r['x_transform'])&(macro.y_transform==r['y_transform'])
                &(macro.adjustment==adjustment)&(macro['mode']=='pooled')].set_index('term')
            for term in ['OS','OV','SV','OSV']:
                q=subset.loc[term]
                comparisons.append(dict(background=r['background'],weighting=r['weighting'],
                    x_transform=r['x_transform'],y_transform=r['y_transform'],adjustment=adjustment,
                    term=term,model=r[term],macro=q.beta,macro_low=q.low,macro_high=q.high,
                    in_marginal_interval=bool(q.low<=r[term]<=q.high),
                    status='DESCRIPTIVE_COORDINATE_CHECK_NOT_FIT_TEST'))
    pd.DataFrame(comparisons).to_csv(OUT/'matched_coordinate_comparison.csv',index=False)
    receipt=dict(macro_specifications=64,model_specifications=72,bootstrap=999,seed=20261029,
        input_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [SITE,VISITS,MODEL]},
        runtime=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__),
        model_sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest(),original_results_replayed=True,
        model_refit=False,density_calibrated=False,observation_model_calibrated=False,
        explanation='Weighted design transport changes analysis weights only. Suitability ranks are not identified with real densities; source grid parameters are unchanged.')
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(model[(model.levels==21)&(model.x_transform=='rank')][['background','weighting','y_transform','OS','OSV','OS_high_minus_low']].to_string(index=False))


if __name__=='__main__':main()
