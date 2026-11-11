from inbo_followup import l,root
import inbo_followup as src
import numpy as np,pandas as pd
import statsmodels.formula.api as sm
# Same event, named newt, explicit zero or positive. Unrecorded species are unknown.
original=src.newts
src.newts=l[l.scientificName.eq("Triturus cristatus") & l.lifeStage.eq("larva")]
observed=src.paired().query("sp=='Hyla arborea' and stage=='larva' and single")
src.newts=src.newts[src.newts.individualCount.gt(0)]
pos=src.paired().query("sp=='Hyla arborea' and stage=='larva' and single")
keys=["site","year"]
g=observed[observed.newt].drop(columns="newt").merge(pos[keys+["newt"]],on=keys,validate="one_to_one")
src.newts=original
print(g.groupby("newt").agg(n=("young","size"),sites=("site","nunique"),frogs_detected=("young",lambda s:(s>0).sum())))
g["x"]=g.call.rank(pct=True);g["y"]=g.young.rank(pct=True)
g["confirmed"]=g.newt.astype(int)
if g.confirmed.nunique()==2 and g.groupby("confirmed").site.nunique().min()>5:
 fit=sm.ols("y ~ x * confirmed + C(year) + day + lag + n_prior",g).fit(cov_type="cluster",cov_kwds={"groups":g.site},use_t=True)
 t="x:confirmed"; r=dict(n=len(g),sites=g.site.nunique(),confirmed=int(g.confirmed.sum()),estimate=fit.params[t],lo=fit.conf_int().loc[t,0],hi=fit.conf_int().loc[t,1]);print(r);pd.DataFrame([r]).to_csv(root/"inbo_newt_interaction.csv",index=False)
