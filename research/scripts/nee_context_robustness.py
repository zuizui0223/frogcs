"""Fixed-design G1 context audit. Descriptive associations, not causal effects."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.linalg import qr
from scipy.spatial import cKDTree
from scipy.stats import rankdata
from naamp_site_use_associations import centered_by_route
from naamp_vegetation_network_associations import TERMS

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/results/nee_context_20261029'
SITE=ROOT/'research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz'
VISITS=ROOT/'research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz'
B=999
SEED=20261029
SURVEY=['n_visits','n_years','mean_air','mean_noise','season_2','season_3','season_4','mean_doy']
ENV=['bio1','bio4','bio12','bio15','water_3000m_mean','herbaceous_3000m_mean']

def zrank(a):
    r=rankdata(a,axis=0);sd=r.std(axis=0)
    return np.divide(r-r.mean(axis=0),sd,out=np.zeros_like(r),where=sd>0)

def group_mean(a,g):
    a=np.asarray(a);s=np.zeros((g.max()+1,)+a.shape[1:]);np.add.at(s,g,a)
    return s/np.bincount(g).reshape((-1,)+(1,)*(a.ndim-1))

def prepare(x,c,y,groups,mode):
    g=pd.factorize(groups,sort=True)[0]
    if mode=='within':
        x=centered_by_route(x,g);c=centered_by_route(c,g);y=centered_by_route(y,g)[:,0]
    elif mode=='between':
        x=group_mean(x,g);c=group_mean(c,g);y=group_mean(y,g);g=np.arange(len(y))
    elif mode!='pooled':raise ValueError(mode)
    nuisance=np.column_stack([np.ones(len(y)),c]) if mode!='within' else c
    if nuisance.shape[1]:
        _,r,p=qr(nuisance,mode='economic',pivoting=True)
        rank=int(np.sum(np.abs(np.diag(r))>max(1.,np.linalg.norm(nuisance))*1e-10))
        nuisance=nuisance[:,p[:rank]]
    resid=x-nuisance@np.linalg.lstsq(nuisance,x,rcond=1e-10)[0] if nuisance.shape[1] else x
    sv=np.linalg.svd(resid,compute_uv=False)
    if len(sv)<7 or sv[-1]<max(1.,sv[0])*1e-9:raise ValueError('Unidentifiable focal interactions after adjustment')
    design=np.column_stack([x,nuisance])
    return design,y,g,dict(rank=int(np.linalg.matrix_rank(design)),columns=design.shape[1],condition=float(np.linalg.cond(design)),focal_residual_condition=float(sv[0]/sv[-1]))

def block_stats(z,y,g):
    k=g.max()+1;p=z.shape[1];xx=np.zeros((k,p,p));xy=np.zeros((k,p))
    np.add.at(xx,g,z[:,:,None]*z[:,None,:]);np.add.at(xy,g,z*y[:,None])
    return xx,xy

def block_fit(z,y,g):
    b=np.linalg.lstsq(z,y,rcond=1e-10)[0]
    return b[:7],y-z@b

def bootstrap_fit(z,y,g,weights):
    xx,xy=block_stats(z,y,g);a=np.einsum('bg,gij->bij',weights,xx);b=weights@xy
    result=np.full((len(weights),7),np.nan)
    for i in range(len(weights)):
        coef,_,rank,_=np.linalg.lstsq(a[i],b[i],rcond=1e-12)
        if rank==z.shape[1]:result[i]=coef[:7]
    return result

def bh(p):
    p=np.asarray(p,float);q=np.full(len(p),np.nan);ok=np.flatnonzero(np.isfinite(p));order=ok[np.argsort(p[ok])]
    q[order]=np.minimum(1,np.minimum.accumulate((p[order]*len(order)/np.arange(1,len(order)+1))[::-1])[::-1])
    return q

def moran(residual,groups,coords):
    g=pd.factorize(groups,sort=True)[0];e=group_mean(residual,g);xy=group_mean(coords,g)
    # Fixed equirectangular approximation, km, for the geographic diagnostic.
    lat,lon=xy.T;xy=np.column_stack([lon*np.cos(np.deg2rad(lat.mean()))*111.,lat*111.])
    nn=cKDTree(xy).query(xy,k=9)[1][:,1:]
    def stat(a):
        a=a-a.mean();den=a@a
        return float(np.mean(a[:,None]*a[nn])*len(a)/den) if den>0 else np.nan
    value=stat(e);rng=np.random.default_rng(SEED);null=np.array([stat(rng.permutation(e)) for _ in range(B)])
    return value,float((1+(np.abs(null-null.mean())>=abs(value-null.mean())).sum())/(B+1))

def load():
    d=pd.read_csv(SITE);assert len(d)==4248 and d.site.is_unique
    v=pd.read_csv(VISITS);v=v[(v.timeout==0)&v.site.isin(d.site)]
    assert not v.duplicated(['run','site']).any()
    n=v.groupby('site').size();np.testing.assert_array_equal(d.site.map(n),d.n_visits)
    assert set(v.season)<= {1,2,3,4}
    for season in [2,3,4]:d['season_'+str(season)]=d.site.map(v.assign(p=v.season==season).groupby('site').p.mean())
    d['mean_doy']=d.site.map(v.groupby('site').doy.mean())
    assert np.isfinite(d[SURVEY+ENV+['lat','lon']].to_numpy()).all()
    centroid=d.groupby('route')[['lat','lon']].mean()
    centroid['region']=np.where(centroid.lat>=38,'N','S')+np.where(centroid.lon>=-82,'E','W')
    centroid['spatial_block']=(np.floor(centroid.lat/2).astype(int).astype(str)+'_'+np.floor(centroid.lon/2).astype(int).astype(str))
    d['region']=d.route.map(centroid.region);d['spatial_block']=d.route.map(centroid.spatial_block)
    return d

def main():
    OUT.mkdir(exist_ok=True,parents=True);d=load()
    d[['site','route','region','spatial_block']+SURVEY].to_csv(OUT/'cohort_and_survey_controls.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    coverage=d.groupby('region').agg(sites=('site','size'),routes=('route','nunique'),vegetated_sites=('flooded_3000m_mean',lambda x:int((x>0).sum())))
    coverage['vegetated_routes']=d[d.flooded_3000m_mean>0].groupby('region').route.nunique()
    coverage.to_csv(OUT/'geographic_coverage.csv')
    obs=zrank(d[SURVEY].to_numpy());env=zrank(d[ENV].to_numpy());ll=zrank(d[['lat','lon']].to_numpy());space=np.column_stack([ll,ll[:,0]**2,ll[:,0]*ll[:,1],ll[:,1]**2])
    covs={'none':np.empty((len(d),0)),'survey':obs,'environment':np.column_stack([obs,env]),'space':np.column_stack([obs,env,space])}
    rows=[];diag=[];spatial=[]
    tasks=[]
    for outcome in ['strong_rate','season_equal_strong_rate']:
        for mode in ['pooled','within','between']:
            for adjustment in covs:tasks.append((outcome,mode,adjustment,'all','route'))
    for region in ['NE','NW','SE','SW']:
        for subset in [region,'without_'+region]:
            for mode in ['pooled','within']:tasks.append(('strong_rate',mode,'space',subset,'route'))
    for mode in ['pooled','within']:tasks.append(('strong_rate',mode,'space','all','spatial_block'))
    for bg in ['uniform','target_group']:
        o=zrank(d['mean_suitability_Odonata_'+bg]);s=zrank(d['mean_suitability_pond_breeding_Caudata_'+bg]);v=zrank(d.flooded_3000m_mean)
        x=np.column_stack([o,s,v,o*s,o*v,s*v,o*s*v])
        for outcome,mode,adjustment,subset,cluster in tasks:
            mask=np.ones(len(d),bool) if subset=='all' else (d.region!=subset[8:]).to_numpy() if subset.startswith('without_') else (d.region==subset).to_numpy()
            sub=d[mask];meta=dict(background=bg,outcome=outcome,mode=mode,adjustment=adjustment,subset=subset,bootstrap_cluster=cluster,sites=len(sub),routes=sub.route.nunique())
            y=zrank(d[outcome].to_numpy())[mask]
            if len(sub)<200 or sub.route.nunique()<20:
                diag.append({**meta,'status':'INSUFFICIENT_GEOGRAPHIC_COVERAGE'});continue
            try:z,yy,g,info=prepare(x[mask],covs[adjustment][mask],y,sub.route,mode)
            except ValueError as error:
                diag.append({**meta,'status':str(error)});continue
            cluster_ids=pd.factorize(sub[cluster],sort=True)[0] if mode!='between' else g
            k=cluster_ids.max()+1;rng=np.random.default_rng(SEED)
            weights=rng.multinomial(k,np.full(k,1/k),size=B)
            point,resid=block_fit(z,yy,g);boot=bootstrap_fit(z,yy,cluster_ids,weights)
            valid=np.isfinite(boot).all(axis=1);lo,hi=np.nanquantile(boot,[.025,.975],axis=0)
            for j,term in enumerate(TERMS):
                tail=(1+(np.abs(boot[valid,j]-point[j])>=abs(point[j])).sum())/(1+valid.sum()) if valid.sum()>=800 else np.nan
                rows.append({**meta,'term':term,'beta':point[j],'low':lo[j],'high':hi[j],'p_centered_bootstrap':tail,'valid_bootstraps':int(valid.sum()),'inference_eligible':bool(valid.sum()>=800)})
            diag.append({**meta,**info,'clusters':k,'status':'OK' if valid.sum()>=800 else 'LOW_BOOTSTRAP_SUPPORT','valid_bootstraps':int(valid.sum())})
            if outcome=='strong_rate' and subset=='all' and mode=='pooled' and cluster=='route':
                stat,p=moran(resid,sub.route,sub[['lat','lon']].to_numpy());spatial.append({**meta,'moran_I':stat,'permutation_p':p})
            print(bg,outcome,mode,adjustment,subset,cluster,'valid',int(valid.sum()),flush=True)
    result=pd.DataFrame(rows);focal=result.term.str.contains(':');result['q_bh']=np.nan;result.loc[focal,'q_bh']=bh(result.loc[focal,'p_centered_bootstrap'])
    result.to_csv(OUT/'coefficients.csv',index=False);pd.DataFrame(diag).to_csv(OUT/'support_diagnostics.csv',index=False);pd.DataFrame(spatial).to_csv(OUT/'residual_spatial_diagnostics.csv',index=False)
    # Original point estimates must match exactly for the unadjusted main estimand.
    original=pd.read_csv(SITE.parent/'network_rank_coefficients.csv');original=original[(original.group=='pond_breeding_Caudata')&(original.vegetation_metric=='mean')&(original.radius_m==3000)]
    for mode,within in [('pooled',False),('within',True)]:
        got=result[(result.outcome=='strong_rate')&(result.subset=='all')&(result.adjustment=='none')&(result['mode']==mode)&(result.bootstrap_cluster=='route')]
        a=got.set_index(['background','term']).beta.sort_index();b=original[original.within_route==within].set_index(['background','term']).beta.sort_index()
        np.testing.assert_allclose(a,b,atol=1e-10,rtol=1e-10)
    receipt=dict(seed=SEED,bootstrap=B,reference_cohort=4248,models=len(diag),focal_tests=int(focal.sum()),source_commit='5e2f0a87c639df373fa2700b29403d2ab417a1cc',inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [SITE,VISITS]],point_replay=True,limits=['Fixed-cohort ranks; bootstrap does not refit SDMs','Geographic sensitivity is not independent validation','Survey controls do not estimate detection probability','BH applies to the new focal interaction family only','Climate/space adjustment does not identify predation','Between-route products are averages of site products, not products of route means'])
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
