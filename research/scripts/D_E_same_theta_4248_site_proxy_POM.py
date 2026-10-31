"""Fixed same-theta source F cohort -> actual 4,248-site six-statistic POM.

This SECOND STEP is an observational PROXY comparison, not a calibrated
larval-to-adult calling model. It consumes ORIGINAL 80y actual finite-N
source F_B and year80 occupied patches; it does not simulate biology again.

The source V,S,D vertex cube is projected by a FROZEN positive-convex
trilinear map over the original observed binary site V and GLOBAL
percentile rank of Odonata/pond-Caudata SDM suitability, not inferred
wild nymph/salamander densities. No response fitting, arbitrary rank
noise, outcome-based warp or post hoc thresholds permitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from select_macro_trophic_scenarios import SITE,VISITS,load_cohort,ROOT
from pattern_oriented_abc_pilot import (
    BACKGROUNDS,PATTERNS,HOLDOUT,SEED,
    get_design,stats_from_y,bootstrap_observed,
    bootstrap_heldout,compare_frozen_macro
)

EXPECTED_SITES=4248
EXPECTED_COMPLETED_VISITS=63180
PREDICTOR_NAMES=("OS","OV","SV","OSV","O_with_S_low","O_with_S_high")
MODEL_KEY=["network","scale","movement","seed","structure_id","draw"]
FIELDS=("mean_cohort_B_last_window","final_occupied_patches",
        "n_local_returns","n_local_extinctions")
VERTICES=tuple((v,s,d) for v in (0,1) for s in (0,1) for d in (0,1))


def original_sites():
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=EXPECTED_SITES)
    if (len(d)!=EXPECTED_SITES or int(d.n.sum())!=EXPECTED_COMPLETED_VISITS
        or int(d.V.sum())!=506 or d.site.duplicated().any()):
        raise AssertionError("Actual original NAAMP source denominator/schema changed")
    return d


def trilinear_source_site_weights(data,background):
    """Original exact source cube V,S,D -> real SOURCE covariate ranks."""
    if background not in BACKGROUNDS:
        raise ValueError("Unexpected SDM background")
    n=len(data)
    V=data.V.to_numpy(int)
    if not np.isin(V,[0,1]).all():
        raise ValueError("Original site vegetation must be source binary 0/1")
    o=data[f"mean_suitability_Odonata_{background}"].to_numpy(float)
    s=data[f"mean_suitability_pond_breeding_Caudata_{background}"].to_numpy(float)
    if not (np.isfinite(o).all() and np.isfinite(s).all()):
        raise ValueError("Original source site covariates nonfinite")
    pp=lambda x:(rankdata(x,method="average")-.5)/len(x)
    orank=pp(o);srank=pp(s)
    weights=np.column_stack([
        (V==v).astype(float)*
        (srank if ss else 1-srank)*
        (orank if dd else 1-orank)
        for v,ss,dd in VERTICES
    ])
    if (weights.shape!=(n,8) or
        not np.allclose(weights.sum(axis=1),1,rtol=0,atol=1e-12) or
        (weights<0).any() or
        (weights>1).any()):
        raise AssertionError("Observed site/source corner mixing weights not convex")
    return weights


def source_model_groups(folder):
    path=Path(folder)/"source_genuine_80year_all_guild_scenarios.csv.gz"
    if not path.exists():
        raise AssertionError("Original complete 16-shard genuine 80year model artifact required")
    data=pd.read_csv(path)
    if (len(data)!=73728 or
        set(data.network)!={"all_active","SF_only","no_SF","no_DF","no_DS","all_off"} or
        set(data.scale)!={3,12} or
        set(data.movement)!={"off","recruits","carryover","both"} or
        set(data.draw)!={0,4,8,12} or
        set(data.seed)!={101,102,103,104} or
        set(data.context)!={"original","D_first_S_overtakes"} or
        set(data.plant_model)!={"SF1_DF0_DS0_L1","SF0_DF0_DS1_L0"} or
        data.duplicated([*MODEL_KEY,"vertex","guild"]).any()):
        raise AssertionError("Original same biological source θ×network×nuisance not complete")
    a=data[data.guild.eq("F")].copy()
    if len(a)!=73728//3:
        raise AssertionError("Missing actual F aquatic cohorts")
    return a


def six_pattern_site_POM(data,source,F_background,out,boot=999):
    if F_background not in BACKGROUNDS or boot!=999:
        raise ValueError("Only frozen original SDM background and 999 spatial resamples")
    design=get_design(data,F_background)
    observed,holdobs=stats_from_y(data.strong_rate.to_numpy(float),
                                   design,holdout=True)
    compare_frozen_macro(observed,F_background)
    bootdata,cov,inv,diagnostics=bootstrap_observed(
        data.strong_rate.to_numpy(float),design,data.spatial_block,
        n_boot=boot,seed=SEED
    )
    holdboot=bootstrap_heldout(
        data.strong_rate.to_numpy(float),design,data.spatial_block,
        n_boot=boot,seed=SEED)
    low=np.quantile(bootdata,.025,axis=0)
    high=np.quantile(bootdata,.975,axis=0)
    w=trilinear_source_site_weights(data,F_background)
    records=[]
    for key,g in source.groupby(MODEL_KEY,sort=True):
        g=g.sort_values("vertex")
        if (len(g)!=8 or set(g.vertex)!=set(range(8)) or
            g.context.nunique()!=1 or g.plant_model.nunique()!=1):
            raise AssertionError("One true source theta×structure group lost 8 VSD vertices")
        y=g.mean_cohort_B_last_window.to_numpy(float)
        if not np.isfinite(y).all() or (y<0).any():
            raise AssertionError("80y cohort mean not a valid biological response")
        predicted=w@y
        rec=dict(zip(MODEL_KEY,key))
        rec.update(background=F_background,context=g.context.iloc[0],
            plant_model=g.plant_model.iloc[0],
            mean_year80_occupied_frog_patches=float(g.final_occupied_patches.mean()),
            mean_model_local_reoccupation_events=float(g.n_local_returns.mean()),
            mean_model_local_extinctions=float(g.n_local_extinctions.mean()),
            proxy_observation_map="ORIGINAL_2X2X2_TRILINEAR_GLOBAL_PERCENTILE_UNFITTED",
            empirical_mechanism_posterior=False)
        if not np.isfinite(predicted).all():
            raise AssertionError("Invalid actual-site source response interpolation")
        if np.ptp(predicted)<1e-12:
            rec.update(status="DEGENERATE_SITE_PREDICTION",
                       n_six_inside_marginal_95=0,distance_mahalanobis=np.nan)
            for pattern in PATTERNS:
                rec["obs_"+pattern]=float(observed[PATTERNS.index(pattern)])
                rec["model_"+pattern]=np.nan
                rec["residual_"+pattern]=np.nan
            records.append(rec)
            continue
        try:
            stats,hold=stats_from_y(predicted,design,holdout=True)
        except ValueError:
            rec.update(status="DEGENERATE_SITE_PREDICTION",
                       n_six_inside_marginal_95=0,distance_mahalanobis=np.nan)
            for pattern in PATTERNS:
                rec["obs_"+pattern]=float(observed[PATTERNS.index(pattern)])
                rec["model_"+pattern]=np.nan
                rec["residual_"+pattern]=np.nan
            records.append(rec)
            continue
        delta=stats-observed
        distance=float(delta@inv@delta)
        n_inside=int(np.sum((stats>=low)&(stats<=high)))
        rec.update(status="VALID_MODEL_NATIVE_SITE_PROXY",
            distance_mahalanobis=distance,
            n_six_inside_marginal_95=n_inside,
            all_six_inside_marginal_95=bool(n_inside==6),
            n_site_predictor_records=EXPECTED_SITES,
            sampled_source_data_uncertainty="56_BLOCK_ORIGINAL_999_SOURCE_BOOTSTRAPS")
        for i,pattern in enumerate(PATTERNS):
            rec["obs_"+pattern]=float(observed[i])
            rec["model_"+pattern]=float(stats[i])
            rec["residual_"+pattern]=float(delta[i])
        for i,pattern in enumerate(HOLDOUT):
            rec["observed_holdout_"+pattern]=float(holdobs[i])
            rec["model_holdout_"+pattern]=float(hold[i])
            rec["holdout_inside_observed_95_"+pattern]=bool(
                np.quantile(holdboot[:,i],.025)<=hold[i]<=
                np.quantile(holdboot[:,i],.975))
        records.append(rec)
    result=pd.DataFrame(records)
    if (len(result)!=3072 or result.duplicated(MODEL_KEY).any() or
        set(result.background)!={F_background} or
        result.n_six_inside_marginal_95.isna().any()):
        raise AssertionError("Actual NAAMP site POM incomplete or outcome-selected")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/("same_theta_80y_4248_site_proxy_POM_"+F_background+".csv.gz"),
                  index=False,compression={"method":"gzip","mtime":0})
    diagnostics=dict(diagnostics)
    report=dict(status="ACTUAL_4248_SITE_SIX_PATTERN_PROXY_POM_SHARED_TRUE80Y_SOURCE_SUCCESS",
         background=F_background,
         original_4248_acoustic_sites=EXPECTED_SITES,
         source_completed_surveys=EXPECTED_COMPLETED_VISITS,
         observed_six_pattern_statistics=dict(zip(PATTERNS,map(float,observed))),
         observed_six_marginal_95_intervals={
            p:[float(lo),float(hi)] for p,lo,hi in zip(PATTERNS,low,high)},
         source_spatial_block_uncertainty=diagnostics,
         n_same_theta_80y_model_cases=len(result),
         n_valid_proxy_cases=int(result.status.eq("VALID_MODEL_NATIVE_SITE_PROXY").sum()),
         n_degenerate_model_cases=int(result.status.eq("DEGENERATE_SITE_PREDICTION").sum()),
         n_all_six_marginal_pattern_cases=int(
             result.get("all_six_inside_marginal_95",pd.Series(False,index=result.index))
                   .fillna(False).sum()),
         absolute_min_valid_mahalanobis=float(result.distance_mahalanobis.min())
              if np.isfinite(result.distance_mahalanobis).any() else None,
         source_unchanged_biological_theta_from_same_80year_run=True,
         original_source_2x2x2_coarse_interpolation=True,
         original_macro_132_scenario_9x9_grids_not_numerically_replicated=True,
         no_empirically_fitted_larval_to_adult_calling_process=True,
         this_is_not_a_wild_trophic_causal_posterior=True,
         original_site_SHA256=hashlib.sha256(SITE.read_bytes()).hexdigest(),
         original_visits_SHA256=hashlib.sha256(VISITS.read_bytes()).hexdigest(),
         source_script_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/("receipt_"+F_background+".json")).write_text(json.dumps(report,indent=2)+"\n")
    print("TRUE80Y_SAME_THETA_SITE_POM_"+F_background.upper(),
          json.dumps({k:v for k,v in report.items() if k in (
              "n_same_theta_80y_model_cases","n_valid_proxy_cases",
              "n_all_six_marginal_pattern_cases",
              "absolute_min_valid_mahalanobis",
              "n_degenerate_model_cases")}),flush=True)
    top=result[result.status.eq("VALID_MODEL_NATIVE_SITE_PROXY")].nsmallest(
        8,"distance_mahalanobis")
    print("TOP_SAME_THETA_FIELD_PROXY_CANDIDATES_"+F_background.upper()+"\n"+
          top[["network","context","plant_model","draw","scale",
               "movement","seed","distance_mahalanobis",
               "n_six_inside_marginal_95",
               "obs_O_with_S_low","model_O_with_S_low",
               "obs_OSV","model_OSV"]].to_string(index=False),flush=True)
    return result,report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--background",choices=BACKGROUNDS,required=True)
    a=p.parse_args()
    src=source_model_groups(a.input)
    sites=original_sites()
    six_pattern_site_POM(sites,src,a.background,a.output)
