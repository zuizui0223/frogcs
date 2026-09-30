#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_LOCAL_MEMORY_SPATIAL_KERNEL_REPAIR_RECEIPT_V0_2.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

v1=loadmod("v1",EXP/"run_naamp_local_memory_spatial_kernel.py")

def build_data():
    raw=v1.load_retry()
    runs,sets=v1.base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=v1.spatial.stop_matrix(raw,eligible)
    site=v1.site_map(raw,eligible)
    ci=v1.ci_map(raw,eligible,sampled)
    meta,by_stratum=v1.build_history(runs)

    allpairs=v1.base.pair_runs(runs,sets).copy().reset_index(drop=True)
    stable=allpairs.loc[
        np.asarray([v1.stable_pair(p,sampled,site) for p in allpairs.itertuples(index=False)],bool)
    ].copy().reset_index(drop=True)
    _,same=v1.sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    rows=[]
    for pid,p in enumerate(stable.itertuples(index=False)):
        rows.extend(v1.pair_rows(
            pid,p,sampled,site,ci,meta,by_stratum,
            (str(p.wet_RunID),str(p.dry_RunID)) in same_keys
        ))
    import pandas as pd
    return pd.DataFrame(rows),stable

def fit_pairwise(df,outcome,left,right):
    d=df.copy()
    # Keep only groups containing at least one stop in each compared class.
    sums=d.groupby("pair_species")[[left,right]].sum()
    good=sums[(sums[left]>0)&(sums[right]>0)].index
    d=d[d.pair_species.isin(good) & ((d[left]==1)|(d[right]==1))].copy()
    if d.empty:
        return None

    d["left_indicator"]=d[left].astype(float)
    d["other_log"]=np.log1p(d.other_species_prior_strong_richness.astype(float))
    for col in (outcome,"left_indicator","other_log","prior_site_effort"):
        d[col+"_w"]=d[col].astype(float)-d.groupby("pair_species")[col].transform("mean").astype(float)

    cols=["left_indicator_w","other_log_w","prior_site_effort_w"]
    X=d[cols].astype(float)
    keep=["left_indicator_w"]+[c for c in cols[1:] if float(np.abs(X[c]).sum())>1e-12]
    X=X[keep]
    m=sm.OLS(d[outcome+"_w"].astype(float),X).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster.astype(str)}
    )
    b=float(m.params["left_indicator_w"]); se=float(m.bse["left_indicator_w"])
    return {
        "outcome":outcome,
        "left_class":left,
        "right_reference":right,
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(d.pair_species.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "left_minus_right_beta":b,
        "se":se,
        "ci95":[b-Q*se,b+Q*se],
        "p":float(m.pvalues["left_indicator_w"]),
        "positive_ci":bool(b>0 and b-Q*se>0),
        "generic_other_species_beta":float(m.params["other_log_w"]) if "other_log_w" in m.params.index else None,
        "prior_site_effort_beta":float(m.params["prior_site_effort_w"]) if "prior_site_effort_w" in m.params.index else None
    }

def main():
    d,stable=build_data()
    primary=fit_pairwise(d,"wet_strong","same_site_memory","adjacent_site_memory_only")
    gate=bool(
        primary is not None
        and primary["n_pair_species_groups"]>=300
        and primary["n_routes"]>=200
        and primary["n_species"]>=20
    )

    out={
      "analysis":"naamp_local_memory_spatial_kernel_v0_2_repair",
      "repair_contract":"exploration/NAAMP_LOCAL_MEMORY_SPATIAL_KERNEL_REPAIR_V0_2.json",
      "supersedes_invalid_full_sample_fit":"NAAMP_LOCAL_MEMORY_SPATIAL_KERNEL_RECEIPT_V0_1.json full-sample simultaneous category coefficients",
      "coverage":{
        "physically_stable_pairs":int(len(stable)),
        "candidate_rows":int(len(d)),
        "candidate_groups":int(d.pair_species.nunique()) if len(d) else 0,
        "gate_pass":gate
      },
      "response_endpoints_read":False
    }
    if not gate:
        out["primary_precheck"]=primary
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    full=primary
    full_chorus=fit_pairwise(d,"wet_full","same_site_memory","adjacent_site_memory_only")
    adj_vs_distant=fit_pairwise(d,"wet_strong","adjacent_site_memory_only","distant_route_memory_only")
    sameobs=d[d.same_observer].copy()
    same_fit=fit_pairwise(sameobs,"wet_strong","same_site_memory","adjacent_site_memory_only")

    out.update({
      "response_endpoints_read":True,
      "primary_same_vs_adjacent_wet_strong":full,
      "secondary_same_vs_adjacent_wet_full":full_chorus,
      "secondary_adjacent_vs_distant_wet_strong":adj_vs_distant,
      "same_observer_sensitivity":same_fit,
      "classification":{
        "fine_scale_same_site_localization_supported":bool(full["positive_ci"]),
        "full_chorus_same_site_localization_supported":bool(full_chorus and full_chorus["positive_ci"]),
        "same_observer_support":bool(same_fit and same_fit["positive_ci"]),
        "adjacent_above_distant_supported":bool(adj_vs_distant and adj_vs_distant["positive_ci"])
      },
      "interpretation_boundary":{
        "v0_1_nonidentifiable_coefficients_discarded":True,
        "biological_contrast_changed":False,
        "route_order_adjacency_not_metric_distance":True,
        "continuous_occupancy_proven":False,
        "causal_memory_claim":False
      }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
