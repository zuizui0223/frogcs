#!/usr/bin/env python3
"""Post-hoc interpretability check for mapped emergent NWI coverage exposure.

No new headline endpoint: translates the frozen continuous 10pp model to the
empirical within-run scale; binary polygon-presence sensitivity is secondary.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
Z=1.959963984540054

def module(name,path):
    sp=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(sp)
    assert sp.loader
    sp.loader.exec_module(m)
    return m

def binary_fit(df):
    d=df.copy()
    d["mapped_PEM_presence"]=(d.pem_raw.astype(float)>0).astype(float)
    predictors=["mapped_PEM_presence","allwet_10pp","woody_10pp",
                "stop_temp_c","sound_index","standardized_stop_number"]
    g=d.groupby("RunID",sort=False)
    X=np.column_stack([(d[name]-g[name].transform("mean")).to_numpy(dtype=float)
                       for name in predictors])
    if np.linalg.matrix_rank(X)<len(predictors):
        return {"status":"nonidentifiable","p":1.0}
    y=(d.y_strong-g.y_strong.transform("mean")).to_numpy(dtype=float)
    m=sm.OLS(y,X).fit(cov_type="cluster",
                     cov_kwds={"groups":d.route_cluster.astype(str)})
    beta=float(m.params[0]);se=float(m.bse[0])
    return {"status":"fitted","beta":beta,
            "ci95":[beta-Z*se,beta+Z*se],"p":float(m.pvalues[0]),
            "interpretation":"difference between stops overlapping/not overlapping mapped NWI PEM polygons, not true plant presence/absence"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--nwi-sites",required=True,type=Path)
    p.add_argument("--nwi-audit",required=True,type=Path)
    p.add_argument("--out",type=Path,default=ROOT/"build"/"aquatic_vegetation_ecology"/"taxon_nwi_exposure_sensitivity_v0_1.json")
    args=p.parse_args()
    source=module("full_veg_source",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    base=module("frogs_by_taxon",ROOT/"exploration/run_naamp_taxon_specific_aquatic_vegetation_v0_1.py")
    nwi,audit=source.read_nwi(args.nwi_sites,args.nwi_audit)
    assert audit["mode"]=="full" and audit["overlay"]["site_records"]==5147
    raw=source.hist.load_retry()
    runs,_=source.base.build_runs(raw)
    by,coverage=base.build(raw,runs,nwi,source)
    old=json.loads((ROOT/"exploration/NAAMP_TAXON_SPECIFIC_AQUATIC_VEGETATION_RESULT_V0_1.json").read_text())
    eligible=sorted([x for x in old["all_taxa"] if x["status"]=="fitted"],key=lambda x:x["taxon"])
    assert len(eligible)==25
    result=[]
    for ref in eligible:
        taxon=ref["taxon"]
        df=pd.DataFrame(by[taxon])
        if len(df)!=ref["n_stop_rows"] or df.RunID.nunique()!=ref["active_runs"] or df.route_cluster.nunique()!=ref["routes"]:
            raise RuntimeError("Taxon-specific study population drift: "+taxon)
        v=df.pem_raw.to_numpy(dtype=float)
        avg=df.groupby("RunID").pem_raw.transform("mean").to_numpy(dtype=float)
        within_sd=float(np.std(v-avg,ddof=0))
        if (v>0).any():
            positive_q=np.quantile(v[v>0],[.25,.5,.75,.9]).tolist()
        else:positive_q=None
        continuous=ref["primary_strong"]["pem_beta_per_10pp"]
        fit=binary_fit(df)
        result.append({
            "taxon":taxon,
            "source_primary_beta_10pp":continuous,
            "source_primary_BH_q":ref["primary_BH_q"],
            "mapped_PEM_presence_fraction":float(np.mean(v>0)),
            "cover_positive_q25_q50_q75_q90":positive_q,
            "within_run_PEM_fraction_sd":within_sd,
            "source_primary_effect_per_within_run_PEM_sd":float(continuous*within_sd/0.1),
            "binary_polygon_overlap_secondary":fit,
            "n_active_runs":int(df.RunID.nunique()),"n_routes":int(df.route_cluster.nunique())
        })
    qs=multipletests([x["binary_polygon_overlap_secondary"]["p"] for x in result],method="fdr_bh")[1]
    for row,q in zip(result,qs):
        row["binary_secondary_BH_q"]=float(q)
        row["binary_secondary_BH_supported"]=bool(q<.05)
    out={"analysis":"naamp_taxon_nwi_exposure_scale_posthoc_sensitivity_v0_1",
         "status":"posthoc_interpretability_not_primary",
         "reference_continuous_BH_25_taxa_source":"exploration/NAAMP_TAXON_SPECIFIC_AQUATIC_VEGETATION_RESULT_V0_1.json",
         "population":coverage,
         "taxa":result,
         "summary":{"eligible_taxa":len(result),
                    "binary_BH_supported":sum(x["binary_secondary_BH_supported"] for x in result),
                    "reference_five_continuous_significant_binary_signs":[
                        {"taxon":x["taxon"],"beta_binary":x["binary_polygon_overlap_secondary"].get("beta"),
                         "q_binary":x["binary_secondary_BH_q"]}
                        for x in result if x["source_primary_BH_q"]<.05]},
         "boundaries":{"NWI_0_is_not_true_absence_of_aquatic_plants":True,
                       "10pp_exposure_may_exceed_typical_within_route_PEM_variation":True,
                       "binary_test_after_reading_continuous_results":True,
                       "binary_is_secondary_not_primary":True,
                       "RC6_frozen":True}}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("NWI_EXPOSURE_SCALE_RESULT_BEGIN",flush=True)
    print(json.dumps(out,sort_keys=True),flush=True)
    print("NWI_EXPOSURE_SCALE_RESULT_END",flush=True)

if __name__=="__main__":
    main()
