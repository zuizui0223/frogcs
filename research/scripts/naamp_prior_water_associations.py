"""Pairwise ecological contrasts with prior water, vegetation, niches and history.

Descriptive estimands, no out-of-sample prediction-gain gate. Preserve every
fixed pair and mark unavailable conditional-water-frequency values explicitly.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from naamp_site_use_associations import load_features
from naamp_network_fixed_pairs import bootstrap

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/results/naamp_prior_water_20261026'
WATER=['mean_water_frequency','water_positive_area_fraction','frequency_on_water_positive_pixels']


def main():
    base=ROOT/'research/results/naamp_three_guild_occurrence/full_naamp_history'
    pairs=pd.read_csv(base/'matched_strong_silent_history.csv')
    visits=pd.read_csv(base/'naamp_completed_site_surveys.csv.gz')
    years=visits[['run','year']].drop_duplicates()
    assert years.run.is_unique
    pairs=pairs.merge(years,on='run',validate='many_to_one');pairs['water_year']=pairs.year-1
    components=pd.read_csv(ROOT/'research/results/naamp_network_fixed_pairs_20261026/route_components.csv')
    pairs=pairs.merge(components,left_on='route',right_on='original_route',validate='many_to_one')
    assert len(pairs)==4040 and pairs.route_component.nunique()==388
    water=pd.read_csv(OUT/'prior_year_site_water_context.csv.gz')
    features,_=load_features()
    veg=pd.read_csv(ROOT/'research/results/naamp_remote_vegetation_20261026/site_landscape_context.csv.gz')
    features=features.merge(veg[['site','flooded_3000m_mean','flooded_3000m_sd','herbaceous_3000m_mean']],on='site',validate='one_to_one')
    selected=[x for x in features if x.startswith('mean_suitability_')]+['flooded_3000m_mean','flooded_3000m_sd','herbaceous_3000m_mean']
    features=features[['site']+selected]
    for side in ['chosen','silent']:
        renamed=features.rename(columns={c:side+'_'+c for c in selected})
        pairs=pairs.merge(renamed,left_on=side+'_site',right_on='site',validate='many_to_one').drop(columns='site')
        for radius in [1000,3000]:
            sub=water[water.radius_m==radius][['site','water_year']+WATER+['valid_fraction','complete']]
            names={c:side+'_'+c+'_'+str(radius)+'m' for c in sub if c not in ['site','water_year']}
            pairs=pairs.merge(sub.rename(columns=names),left_on=[side+'_site','water_year'],right_on=['site','water_year'],how='left',validate='many_to_one').drop(columns='site')
    assert (pairs.year-pairs.water_year==1).all()
    pairs.to_csv(OUT/'fixed_pairs_joint_ecological_context.csv.gz',index=False)
    rows=[];coverage=[]
    for radius in [1000,3000]:
        for feature in WATER:
            col=feature+'_'+str(radius)+'m';a=pairs['chosen_'+col];b=pairs['silent_'+col]
            ok=a.notna()&b.notna();q=pairs.loc[ok].copy();q['difference']=a[ok]-b[ok]
            point,lo,hi=bootstrap(q.groupby('route_component').difference.mean(),20261101)
            rows.append(dict(feature=feature,radius_m=radius,pairs=len(q),routes=q.route_component.nunique(),
                             mean_chosen=float(pd.DataFrame({'route':pairs.loc[ok,'route_component'],'v':a[ok]}).groupby('route').v.mean().mean()),
                             mean_silent=float(pd.DataFrame({'route':pairs.loc[ok,'route_component'],'v':b[ok]}).groupby('route').v.mean().mean()),
                             difference=point,low=lo,high=hi))
            coverage.append(dict(feature=feature,radius_m=radius,valid_pairs=int(ok.sum()),missing_pairs=int((~ok).sum()),
                                 chosen_missing=int(a.isna().sum()),silent_missing=int(b.isna().sum())))
    pd.DataFrame(rows).to_csv(OUT/'matched_water_differences.csv',index=False)
    pd.DataFrame(coverage).to_csv(OUT/'matched_water_coverage.csv',index=False)
    # Symmetric pair-average prior frequency defines strata, independent of side.
    f='frequency_on_water_positive_pixels_3000m'
    mask=pairs['chosen_'+f].notna()&pairs['silent_'+f].notna()
    eligible=pairs.loc[mask].copy();mean=(eligible['chosen_'+f]+eligible['silent_'+f])/2
    cuts=mean.quantile([1/3,2/3]).to_numpy();eligible['water_stratum']=np.searchsorted(cuts,mean,side='left')
    strata=[]
    comparison=selected+['prior']
    for label,sub in eligible.groupby('water_stratum'):
        for feature in comparison:
            diff=sub['chosen_'+feature]-sub['silent_'+feature]
            point,lo,hi=bootstrap(pd.DataFrame({'route':sub.route_component,'diff':diff}).groupby('route')['diff'].mean(),20261102)
            strata.append(dict(water_stratum=int(label),feature=feature,pairs=len(sub),routes=sub.route_component.nunique(),difference=point,low=lo,high=hi))
    pd.DataFrame(strata).to_csv(OUT/'water_stratified_joint_differences.csv',index=False)
    meta=dict(fixed_pairs=len(pairs),route_components=pairs.route_component.nunique(),all_preceding_year_verified=True,
              water_stratum_cuts=cuts.tolist(),water_stratum_definition='Symmetric pair mean prior frequency among water-positive pixels; only both-side defined pairs',
              water_strata_pairs=len(eligible),water_strata_pair_counts=eligible.water_stratum.value_counts().sort_index().to_dict(),
              uncertainty='2000 route-component bootstraps; fitted niches fixed; no multiple-testing correction',
              joint_table='Saved all prior-water, remote vegetation, three-guild suitability and strict history fields for the same fixed pairs',
              interpretation='Joint descriptive table and conditional contrasts, not multivariable causal effects or measured plant use')
    (OUT/'association_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(pd.DataFrame(rows).to_string(index=False));print(json.dumps(meta,indent=2))


if __name__=='__main__':main()
