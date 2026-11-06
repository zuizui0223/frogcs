"""Diagnose archived G5 predictions; no model fitting or new source selection.

The original G4/G5 artifacts and field file are checked byte-for-byte before
context aggregation. Contextual prediction gains are not vegetation effects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


CANDIDATES = ("env_add", "env_all", "flex_add", "flex_all", "flex_prior_00", "flex_prior_11")
BACKGROUNDS = ("uniform", "target_group")
SOURCE_SHA256 = {
    "primary_site_landscape_context.csv.gz": "cbb389264f8bf167f53b5dfd38c5e1a17aec6243cc6ce30cbb7ae3b5417f75ff",
    "G4_all_4248_site_source_tertile_assignments.csv.gz": "948195dd1419d01693c41b02c652c96650bcdc64f2cf1c643481be6548385ea8",
    "G4_source_geometry_receipt.json": "585a2c5d32db0f874351b9a2847461c5bf93ee79392c1e5a24fef343244abe58",
    "G5_4248_original_site_source_holdout_predictions.csv.gz": "037a363a8b327d8cb3ad003b4baee0f14e33cc5e3b69bf18b690cc7f03eced49",
    "G5_original_site_binomial_acoustic_scores.csv": "160b0c85f09d13255486f4800d89b14382596b5f03a381c0fbd1bb344ef182b0",
    "G5_source_constrained_observation_receipt.json": "2370895c4c9f1635ce9799e0b31bf023e33e20fbd00fd9236241e02331a3d025",
}


def build_wide(predictions, classifications, sites):
    """Retain each source site/background once; reject unpaired source records."""
    p, c, raw = predictions.copy(), classifications.copy(), sites.copy()
    keys = ["site", "background"]
    required_p = set(keys + ["route", "spatial_block", "fold", "candidate", "n_completed", "k_strong", "predicted"])
    required_c = set(keys + ["route", "spatial_block", "vegetation", "caudata_tertile", "odonata_tertile", "n_completed", "n_strong"])
    required_raw = {"site", "strong_rate", "flooded_3000m_mean"} | {"mean_suitability_Odonata_" + bg for bg in BACKGROUNDS}
    if not required_p.issubset(p) or not required_c.issubset(c) or not required_raw.issubset(raw):
        raise ValueError("incomplete source columns")
    if p.duplicated(keys + ["candidate"]).any() or c.duplicated(keys).any() or raw.site.duplicated().any():
        raise ValueError("duplicate source site/candidate record")
    if not np.isfinite(p.predicted).all() or not p.predicted.between(0, 1, inclusive="neither").all():
        raise ValueError("invalid source probability")
    if set(p.background) != set(BACKGROUNDS) or set(c.background) != set(BACKGROUNDS):
        raise ValueError("incomplete source backgrounds")
    if set(p.candidate) != set(CANDIDATES) or not p.groupby(keys).candidate.nunique().eq(len(CANDIDATES)).all():
        raise ValueError("incomplete candidate/site matrix")
    meta = ["route", "spatial_block", "fold", "n_completed", "k_strong"]
    if not p.groupby(keys)[meta].nunique(dropna=False).eq(1).all().all():
        raise ValueError("conflicting source metadata or fold")
    if p[meta].isna().any().any():
        raise ValueError("missing source metadata")
    base = p[keys + meta].drop_duplicates(keys)
    probs = p.pivot(index=keys, columns="candidate", values="predicted").reset_index()
    wide = base.merge(probs, on=keys, validate="one_to_one")
    c = c.rename(columns={"vegetation": "V", "n_strong": "k_strong"})
    wide = wide.merge(c[list(required_c - {"vegetation", "n_strong"}) + ["V", "k_strong"]],
                      on=keys, how="outer", suffixes=("", "_g4"), validate="one_to_one", indicator=True)
    if not wide["_merge"].eq("both").all():
        raise ValueError("source site coverage mismatch")
    wide = wide.drop(columns="_merge")
    for name in ("route", "spatial_block", "n_completed", "k_strong"):
        if not wide[name].eq(wide[name + "_g4"]).all():
            raise ValueError("G4/G5 " + name + " mismatch")
        wide = wide.drop(columns=name + "_g4")
    if set(wide.site) != set(raw.site):
        raise ValueError("raw field site coverage mismatch")
    wide = wide.merge(raw[list(required_raw)], on="site", validate="many_to_one")
    wide["observed_rate"] = wide.k_strong / wide.n_completed
    if not np.allclose(wide.observed_rate, wide.strong_rate, atol=1e-12, rtol=0):
        raise ValueError("original field strong-call fraction mismatch")
    if not wide.V.eq((wide.flooded_3000m_mean > 0).astype(int)).all():
        raise ValueError("original vegetation classification mismatch")
    wide["odonata_suitability"] = np.where(
        wide.background.eq("uniform"), wide.mean_suitability_Odonata_uniform,
        wide.mean_suitability_Odonata_target_group)
    if not wide.groupby("site")[meta + ["V"]].nunique().eq(1).all().all():
        raise ValueError("between-background source metadata mismatch")
    if wide.groupby("spatial_block").fold.nunique().max() != 1:
        raise ValueError("geographic source fold mismatch")
    return wide.sort_values(keys).reset_index(drop=True)


def run(sites, g4_dir, g5_dir, out):
    from g6_context_diagnostic import analyze_contexts
    from g6_rank_pattern_diagnostic import summarize_rank_patterns

    g4_dir, g5_dir, out = Path(g4_dir), Path(g5_dir), Path(out)
    paths = {"primary_site_landscape_context.csv.gz": Path(sites)}
    for name in SOURCE_SHA256:
        if name.startswith("G4_"):
            paths[name] = g4_dir / name
        elif name.startswith("G5_"):
            paths[name] = g5_dir / name
    actual_hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
    if actual_hashes != SOURCE_SHA256:
        raise ValueError("an original source file failed the pinned SHA256 check")
    g4 = json.loads(paths["G4_source_geometry_receipt.json"].read_text())
    g5 = json.loads(paths["G5_source_constrained_observation_receipt.json"].read_text())
    if g4["observed_cells_supported"] != 15 or g5["independent_geographic_predictive_gain_both_backgrounds"]:
        raise ValueError("original source G4/G5 conclusion changed")
    pred = pd.read_csv(paths["G5_4248_original_site_source_holdout_predictions.csv.gz"])
    classes = pd.read_csv(paths["G4_all_4248_site_source_tertile_assignments.csv.gz"])
    raw = pd.read_csv(sites)
    wide = build_wide(pred, classes, raw)
    for bg, d in wide.groupby("background"):
        observed = (len(d), int(d.n_completed.sum()), int(d.k_strong.sum()),
                    d.route.nunique(), d.spatial_block.nunique(), int(d.V.sum()))
        if observed != (4248, 63180, 36554, 432, 56, 506):
            raise ValueError("original cohort changed: " + bg + " " + str(observed))
    # Source-only tertile replay; no acoustic outcomes enter the boundaries.
    cuts = []
    for bg in BACKGROUNDS:
        d = wide[wide.background.eq(bg)].set_index("site")
        original = raw.set_index("site").loc[d.index]
        for guild, prefix in (("caudata", "mean_suitability_pond_breeding_Caudata_"),
                              ("odonata", "mean_suitability_Odonata_")):
            values = original[prefix + bg].to_numpy(float)
            quantiles = np.quantile(values, [1 / 3, 2 / 3])
            if not np.array_equal(np.searchsorted(quantiles, values, side="left"), d[guild + "_tertile"]):
                raise ValueError("original predictor tertile changed")
            cuts.append(dict(background=bg, guild=guild, cut_low=quantiles[0], cut_high=quantiles[1]))
    context = analyze_contexts(wide)
    ranks = summarize_rank_patterns(wide)
    old_scores = pd.read_csv(paths["G5_original_site_binomial_acoustic_scores.csv"])
    replay = context["scores"].query("partition == 'all'").merge(
        old_scores[["background", "candidate", "nll_per_visit", "brier_per_visit"]],
        on=["background", "candidate"], suffixes=("", "_original"), validate="one_to_one")
    replay["nll_absolute_error"] = abs(replay.nll_per_visit - replay.nll_per_visit_original)
    replay["brier_absolute_error"] = abs(replay.brier_per_visit - replay.brier_per_visit_original)
    if len(replay) != 12 or replay[["nll_absolute_error", "brier_absolute_error"]].to_numpy().max() > 1e-12:
        raise ValueError("original G5 score replay failed")
    original_rho = {"uniform": -0.38475, "target_group": -0.17869}
    for bg, expected in original_rho.items():
        r = ranks[(ranks.background == bg) & (ranks.subset == "all") & (ranks.response == "observed_rate")]
        if len(r) != 1 or abs(r.iloc[0].contrast_high_minus_low - expected) > 1e-5:
            raise ValueError("original observed R1 point contrast replay failed: " + bg)
    conservation_errors = []
    for (bg, baseline), a in context["gains"].groupby(["background", "baseline"]):
        total = a[a.partition.eq("all")].gain_per_visit.iloc[0]
        for partition in ("V", "V_S", "V_S_O"):
            contribution = a[a.partition.eq(partition)].full_total_weighted_contribution.sum()
            conservation_errors.append(abs(total - contribution))
    if max(conservation_errors) > 1e-12:
        raise ValueError("context contributions do not conserve original whole-cohort gain")
    out.mkdir(parents=True, exist_ok=True)
    for key, table in context.items():
        table.to_csv(out / ("G6_context_" + key + ".csv"), index=False)
    ranks.to_csv(out / "G6_R1_observed_and_heldout_rank_contrasts.csv", index=False)
    replay.to_csv(out / "G6_original_G5_score_replay.csv", index=False)
    pd.DataFrame(cuts).to_csv(out / "G6_original_predictor_tertile_boundaries.csv", index=False)
    # Keep a compact join manifest; original probabilities remain in the pinned G5 artifact.
    wide[["site", "background", "route", "spatial_block", "fold", "V", "caudata_tertile",
          "odonata_tertile", "n_completed", "k_strong"]].to_csv(
        out / "G6_source_site_context_manifest.csv.gz", index=False,
        compression={"method": "gzip", "mtime": 0})
    receipt = dict(
        status="G6_ARCHIVED_PREDICTION_CONTEXT_DIAGNOSTIC_VERIFIED",
        original_repository_sha="e963b2bf8f8522117f7ac1cf6c10389f1766fbb2",
        protocol_commit="adb76a9",
        original_G4_run=42173236906, original_G5_run=42173456057,
        original_sites=4248, original_visits=63180, original_source_predictions=len(pred),
        original_blocks=56, original_routes=432, original_vegetated_sites=506,
        nll_replay_max_error=float(replay.nll_absolute_error.max()),
        brier_replay_max_error=float(replay.brier_absolute_error.max()),
        whole_cohort_contribution_max_error=float(max(conservation_errors)),
        original_R1_points_reproduced=True,
        source_sha256=actual_hashes,
        outputs={key: len(value) for key, value in context.items()}, rank_output_rows=len(ranks),
        model_refits=0, original_G4_all_corner_gate_passed=False,
        original_G5_two_background_primary_gate_passed=False,
        independent_new_validation=False, causal_vegetation_effect=False,
        uncertainty="pointwise 999 paired whole-block draws, conditional on archived fits; no multiplicity adjustment",
        rank_diagnostic="smooth predicted probabilities versus noisy observed visit fractions; not full predictive distributions",
    )
    (out / "G6_source_and_replay_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2), flush=True)
    return context, ranks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("sites", "g4-dir", "g5-dir", "out"):
        parser.add_argument("--" + option, type=Path, required=True)
    a = parser.parse_args()
    run(a.sites, a.g4_dir, a.g5_dir, a.out)
