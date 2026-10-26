"""Does mapped vegetation modify three-guild associations? Exploratory only.

Saved primary cohort; both backgrounds; all/pond Caudata; no variable selection.
Flooded > 0 is a coarse landcover contrast, not measured refuge architecture.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from naamp_site_use_associations import centered_by_route

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/results/naamp_odonata_caudata_associations_20261026'
TERMS=['Odonata','Caudata','vegetation','Odonata:Caudata','Odonata:vegetation','Caudata:vegetation','Odonata:Caudata:vegetation']


def fit(x,s,v,y,routes,within):
    x=rankdata(x);s=rankdata(s);y=rankdata(y)
    x=(x-x.mean())/x.std();s=(s-s.mean())/s.std();y=(y-y.mean())/y.std()
    design=np.column_stack([x,s,v,x*s,x*v,s*v,x*s*v])
    if within:
        g=pd.factorize(routes)[0]
        design=centered_by_route(design,g);y=centered_by_route(y,g)[:,0]
    design=np.column_stack([np.ones(len(y)),design])
    coef,_,rank,_=np.linalg.lstsq(design,y,rcond=None)
    if rank<8:return np.full(7,np.nan)
    return coef[1:]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(ROOT/'research/results/naamp_site_use_associations_20261026/primary_site_characteristics.csv.gz')
    v=d.flooded.gt(0).to_numpy(dtype=float);y=d.strong_rate.to_numpy();r=d.route.to_numpy()
    blocks=[np.flatnonzero(r==z) for z in sorted(set(r))]
    rng=np.random.default_rng(20261028)
    draws=[np.concatenate([blocks[k] for k in rng.integers(0,len(blocks),len(blocks))]) for _ in range(1000)]
    rows=[]
    for bg in ['uniform','target_group']:
        for group in ['Caudata','pond_breeding_Caudata']:
            x=d['mean_suitability_Odonata_'+bg].to_numpy();s=d['mean_suitability_'+group+'_'+bg].to_numpy()
            for within in [False,True]:
                point=fit(x,s,v,y,r,within)
                boot=np.array([fit(x[i],s[i],v[i],y[i],r[i],within) for i in draws])
                lo,hi=np.nanquantile(boot,[.025,.975],axis=0)
                for k,t in enumerate(TERMS):
                    rows.append(dict(background=bg,group=group,within_route=within,term=t,beta=point[k],
                                     low=lo[k],high=hi[k],valid_bootstraps=int(np.isfinite(boot[:,k]).sum())))
    result=pd.DataFrame(rows);result.to_csv(OUT/'vegetation_network_rank_interactions.csv',index=False)
    coverage=d.groupby(d.flooded.gt(0)).agg(sites=('site','size'),routes=('route','nunique'),mean_strong_rate=('strong_rate','mean'))
    coverage.to_csv(OUT/'vegetation_coverage.csv')
    metadata=dict(vegetation_indicator='EarthEnv flooded vegetation cover > 0',positive_sites=int(v.sum()),
                  positive_routes=int(d.loc[v>0,'route'].nunique()),zero_sites=int((v==0).sum()),
                  varying_routes=int(d.assign(v=v).groupby('route').v.nunique().gt(1).sum()),
                  seed=20261028,bootstrap=1000,
                  model='Rank-standardized Y ~ O + S + V + O:S + O:V + S:V + O:S:V; V is 0/1',
                  scope='Association modification, not measured predation, plant use or a calibrated interaction network',
                  limits='Only 46 mapped-positive sites; coarse landcover cannot distinguish refuge, spawning substrate or emergence substrate. No multiplicity adjustment or SDM uncertainty propagation.')
    (OUT/'vegetation_network_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(result[result.term=='Odonata:Caudata:vegetation'].to_string(index=False))


if __name__=='__main__':main()
