"""Refit published predator habitat indices without flooded vegetation; paired route bootstrap."""
from pathlib import Path
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from broad_species_sdm import thin, features
from naamp_remote_vegetation_network import standardized_rank
from naamp_vegetation_network_associations import fit, TERMS

ROOT = Path(__file__).resolve().parents[2] / "research/results"
source = ROOT / "interaction_species_sdm_20261026"
remote = ROOT / "naamp_remote_vegetation_20261026"
taxa = pd.read_csv(source / "training_presence_environment.csv.gz")
bg = pd.read_csv(source / "background.csv.gz")
site = pd.read_csv(remote / "primary_site_landscape_context.csv.gz")
env = pd.read_csv(source / "naamp_site_environment.csv.gz").set_index("site").loc[site.site]
models = pd.read_json(source / "models.json")
models = models[(models.status=="fit") & (models.guild.eq("Odonata") | models.species.str.startswith(("Ambystoma ","Notophthalmus ")))]
base = ["bio1","bio4","bio12","bio15","water"]
raw = site.flooded_3000m_mean.to_numpy()
routes = site.route.to_numpy()
y = site.strong_rate.to_numpy()
blocks = [np.flatnonzero(routes==r) for r in sorted(set(routes))]
rng = np.random.default_rng(20261031)
draws = [np.arange(len(site))]+[np.concatenate([blocks[k] for k in rng.integers(len(blocks),size=len(blocks))]) for _ in range(1000)]
def refit(m,cols):
    presence=taxa[taxa.species.eq(m.species)]
    other=bg if m.background=="uniform" else pd.DataFrame(thin(taxa[taxa.guild.eq(m.guild)&taxa.species.ne(m.species)].to_dict("records")))
    assert (len(presence),len(other))==(m.cells,m.background_cells)
    x=pd.concat([presence,other])[cols].to_numpy()
    model=features(x).fit(x,np.r_[np.ones(len(presence)),np.zeros(len(other))])
    return np.searchsorted(np.sort(model.decision_function(bg[cols].to_numpy())),model.decision_function(env[cols].to_numpy()),side="right")/len(bg)

def run():
    result=[]
    assert len(models)==22 and len(site)==4248
    for b,ms in models.groupby("background"):
        fitted=[]
        for which in ("original","omit_flooded"):
            guilds=[]
            for guild,key in [("Odonata","Odonata"),("Caudata","pond_breeding_Caudata")]:
                cols=base[:4]+(["flooded"] if which=="original" else [])+["water"]
                v=np.mean([refit(m,cols) for m in ms[ms.guild.eq(guild)].itertuples()],axis=0)
                if which=="original":
                    old=site[f"mean_suitability_{key}_{b}"].to_numpy()
                    print(b,key,"max baseline difference",max(abs(v-old)),flush=True)
                    np.testing.assert_allclose(v,old,atol=.00025,rtol=0)
                    v=old
                guilds.append(v)
            o,s=guilds
            fitted.append(np.array([[fit(o[i],s[i],standardized_rank(raw[i]),y[i],routes[i],within) for within in [False,True]] for i in draws]))
        for arm,arr in zip(["original","omit_flooded","paired_change"],[*fitted,fitted[1]-fitted[0]]):
            for within in [0,1]:
                for j,term in enumerate(TERMS):
                    lo,hi=np.quantile(arr[1:,within,j],[.025,.975]);result.append([b,arm,within,term,arr[0,within,j],lo,hi])
    out=ROOT/"sdm_flooded_omission_20261111";out.mkdir(exist_ok=True)
    pd.DataFrame(result,columns=["background","arm","within_route","term","beta","lo","hi"]).to_csv(out/"coefficients.csv",index=False)
if __name__=="__main__":
    with threadpool_limits(limits=1):run()
