from pathlib import Path
import argparse
import hashlib
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from threadpoolctl import threadpool_limits
from naamp_species_strong_call_sensitivity import ROOT, read_source

SPECIES = ['Pseudacris crucifer', 'Acris gryllus']
SEED = 20261109

def get_panel(raw, sites, species=SPECIES):
    visits = pd.read_csv(ROOT / 'research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz')
    visits = visits[visits.site.isin(sites.index) & visits.timeout.eq(0)].copy()
    stops = read_source(raw, 'Stops.csv', ['RunID','StopNumber','SiteID'])
    for col, source in [('run','RunID'),('site','SiteID')]:
        stops[col] = stops[source].map({v:hashlib.sha256(v.encode()).hexdigest()[:16] for v in stops[source].dropna().unique()})
    visits = visits.merge(stops,on=['site','run'],validate='one_to_many')
    assert len(visits)==63180 and not visits.duplicated(['site','run']).any()
    raw_calls = read_source(raw,'Counts.csv',['RunID','StopNumber','Species','CallingIndex'])
    calls = raw_calls[raw_calls.Species.isin(species) & raw_calls.CallingIndex.isin(['1','2','3'])].copy()
    calls['index'] = calls.CallingIndex.astype(int)
    maxima = calls.groupby(['RunID','StopNumber','Species'])['index'].max().unstack()
    visits = visits.join(maxima,on=['RunID','StopNumber']); visits[species]=visits[species].fillna(0)
    for sp in species:
        from_names=visits.source_taxa.fillna('').str.split('|',regex=False).map(lambda names:sp in names)
        assert np.array_equal(from_names,visits[sp]>0)
    return visits

def ranked(a):
    r=rankdata(a,axis=0)
    return (r-r.mean(axis=0))/r.std(axis=0)

def coefficients(frame):
    outcomes=ranked(frame[SPECIES].to_numpy())
    route=pd.factorize(frame.route)[0];counts=np.bincount(route)
    result=[]
    for bg in ['uniform','target_group']:
        o,s,v=ranked(frame[['mean_suitability_Odonata_'+bg,'mean_suitability_pond_breeding_Caudata_'+bg,'flooded_3000m_mean']].to_numpy()).T
        x=np.column_stack([o,s,v,o*s,o*v,s*v,o*s*v])
        for within in [False,True]:
            if within:
                x=x-np.column_stack([np.bincount(route,weights=c)/counts for c in x.T])[route]
            design=np.column_stack([np.ones(len(x)),x])
            beta,_,rank,_=np.linalg.lstsq(design,outcomes,rcond=None)
            terms=beta[[4,5]] if rank==8 else np.full((2,2),np.nan)
            result.append(np.column_stack([terms,terms[:,1]-terms[:,0]]))
    return np.array(result)

def analyse(name, responses, sites, results):
    frame=sites.join(responses,how='inner')
    groups=list(frame.groupby('route',sort=True).indices.values())
    rng=np.random.default_rng(SEED)
    estimates=[coefficients(frame)]
    for _ in range(1000):
        sample=np.concatenate([groups[k] for k in rng.integers(len(groups),size=len(groups))])
        estimates.append(coefficients(frame.iloc[sample]))
    draws=np.array(estimates)
    for k,(bg,within) in enumerate([(b,w) for b in ['uniform','target_group'] for w in [False,True]]):
        for t,term in enumerate(['OS','OV']):
            for j,target in enumerate(SPECIES+['A minus P']):
                boot=draws[1:,k,t,j];boot=boot[np.isfinite(boot)]
                low,high=np.quantile(boot,[.025,.975])
                results.append([name,len(frame),len(groups),bg,within,term,target,draws[0,k,t,j],low,high,len(boot)])

