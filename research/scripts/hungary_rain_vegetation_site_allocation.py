#!/usr/bin/env python3
"""Real Hungary wetland: rain × emergent/depth environmental interaction.

This is a POST-HOC exploratory extension of existing site-blocked model
(Mizsei & Wenner 2025, 29 wetlands, 129 acoustic visits in spring 2024).
Rain = actual source 'prec', not NAAMP 72h antecedent precipitation.
Depth = source site scalar, NOT hydroperiod-days or pond dry-down.
Response is frog presence under 'acoustic' survey, NOT chorus index intensity
or RC6 multi-site concentration. No predator or tadpole stage surveyed here.

Frozen source/effect test:
research/CHORUS_RAIN_VEGETATION_HYDROPERIOD_STAGE_COMPETITION_SPEC_2026-10-26.md
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from hungary_vegetation_chorus import load_data, BASE

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"research/external/zenodo_15044115"
PROTOCOL="research/CHORUS_RAIN_VEGETATION_HYDROPERIOD_STAGE_COMPETITION_SPEC_2026-10-26.md"
EXPECTED_BRIER_BASELINE=0.17419253217986866
NUMERIC={
 "E1_weather_depth_site_context":BASE+["depth"],
 "E2_rain_x_emergent":BASE+["depth","cover_emerged","rain_x_emergent"],
 "E3_plus_rain_x_depth":BASE+["depth","cover_emerged","rain_x_emergent","rain_x_depth"],
}
SEED=20261026

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    sites,visits,allrows=load_data(SOURCE)
    a=allrows.loc[allrows.method=="acoustic"].copy().reset_index(drop=True)
    assert len(a)==129 and a.site.nunique()==29
    a["rain_x_emergent"]=a.prec.astype(float)*a.cover_emerged.astype(float)
    a["rain_x_depth"]=a.prec.astype(float)*a.depth.astype(float)
    a["frog_any"]=a.frog_any.astype(int)
    ids=a.site.astype(str).to_numpy()
    y=a.frog_any.to_numpy()
    splits=list(GroupKFold(5).split(a,y,ids))
    otu={}
    for name,columns in NUMERIC.items():
        probs=np.full(len(a),np.nan)
        for tr,te in splits:
            prep=ColumnTransformer([
                ("num",StandardScaler(),columns),
                ("category",OneHotEncoder(handle_unknown="ignore"),["ci"]),
            ])
            model=Pipeline([("prep",prep),
                            ("model",LogisticRegression(C=1,max_iter=3000))])
            if len(set(y[tr]))!=2:raise ValueError("Training fold response single class")
            model.fit(a.iloc[tr][columns+["ci"]],y[tr])
            probs[te]=model.predict_proba(a.iloc[te][columns+["ci"]])[:,1]
        if not np.isfinite(probs).all():raise ValueError("No predictions for held-out site")
        pp=np.clip(probs,1e-9,1-1e-9)
        otu[name]={
          "brier":(y-probs)**2,
          "logloss":-(y*np.log(pp)+(1-y)*np.log(1-pp)),
        }
    groups=sorted(set(ids))
    for name,r in otu.items():
        r["brier_site"]=np.array([np.mean(r["brier"][ids==site]) for site in groups])
        r["logloss_site"]=np.array([np.mean(r["logloss"][ids==site]) for site in groups])
    baseline=float(np.mean(otu["E1_weather_depth_site_context"]["brier_site"]))
    if abs(baseline-EXPECTED_BRIER_BASELINE)>0.002:
        raise ValueError(f"Historical prefit baseline drift {baseline} != {EXPECTED_BRIER_BASELINE}")
    rng=np.random.default_rng(SEED)
    draw=rng.integers(0,len(groups),size=(2000,len(groups)))
    outcomes={}
    for name,r in otu.items():
        outcomes[name]={
          "site_equal_weight_brier":float(np.mean(r["brier_site"])),
          "site_equal_weight_logloss":float(np.mean(r["logloss_site"])),
          "individual_visit_brier":float(np.mean(r["brier"])),
          "individual_visit_logloss":float(np.mean(r["logloss"])),
        }
    comparisons={}
    for full,ref in [("E2_rain_x_emergent","E1_weather_depth_site_context"),
                     ("E3_plus_rain_x_depth","E2_rain_x_emergent"),
                     ("E3_plus_rain_x_depth","E1_weather_depth_site_context")]:
        rec={}
        for metric in ("brier_site","logloss_site"):
            delta=otu[ref][metric]-otu[full][metric]
            ci=np.quantile(np.mean(delta[draw],axis=1),[.025,.975])
            rec[metric]={
              "positive_means_added_term_helps":True,
              "site_equal_weight_heldout_gain":float(np.mean(delta)),
              "ci95_site_resample_conditional_oof":[float(x) for x in ci],
            }
        comparisons[full+"_vs_"+ref]=rec
    rainvals=a.prec.to_numpy(dtype=float)
    days=a.groupby("date").site.nunique()
    out={
      "status":"OBSERVED_EXPLORATORY_RAIN_WETLAND_PLANT_ACOUSTIC_SITE_TEST",
      "study":"Mizsei & Wenner (2025), Zenodo 10.5281/zenodo.15044115, CC BY 4.0",
      "source_experiment":"Observational one-year Hungarian restored wetlands, not randomized rain",
      "frozen_postRC6_protocol":PROTOCOL,
      "n_sites":len(groups),"n_acoustic_visits":len(a),
      "n_acoustic_frog_positive_visits":int(y.sum()),
      "n_acoustic_dates":int(days.size),
      "days_with_3plus_source_sites":int(np.sum(days>=3)),
      "days_with_5plus_source_sites":int(np.sum(days>=5)),
      "prec_missing":int(np.sum(~np.isfinite(rainvals))),
      "prec_observed_range":[float(np.min(rainvals)),float(np.max(rainvals))],
      "source_emergent_cover_pct_range":[float(a.cover_emerged.min()),float(a.cover_emerged.max())],
      "source_submerged_cover_pct_range":[float(a.cover_submers.min()),float(a.cover_submers.max())],
      "source_one_time_water_depth_range":[float(a.depth.min()),float(a.depth.max())],
      "previous_2026_10_25_archived_W1_site_Brier":EXPECTED_BRIER_BASELINE,
      "current_environment_original_baseline_site_Brier":baseline,
      "current_vs_archived_W1_implementation_drift":baseline-EXPECTED_BRIER_BASELINE,
      "baseline_compatibility_within_0p002":True,
      "method_note":"New models compared on same rows/current environment; old archived fit differs slightly, do not subtract coefficients across distinct execution environments.",
      "models":outcomes,"frozen_addition_comparisons":comparisons,
      "source_rain_is_72h_NAAMP_contrast":False,
      "source_depth_is_hydroperiod_duration":False,
      "true_RC6_multisite_concentration_C_estimated":False,
      "source_predator_stage_abundance_measured":False,
      "frog_competition_causally_identified":False,
      "description":"Binary frog acoustic detection, not calling intensity or breeding success",
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BEGIN_HUNGARY_RAIN_VEG_STAGE_SCOPE")
    print(json.dumps(out,ensure_ascii=False,indent=2))
    print("END_HUNGARY_RAIN_VEG_STAGE_SCOPE")
if __name__=="__main__":main()
