"""Compare the stored ABC draws. No simulation, refitting or new outcomes."""
from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "results"
OUT = ROOT / "two_sign_pathways_20261111"
OUT.mkdir(exist_ok=True)
d = pd.concat([pd.read_csv(f) for f in sorted((ROOT / "g12_abc_pom_prior_20261107/original_20k").glob("shard_*.csv.gz"))], ignore_index=True)
assert len(d) == d.draw_id.nunique() == 20000
eps = 1e-6
d["os"] = d.log_OS < -eps
d["ov"] = d.log_OV < -eps
d["joint"] = d.os & d.ov
assert (d.os.sum(), d.ov.sum(), d.joint.sum()) == (5199,9517,1925)
d["edges"] = np.select([d.edge_DS.eq(1) & d.edge_SD.eq(1), d.edge_DS.eq(1), d.edge_SD.eq(1)],
                       ["both", "odonate_eats_caudate", "caudate_eats_odonate"], default="neither")
# At each vegetation level reconstruct the SD contrast from its average and difference.
d["os_v0"] = d.log_OS - d.log_OSV / 2
d["os_v1"] = d.log_OS + d.log_OSV / 2
d["joint_strict"] = (d.log_OS < -.01) & (d.log_OV < -.01)
d["joint_raw"] = (d.raw_OS < -eps) & (d.raw_OV < -eps)
d["joint_floor"] = d.joint & d.floor_ok.astype(bool)
groupings = [["context_id"],["edges"],["litter"],["gate_code"],["context_id","edges","litter"]]
rows = []
for cols in groupings:
    for key, g in d.groupby(cols):
        key = key if isinstance(key,tuple) else (key,)
        rows.append(dict(zip(cols,key), grouping="+".join(cols), n=len(g), both=g.joint.sum(),
                         nonjoint=(~g.joint).sum(), os_only=(g.os & ~g.ov).sum(), ov_only=(g.ov & ~g.os).sum(),
                         neither=(~g.os & ~g.ov).sum(), joint_rate=g.joint.mean(),
                         os_given_ov=g.joint.sum()/g.ov.sum() if g.ov.any() else np.nan,
                         median_log_os=g.log_OS.median(), median_os_v0=g.os_v0.median(),
                         median_os_v1=g.os_v1.median(), strict=g.joint_strict.mean(),
                         raw=g.joint_raw.mean(), joint_and_floor=g.joint_floor.mean()))
pd.DataFrame(rows).to_csv(OUT/"scenario_counts.csv",index=False)
# Exact comparisons hold every other sampled input fixed. Also compare on
# common rate / developmental / edge / response strata for broader support.
design=list(d.loc[:,"context_id":"reverse"].columns)
focus=["context_id","edge_DS","edge_SD","litter","gate_code"]
rates=["attack","rho","conversion"]
matches=[]
for factor in focus:
    for first,second in combinations(sorted(d[factor].unique()),2):
        for method, keys in [("all_other_inputs",design),("rate_and_focal_inputs",rates+focus)]:
            keys=[k for k in keys if k!=factor]
            for population,g in [("all",d),("OV_negative",d.loc[d.ov])]:
                measures=["os","joint","log_OS","os_v0","os_v1","joint_strict","joint_raw"]
                by=g.groupby(keys+[factor])[measures].mean()
                a,b=by.xs(first,level=factor),by.xs(second,level=factor)
                common=a.index.intersection(b.index)
                if not len(common):continue
                paired=b.loc[common]-a.loc[common]
                for m in measures:
                    matches.append(dict(factor=factor,first=first,second=second,method=method,population=population,
                                        metric=m,matched_strata=len(common),first_mean=a.loc[common,m].mean(),
                                        second_mean=b.loc[common,m].mean(),difference=paired[m].mean(),
                                        lower_strata=(paired[m]<0).sum(),higher_strata=(paired[m]>0).sum()))
pd.DataFrame(matches).to_csv(OUT/"matched_contrasts.csv",index=False)

# Describe the requested case/control composition as well as rates within settings.
case_tables = []
for factor in ["context_id", "edges", "litter", "gate_code"]:
    table = pd.crosstab(d[factor], d.joint).rename(columns={True:"cases", False:"controls"})
    table["case_fraction"] = table.cases / d.joint.sum()
    table["control_fraction"] = table.controls / (~d.joint).sum()
    case_tables.append(table.rename_axis("setting").reset_index().assign(factor=factor))
pd.concat(case_tables, ignore_index=True).to_csv(OUT/"case_composition.csv",index=False)
