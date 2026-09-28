#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
Q90=1.6448536269514722
MARGIN=0.025

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

meta=loadmod("meta",ROOT/"run_naamp_metacommunity_alpha_beta_gamma.py")

def one(d):
    fit=meta.fit(d,"delta_mean_pairwise_sorensen_active")
    b=float(fit["beta_rain_contrast"])
    se=float(fit["se_cluster"])
    ci=[b-Q90*se,b+Q90*se]
    return {
      "n_pairs":int(fit["n_pairs"]),
      "n_routes":int(fit["n_routes"]),
      "beta":b,
      "se_cluster":se,
      "ci90":ci,
      "margin":[-MARGIN,MARGIN],
      "equivalent":bool(ci[0] > -MARGIN and ci[1] < MARGIN)
    }

def main():
    d=meta.build()
    primary=one(d)
    exact=one(d[d.year_gap==1].copy())
    result={
      "analysis":"naamp_sorensen_equivalence_v0_1",
      "contract":"provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json#items/NAAMP_SORENSEN_EQUIVALENCE_CONTRACT_V0_1",
      "status":"post-hoc margin frozen before equivalence readback; conventional coefficient already known",
      "primary":primary,
      "exact_consecutive_year":exact,
      "decision":{
        "primary_pass":primary["equivalent"],
        "exact_year_pass":exact["equivalent"],
        "title_level_equivalence_support":bool(primary["equivalent"] and exact["equivalent"])
      },
      "interpretation_boundary":{
        "equivalence_applies_only_to_pairwise_sorensen_slope":True,
        "exact_invariance_claim_authorized":False,
        "retuning_margin_after_readback_authorized":False
      }
    }
    Path("provenance/receipts/NAAMP_SORENSEN_EQUIVALENCE_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
