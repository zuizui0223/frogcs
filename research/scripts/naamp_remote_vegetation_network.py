"""Landscape vegetation as a modifier of Odonata/Caudata/calling associations.

Main: 3-km mean flooded consensus and spatial SD, analyzed separately.
Sensitivity: same 1-km metrics. Both SDM backgrounds and Caudata groups;
whole-area and route-adjusted estimates. No predictor/outcome selection.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from naamp_vegetation_network_associations import fit,TERMS
from naamp_site_use_associations import rank_association

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/results/naamp_remote_vegetation_20261026'


def standardized_rank(values):
    r=rankdata(values)
    return (r-r.mean())/r.std() if r.std()>0 else np.zeros(len(r))


def main():
    d=pd.read_csv(OUT/'primary_site_landscape_context.csv.gz')
    y=d.strong_rate.to_numpy();routes=d.route.to_numpy()
    blocks=[np.flatnonzero(routes==r) for r in sorted(set(routes))]
    rng=np.random.default_rng(20261031)
    indices=[np.concatenate([blocks[k] for k in rng.integers(0,len(blocks),len(blocks))]) for _ in range(1000)]
    rows=[];sensitivity=[];context=[]
    for col in [c for c in d if c.endswith(('_mean','_sd')) and 'm_' in c]:
        for within in [False,True]:
            context.append(dict(feature=col,within_route=within,rho=rank_association(d[col],y,routes,within)))
    for background in ['uniform','target_group']:
        x=d['mean_suitability_Odonata_'+background].to_numpy()
        for group in ['Caudata','pond_breeding_Caudata']:
            s=d['mean_suitability_'+group+'_'+background].to_numpy()
            for measure in ['mean','sd']:
                raw=d['flooded_3000m_'+measure].to_numpy();v=standardized_rank(raw)
                assert np.isfinite(raw).all()
                for within in [False,True]:
                    point=fit(x,s,v,y,routes,within)
                    boot=np.array([fit(x[i],s[i],standardized_rank(raw[i]),y[i],routes[i],within) for i in indices])
                    lo,hi=np.nanquantile(boot,[.025,.975],axis=0)
                    for j,term in enumerate(TERMS):
                        rows.append(dict(background=background,group=group,vegetation_metric=measure,
                                         radius_m=3000,within_route=within,term=term,beta=point[j],low=lo[j],high=hi[j],
                                         valid_bootstraps=int(np.isfinite(boot[:,j]).sum())))
                    small=fit(x,s,standardized_rank(d['flooded_1000m_'+measure]),y,routes,within)
                    for j,term in enumerate(TERMS):
                        sensitivity.append(dict(background=background,group=group,vegetation_metric=measure,radius_m=1000,
                                                within_route=within,term=term,beta=small[j]))
            print('completed',background,group,flush=True)
    frame=pd.DataFrame(rows);frame.to_csv(OUT/'network_rank_coefficients.csv',index=False)
    pd.DataFrame(sensitivity).to_csv(OUT/'one_km_sensitivity_coefficients.csv',index=False)
    pd.DataFrame(context).to_csv(OUT/'marginal_context_correlations.csv',index=False)
    meta=dict(sites=len(d),route_components=len(blocks),bootstrap=1000,seed=20261031,
              main_radius_m=3000,sensitivity_radius_m=1000,all_lower_order_terms=True,
              vegetation_metrics='Separate models for mean and spatial SD of flooded consensus; not independently identified structural effects',
              scaling='Odonata, Caudata, vegetation and outcome ranked and standardized within each bootstrap draw',
              scope='Landscape modification of associations; does not demonstrate refuge use, predation or emergence substrate',
              sensitivity_uncertainty='1-km coefficients are point sensitivities only',
              uncertainty='Conditional on fitted species scores; no multiple-testing adjustment')
    (OUT/'network_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(frame.query("term=='Odonata:Caudata:vegetation'").to_string(index=False))


if __name__=='__main__':main()
