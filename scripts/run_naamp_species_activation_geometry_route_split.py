#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr, binomtest

ROOT=Path(__file__).resolve().parent
Q=1.959963984540054
YEARS=set(range(2001,2016))

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

geom=loadmod("activation_geometry",ROOT/"run_naamp_species_activation_geometry_repeatability.py")
base=geom.base
spatial=geom.spatial

def route_split(route_cluster:str)->str:
    b=hashlib.sha256(str(route_cluster).encode("utf-8")).digest()[0]
    return "A" if b < 128 else "B"

def weighted_regression(m):
    x=m.copy()
    f=smf.wls(
        "geometry_B ~ geometry_A",
        data=x,
        weights=1/(x["se_B"]**2)
    ).fit(cov_type="HC3")
    b=float(f.params["geometry_A"])
    se=float(f.bse["geometry_A"])
    p=float(f.pvalues["geometry_A"])
    return {
        "beta":b,
        "se_hc3":se,
        "ci95":[b-Q*se,b+Q*se],
        "p_value":p,
        "positive_ci_support":bool(b-Q*se>0)
    }

def sign_concordance(m):
    x=m[(m["geometry_A"]!=0)&(m["geometry_B"]!=0)].copy()
    same=np.sign(x["geometry_A"])==np.sign(x["geometry_B"])
    n=int(len(x)); k=int(same.sum())
    bt=binomtest(k,n,p=.5,alternative="greater") if n else None
    return {
        "n_species":n,
        "same_sign":k,
        "fraction_same_sign":float(k/n) if n else None,
        "one_sided_binomial_p":float(bt.pvalue) if bt else None
    }

def split_diagnostics(pairs):
    x=pairs.copy()
    x["route_split"]=x["route_cluster"].astype(str).map(route_split)
    out={}
    for label,d in x.groupby("route_split"):
        out[str(label)]={
            "matched_pairs":int(len(d)),
            "routes":int(d["route_cluster"].nunique()),
            "states":int(d["State"].astype(str).nunique()),
            "state_names":sorted(d["State"].astype(str).unique().tolist())
        }
    return out

def main():
    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,stop_species=spatial.stop_matrix(raw,eligible)

    pruns,pairs,rows,uninformative=geom.period_gain_rows(
        runs,route_sets,sampled,stop_species,YEARS
    )
    rows=rows.copy()
    rows["route_split"]=rows["route_cluster"].astype(str).map(route_split)

    A=geom.fit_period(rows[rows["route_split"]=="A"].copy())
    B=geom.fit_period(rows[rows["route_split"]=="B"].copy())
    AA=A[A["estimable"]==True].copy()
    BB=B[B["estimable"]==True].copy()

    a=AA[[
        "species","activation_geometry_log_odds","se_cluster",
        "n_informative_wet_gain_incidences","n_routes","n_pairs",
        "raw_new_site_fraction","mean_available_inactive_fraction"
    ]].rename(columns={
        "activation_geometry_log_odds":"geometry_A",
        "se_cluster":"se_A",
        "n_informative_wet_gain_incidences":"gain_incidences_A",
        "n_routes":"routes_A",
        "n_pairs":"pairs_A",
        "raw_new_site_fraction":"raw_new_site_fraction_A",
        "mean_available_inactive_fraction":"mean_available_inactive_fraction_A"
    })
    b=BB[[
        "species","activation_geometry_log_odds","se_cluster",
        "n_informative_wet_gain_incidences","n_routes","n_pairs",
        "raw_new_site_fraction","mean_available_inactive_fraction"
    ]].rename(columns={
        "activation_geometry_log_odds":"geometry_B",
        "se_cluster":"se_B",
        "n_informative_wet_gain_incidences":"gain_incidences_B",
        "n_routes":"routes_B",
        "n_pairs":"pairs_B",
        "raw_new_site_fraction":"raw_new_site_fraction_B",
        "mean_available_inactive_fraction":"mean_available_inactive_fraction_B"
    })
    m=a.merge(b,on="species",how="inner",validate="one_to_one")
    if len(m)<15:
        raise SystemExit(
            f"overlap species below frozen minimum: {len(m)} "
            f"(A={len(AA)}, B={len(BB)})"
        )

    rho,p=spearmanr(m["geometry_A"],m["geometry_B"])
    primary={
        "n_species":int(len(m)),
        "spearman_rho":float(rho),
        "p_value":float(p),
        "positive_support":bool(rho>0 and p<0.05)
    }
    wls=weighted_regression(m)
    signs=sign_concordance(m)

    result={
        "analysis":"naamp_species_activation_geometry_route_split_v0_1",
        "contract":"NAAMP_SPECIES_ACTIVATION_GEOMETRY_ROUTE_SPLIT_CONTRACT_V0_1.json",
        "route_split":{
            "algorithm":"SHA-256 route_cluster first byte <128 => A, else B",
            "disjoint_routes":True,
            "diagnostics":split_diagnostics(pairs)
        },
        "source":{
            "eligible_runs":int(len(pruns)),
            "matched_pairs":int(len(pairs)),
            "structurally_uninformative_pairs":int(uninformative),
            "species_with_any_informative_gain":int(rows["species"].nunique())
        },
        "estimable_species":{
            "split_A":int(len(AA)),
            "split_B":int(len(BB)),
            "overlap":int(len(m))
        },
        "primary_route_transfer":primary,
        "weighted_regression_sensitivity":wls,
        "sign_concordance":signs,
        "species_table":[
            {
                "species":str(r.species),
                "geometry_A":float(r.geometry_A),
                "se_A":float(r.se_A),
                "gain_incidences_A":int(r.gain_incidences_A),
                "routes_A":int(r.routes_A),
                "geometry_B":float(r.geometry_B),
                "se_B":float(r.se_B),
                "gain_incidences_B":int(r.gain_incidences_B),
                "routes_B":int(r.routes_B),
                "same_sign":bool(np.sign(r.geometry_A)==np.sign(r.geometry_B))
            }
            for r in m.itertuples(index=False)
        ],
        "interpretation_boundary":{
            "same_species_disjoint_routes":True,
            "independent_species_replication":False,
            "geographic_gradient_claim_authorized":False,
            "occupancy_dispersal_colonization_claim_authorized":False,
            "endpoint_retuning_after_readback_authorized":False
        }
    }
    Path("NAAMP_SPECIES_ACTIVATION_GEOMETRY_ROUTE_SPLIT_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
