"""Audit species contributions to the Fig. 1 strong-call associations.
Usage: python research/scripts/naamp_species_strong_call_sensitivity.py RAW_DIR OUTPUT_DIR
RAW_DIR contains the pinned USGS Counts.csv and Stops.csv (DOI 10.5066/F7G44NG0).
"""
import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from naamp_remote_vegetation_network import standardized_rank
from naamp_vegetation_network_associations import fit
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
PINS = {'Counts.csv':'60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086',
        'Stops.csv':'28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f'}


def read_source(directory, name, columns):
    path = directory / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == PINS[name]
    return pd.read_csv(path, usecols=columns, dtype=str)


def build_outcomes(directory, sites):
    visits = pd.read_csv(ROOT/'research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz')
    visits = visits.loc[visits.site.isin(sites.site) & visits.timeout.eq(0)].reset_index(drop=True)
    stops = read_source(directory,'Stops.csv',['RunID','StopNumber','SiteID'])
    for name, key in [('run','RunID'),('site','SiteID')]:
        stops[name] = stops[key].map({x:hashlib.sha256(x.encode()).hexdigest()[:16] for x in stops[key].dropna().unique()})
    selected = visits[['run','site']].merge(stops,on=['run','site'],validate='one_to_many',how='left')
    assert len(selected)==len(visits)==63180 and selected.StopNumber.notna().all()
    raw = read_source(directory,'Counts.csv',['RunID','StopNumber','Species','CallingIndex'])
    events = selected.reset_index(names='visit').merge(raw,on=['RunID','StopNumber'])
    events = events.loc[events.CallingIndex.isin(['1','2','3'])].copy()
    events['strong'] = events.CallingIndex.isin(['2','3'])
    events = events.groupby(['visit','Species']).strong.max().reset_index()
    labels = events.Species.value_counts().index
    table = events.pivot(index='visit',columns='Species',values='strong').reindex(index=visits.index,columns=labels)
    any_call = table.notna().to_numpy()
    strong = table.eq(True).to_numpy()
    assert np.array_equal(any_call.any(axis=1),visits['any'])
    assert np.array_equal(strong.any(axis=1),visits.strong)
    assert np.array_equal(np.sort(sites.n_visits),np.sort(visits.groupby('site').size()))
    species = [s for s in labels if ' complex' not in s]
    by_strong = sorted(species,key=lambda s:-strong[:,labels.get_loc(s)].sum())
    outcomes = {'all':strong.any(axis=1)}
    for n in [1,3,5,10]:
        for name,order in [('any',species),('strong',by_strong)]:
            keep = ~labels.isin(order[:n])
            outcomes[f'exclude_top{n}_{name}'] = strong[:,keep].any(axis=1)
            if n==5:
                excluded = {word for s in order[:n] for word in [s]}
                keep_complex = [not (s.endswith(' complex') and any(s.split()[0]+' '+ep in excluded for ep in s.split()[1].split('/'))) for s in labels]
                outcomes[f'exclude_top5_{name}_and_ambiguous'] = strong[:,keep & keep_complex].any(axis=1)
    outcomes['only_species_labels'] = strong[:,labels.isin(species)].any(axis=1)
    total = strong.sum(axis=1)
    for i,label in enumerate(labels):
        outcomes['species|'+label]=strong[:,i]
        outcomes['leave_out|'+label]=total>strong[:,i].astype(int)
    counts = pd.DataFrame(outcomes).groupby(visits.site).sum().loc[sites.site]
    frequency = counts.to_numpy()/sites.n_visits.to_numpy()[:,None]
    np.testing.assert_allclose(frequency[:,0],sites.strong_rate)
    summary = pd.DataFrame({'label':labels,'any_visits':any_call.sum(axis=0),'strong_visits':strong.sum(axis=0),
                            'sole_strong_visits':(strong & (total==1)[:,None]).sum(axis=0)})
    for col in ['sites','routes','vegetated_sites']:
        summary[col]=[len(set(sites.loc[(counts['species|'+s].to_numpy()>0) & ((sites.flooded_3000m_mean>0) if col=='vegetated_sites' else True),'route' if col=='routes' else 'site'])) for s in labels]
    site_routes = visits.site.map(sites.set_index('site').route)
    ranges = {label: set(site_routes[any_call[:,labels.get_loc(label)]]) for label in species[:10]}
    return frequency,counts,summary,ranges


