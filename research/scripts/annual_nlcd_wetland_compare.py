"""Survey-weighted wetland cover; compare herbaceous and woody moderation in one model."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from threadpoolctl import threadpool_limits
from annual_nlcd_wetland_extract import cohort
import sdm_flooded_omission as sdm

def zrank(values):
    x=rankdata(values)
    return (x-x.mean())/x.std()

def coefficients(o,s,h,w,y,route,within):
    x=np.column_stack([o,s,h,w,o*s,o*h,o*w,s*h,s*w,o*s*h,o*s*w])
    if within:
        g=np.unique(route,return_inverse=True)[1]
        n=np.bincount(g)
        x=x-np.column_stack([np.bincount(g,weights=col)/n for col in x.T])[g]
        y=y-(np.bincount(g,weights=y)/n)[g]
    x=np.column_stack([np.ones(len(y)),x])
    b,_,rk,_=np.linalg.lstsq(x,y,rcond=None)
    assert rk==x.shape[1]
    # At mean ranked salamander suitability the difference in O-slopes is b6-b7.
    h25,h50,h75=np.quantile(h,[.25,.5,.75])
    w25,w50,w75=np.quantile(w,[.25,.5,.75])
    slopes=[b[1]+b[6]*H+b[7]*W for H,W in [(h25,w50),(h75,w50),(h50,w25),(h50,w75)]]
    return [b[6],b[7],b[6]-b[7],b[1],*slopes]

def analyze(directory,out):
    yearly=pd.concat([pd.read_csv(directory/f"{y}.csv") for y in range(2001,2016)],ignore_index=True)
    keys=["site","year","visits","strong"]
    pd.testing.assert_frame_equal(yearly[keys].sort_values(keys).reset_index(drop=True),cohort()[keys].sort_values(keys).reset_index(drop=True),check_dtype=False)
    assert (yearly.valid_cells>0).all() and (yearly.herb_cells+yearly.woody_cells<=yearly.valid_cells).all()
    yearly["coverage"]=yearly.valid_cells/yearly.circle_cells
    yearly["herb"]=yearly.herb_cells/yearly.valid_cells
    yearly["woody"]=yearly.woody_cells/yearly.valid_cells
    for col in ["woody","herb"]:
        yearly[col+"_weighted"]=yearly[col]*yearly.visits
    groups=yearly.groupby("site")
    ordered=groups.sum().loc[sdm.site.site]
    h=(ordered.herb_weighted/ordered.visits).to_numpy()
    w=(ordered.woody_weighted/ordered.visits).to_numpy()
    out.mkdir(exist_ok=True,parents=True)
    yearly.to_csv(out/"survey_year_wetlands.csv.gz",index=False)
    pd.DataFrame(dict(site=ordered.index,herb_fraction=h,woody_fraction=w,minimum_coverage=groups.coverage.min().loc[ordered.index].values)).to_csv(out/"site_wetlands.csv.gz",index=False)
    records=[]
    for bg,ms in sdm.models.groupby("background"):
        guilds=[np.mean([sdm.refit(m,sdm.base) for m in ms[ms.guild.eq(g)].itertuples()],axis=0) for g in ["Odonata","Caudata"]]
        samples=[]
        for i in sdm.draws:
            o,s=[zrank(v[i]) for v in guilds]
            y=zrank(sdm.y[i])
            sample=[]
            for H,W in [((h[i]-h[i].mean())*10,(w[i]-w[i].mean())*10),(zrank(h[i]),zrank(w[i]))]:
                sample.append([coefficients(o,s,H,W,y,sdm.routes[i],within) for within in [False,True]])
            samples.append(sample)
        arr=np.array(samples)
        for k,scale in enumerate(["10_percentage_points","standardized_rank"]):
            for j,within in enumerate([False,True]):
                for t,term in enumerate(["odonate_x_herb","odonate_x_woody","herb_minus_woody","odonate_at_mean_context","slope_herb_q25_woody_median","slope_herb_q75_woody_median","slope_woody_q25_herb_median","slope_woody_q75_herb_median"]):
                    v=arr[:,k,j,t];lo,hi=np.quantile(v[1:],[.025,.975])
                    records.append(dict(background=bg,scale=scale,within_route=within,term=term,estimate=v[0],low=lo,high=hi))
    estimates=pd.DataFrame(records);estimates.to_csv(out/"coefficients.csv",index=False)
    print(estimates.query("background=='uniform'").round(4).to_string(index=False))
    print("Minimum valid coverage",yearly.coverage.min(),"site-years below 90%",sum(yearly.coverage<.9))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("directory",type=Path);p.add_argument("out",type=Path)
    a=p.parse_args()
    with threadpool_limits(limits=1):analyze(a.directory,a.out)
