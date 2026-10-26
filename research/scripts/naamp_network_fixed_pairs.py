"""Describe fixed strong/silent pairs conditional on Caudata niche context.

Reuse the same 4,040 pairs, source-frozen matching, and the predictor cutpoints
from the 4,248-site exploratory analysis. No rematching or prediction scoring.
"""
from pathlib import Path
import ast
import hashlib
import json
import numpy as np
import pandas as pd
from naamp_site_use_associations import load_features, canonicalize_routes

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/results/naamp_network_fixed_pairs_20261026'


def bootstrap(values,seed):
    values=np.asarray(values,float)
    if len(values)<2:return float(np.mean(values)),np.nan,np.nan
    rng=np.random.default_rng(seed)
    means=np.array([rng.choice(values,len(values),replace=True).mean() for _ in range(2000)])
    lo,hi=np.quantile(means,[.025,.975])
    return float(values.mean()),float(lo),float(hi)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=ROOT/'research/results/naamp_three_guild_occurrence/full_naamp_history/matched_strong_silent_history.csv'
    pairs=pd.read_csv(source)
    # Independent chronological replay, without trusting saved prior columns.
    visits=pd.read_csv(source.parent/'naamp_completed_site_surveys.csv.gz').drop(columns=['prior','prior_n'])
    annual=visits.groupby(['site','season','year']).strong.agg(['sum','count']).sort_index()
    annual['prior_sum']=annual.groupby(level=[0,1])['sum'].cumsum()-annual['sum']
    annual['prior_n']=annual.groupby(level=[0,1])['count'].cumsum()-annual['count']
    annual['prior']=annual.prior_sum/annual.prior_n
    replay=visits.merge(annual[['prior','prior_n']],left_on=['site','season','year'],right_index=True,validate='many_to_one')
    checks={}
    for side in ['chosen','silent']:
        q=pairs.merge(replay,left_on=['run',side+'_site'],right_on=['run','site'],validate='many_to_one',suffixes=('','_survey'))
        checks[side+'_max_prior_error']=float(abs(q[side+'_prior']-q.prior).max())
        checks[side+'_minimum_prior_n']=int(q.prior_n.min())
        assert checks[side+'_max_prior_error']<1e-14 and q.prior_n.min()>=2
    checks.update(pairs=len(pairs),method='Independent site-season annual cumulative sums excluding the entire current year')
    (OUT/'history_independent_replay.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    original_routes=int(pairs.route.nunique())
    endpoints=pd.concat([pairs[['route','chosen_site']].rename(columns={'chosen_site':'site'}),
                         pairs[['route','silent_site']].rename(columns={'silent_site':'site'})])
    shared_sites=int(endpoints.groupby('site').route.nunique().gt(1).sum())
    _,route_map=canonicalize_routes(endpoints)
    pairs['original_route']=pairs.route
    pairs['route']=pairs.route.map(route_map)
    pd.DataFrame([dict(original_route=k,route_component=v) for k,v in route_map.items()]).to_csv(OUT/'route_components.csv',index=False)
    features,_=load_features();features=features.set_index('site')
    assert len(pairs)==4040 and len(features.index.unique())==len(features)
    assert pairs[['chosen_site','silent_site']].isin(features.index).all().all()
    chosen=features.reindex(pairs.chosen_site).reset_index(drop=True)
    silent=features.reindex(pairs.silent_site).reset_index(drop=True)
    config=pd.read_csv(ROOT/'research/results/naamp_odonata_caudata_associations_20261026/predictor_config.csv')
    rows=[];contrasts=[];membership=[]
    for c in config.itertuples():
        x='mean_suitability_Odonata_'+c.background;s='mean_suitability_'+c.group+'_'+c.background
        cuts=ast.literal_eval(c.caudata_cuts)
        a=np.searchsorted(cuts,chosen[s],side='left');b=np.searchsorted(cuts,silent[s],side='left')
        strata=np.where(a!=b,'mixed',np.array(['low','middle','high'])[a])
        q=pd.DataFrame(dict(route=pairs.route,stratum=strata,
                            odonata_difference=chosen[x]-silent[x],
                            caudata_difference=chosen[s]-silent[s],
                            history_difference=pairs.history_difference,
                            flooded_difference=chosen.flooded-silent.flooded,
                            water_difference=chosen.water-silent.water))
        member=pairs[['run','route','chosen_site','silent_site']].copy()
        member['background']=c.background;member['group']=c.group;member['stratum']=strata
        membership.append(member)
        for label in ['all','low','middle','high','mixed']:
            sub=q if label=='all' else q[q.stratum==label]
            for var in q.columns[2:]:
                means=sub.groupby('route')[var].mean()
                point,lo,hi=bootstrap(means,20261029)
                rows.append(dict(background=c.background,group=c.group,stratum=label,feature=var,
                                 pairs=len(sub),routes=len(means),mean=point,low=lo,high=hi))
        # Same sampled route components for both strata, retaining covariance.
        routes=np.array(sorted(q.route.unique()));rng=np.random.default_rng(20261030)
        estimates=[]
        wide=q.groupby(['route','stratum']).odonata_difference.mean().unstack().reindex(routes)
        for _ in range(2000):
            z=wide.iloc[rng.integers(0,len(routes),len(routes))]
            estimates.append(z['high'].mean()-z['low'].mean())
        lo,hi=np.nanquantile(estimates,[.025,.975])
        contrasts.append(dict(background=c.background,group=c.group,
                              high_minus_low=wide['high'].mean()-wide['low'].mean(),low=lo,high=hi,
                              interpretation='Difference between stratum-specific route-weighted chosen-minus-silent Odonata score differences'))
    pd.DataFrame(rows).to_csv(OUT/'matched_stratum_differences.csv',index=False)
    pd.DataFrame(contrasts).to_csv(OUT/'high_low_difference_contrasts.csv',index=False)
    pd.concat(membership,ignore_index=True).to_csv(OUT/'fixed_pair_strata.csv.gz',index=False)
    meta=dict(pair_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),pairs=len(pairs),routes=pairs.route.nunique(),
              original_routes=original_routes,shared_physical_sites=shared_sites,
              rematched=False,bootstrap=2000,weighting='Each route equal weight within each stratum',
              strata='Both endpoints low, middle or high Caudata suitability; cross-boundary pairs retained as mixed',
              cuts='Fixed from prior 4248-site predictor-only tertiles',
              limits='Matched habitat restricts local niche variation. No causal preference or predation claim. No SDM uncertainty propagation or multiple-testing adjustment.')
    (OUT/'observed_results.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(pd.DataFrame(rows).query("feature=='odonata_difference'").to_string(index=False))


if __name__=='__main__':main()
