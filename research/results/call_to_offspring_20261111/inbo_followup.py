"""Reproduce from INBO publisher DwC archives. Outputs contain aggregate results only."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import numpy as np
import pandas as pd
from scipy.stats import rankdata

root=Path(__file__).resolve().parent
def load(k,digest):
    p=root/(k+".zip")
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
    with ZipFile(p) as z:
        def table(n):
            return pd.read_csv(z.open(n+".txt"),sep="\t")
        o=table("occurrence")
        e=table("event")
        d=o.merge(e[["id","locationID","locality","eventDate","samplingProtocol"]],on="id",validate="many_to_one")
        assert len(d)==len(o)
        if k=="larva":
            m=table("measurementorfacts")
            effort=m[m.measurementType=="sampling effort type"][["id","measurementValue"]].drop_duplicates()
            d=d.merge(effort,on="id",how="left",validate="many_to_one")
    d["date"]=pd.to_datetime(d.eventDate)
    d["year"]=d.date.dt.year
    return d
a=load("adult","686c5a7aacc8f49e41a0642ecaa9efd8c3564304b0a4d4b027f3df2debec69fd")
l=load("larva","c2cc960122ea398545edb661318160cd2b5b66a75a73dba8f7a3f61bd9c4f920")
assert pd.concat([a,l]).groupby("locationID").locality.nunique().max()==1
def valid(d):
    return d[(d.individualCount.gt(0)&d.occurrenceStatus.eq("present"))|(d.individualCount.eq(0)&d.occurrenceStatus.eq("absent"))]
a=valid(a[a.lifeStage=="adult"])
l=valid(l)
newts=l[l.scientificName.str.match(r"^(Triturus|Lissotriton|Ichthyosaura) ") & l.lifeStage.eq("larva") & l.individualCount.gt(0)]
ac=a.groupby(["scientificName","locationID","year"])
def paired():
    rows=[]
    for (sp,site,yr,stage),g in l[l.lifeStage.isin(["larva","metamorph"])].groupby(["scientificName","locationID","year","lifeStage"]):
        key=(sp,site,yr)
        if key not in ac.groups:continue
        calls=ac.get_group(key).groupby("date").individualCount.median()
        for day,visit in g.groupby("date",sort=True):
            prior=calls[calls.index<day]
            if prior.empty:continue
            # Explicit land counts for metamorphs, exclude explicitly incompatible effort in primary sample.
            land=visit.measurementValue.isin(["sweep for larvae, metamorphs counted on land","alleen metamorfen op land geteld"])
            incompatible=visit.measurementValue.eq("sweep for larvae only") if stage=="metamorph" else visit.measurementValue.eq("alleen metamorfen op land geteld")
            visit=visit.loc[~incompatible]
            if visit.empty:continue
            rows.append(dict(sp=sp,site=site,year=yr,stage=stage,call=prior.mean(),positive_frequency=(prior>0).mean(),n_prior=len(prior),day=day.dayofyear,lag=(day-prior.index.max()).days,
                young=visit.individualCount.median(),single=len(visit)==1,land=bool(land.loc[visit.index].all()),newt=visit.id.isin(newts.id).any()))
            break
    return pd.DataFrame(rows)
def corr(x,y):
    if min(len(np.unique(x)),len(np.unique(y)))<2:return np.nan
    return np.corrcoef(rankdata(x),rankdata(y))[0,1]
def estimate(label,g,x="call"):
    y=g.young.to_numpy(); xx=g[x].to_numpy()
    pos=np.flatnonzero(y>0)
    row=dict(group=label,n=len(g),sites=g.site.nunique(),year_min=g.year.min(),year_max=g.year.max(),positive=len(pos),prior_days_median=g.n_prior.median(),rho=corr(xx,y))
    if len(g) and np.isfinite(row["rho"]):
        rng=np.random.default_rng(1452);groups=list(g.reset_index(drop=True).groupby("site").indices.values());r=[]
        for _ in range(1500):
            idx=np.concatenate([groups[i] for i in rng.integers(0,len(groups),len(groups))]);r.append(corr(xx[idx],y[idx]))
        row["lo"],row["hi"]=np.nanquantile(r,[.025,.975])
    return row
if __name__=="__main__":
    p=paired(); print(p.groupby(["sp","stage"]).size())
    out=[]
    for stage,g in p[p.sp=="Hyla arborea"].groupby("stage"):
        for label,z in [("all",g),("single_count_record",g[g.single]),("positive_chorus",g[g.call>0]),("both_detected",g[(g.call>0)&(g.young>0)]),("confirmed_newt",g[g.newt]),("land_count_documented",g[g.land])]:
            if len(z):out.append(estimate(stage+" "+label,z))
        repeated=g[g.n_prior>=2]
        if len(repeated):out.append(estimate(stage+" fraction_prior_days_calling",repeated,"positive_frequency"))
        # Compare across ponds after pooling repeated years with equal weight for each pond.
        bysite=g.groupby("site",as_index=False).agg(dict(call="mean",young="mean",year="min",n_prior="median"))
        out.append(estimate(stage+" pond_means",bysite))
    res=pd.DataFrame(out);print(res.round(3).to_string(index=False));res.to_csv(root/"inbo_summary.csv",index=False)
