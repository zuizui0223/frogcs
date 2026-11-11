"""Species-level tests of woody versus herbaceous moderation in NAAMP."""
import argparse
from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from threadpoolctl import threadpool_limits
from naamp_species_strong_call_sensitivity import build_outcomes
import sdm_flooded_omission as sdm

FOREST=["Lithobates sylvaticus","Pseudacris crucifer","Hyla versicolor"]
COMPARISON=["Lithobates clamitans","Lithobates catesbeianus","Lithobates palustris"]
def rank_columns(x):
    r=rankdata(x,axis=0)
    sd=r.std(axis=0)
    return (r-r.mean(axis=0))/np.where(sd==0,np.nan,sd)

def estimates(x,y,route,scale):
    o,s=rank_columns(x[:,:2]).T
    h,w=(rank_columns(x[:,2:]) if scale=="rank" else (x[:,2:]-x[:,2:].mean(0))*10).T
    m=np.column_stack([o,s,h,w,o*s,o*h,o*w,s*h,s*w,o*s*h,o*s*w])
    y=rank_columns(y)
    good=np.isfinite(y).all(0)
    idx=np.unique(route,return_inverse=True)[1]
    n=np.bincount(idx)
    def demean(v):
        # Equivalent to fixed route effects; vectorized for multiple species.
        sums=np.zeros((len(n),v.shape[1]))
        np.add.at(sums,idx,v)
        return v-(sums/n[:,None])[idx]
    out=np.full((2,3,y.shape[1]),np.nan)
    for j,(a,b) in enumerate([(m,y[:,good]),(demean(m),demean(y[:,good]))]):
        a=np.column_stack([np.ones(len(o)),a])
        coef,_,rk,_=np.linalg.lstsq(a,b,rcond=None)
        if rk==a.shape[1]:
            out[j][:,good]=np.stack([coef[6],coef[7],coef[7]-coef[6]])
    return out

def run(raw,out):
    out.mkdir(exist_ok=True,parents=True)
    freq,counts,support,_=build_outcomes(raw,sdm.site)
    names=[s for s in support.label if " complex" not in s]
    assert len(names)==44
    y=freq[:,[counts.columns.get_loc("species|"+s) for s in names]]
    panel=FOREST+COMPARISON
    common=set.intersection(*[set(sdm.routes[y[:,names.index(s)]>0]) for s in panel])
    wet=pd.read_csv(sdm.ROOT/"annual_nlcd_wetlands_20261111/site_wetlands.csv.gz").set_index("site").loc[sdm.site.site]
    ms=sdm.models[sdm.models.background.eq("uniform")]
    x=np.column_stack([*[np.mean([sdm.refit(m,sdm.base) for m in ms[ms.guild.eq(g)].itertuples()],0) for g in ["Odonata","Caudata"]],wet.herb_fraction,wet.woody_fraction])
    outputs=[]; stats=[]; permutations=[]
    for domain,keep in [("all",np.ones(len(x),bool)),("shared_routes",np.isin(sdm.routes,list(common)))]:
        xx,yy,rr=x[keep],y[keep],sdm.routes[keep]
        parts=[np.flatnonzero(rr==r) for r in sorted(set(rr))]
        rng=np.random.default_rng(20261031)
        inds=[np.arange(len(rr))]+[np.concatenate([parts[k] for k in rng.integers(len(parts),size=len(parts))]) for b in range(1000)]
        print(domain,len(rr),len(parts),flush=True)
        for scale in ["rank","10pp"]:
            arr=np.stack([estimates(xx[i],yy[i],rr[i],scale) for i in inds])
            for within in [0,1]:
                def record(v):
                    b=v[1:];valid=b[np.isfinite(b)]
                    ci=np.quantile(valid,[.025,.975]) if len(valid) else [np.nan,np.nan]
                    return [v[0],*ci,len(valid)]
                for k,term in enumerate(["herbaceous","woody","woody_minus_herbaceous"]):
                    vals=arr[:,within,k]
                    for j,s in enumerate(names):
                        outputs.append([domain,len(rr),len(parts),scale,within,term,s,int((yy[:,j]>0).sum()),*record(vals[:,j])])
                    if term=="woody_minus_herbaceous":
                        a=vals[0,[names.index(s) for s in panel]]
                        observed=a[:3].mean()-a[3:].mean()
                        # Descriptive exact species-label check; species are not a random taxonomic sample.
                        alternatives=[]
                        for chosen in combinations(range(6),3):
                            mask=np.isin(np.arange(6),chosen)
                            alternatives.append(a[mask].mean()-a[~mask].mean())
                        permutations.append(dict(domain=domain,scale=scale,within_route=within,
                            difference=observed,assignments=20,lower_tail=np.mean(np.array(alternatives)<=observed+1e-12)))
                    def group(items):return vals[:,[names.index(s) for s in items]].mean(axis=1)
                    for tag,f,c in [("primary",FOREST,COMPARISON),("within_Lithobates",[FOREST[0]],COMPARISON),
                        ("exclude_spring_peeper",FOREST[:1]+FOREST[2:],COMPARISON),("add_grassland_leopard",FOREST,COMPARISON+["Lithobates pipiens"])]:
                        a,b=group(f),group(c)
                        for label,v in [("forest",a),("comparator",b),("forest_minus_comparator",a-b)]:
                            stats.append([domain,len(rr),len(parts),scale,within,term,tag,label,*record(v)])
    fields=["domain","sites","routes","scale","within_route","term"]
    metrics=["estimate","low","high","valid_draws"]
    pd.DataFrame(outputs,columns=fields+["species","strong_sites"]+metrics).to_csv(out/"species.csv",index=False)
    pd.DataFrame(stats,columns=fields+["panel","contrast"]+metrics).to_csv(out/"groups.csv",index=False)
    pd.DataFrame(permutations).to_csv(out/"species_label_check.csv",index=False)
    support["panel_status"]=["forest" if s in FOREST else "comparator" if s in COMPARISON else "grassland sensitivity" if s=="Lithobates pipiens" else "ambiguous taxon" if " complex" in s else "outside matched literature panel" for s in support.label]
    support.to_csv(out/"taxon_accounting.csv",index=False)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("raw",type=Path);p.add_argument("out",type=Path);a=p.parse_args()
    with threadpool_limits(limits=1):run(a.raw,a.out)
