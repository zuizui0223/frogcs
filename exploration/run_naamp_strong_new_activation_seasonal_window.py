#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_STRONG_NEW_ACTIVATION_SEASONAL_WINDOW_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec)
    assert spec.loader; spec.loader.exec_module(mod); return mod

strength=loadmod("strength_base",EXP/"run_naamp_new_activation_strength.py")
base=strength.base; spatial=strength.spatial

def fit_window(df):
    formula="strong_new_score ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State)"
    m=smf.ols(formula,data=df).fit(cov_type="cluster",cov_kwds={"groups":df["route_cluster"]})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {
      "n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique()),
      "beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"]),
      "formula":formula
    }

def main():
    raw=base.load(); runs,sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible); by=strength.build_ci(raw,eligible,sampled)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    rows=[]
    for p in pairs.itertuples(index=False):
        r=p._asdict(); r.update(strength.metrics(p,sampled,by)); rows.append(r)
    df=pd.DataFrame(rows)

    reports={}
    eligible_windows=[]
    for rn,g in df.groupby(df["RunNumber"].astype(str),sort=True):
        n=len(g); nr=int(g.route_cluster.nunique())
        estimable=bool(n>=300 and nr>=75)
        rep={"n_pairs":int(n),"n_routes":nr,"estimable":estimable}
        if estimable:
            rep.update(fit_window(g.copy()))
            eligible_windows.append(str(rn))
        reports[str(rn)]=rep

    formula="strong_new_score ~ rain_contrast * C(RunNumber) + temp_difference + doy_difference + year_gap + C(State)"
    m=smf.ols(formula,data=df).fit(cov_type="cluster",cov_kwds={"groups":df["route_cluster"]})
    names=list(m.params.index)
    interaction_names=[
        name for name in names
        if "rain_contrast:C(RunNumber)" in name or "C(RunNumber)" in name and ":rain_contrast" in name
    ]
    if interaction_names:
        R=np.zeros((len(interaction_names),len(names)),float)
        for i,name in enumerate(interaction_names):
            R[i,names.index(name)]=1.0
        wt=m.wald_test(R,scalar=True)
        joint_p=float(wt.pvalue)
        joint_stat=float(np.asarray(wt.statistic).reshape(-1)[0])
    else:
        joint_p=joint_stat=None

    directional=bool(eligible_windows and all(reports[w]["beta"]>0 for w in eligible_windows))
    strong=bool(eligible_windows and all(reports[w]["ci95"][0]>0 for w in eligible_windows))
    output={
      "analysis":"naamp_strong_new_activation_seasonal_window_audit_v0_1",
      "contract":"exploration/NAAMP_STRONG_NEW_ACTIVATION_SEASONAL_WINDOW_CONTRACT_V0_1.json",
      "eligible_windows":eligible_windows,
      "windows":reports,
      "interaction":{
        "formula":formula,
        "terms":interaction_names,
        "joint_wald_stat":joint_stat,
        "joint_p":joint_p
      },
      "classification":{
        "directional_generality":directional,
        "strong_generality":strong
      },
      "interpretation_boundary":{
        "single_season_only_supported":False if directional else None,
        "identical_effect_across_windows":False,
        "species_strategy_mechanism_identified":False,
        "causal_rainfall_claim":False
      }
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n"); print(json.dumps(output,indent=2,sort_keys=True))

if __name__=="__main__": main()