def weighted_ranks(codes,weight):
    # Midranks of a sample in which each site occurs weight times; omitted sites have zero weight.
    ranked=[]
    for code in codes:
        mass=np.bincount(code,weights=weight)
        ranks=(mass.cumsum()-.5*mass)[code]
        centered=ranks-weight@ranks/weight.sum()
        sd=np.sqrt(weight@(centered**2)/weight.sum())
        ranked.append(centered/sd if sd>0 else np.full(len(code),np.nan))
    return np.column_stack(ranked)


def run(raw,out):
    out.mkdir(exist_ok=True,parents=True)
    base=ROOT/'research/results/naamp_remote_vegetation_20261026'
    sites=pd.read_csv(base/'primary_site_landscape_context.csv.gz')
    freq,counts,summary,ranges=build_outcomes(raw,sites)
    summary.to_csv(out/'species_support.csv',index=False)
    backgrounds=['uniform','target_group']
    cov=sites[[f'mean_suitability_{guild}_{bg}' for bg in backgrounds for guild in ['Odonata','pond_breeding_Caudata']]+['flooded_3000m_mean']].to_numpy()
    local = []
    for label, recorded_routes in ranges.items():
        keep = sites.route.isin(recorded_routes)
        y = freq[keep,counts.columns.get_loc('species|'+label)]
        for bg_index, bg_name in enumerate(backgrounds):
            o,s = cov[keep,2*bg_index:2*bg_index+2].T
            v = standardized_rank(cov[keep,4])
            for within in [False, True]:
                coefficients = fit(o,s,v,y,sites.loc[keep,'route'].to_numpy(),within)
                local.append([label,bg_name,within,len(recorded_routes),int(keep.sum()),coefficients[3],coefficients[4]])
    pd.DataFrame(local,columns=['label','background','within_route','routes','sites','OS','OV']).to_csv(out/'detected_route_sensitivity.csv',index=False)
    codes=[np.unique(col,return_inverse=True)[1] for col in np.column_stack([cov,freq]).T]
    routes,names=pd.factorize(sites.route,sort=True)
    groups=np.bincount(routes)
    rng=np.random.default_rng(20261031)
    repetitions=1000
    draws=np.stack([np.bincount(rng.integers(len(names),size=len(names)),minlength=len(names)) for _ in range(repetitions)])
    samples=np.empty((repetitions+1,2,2,2,len(counts.columns)))
    for b,w in enumerate(np.vstack([np.ones((1,len(names))),draws])):
        weights=w[routes]
        ranked=weighted_ranks(codes,weights)
        y=ranked[:,5:]
        for bg in range(2):
            o,s=ranked[:,2*bg:2*bg+2].T
            v=ranked[:,4]
            x=np.column_stack([np.ones(len(o)),o,s,v,o*s,o*v,s*v,o*s*v])
            for within in range(2):
                if within:
                    means=np.column_stack([np.bincount(routes,weights=col)/groups for col in x.T])
                    x=x-means[routes];x[:,0]=1
                # Within-route design is centered, so response centering does not change slopes.
                weighted=x.T*weights
                samples[b,bg,within]=((np.linalg.solve(weighted@x,weighted))[[4,5]])@y
    records=[]
    for bg,background in enumerate(backgrounds):
        for within in range(2):
            for j,term in enumerate(['OS','OV']):
                vals=samples[:,bg,within,j];diff=vals-vals[:,[0]]
                for k,label in enumerate(counts):
                    boot=vals[1:,k];valid=np.isfinite(boot)
                    ci=np.quantile(boot[valid],[.025,.975]) if valid.any() else [np.nan]*2
                    paired=np.quantile(diff[1:,k][valid],[.025,.975]) if valid.any() else [np.nan]*2
                    records.append([background,within,term,label,int(counts[label].sum()),vals[0,k],*ci,int(valid.sum()),diff[0,k],*paired])
    result=pd.DataFrame(records,columns=['background','within_route','term','outcome','strong_visits','beta','low','high','valid_draws','delta_vs_all','delta_low','delta_high'])
    ref=pd.read_csv(base/'network_rank_coefficients.csv')
    for r in result[result.outcome=='all'].itertuples():
        term={'OS':'Odonata:Caudata','OV':'Odonata:vegetation'}[r.term]
        a=ref[(ref.background==r.background)&(ref.within_route==bool(r.within_route))&(ref.group=='pond_breeding_Caudata')&(ref.vegetation_metric=='mean')&(ref.term==term)].iloc[0]
        np.testing.assert_allclose([r.beta,r.low,r.high],[a.beta,a.low,a.high],atol=1e-9)
    result.to_csv(out/'interaction_results.csv',index=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw',type=Path);parser.add_argument('out',type=Path)
    args=parser.parse_args()
    with threadpool_limits(limits=1):
        run(args.raw,args.out)