def main(raw,out):
    out.mkdir(parents=True,exist_ok=True)
    sites=pd.read_csv(ROOT/'research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz').set_index('site')
    visits=get_panel(raw,sites);both=(visits.groupby('site')[SPECIES].max()>0).all(axis=1)
    q=visits[visits.site.isin(both[both].index)].copy()
    # Each completed visit supplies both species' denominators, including silent visits.
    strong=q[SPECIES].ge(2)
    yearboth=q.groupby(['site','year'])[SPECIES].transform('max').gt(0).all(axis=1)
    results=[]
    analyse('both_ever',strong.groupby(q.site).mean(),sites,results)
    # Estimate the calendar expectation for each visit from the OTHER routes' visits
    # in that month. The resulting bootstrap conditions on those calendar expectations.
    route = q.site.map(sites.route)
    month_n = q.groupby('month').site.transform('size')
    route_month_n = q.groupby([route,q.month]).site.transform('size')
    if not (month_n>route_month_n).all():
        raise ValueError('Missing out-of-route month support')
    predicted = (strong.groupby(q.month).transform('sum')-strong.groupby([route,q.month]).transform('sum')).div(month_n-route_month_n,axis=0)
    analyse('both_ever_month_adjusted', (strong.astype(float)-predicted).groupby(q.site).mean(),sites,results)

    analyse('both_same_year',strong[yearboth].groupby(q.loc[yearboth,'site']).mean(),sites,results)
    # Common calendar weighting: one early and one late mean per site-year, then equal years per site.
    season=q.month.map({3:'early',4:'early',5:'late',6:'late'})
    bands=strong.groupby([q.site,q.year,season.rename('band')]).mean().unstack('band').dropna()
    balanced=pd.DataFrame({sp:bands[sp].mean(axis=1).groupby(level='site').mean() for sp in SPECIES})
    analyse('matched_MarApr_MayJun',balanced,sites,results)
    pd.DataFrame(results,columns=['cohort','sites','routes','background','within_route','term','target','beta','low','high','valid']).to_csv(out/'paired_coefficients.csv',index=False)
    monthly=[]
    for month,g in q.groupby('month'):
        for sp in SPECIES: monthly.append([month,sp,len(g),int(g[sp].gt(0).sum()),int(g[sp].ge(2).sum())])
    pd.DataFrame(monthly,columns=['month','species','visits','any','strong']).to_csv(out/'monthly.csv',index=False)
    timing=[]
    for threshold in [1,2]:
        dates=pd.concat({sp:q[q[sp]>=threshold].groupby(['site','year']).doy.median() for sp in SPECIES},axis=1).dropna()
        # Median observed calling day per species per site-year. Then equal weight per site.
        differences=(dates.iloc[:,1]-dates.iloc[:,0]);by_site=differences.groupby(level='site').mean()
        by_route=sites.loc[by_site.index,'route']; groups=list(by_site.groupby(by_route).indices.values());v=by_site.to_numpy()
        rng=np.random.default_rng(SEED)
        boot=[v[np.concatenate([groups[j] for j in rng.integers(len(groups),size=len(groups))])].mean() for _ in range(1000)]
        timing.append([threshold,len(dates),len(v),len(groups),dates.iloc[:,0].median(),dates.iloc[:,1].median(),int((differences>0).sum()),int((differences==0).sum()),int((differences<0).sum()),v.mean(),*np.quantile(boot,[.025,.975])])
    pd.DataFrame(timing,columns=['minimum_index','paired_site_years','sites','routes','P_median_doy','A_median_doy','A_later','same','A_earlier','mean_paired_days_equal_site','low','high']).to_csv(out/'timing.csv',index=False)
    print('Shared visits, sites, routes, years, positive vegetation sites:',len(q),q.site.nunique(),sites.loc[both[both].index].route.nunique(),q.year.nunique(),sites.loc[both[both].index].flooded_3000m_mean.gt(0).sum())
    print('Same-year visits and calendar-balanced site-years:',yearboth.sum(),len(bands))
    print('Both heard on same visit:',q[SPECIES].gt(0).all(axis=1).sum())
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('raw',type=Path);parser.add_argument('out',type=Path);args=parser.parse_args()
    with threadpool_limits(1):main(args.raw,args.out)
