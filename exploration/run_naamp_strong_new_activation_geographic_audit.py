#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_STRONG_NEW_ACTIVATION_GEOGRAPHIC_AUDIT_RECEIPT_V0_1.json"
Q=1.959963984540054


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


strength=loadmod("strength_base",EXP/"run_naamp_new_activation_strength.py")
base=strength.base
spatial=strength.spatial


def fit_geo(df,include_state):
    formula=(
        "strong_new_score ~ rain_contrast + temp_difference + doy_difference + year_gap + "
        + ("C(State) + " if include_state else "")
        + "C(RunNumber)"
    )
    m=smf.ols(formula,data=df).fit(
        cov_type="cluster",cov_kwds={"groups":df["route_cluster"]}
    )
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {
        "n_pairs":int(len(df)),
        "n_routes":int(df["route_cluster"].nunique()),
        "beta":b,
        "se":se,
        "ci95":[b-Q*se,b+Q*se],
        "p":float(m.pvalues["rain_contrast"]),
        "formula":formula,
    }


def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    by=strength.build_ci(raw,eligible,sampled)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)

    rows=[]
    for p in pairs.itertuples(index=False):
        r=p._asdict()
        r.update(strength.metrics(p,sampled,by))
        rows.append(r)
    df=pd.DataFrame(rows)

    loo=[]
    for state in sorted(df["State"].astype(str).unique()):
        sub=df[df["State"].astype(str)!=state].copy()
        rep=fit_geo(sub,True)
        rep["omitted_state"]=state
        loo.append(rep)

    state_reports=[]
    for state,g in df.groupby("State",sort=True):
        if len(g)<50 or g["route_cluster"].nunique()<8:
            continue
        rep=fit_geo(g.copy(),False)
        rep["State"]=str(state)
        state_reports.append(rep)

    all_positive=bool(all(x["beta"]>0 for x in loo))
    all_ci_positive=bool(all(x["ci95"][0]>0 for x in loo))
    positive_state_fraction=(
        float(np.mean([x["beta"]>0 for x in state_reports]))
        if state_reports else None
    )

    output={
        "analysis":"naamp_strong_new_activation_geographic_audit_v0_1",
        "contract":"exploration/NAAMP_STRONG_NEW_ACTIVATION_GEOGRAPHIC_AUDIT_CONTRACT_V0_1.json",
        "coverage":{
            "pairs":int(len(df)),
            "routes":int(df["route_cluster"].nunique()),
            "states":int(df["State"].nunique()),
            "state_specific_eligible":int(len(state_reports)),
        },
        "leave_one_state_out":loo,
        "state_specific":state_reports,
        "summary":{
            "all_leave_one_state_out_betas_positive":all_positive,
            "all_leave_one_state_out_ci95_positive":all_ci_positive,
            "eligible_state_positive_beta_fraction":positive_state_fraction,
        },
        "classification":{
            "not_single_state_driven":all_positive,
            "rule":"all leave-one-state-out rain_contrast coefficients >0"
        },
        "interpretation_boundary":{
            "every_state_effect_claim":False,
            "equal_effect_across_states_claim":False,
            "cross_continental_universality":False,
            "causal_rainfall_claim":False
        }
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
