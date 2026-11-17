"""First strictly subsequent USGS survey by site and year, using inside-site calls."""
from pathlib import Path
import hashlib
import pandas as pd
import numpy as np
import rasterio
import statsmodels.formula.api as smf
from rasterio.windows import Window
root=Path(__file__).resolve().parent
def read(name,sha=None):
    p=next((root/"usgs").rglob("*_"+name+".csv"))
    if sha:assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
    d=pd.read_csv(p,encoding="latin1");d.columns=d.columns.str.strip();return d
s=read("Sample_Data","24fed6f95e262cb287f755a7782b2ee213f59b81d869bfde7d8060705b839da8").dropna(subset=["Sample #"])
v=read("Vocalizations","e776f9baaf3f972edfa3fe302501a8721d954bc820effb096ef106a9b22be9af")
l=read("Tadpoles_Larvae","274914675782cd241ce10878faaf932be4baee8c6c023f82ba244fcd4d8487b4")
taxa=[t for t in l.columns if t+"_In" in v]
s["day"]=pd.to_datetime(s.Date);s["year"]=s.day.dt.year
def linked(t):
    return t.merge(s[["Sample ID","Site","day","year"]],on="Sample ID",validate="one_to_one")
v,l=linked(v),linked(l)
geo=read("Site_Var_Loc_Desc")
flood={}
with rasterio.open(root.parent/"earthenv_cache/earthenv_8.tif") as src:
    for _,g in geo.iterrows():
        i,j=src.index(g.Longitude,g.Latitude);w=Window(j-5,i-5,11,11)
        values=src.read(1,window=w,masked=True);rr,cc=np.indices(values.shape)
        xs=src.transform.c+(j-5+cc+.5)*src.transform.a;ys=src.transform.f+(i-5+rr+.5)*src.transform.e
        rad=6371000;dist=2*rad*np.arcsin(np.sqrt(np.sin(np.deg2rad(ys-g.Latitude)/2)**2+np.cos(np.deg2rad(ys))*np.cos(np.deg2rad(g.Latitude))*np.sin(np.deg2rad(xs-g.Longitude)/2)**2));flood[g.Site]=float(values[(dist<=3000)&(values<=100)].mean())
rows=[]
for (site,year),lg in l.groupby(["Site","year"]):
    vg=v[(v.Site==site)&(v.year==year)]
    eligible=lg[lg.day>vg.day.min()].sort_values(["day","Sample ID"])
    if eligible.empty:continue
    first=eligible.iloc[0]; prior=vg[vg.day<first.day]
    for t in taxa:
        idx=prior[t+"_In"]; assert idx.isin([0,1,2,3]).all()
        rows.append(dict(site=site,year=year,species=t,young=first[t],strong=int(idx.max()>=2),anycall=int(idx.max()>0),fraction=(idx>=2).mean(),nprior=len(idx),doy=first.day.dayofyear,lag=(first.day-prior.day.max()).days,newt=first["Ambystoma opacum"],veg=flood[site]))
d=pd.DataFrame(rows);assert len(d)==2990 and d.site.nunique()==64
assert d.veg.between(0,100).all()
print(d.groupby("strong").young.agg(["size","sum","mean"]))
print("matched salamander surveys",d.drop_duplicates(["site","year"]).newt.sum(),"positive tadpole records",d[d.newt==1].young.sum())
print("vegetation",d.drop_duplicates("site").veg.describe())
out=[]
for label,expr in [("strong","strong"),("frequency_2plus","fraction"),("flooded_vegetation","strong * veg10")]:
    p=d[d.nprior>=2].copy() if label=="frequency_2plus" else d.copy()
    if p.empty:continue
    p["veg10"]=(p.veg-p.drop_duplicates("site").veg.mean())/10
    # Risk differences on probability scale; repeated species, years and visits clustered by site.
    fit=smf.ols("young ~ "+expr+" + C(species) + C(year) + doy + I(doy**2) + lag",p).fit(cov_type="cluster",cov_kwds={"groups":p.site})
    term="strong:veg10" if label=="flooded_vegetation" else expr
    out.append(dict(test=label,rows=len(p),sites=p.site.nunique(),estimate=fit.params[term],lo=fit.conf_int().loc[term,0],hi=fit.conf_int().loc[term,1]))
print(pd.DataFrame(out));pd.DataFrame(out).to_csv(root/"usgs_summary.csv",index=False)
d.groupby(["species","strong"]).young.agg(["size","sum","mean"]).to_csv(root/"usgs_species_summary.csv")
