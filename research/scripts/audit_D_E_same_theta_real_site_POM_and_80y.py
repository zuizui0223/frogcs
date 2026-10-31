"""Independent original-source audit joining SAME genuine80y theta model outputs
with BOTH real 4248-site six-pattern POM proxy results.

Every accepted model must carry the same network×context×plant×rate×q×mobility
across field site projection, original four-sign source POM and original
year80 patch occupancy. No model reruns, source shuffling, cherry-picked
seed, posterior fabricated from hypothetical rates or fitted observation
likelihood. All three outputs are audit-linked at source identity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

BACKGROUNDS=("uniform","target_group")
KEY=["network","scale","movement","structure_id","draw"]
COLUMNS=("OS","OV","SV","OSV","O_with_S_low","O_with_S_high")

def load(source_dir,sites_dir):
    original=pd.read_csv(Path(source_dir)/"same_run_model_native_F_signs_and_demography.csv")
    if (len(original)!=3072 or
        original.duplicated(KEY+["seed"]).any() or
        set(original.seed)!={101,102,103,104}):
        raise AssertionError("Original true80y full source structural sign table incomplete")
    alpha=(original.groupby(KEY,sort=True)
           .agg(n_biological_seed_labels=("seed","nunique"),
                source_four_sign_fraction_log1p=("matches_log1p","mean"),
                source_four_sign_fraction_raw=("matches_raw","mean"),
                source_year80_occupied=("f_year80_occupied_mean","mean"),
                source_local_reoccupation=("n_local_returns_mean","mean"))
           .reset_index())
    if len(alpha)!=768 or not alpha.n_biological_seed_labels.eq(4).all():
        raise AssertionError("Some posterior candidate was not simulated at 4 genuine seeds")
    combined=[]
    for background in BACKGROUNDS:
        folder=Path(sites_dir)/("frogcs-DE-same-theta-real4248-site-six-pattern-"+background)
        if not folder.exists():
            raise AssertionError("Expected both independent original-background site POM outputs")
        report=json.loads((folder/("receipt_"+background+".json")).read_text())
        if (report.get("status")!="ACTUAL_4248_SITE_SIX_PATTERN_PROXY_POM_SHARED_TRUE80Y_SOURCE_SUCCESS"
            or report.get("background")!=background
            or report.get("original_4248_acoustic_sites")!=4248
            or report.get("source_completed_surveys")!=63180
            or report.get("n_expected_four_seed_source_models")!=768
            or report.get("no_empirically_fitted_larval_to_adult_calling_process") is not True):
            raise AssertionError("Site POM original data and observation link no longer fixed")
        p=pd.read_csv(folder/("four_seed_expected_site_proxy_POM_"+background+".csv"))
        if (len(p)!=768 or p.duplicated(KEY).any() or
            not p.background.eq(background).all() or
            not p.n_original_stochastic_seeds.eq(4).all() or
            p.n_six_inside_marginal_95.isna().any()):
            raise AssertionError("Site POM only retained a selected network/biological rate")
        m=p.merge(alpha,on=KEY,validate="one_to_one",indicator=True)
        if len(m)!=768 or not m._merge.eq("both").all():
            raise AssertionError("Cannot join field proxy and actual year80 biology at SAME theta")
        if not np.allclose(m.mean_year80_occupied_frog_patches,
                           m.source_year80_occupied,rtol=0,atol=1e-8):
            raise AssertionError("Source year80 demographics were changed in site mapping")
        for field in COLUMNS:
            v="model_"+field
            for col in ("obs_"+field,v,"residual_"+field):
                if col not in m:
                    raise AssertionError("A real-site target was dropped: "+col)
            okay=m.status.eq("VALID_FOUR_SEED_EXPECTED_SITE_PROXY")
            if not np.allclose((m.loc[okay,v]-m.loc[okay,"obs_"+field]),
                                m.loc[okay,"residual_"+field],
                                rtol=0,atol=1e-9):
                raise AssertionError("Recorded source site residual was changed")
        m=m.drop(columns=["_merge"])
        combined.append(m)
    result=pd.concat(combined,ignore_index=True)
    if len(result)!=2*768:
        raise AssertionError("Missing observed background or biological model")
    # Both backgrounds have the exact SAME biological simulation hypothesis
    # and original year80 demographic response (different SDM site predictors).
    u=result[result.background.eq("uniform")].set_index(KEY).sort_index()
    t=result[result.background.eq("target_group")].set_index(KEY).sort_index()
    if not u.index.equals(t.index) or not np.array_equal(
        u.source_year80_occupied.to_numpy(),
        t.source_year80_occupied.to_numpy()):
        raise AssertionError("Background contrast changed the biological source")
    return result

def summarize(result,out):
    per_bg=[]
    for bg,g in result.groupby("background",sort=True):
        valid=g[g.status.eq("VALID_FOUR_SEED_EXPECTED_SITE_PROXY")]
        nfit=int(g.all_six_inside_marginal_95.sum())
        top=valid.nsmallest(1,"distance_mahalanobis")
        row=dict(background=bg,
            n_full_same_theta_candidate_models=len(g),
            n_finite_four_seed_source_site_models=len(valid),
            n_six_marginal_interval_compatible=nfit,
            minimum_source_site_mahalanobis=float(top.distance_mahalanobis.iloc[0])
                   if len(top) else np.nan,
            best_structural_network=(top.network.iloc[0] if len(top) else None),
            best_original_source_structure=(top.structure_id.iloc[0] if len(top) else None),
            best_original_biological_rate_draw=(int(top.draw.iloc[0]) if len(top) else None),
            best_synthetic_q=(int(top.scale.iloc[0]) if len(top) else None),
            best_annual_mobility=(top.movement.iloc[0] if len(top) else None),
            best_site_patterns_inside_95=(int(top.n_six_inside_marginal_95.iloc[0]) if len(top) else None),
            best_model_native_four_sign_fraction=(
                 float(top.source_four_sign_fraction_log1p.iloc[0]) if len(top) else None),
            best_original_source_year80_patch_occupancy=(
                 float(top.source_year80_occupied.iloc[0]) if len(top) else None))
        per_bg.append(row)
    outcome=pd.DataFrame(per_bg)
    networks=(result.groupby(["background","network"],sort=True)
       .agg(n_source_models=("draw","size"),
            n_six_compatible=("all_six_inside_marginal_95","sum"),
            mean_num_six_inside=("n_six_inside_marginal_95","mean"),
            min_mahalanobis=("distance_mahalanobis","min"),
            source_log1p_four_sign_fraction=("source_four_sign_fraction_log1p","mean"),
            source_year80_patches=("source_year80_occupied","mean"))
       .reset_index())
    if len(networks)!=2*6 or not networks.n_source_models.eq(128).all():
        raise AssertionError("Biological candidate family count changed after site POM")
    qmove=(result.groupby(["background","scale","movement"],sort=True)
       .agg(n_source_models=("draw","size"),
            n_six_compatible=("all_six_inside_marginal_95","sum"),
            min_distance=("distance_mahalanobis","min"),
            mean_patterns_in_observed_bands=("n_six_inside_marginal_95","mean"))
       .reset_index())
    if len(qmove)!=2*2*4 or not qmove.n_source_models.eq(96).all():
        raise AssertionError("Some nuisance parameter was optimized/selected away")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for filename,table in (
        ("all_original_same_theta_4248_site_POM_and_80year_outcomes.csv.gz",result),
        ("real_site_six_pattern_model_adequacy_by_background.csv",outcome),
        ("real_site_proxy_adequacy_by_directed_trophic_network.csv",networks),
        ("real_site_proxy_adequacy_by_q_and_mobility.csv",qmove)):
        table.to_csv(out/filename,index=False,compression=(
           {"method":"gzip","mtime":0} if filename.endswith(".gz") else None))
    receipt=dict(
       status="SAME_THETA_TRUE80Y_4248SITE_BOTH_BACKGROUNDS_INDEPENDENT_POM_AUDIT_SUCCESS",
       same_source_seasonal_trophic_and_finite_N_model=True,
       original_4_lhs_rate_vectors=4,
       n_actual_annual_mobility_modes=4,
       n_synthetic_population_scales=2,
       n_main_legal_source_plant_roles=2,
       n_original_timing_contexts=2,
       n_paired_directed_trophic_networks=6,
       n_source_stochastic_seed_replicates_each=4,
       n_source_biological_model_nuisance_candidates_each_bg=768,
       n_total_actual_site_mapped_model_background_rows=len(result),
       total_six_pattern_compatible_by_background={
           r.background:int(r.n_six_marginal_interval_compatible) for r in outcome.itertuples()
       },
       no_fitted_larval_to_adult_calling_model=True,
       no_actual_field_predator_density_estimation=True,
       site_four_seed_pattern_proxy_is_unfitted=True,
       population_demographic_predictions_conditionally_calibrated_to_wild=False,
       absolute_source_95_bands_not_joint_hypothesis_test=True)
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    words=[
        "# Frogcs D+E source-matched actual site POM plus SAME θ 80year consequences",
        "",
        "All 768 original true80year rate/structure/network/q/mobility models"
        " are source-joined across the two original 4248-site SDM backgrounds"
        " AND to their genuine stochastic four-seed demographic outputs.",
        "This is a *fixed coarse 2×2×2 trilinear supply proxy* and"
        " monotone F aquatic-to-acoustic rank assumption, NOT a biologically"
        " field-calibrated larval-to-adult observation link.",
        "",
        "## All-source six-pattern adequacy (same theta, each background)",
        "",
        outcome.to_markdown(index=False,floatfmt=".4f"),
        "",
        "## Directed trophic network comparisons against all six observed magnitudes",
        "",
        networks.to_markdown(index=False,floatfmt=".4f"),
        "",
        "## q and mobility nuisance assumptions are all included",
        "",
        qmove.to_markdown(index=False,floatfmt=".4f"),
        "",
        "The original prior ABC 4-sign model-native successes and the"
        " new actual-site 6-pattern proxy adequacy were both derived"
        " from the same genuine 80year source theta in this pilot."
        " Full empirical mechanism posterior support remains unearned"
        " unless proxy source mapping is adequate and externally defensible.",
        "",
        "The six observed 95% marginal intervals are descriptive, not a"
        " joint calibrated 95% test, and candidate count under a selected"
        " hypothetical four-rate design is not a biological prevalence."
        " Original 132-case POM used 9×9×2, so these 2×2×2 trilinear"
        " outputs are NOT replicates of that old 132-case mechanism library.",
    ]
    (out/"AUDITED_SAME_THETA_4248_SITE_POM_AND_LONGRUN_RESULT.md").write_text(
        "\n".join(words)+"\n")
    print("SAME_THETA_SITE_POM_80Y_JOIN_AUDIT_SUCCESS",
          json.dumps(receipt),flush=True)
    print("SOURCE_SITE_POM_BOTH_BACKGROUNDS\n"+outcome.to_string(index=False),flush=True)
    print("SOURCE_SITE_POM_DIRECTED_TROPHIC_NETWORKS\n"+
          networks.to_string(index=False),flush=True)
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--full-80y-audit",type=Path,required=True)
    p.add_argument("--two-site-POM-artifacts",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    x=load(a.full_80y_audit,a.two_site_POM_artifacts)
    summarize(x,a.output)
