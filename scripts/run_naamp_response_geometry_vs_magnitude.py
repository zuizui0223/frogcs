#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parent
Q=1.959963984540054

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

breadth=loadmod("breadth_response",ROOT/"run_naamp_spatial_niche_breadth_response.py")
base=breadth.base

def main():
    geom=json.loads(Path("NAAMP_SPECIES_ACTIVATION_GEOMETRY_REPEATABILITY_SUMMARY_V0_1.json").read_text())
    early=pd.DataFrame([
        {"species":r["species"],"early_geometry":float(r["early"])}
        for r in geom["species_table"]
    ])

    raw=base.load()
    runs,sets=base.build_runs(raw)
    late_runs,late_pairs,late=breadth.late_responses(runs,sets)
    m=early.merge(late,on="species",how="inner",validate="one_to_one")
    if len(m)<15:
        raise SystemExit(f"intersection below frozen minimum: {len(m)}")

    rho,p=spearmanr(m["early_geometry"],m["late_adjusted_log_odds"])
    strong=bool(abs(rho)>=0.6 and p<0.05)

    w=1/(m["late_se"]**2)
    f=smf.wls("late_adjusted_log_odds ~ early_geometry",data=m,weights=w).fit(cov_type="HC3")
    b=float(f.params["early_geometry"]);se=float(f.bse["early_geometry"]);pw=float(f.pvalues["early_geometry"])

    edge=m[m["early_geometry"]>0].copy()
    deep=m[m["early_geometry"]<0].copy()
    def wmean(d):
        ww=1/(d["late_se"]**2)
        return float(np.sum(ww*d["late_adjusted_log_odds"])/np.sum(ww))
    result={
      "analysis":"naamp_response_geometry_vs_magnitude_holdout_v0_1",
      "contract":"NAAMP_RESPONSE_GEOMETRY_VS_MAGNITUDE_CONTRACT_V0_1.json",
      "time_split":{"predictor":[2001,2007],"outcome":[2008,2015]},
      "late_response_rebuild":{
        "eligible_runs":int(len(late_runs)),
        "matched_pairs":int(len(late_pairs)),
        "estimable_species":int(len(late))
      },
      "intersection_species":int(len(m)),
      "primary":{
        "spearman_rho":float(rho),
        "two_sided_p":float(p),
        "strong_cross_axis_coupling":strong,
        "frozen_strong_coupling_rule":"abs(rho)>=0.6 and P<0.05"
      },
      "weighted_regression":{
        "beta":b,
        "se_hc3":se,
        "ci95":[b-Q*se,b+Q*se],
        "p_value":pw
      },
      "sign_groups":{
        "spatial_edge_activators_n":int(len(edge)),
        "local_deepeners_n":int(len(deep)),
        "weighted_mean_late_response_edge":wmean(edge) if len(edge) else None,
        "weighted_mean_late_response_deepener":wmean(deep) if len(deep) else None
      },
      "species_table":[
        {
          "species":str(r.species),
          "early_geometry":float(r.early_geometry),
          "late_response_log_odds":float(r.late_adjusted_log_odds),
          "late_response_se":float(r.late_se)
        }
        for r in m.itertuples(index=False)
      ],
      "interpretation_boundary":{
        "statistical_independence_claim_authorized":False,
        "equivalence_claim_authorized":False,
        "same_species_nonoverlapping_periods":True,
        "causal_claim_authorized":False
      }
    }
    Path("NAAMP_RESPONSE_GEOMETRY_VS_MAGNITUDE_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
