#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.sandwich_covariance import cov_cluster

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_MONITORING_INDEPENDENCE_IMPACT_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

rain=loadmod("rain_amount_common",EXP/"run_naamp_rain_amount_common_environment_null.py")
flex=rain.flex

def term(beta,se):
    return {
        "beta":float(beta),
        "se":float(se),
        "ci95":[float(beta-Q*se),float(beta+Q*se)]
    }

def main():
    dep=json.loads((EXP/"NAAMP_SPECIES_ROUTE_NIGHT_RESIDUAL_DEPENDENCE_RECEIPT_V0_1.json").read_text())
    if not dep["residual_dependence"]["positive_dependence_supported"]:
        out={
            "analysis":"naamp_monitoring_independence_impact_v0_1",
            "status":"not_run_positive_dependence_trigger_not_met"
        }
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    weather,weather_sha=rain.antecedent_amounts(mid)

    mask=np.asarray([
        str(p.wet_RunID) in weather and str(p.dry_RunID) in weather
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(mask)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]

    if len(pw)!=2835:
        raise RuntimeError(f"weather subset drift {len(pw)} != 2835")

    rows=[]
    for p,dct in zip(pw.itertuples(index=False),dw):
        pair_id=f"{p.wet_RunID}|{p.dry_RunID}"
        dry=dct["dry"].astype(bool)
        wet=dct["wet"].astype(bool)
        for si,sp in enumerate(dct["species"]):
            at_risk=~dry[si]
            js=np.flatnonzero(at_risk)
            if not len(js):
                continue
            cluster=f"{pair_id}|{sp}"
            for j in js:
                rows.append({
                    "wet_activation":int(wet[si,j]),
                    "rain_contrast":float(p.rain_contrast),
                    "temp_difference":float(p.temp_difference),
                    "doy_difference":float(p.doy_difference),
                    "year_gap":float(p.year_gap),
                    "State":str(p.State),
                    "RunNumber":str(p.RunNumber),
                    "species":str(sp),
                    "species_pair_cluster":cluster,
                    "pair_cluster":pair_id
                })
    df=pd.DataFrame(rows)
    if len(df)<100000:
        raise RuntimeError(f"unexpectedly small risk set {len(df)}")

    formula=(
        "wet_activation ~ rain_contrast + temp_difference + doy_difference + "
        "year_gap + C(State) + C(RunNumber) + C(species)"
    )
    base=smf.glm(formula,data=df,family=sm.families.Binomial()).fit(maxiter=200,disp=0)
    name="rain_contrast"
    idx_name=list(base.params.index).index(name)
    beta=float(base.params[name])
    iid_se=float(base.bse[name])

    cov_sp=cov_cluster(base,df["species_pair_cluster"].to_numpy(),use_correction=True)
    sp_se=float(np.sqrt(cov_sp[idx_name,idx_name]))

    cov_pair=cov_cluster(base,df["pair_cluster"].to_numpy(),use_correction=True)
    pair_se=float(np.sqrt(cov_pair[idx_name,idx_name]))

    out={
        "analysis":"naamp_monitoring_independence_impact_v0_1",
        "contract":"exploration/NAAMP_MONITORING_INDEPENDENCE_IMPACT_CONTRACT_V0_1.json",
        "status":"posthoc_diagnostic_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "risk_set_species_stop_cells":int(len(df)),
            "species_pair_clusters":int(df.species_pair_cluster.nunique()),
            "pair_clusters":int(df.pair_cluster.nunique()),
            "species":int(df.species.nunique())
        },
        "model":{
            "formula":formula,
            "converged":bool(base.converged),
            "rain_contrast_beta":beta
        },
        "uncertainty":{
            "iid_model_based":term(beta,iid_se),
            "species_route_night_clustered":term(beta,sp_se),
            "route_pair_clustered":term(beta,pair_se),
            "species_route_night_se_inflation_ratio":float(sp_se/iid_se),
            "route_pair_se_inflation_ratio":float(pair_se/iid_se),
            "iid_to_species_cluster_information_ratio_heuristic":float((iid_se/sp_se)**2),
            "iid_to_route_pair_information_ratio_heuristic":float((iid_se/pair_se)**2)
        },
        "weather_provenance":{
            "era5_antecedent_amount_sha256":weather_sha
        },
        "interpretation":{
            "species_route_night_clustering_increases_se":bool(sp_se>iid_se),
            "route_pair_clustering_increases_se":bool(pair_se>iid_se),
            "exact_effect_on_published_occupancy_trend_estimator":False,
            "general_all_monitoring_models_claim":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
