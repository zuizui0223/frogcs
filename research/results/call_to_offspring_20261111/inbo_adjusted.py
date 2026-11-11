import inbo_followup as src
import pandas as pd,numpy as np
import statsmodels.formula.api as sm
p=src.paired().query("sp=='Hyla arborea'").copy()
rows=[]
for stage,g in p.groupby("stage"):
 print(stage,"years",g.year.min(),g.year.max(),"lag median",g.lag.median(),"frequency strict land",src.estimate(stage,g[g.land & (g.n_prior>=2)],"positive_frequency"))
 for key, exp in [("callers","call"),("fraction","positive_frequency")]:
  x=g[g.n_prior>=2].copy() if key=="fraction" else g.copy()
  for c in ["young",exp]: x[c+"_rank"]=x[c].rank(pct=True)
  for design in [""," + C(site)"]:
   tmp=x if not design else x.groupby("site").filter(lambda v:len(v)>1)
   if len(tmp)<20 or tmp.site.nunique()<10:continue
   fit=sm.ols("young_rank ~ "+exp+"_rank + C(year) + day + I(day**2) + lag + n_prior"+design,tmp).fit(cov_type="cluster",cov_kwds={"groups":tmp.site},use_t=True)
   term=exp+"_rank";rows.append(dict(stage=stage,exposure=key,within_site=bool(design),n=len(tmp),sites=tmp.site.nunique(),estimate=fit.params[term],lo=fit.conf_int().loc[term,0],hi=fit.conf_int().loc[term,1]))
print(pd.DataFrame(rows));pd.DataFrame(rows).to_csv(src.root/"inbo_adjusted.csv",index=False)
