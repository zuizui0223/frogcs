"""R5 response-blind, no-simulation data/model identifiability preflight.
Uses original G4 source two-arm eight-corner surfaces and G14 field geometry.
Never fits an observer simulation, searches effect strengths or estimates power.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

from g14_abc_ensemble_geographic_acoustic_holdout import read_field
from g5_source_constrained_acoustic_holdout_20261106 import (
    read_corner_source, features_by_background)
from g4_field_model_alignment_8corner_audit_20261106 import (
    original_rank01, predictor_basis)
from g1_shared_environment_spatial_block import design_matrices

SEED = 20261108
BG = ("uniform", "target_group")

def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(source_path: Path, out: Path):
    data, folds = read_field()
    source = read_corner_source(source_path)
    require(tuple(sorted(source)) == ("00", "11"),
            "Require both original off/on model-source arms")
    require(data.site.is_unique and len(data) == 4248, "Field site lost")
    require(data.n.sum() == 63180 and data.k.sum() == 36554, "Visits changed")
    require(data.spatial_block.nunique() == 56, "Blocks changed")
    require(data.V.sum() == 506 and len(np.unique(folds)) == 5, "V/fold changed")
    require(data.assign(fold=folds).groupby("spatial_block").fold.nunique().eq(1).all(),
            "Spatial fold leakage")

    spatial = {}
    full = {}
    for bg in BG:
        o = original_rank01(data["mean_suitability_Odonata_" + bg])
        s = original_rank01(data["mean_suitability_pond_breeding_Caudata_" + bg])
        v = data.V.to_numpy(dtype=float)
        q = predictor_basis(o, s, v)
        require(np.linalg.matrix_rank(q) == 8, "Original O/S/V eight basis rank deficient")
        dims = {}
        designs, _ = features_by_background(data, bg, source)
        for arm in ("00", "11"):
            # Genuine original G4 log aquatic frog-cohort surface, not observed calls.
            y = q @ source[arm]
            x = designs["env_all"]
            xf = np.column_stack((np.ones(len(data)), x))
            beta = np.linalg.lstsq(xf, y, rcond=None)[0]
            resid = np.max(np.abs(xf @ beta - y))
            require(resid < 1e-8,
                    "Original source surface outside unrestricted observation covariates")
            dims[arm] = {
                "source_log_cohort_range": [float(y.min()), float(y.max())],
                "source_log_cohort_sd": float(y.std()),
                "max_saturated_OLS_projection_residual": float(resid),
                "source_has_unique_field_linear_dimension": False,
            }
            full[bg + "_" + arm] = y
        contrast = full[bg + "_11"] - full[bg + "_00"]
        # Residual after flexible additive environmental predictors, not an estimate
        # of wild trophic signal or biological effect.
        z = np.column_stack((np.ones(len(data)), design_matrices(data,bg)["flex_add"]))
        residual = contrast - z @ np.linalg.lstsq(z,contrast,rcond=None)[0]
        spatial[bg] = {
            "source": dims,
            "model_11_minus_00_mean_log_cohort": float(contrast.mean()),
            "model_11_minus_00_sd_over_sites": float(contrast.std()),
            "model_11_minus_00_95pct_site_distribution": list(
                map(float,np.quantile(contrast,[.025,.975]))),
            "contrast_residual_sd_after_flexible_additive": float(residual.std()),
            "source_contrast_nonzero": bool(np.std(contrast) > 1e-10),
            "spatial_blocks": int(data.spatial_block.nunique()),
            "sites": int(len(data)),
            "surveys": int(data.n.sum()),
            "mapped_vegetation_positive_sites": int(data.V.sum()),
        }
    rank = {}
    for group in ("Odonata", "pond_breeding_Caudata"):
        a = data["mean_suitability_" + group + "_uniform"].to_numpy(dtype=float)
        b = data["mean_suitability_" + group + "_target_group"].to_numpy(dtype=float)
        rank[group] = float(spearmanr(a,b).statistic)
    result = {
        "status": "R5_RESPONSE_BLIND_SOURCE_GEOMETRY_PREFLIGHT_PASS",
        "frozen_protocol": "research/R5_VIRTUAL_ECOLOGIST_OBSERVABILITY_FROZEN_PROTOCOL_2026-11-08.md",
        "source_origin": "original G4 original source 42173236906",
        "original_g4_input_sha256": sha(source_path),
        "original_sampling_site_count": 4248,
        "original_completed_visits": 63180,
        "original_strong_event_count": 36554,
        "original_spatial_blocks": 56,
        "original_sites_with_landscape_V": 506,
        "conditional_true_rank_worlds": list(BG),
        "source_model_arms": ["00","11"],
        "structural_eight_term_span_proven_exactly": True,
        "independent_natural_trophic_mechanism_identified": False,
        "adult_acoustics_to_larval_abundance_calibrated": False,
        "pond_vegetation_to_landscape_error_calibrated": False,
        "observed_salamander_arrival_duration": False,
        "observed_SDM_background_spearman": rank,
        "per_rank_world": spatial,
        "observer_simulation_replicates": 0,
        "power_estimated": False,
        "empirical_reason_for_original_G14_failure_identified": False,
    }
    out.mkdir(parents=True,exist_ok=True)
    (out/"R5_RESPONSE_BLIND_ORIGINAL_GEOMETRY_PREFLIGHT.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("R5_RESPONSE_BLIND_ORIGINAL_GEOMETRY_PREFLIGHT_PASS",
          json.dumps({k:v for k,v in result.items()
            if k in ("status","original_sampling_site_count","original_spatial_blocks",
                    "structural_eight_term_span_proven_exactly",
                    "power_estimated","observed_SDM_background_spearman")}),flush=True)

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.source,a.out)
