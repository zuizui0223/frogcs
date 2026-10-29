"""Internal robustness to flexible habitat structure, not external validation."""
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import GroupKFold
from nee_context_robustness import ROOT,SURVEY,ENV,load,zrank,block_stats,centered_by_route
from confront_mechanism_sites import fit_setup
from common_scale_comparison import features

OUT=ROOT/'research/results/nee_crossfit_20261029'
TERMS=['O','S','V','OS','OV','SV','OSV']


def folds_for(groups):
    folds=np.full(len(groups),-1)
    for i,(_,test) in enumerate(GroupKFold(n_splits=5).split(np.zeros(len(groups)),groups=groups)):
        folds[test]=i
    assert (folds>=0).all()
    assert pd.DataFrame({'g':groups,'fold':folds}).groupby('g').fold.nunique().max()==1
    return folds


def cross_residuals(c,targets,folds,kind):
    pred=np.zeros_like(targets)
    for fold in sorted(set(folds)):
        test=folds==fold;train=~test
        if kind=='linear':
            z=np.column_stack([np.ones(len(c)),c])
            pred[test]=z[test]@np.linalg.lstsq(z[train],targets[train],rcond=1e-10)[0]
        else:
            leaf=int(kind.split('_')[-1])
            model=ExtraTreesRegressor(n_estimators=300,min_samples_leaf=leaf,max_features=1.,random_state=20261029,n_jobs=2)
            model.fit(c[train],targets[train]);pred[test]=model.predict(c[test])
    return targets-pred,pred


def fit_residual(x,y,ids,draws):
    z=np.column_stack([x,np.ones(len(x))])
    beta=np.linalg.lstsq(z,y,rcond=1e-10)[0][:7]
    xx,xy=block_stats(z,y,ids);aa=np.einsum('bg,gij->bij',draws,xx);bb=draws@xy
    boot=[]
    for a,b in zip(aa,bb):
        coef,_,rank,_=np.linalg.lstsq(a,b,rcond=1e-12)
        if rank==8:boot.append(coef[:7])
    return beta,np.quantile(boot,[.025,.975],axis=0),len(boot),float(np.linalg.cond(z))


def main():
    OUT.mkdir(parents=True,exist_ok=True);d=load();n=len(d)
    ids=pd.factorize(d.spatial_block,sort=True)[0];k=ids.max()+1;folds=folds_for(ids)
    d[['site','route','spatial_block']].assign(fold=folds).to_csv(OUT/'fold_assignment.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    ll=zrank(d[['lat','lon']].to_numpy());c=np.column_stack([zrank(d[SURVEY].to_numpy()),zrank(d[ENV].to_numpy()),ll,ll[:,0]**2,ll[:,0]*ll[:,1],ll[:,1]**2])
    y=zrank(d.strong_rate.to_numpy());v=zrank(d.flooded_3000m_mean.to_numpy())
    route=pd.factorize(d.route)[0]
    draws=np.random.default_rng(20261029).multinomial(k,np.full(k,1/k),size=999)
    rows=[];diags=[];residuals=[]
    old=pd.read_csv(ROOT/'research/results/scale_comparison_20261029/macro_common_estimators.csv')
    for bg in ['uniform','target_group']:
        x=features(zrank(d['mean_suitability_Odonata_'+bg]),zrank(d['mean_suitability_pond_breeding_Caudata_'+bg]),v)
        for kind in ['full_linear','linear','trees_20','trees_60']:
            if kind!='full_linear':
                targets=np.column_stack([y,x]);res,pred=cross_residuals(c,targets,folds,kind)
                for j,name in enumerate(['Y']+TERMS):
                    diags.append(dict(background=bg,nuisance=kind,term=name,oof_mse=np.mean(res[:,j]**2),residual_variance=np.var(res[:,j]),reference_variance=np.var(targets[:,j])))
                residuals.append(pd.DataFrame(res,columns=['Y']+TERMS).assign(site=d.site.to_numpy(),background=bg,nuisance=kind))
            for mode in ['pooled','within']:
                if kind=='full_linear':
                    z,yy,_=fit_setup(x,c,y,d.route,mode)
                    beta=np.linalg.lstsq(z,yy,rcond=1e-10)[0][:7]
                    # Return original full-model resampling, not a residual-only bootstrap.
                    xx,xy=block_stats(z,yy,ids);boots=[]
                    for aa,bb in zip(np.einsum('bg,gij->bij',draws,xx),draws@xy):
                        b,_,rank,_=np.linalg.lstsq(aa,bb,rcond=1e-12)
                        if rank==z.shape[1]:boots.append(b[:7])
                    bounds=np.quantile(boots,[.025,.975],axis=0);valid=len(boots);condition=float(np.linalg.cond(z))
                    previous=old[(old.background==bg)&(old.vegetation=='continuous')&(old.x_transform=='rank')&(old.y_transform=='rank')&(old.adjustment=='space')&(old['mode']==mode)].set_index('term')
                    for i,t in enumerate(TERMS[3:],3):np.testing.assert_allclose([beta[i],bounds[0,i],bounds[1,i]],previous.loc[t,['beta','low','high']].to_numpy(float),atol=1e-8)
                else:
                    rx=res[:,1:];ry=res[:,0]
                    if mode=='within':rx=centered_by_route(rx,route);ry=centered_by_route(ry,route)[:,0]
                    beta,bounds,valid,condition=fit_residual(rx,ry,ids,draws)
                for i,t in enumerate(TERMS):
                    rows.append(dict(background=bg,nuisance=kind,mode=mode,term=t,beta=beta[i],low=bounds[0,i],high=bounds[1,i],valid_bootstraps=valid,condition=condition,interval_scope='full_linear_design' if kind=='full_linear' else 'conditional_on_fixed_crossfitted_nuisance'))
                print('Done',bg,kind,mode,flush=True)
    pd.DataFrame(rows).to_csv(OUT/'coefficients.csv',index=False)
    pd.DataFrame(diags).to_csv(OUT/'nuisance_diagnostics.csv',index=False)
    pd.concat(residuals).to_csv(OUT/'oof_residuals.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    (OUT/'receipt.json').write_text(json.dumps(dict(sites=n,spatial_blocks=int(k),folds=5,bootstrap=999,seed=20261029,global_rank_reference='existing fixed cohort; internal sensitivity, not deployment prediction',independent_replication=False,nuisance_refit_inside_bootstrap=False,full_linear_replayed=True),indent=2)+'\n')


if __name__=='__main__':main()
