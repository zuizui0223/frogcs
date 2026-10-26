"""Characterize repeated calling-site use with existing data, not predictive gains."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import argparse
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT=Path(__file__).resolve().parents[2]
POND={'Notophthalmus viridescens','Ambystoma maculatum','Ambystoma tigrinum','Ambystoma laterale','Ambystoma mavortium'}


def canonicalize_routes(d):
    parent={r:r for r in d.route.unique()}
    def root(r):
        while parent[r]!=r:
            parent[r]=parent[parent[r]];r=parent[r]
        return r
    for routes in d.groupby('site').route.unique():
        for r in routes[1:]:
            a,b=root(routes[0]),root(r)
            parent[max(a,b)]=min(a,b)
    mapping={r:root(r) for r in parent}
    result=d.copy();result['route']=result.route.map(mapping)
    return result,mapping


def aggregate_sites(d):
    if d.groupby('site').route.nunique().max()>1:
        raise ValueError('A physical site maps to multiple routes')
    a=d.groupby('site').agg(route=('route','first'),n_visits=('strong','size'),n_years=('year','nunique'),
                           n_seasons=('season','nunique'),strong_rate=('strong','mean'),any_rate=('any','mean'),
                           mean_air=('air','mean'),mean_noise=('noise','mean'))
    annual=d.groupby(['site','year']).strong.agg(['mean','max'])
    a['strong_year_fraction']=annual['max'].groupby('site').mean()
    a['year_equal_strong_rate']=annual['mean'].groupby('site').mean()
    a['season_equal_strong_rate']=d.groupby(['site','season']).strong.mean().groupby('site').mean()
    return a.reset_index()


def centered_by_route(x,g):
    x=np.asarray(x,float)
    if x.ndim==1: x=x[:,None]
    counts=np.bincount(g)
    sums=np.zeros((len(counts),x.shape[1]))
    np.add.at(sums,g,x)
    means=np.divide(sums,counts[:,None],out=np.zeros_like(sums),where=counts[:,None]>0)
    return x-means[g]


def cross_correlations(x,y):
    x=x-x.mean(axis=0); y=y-y.mean(axis=0)
    denom=np.sqrt((x*x).sum(axis=0)[:,None]*(y*y).sum(axis=0)[None,:])
    return np.divide(x.T@y,denom,out=np.full(denom.shape,np.nan),where=denom>0)


def rank_matrices(x,y,g):
    rx=rankdata(x,axis=0); ry=rankdata(y,axis=0)
    return np.stack([cross_correlations(rx,ry),
                     cross_correlations(centered_by_route(rx,g),centered_by_route(ry,g))])


def rank_association(x,y,routes,within):
    x=np.asarray(x,float); y=np.asarray(y,float); routes=np.asarray(routes)
    ok=np.isfinite(x)&np.isfinite(y)
    if ok.sum()<3:return None
    g=pd.factorize(routes[ok],sort=True)[0]
    value=rank_matrices(x[ok,None],y[ok,None],g)[int(within),0,0]
    return float(value) if np.isfinite(value) else None


def load_features():
    source=ROOT/'research/results/interaction_species_sdm_20261026'
    env=pd.read_csv(source/'naamp_site_environment.csv.gz')
    stacks=pd.read_csv(source/'ssdm/naamp_group_potential_richness.csv.gz')
    stacks=stacks[stacks.omission==.1].copy()
    stacks['feature']='richness_'+stacks['group']+'_'+stacks.background
    wide=stacks.pivot(index='site',columns='feature',values='potential_richness')
    pred=pd.read_csv(source/'naamp_species_suitability.csv.gz',dtype={'species_key':str})
    means=pred.groupby(['site','guild','background']).suitability_percentile.mean().reset_index()
    means['feature']='mean_suitability_'+means.guild+'_'+means.background
    wide=wide.join(means.pivot(index='site',columns='feature',values='suitability_percentile'))
    pond=pred[pred.species.isin(POND)].groupby(['site','background']).suitability_percentile.mean().reset_index()
    pond['feature']='mean_suitability_pond_breeding_Caudata_'+pond.background
    wide=wide.join(pond.pivot(index='site',columns='feature',values='suitability_percentile'))
    env=env.set_index('site').drop(columns=['route'])
    if not env.index.is_unique:raise ValueError('Duplicate environmental site')
    wide=wide.join(env)
    return wide.reset_index(),pred


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--bootstraps',type=int,default=1000)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz'
    original=pd.read_csv(source)
    if original.duplicated(['site','run']).any():raise ValueError('Duplicate completed site/run')
    d=original[original.timeout==0].copy()
    multi_route_sites=int(d.groupby('site').route.nunique().gt(1).sum())
    same_day_rows=int(d.duplicated(['site','date','season'],keep=False).sum())
    d,route_map=canonicalize_routes(d)
    pd.DataFrame([dict(original_route=k,route_cluster=v) for k,v in route_map.items()]).to_csv(a.out/'route_identity_components.csv',index=False)
    sites=aggregate_sites(d)
    sites['day_equal_strong_rate']=sites.site.map(d.groupby(['site','date']).strong.mean().groupby('site').mean())
    features,pred=load_features()
    sites=sites.merge(features,on='site',how='left',validate='one_to_one',indicator=True)
    sites['use_class']=np.where(sites.strong_rate>=.75,'high',np.where(sites.strong_rate<=.25,'low','intermediate'))
    sites.to_csv(a.out/'all_site_characteristics.csv.gz',index=False)
    cohort=sites[(sites.n_visits>=6)&(sites.n_years>=3)].copy()
    feature_cols=sorted(c for c in sites if c.startswith(('richness_','mean_suitability_')))+['flooded','water']
    outcomes=['strong_rate','strong_year_fraction']
    complete=cohort.dropna(subset=feature_cols+outcomes).copy()
    complete.to_csv(a.out/'primary_site_characteristics.csv.gz',index=False)
    x=complete[feature_cols].to_numpy();y=complete[outcomes].to_numpy()
    g=pd.factorize(complete.route,sort=True)[0]
    point=rank_matrices(x,y,g)
    rng=np.random.default_rng(20261026)
    blocks=[np.flatnonzero(g==k) for k in range(g.max()+1)]
    draws=[]
    for i in range(a.bootstraps):
        idx=np.concatenate([blocks[k] for k in rng.integers(0,len(blocks),len(blocks))])
        draws.append(rank_matrices(x[idx],y[idx],g[idx]))
        if (i+1)%250==0:print('route bootstrap',i+1,flush=True)
    draws=np.asarray(draws)
    lo,hi=np.nanquantile(draws,[.025,.975],axis=0)
    records=[]
    for mode in (0,1):
        for j,feature in enumerate(feature_cols):
            varying=complete.groupby('route')[feature].nunique().gt(1).sum()
            for k,outcome in enumerate(outcomes):
                records.append(dict(feature=feature,outcome=outcome,scale='within_route_ranks' if mode else 'whole_sample_spearman',
                                    correlation=point[mode,j,k],low=lo[mode,j,k],high=hi[mode,j,k],sites=len(complete),
                                    routes=len(blocks),routes_with_predictor_variation=int(varying),
                                    valid_bootstraps=int(np.isfinite(draws[:,mode,j,k]).sum())))
    pd.DataFrame(records).to_csv(a.out/'primary_correlations.csv',index=False)
    secondary=[]
    context=['bio1','bio4','bio12','bio15','lat','lon','n_visits','n_years','mean_air','mean_noise']
    for feature in context:
        for outcome in outcomes:
            for within in (False,True):
                secondary.append(dict(feature=feature,outcome=outcome,within_route=within,
                                      correlation=rank_association(complete[feature],complete[outcome],complete.route,within)))
    pd.DataFrame(secondary).to_csv(a.out/'geography_effort_context.csv',index=False)
    sensitivities=[]
    for label,mask,outcome in [
        ('3_visits_2_years',(sites.n_visits>=3)&(sites.n_years>=2),'strong_rate'),
        ('10_visits_5_years',(sites.n_visits>=10)&(sites.n_years>=5),'strong_rate'),
        ('equal_year_weight',(sites.n_visits>=6)&(sites.n_years>=3),'year_equal_strong_rate'),
        ('equal_day_weight',(sites.n_visits>=6)&(sites.n_years>=3),'day_equal_strong_rate'),
        ('all_3_seasons_equal_weight',(sites.n_visits>=6)&(sites.n_years>=3)&(sites.n_seasons==3),'season_equal_strong_rate'),
        ('any_call',(sites.n_visits>=6)&(sites.n_years>=3),'any_rate')]:
        sub=sites.loc[mask].dropna(subset=feature_cols+[outcome])
        for feature in feature_cols:
            for within in (False,True):
                sensitivities.append(dict(sensitivity=label,feature=feature,within_route=within,sites=len(sub),routes=sub.route.nunique(),
                                          correlation=rank_association(sub[feature],sub[outcome],sub.route,within)))
    pd.DataFrame(sensitivities).to_csv(a.out/'sensitivity_correlations.csv',index=False)
    species_rows=[]
    for (sid,bg),group in pred.groupby(['species_key','background']):
        q=complete[['site','route']+outcomes].merge(group[['site','suitability_percentile']],on='site',validate='one_to_one')
        for outcome in outcomes:
            for within in (False,True):
                species_rows.append(dict(species_key=sid,species=group.species.iloc[0],guild=group.guild.iloc[0],background=bg,
                                         outcome=outcome,within_route=within,sites=len(q),
                                         correlation=rank_association(q.suitability_percentile,q[outcome],q.route,within)))
    pd.DataFrame(species_rows).to_csv(a.out/'exploratory_species_correlations.csv',index=False)
    descriptions=[]
    for label in ('low','intermediate','high'):
        sub=complete[complete.use_class==label]
        for feature in feature_cols+context+outcomes:
            v=sub[feature].dropna()
            descriptions.append(dict(use_class=label,feature=feature,sites=len(v),routes=sub.route.nunique(),
                                     median=v.median(),q25=v.quantile(.25),q75=v.quantile(.75)))
    pd.DataFrame(descriptions).to_csv(a.out/'use_class_characteristics.csv',index=False)
    meta=dict(input_rows=len(original),valid_completed_rows=len(d),all_sites=len(sites),primary_before_join=len(cohort),
              primary_complete_sites=len(complete),primary_routes=len(blocks),
              valid_year_range=[int(d.year.min()),int(d.year.max())],
              primary_use_classes=complete.use_class.value_counts().to_dict(),
              missing_feature_join_sites=int((sites['_merge']!='both').sum()),
              physical_sites_with_multiple_route_labels=multi_route_sites,
              route_labels_before=len(route_map),route_components_after=len(set(route_map.values())),
              rows_sharing_site_date_season=same_day_rows,
              bootstrap_replicates=a.bootstraps,source_survey_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              estimand='Association of calling-use frequency and recurring-year use with saved environmental/SDM characteristics',
              limitations=['Acoustic locations are not delineated ponds; calling is not breeding success',
                           'Rank associations are descriptive, not causal preference or competition',
                           'Bootstrap does not propagate SDM fitting uncertainty; no multiplicity correction',
                           'Existing SDM pool contains 28 modeled interaction-associated species, not total regional diversity'])
    (a.out/'observed_results.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
    print(json.dumps(meta,indent=2))


if __name__=='__main__':main()
