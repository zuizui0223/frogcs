#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import norm, spearmanr

ROOT=Path(__file__).resolve().parent

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base=loadmod("pulse_base",ROOT/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",ROOT/"run_naamp_spatial_taxonomic_activation_decomposition.py")

Q95=1.959963984540054
Q90=1.6448536269514722
MARGIN=0.05

def run_matrix_metrics(rid,stops,ss):
    sets=[set(ss.get((rid,st),set())) for st in stops]
    active=[x for x in sets if x]
    n_active=len(active)
    gamma=len(set().union(*active)) if active else 0
    incid=sum(len(x) for x in active)
    alpha=incid/n_active if n_active else np.nan
    connectance=incid/(gamma*n_active) if gamma>0 and n_active>0 else np.nan
    if np.isfinite(connectance) and np.isfinite(alpha) and abs(connectance-alpha/gamma)>1e-12:
        raise RuntimeError("connectance identity failed")
    return {
        "n_active":n_active,
        "gamma":gamma,
        "incidences":incid,
        "alpha_active":alpha,
        "connectance":connectance
    }

def build():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,ss=spatial.stop_matrix(raw,eligible)
    pairs=base.pair_runs(runs,sets).copy()
    rows=[]
    for p in pairs.itertuples(index=False):
        w,d=str(p.wet_RunID),str(p.dry_RunID)
        sw=set(sampled[w]);sd=set(sampled[d])
        if len(sw)!=10 or sw!=sd:
            raise RuntimeError(f"stop alignment failed wet={w} dry={d}")
        stops=sorted(sw)
        W=run_matrix_metrics(w,stops,ss)
        D=run_matrix_metrics(d,stops,ss)
        if not (np.isfinite(W["connectance"]) and np.isfinite(D["connectance"])):
            raise RuntimeError(f"eligible run lacks finite active matrix: wet={w} dry={d}")
        row=p._asdict()
        row.update({
            "wet_connectance":float(W["connectance"]),
            "dry_connectance":float(D["connectance"]),
            "delta_connectance":float(W["connectance"]-D["connectance"]),
            "delta_alpha_active":float(W["alpha_active"]-D["alpha_active"]),
            "delta_gamma_check":float(W["gamma"]-D["gamma"]),
            "delta_incidences_check":float(W["incidences"]-D["incidences"]),
            "delta_active_stops_check":float(W["n_active"]-D["n_active"])
        })
        if abs(row["delta_gamma_check"]-float(row["richness_gain"]))>1e-12:
            raise RuntimeError("gamma/richness identity drift")
        rows.append(row)
    return pd.DataFrame(rows)

def fit(d):
    x=d[np.isfinite(d["delta_connectance"])].copy()
    formula=(
        "delta_connectance ~ rain_contrast + temp_difference + doy_difference + "
        "year_gap + C(State) + C(RunNumber)"
    )
    f=smf.ols(formula,data=x).fit(
        cov_type="cluster",cov_kwds={"groups":x["route_cluster"]}
    )
    b=float(f.params["rain_contrast"])
    se=float(f.bse["rain_contrast"])
    ci95=[b-Q95*se,b+Q95*se]
    ci90=[b-Q90*se,b+Q90*se]
    # TOST: H01 beta <= -MARGIN, H02 beta >= +MARGIN.
    z_lower=(b-(-MARGIN))/se
    z_upper=(MARGIN-b)/se
    p_lower=float(1-norm.cdf(z_lower))
    p_upper=float(1-norm.cdf(z_upper))
    # Equivalent implementation: both one-sided p-values < .05.
    equivalent=bool(ci90[0]>-MARGIN and ci90[1]<MARGIN)
    return {
        "n_pairs":int(len(x)),
        "n_routes":int(x["route_cluster"].nunique()),
        "formula":formula,
        "beta_rain_contrast":b,
        "se_cluster":se,
        "ci95":ci95,
        "ci90_equivalence":ci90,
        "margin":MARGIN,
        "tost_p_lower":p_lower,
        "tost_p_upper":p_upper,
        "equivalence_supported":equivalent
    }

def desc(d):
    rho_a,p_a=spearmanr(d["delta_connectance"],d["delta_alpha_active"])
    rho_g,p_g=spearmanr(d["delta_connectance"],d["richness_gain"])
    return {
        "n_pairs":int(len(d)),
        "n_routes":int(d["route_cluster"].nunique()),
        "mean_wet_connectance":float(d["wet_connectance"].mean()),
        "mean_dry_connectance":float(d["dry_connectance"].mean()),
        "mean_delta_connectance":float(d["delta_connectance"].mean()),
        "sd_delta_connectance":float(d["delta_connectance"].std(ddof=0)),
        "spearman_delta_connectance_vs_delta_alpha":{
            "rho":float(rho_a),"p_value":float(p_a)
        },
        "spearman_delta_connectance_vs_richness_gain":{
            "rho":float(rho_g),"p_value":float(p_g)
        }
    }

def main():
    d=build()
    primary=fit(d)
    exact=d[d["year_gap"]==1].copy()
    sens=fit(exact)
    result={
        "analysis":"naamp_matrix_density_invariance_v0_1",
        "contract":"NAAMP_MATRIX_DENSITY_INVARIANCE_CONTRACT_V0_1.json",
        "descriptive":desc(d),
        "primary":primary,
        "exact_consecutive_year":{
            "descriptive":desc(exact),
            "model":sens
        },
        "frozen_support_rule_pass":bool(
            primary["equivalence_supported"] and sens["equivalence_supported"]
        ),
        "interpretation_boundary":{
            "connectance":"Observed acoustic species-by-active-site matrix fill, not interaction-network connectance.",
            "equivalence_margin":MARGIN,
            "exact_invariance_claim_authorized":False,
            "causal_rainfall_claim_authorized":False,
            "endpoint_retuning_after_readback_authorized":False
        }
    }
    Path("NAAMP_MATRIX_DENSITY_INVARIANCE_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
