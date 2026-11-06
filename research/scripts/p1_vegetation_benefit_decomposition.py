"""Post-hoc full-factorial decomposition of the existing source-locked P1 outputs.

No biology is re-simulated and no source is selected for its outcome. All 256
backgrounds, four developmental contexts and four vegetation interventions enter.
Intervals describe synthetic-source variation, not field uncertainty.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

TIMINGS = ("LS", "LL", "ES", "EL")
ARMS = ("00", "10", "01", "11")
TERMS = ("refuge", "feeding_support", "nonadditivity", "net")
CHANGES = ("pure_arrival", "pure_duration", "arrival_x_duration", "EL_minus_LS")
SEED = 20261126
BOOT = 10000
SOURCE_COMMIT = "053add0cc445975f26a6a0f61445a98810d177f2"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO / "research/results/submission_frozen_sources_20261106/P1"
DEFAULT_OUT = REPO / "research/results/p1_vegetation_benefit_20261106"


def require(condition, message):
    if not bool(condition):
        raise ValueError(message)


def decompose(effects, *, expected_sources=256):
    """Return exactly one row per background/timing with all four exact terms."""
    keys = ["source_id", "stage_design", "arm"]
    require(set(keys + ["mean_log_F_B"]).issubset(effects.columns),
            "Missing P1 scenario columns")
    require(not effects[keys].isna().any().any() and
            not effects.duplicated(keys).any(), "Missing or duplicated scenario identity")
    require(set(effects.stage_design) == set(TIMINGS) and
            set(effects.arm) == set(ARMS), "Timing/arm labels changed or lost leading zeroes")
    ids = sorted(effects.source_id.unique())
    require(len(ids) == expected_sources and len(effects) == expected_sources * 16,
            "The complete source-by-timing-by-arm factorial is required")
    idx = pd.MultiIndex.from_product([ids, TIMINGS, ARMS], names=keys)
    y = effects.set_index(keys)["mean_log_F_B"].reindex(idx)
    require(np.isfinite(y.to_numpy(float)).all(), "Missing/nonfinite paired source outcome")
    a = y.to_numpy(float).reshape(expected_sources, 4, 4)
    refuge = a[:, :, 1] - a[:, :, 0]
    support = a[:, :, 2] - a[:, :, 0]
    interaction = a[:, :, 3] - a[:, :, 1] - a[:, :, 2] + a[:, :, 0]
    net = a[:, :, 3] - a[:, :, 0]
    require(np.allclose(refuge + support + interaction, net, rtol=0, atol=1e-12),
            "Source-level decomposition identity failed")
    rows = pd.DataFrame({"source_id": np.repeat(ids, 4),
                         "timing": np.tile(TIMINGS, expected_sources)})
    for term, values in zip(TERMS, (refuge, support, interaction, net)):
        rows[term] = values.ravel()
    return rows


def summarize(decomposition, *, n_boot=BOOT, seed=SEED):
    """Use one source-resampling array for every term, context and moderator."""
    ids = sorted(decomposition.source_id.unique())
    n = len(ids)
    require(n > 0 and len(decomposition) == 4 * n and n_boot > 0,
            "Empty/incomplete source decomposition or invalid bootstrap count")
    require(not decomposition.duplicated(["source_id", "timing"]).any(),
            "Duplicated source/timing decomposition")
    index = pd.MultiIndex.from_product([ids, TIMINGS], names=["source_id", "timing"])
    a = decomposition.set_index(["source_id", "timing"]).reindex(index)[list(TERMS)]
    require(np.isfinite(a.to_numpy(float)).all(), "Incomplete decomposition terms")
    a = a.to_numpy(float).reshape(n, 4, 4)
    indices = np.random.default_rng(seed).integers(0, n, size=(n_boot, n))
    vectors = {("timing", timing): a[:, j, :] for j, timing in enumerate(TIMINGS)}
    ls, ll, es, el = (a[:, j, :] for j in range(4))
    vectors.update({
        ("change", "pure_arrival"): (es - ls + el - ll) / 2,
        ("change", "pure_duration"): (ll - ls + el - es) / 2,
        ("change", "arrival_x_duration"): el - es - ll + ls,
        ("change", "EL_minus_LS"): el - ls,
    })
    records, draws, labels = [], [], []
    for (kind, contrast), values in vectors.items():
        require(np.allclose(values[:, :3].sum(axis=1), values[:, 3],
                            rtol=0, atol=1e-12), "A derived contrast lost decomposition")
        sampled = values[indices].mean(axis=1)
        require(np.allclose(sampled[:, :3].sum(axis=1), sampled[:, 3],
                            rtol=0, atol=1e-12), "Bootstrap lost source pairing")
        for j, term in enumerate(TERMS):
            lo, hi = np.quantile(sampled[:, j], [0.025, 0.975])
            records.append(dict(kind=kind, contrast=contrast, term=term,
                                mean=float(values[:, j].mean()), mc95_low=float(lo),
                                mc95_high=float(hi), n_sources=n))
            labels.append((kind, contrast, term))
            draws.append(sampled[:, j])
    return pd.DataFrame(records), np.column_stack(draws), labels, indices


def sign_counts(decomposition):
    """Keep endpoint sign reversals separate from positive shifts of any size."""
    rows = []
    for timing in TIMINGS:
        v = decomposition.loc[decomposition.timing == timing, "net"].to_numpy(float)
        rows.append(dict(timing=timing, n_sources=len(v), positive=int((v > 0).sum()),
                         negative=int((v < 0).sum()), zero=int((v == 0).sum())))
    d = decomposition.pivot(index="source_id", columns="timing", values="net")
    def signs(v):
        return np.where(v > 0, "positive", np.where(v < 0, "negative", "zero"))
    transition = d[list(TIMINGS)].reset_index()
    transition["LS_sign"] = signs(transition.LS)
    transition["EL_sign"] = signs(transition.EL)
    transition["shift"] = transition.EL - transition.LS
    transition["negative_to_positive"] = (transition.LS < 0) & (transition.EL > 0)
    transition["positive_to_negative"] = (transition.LS > 0) & (transition.EL < 0)
    return pd.DataFrame(rows), transition


def verify_vertices(effects, vertices):
    """Rebuild the reported scenario responses independently from their vertices."""
    require(len(effects) == 4096 and len(vertices) == 32768,
            "The complete P1 source package is required")
    require(not effects.draw_id.duplicated().any() and
            not vertices.duplicated(["draw_id", "vertex"]).any(), "Duplicated original source ID")
    require(set(vertices.draw_id) == set(effects.draw_id) and
            vertices.groupby("draw_id").size().eq(8).all() and
            set(vertices.vertex) == set(range(8)), "Missing source corner")
    require(np.isfinite(vertices.F_B).all() and (vertices.F_B > 0).all(),
            "Source log response requires positive finite F_B")
    meta = vertices[["draw_id", "source_id", "stage_design", "arm"]].drop_duplicates()
    matched = meta.merge(effects[["draw_id", "source_id", "stage_design", "arm"]],
                         on="draw_id", suffixes=("_vertex", "_effect"), validate="one_to_one")
    for column in ("source_id", "stage_design", "arm"):
        require((matched[column + "_vertex"] == matched[column + "_effect"]).all(),
                "Vertex/source identity mismatch: " + column)
    require(set(vertices.vegetation) == {0, 1} and
            vertices.groupby(["draw_id", "vegetation"]).size().eq(4).all(),
            "Vegetation corner weights changed")
    rebuilt = vertices.assign(log_F=np.log(vertices.F_B)).groupby("draw_id").agg(
        mean_log_F_B=("log_F", "mean"), mean_F_B=("F_B", "mean"))
    recorded = effects.set_index("draw_id").loc[rebuilt.index]
    errors = {}
    for col in ("mean_log_F_B", "mean_F_B"):
        errors[col] = float(np.abs(rebuilt[col] - recorded[col]).max())
        require(errors[col] < 1e-12, "Vertex-derived response differs: " + col)
    control = vertices.loc[vertices.vegetation == 0].groupby(
        ["source_id", "stage_design", "vertex"]).F_B.agg(["min", "max"])
    gap = float((control["max"] - control["min"]).abs().max())
    require(gap < 1e-12, "The vegetation-absent negative control failed")
    return dict(response_reconstruction_max_abs_errors=errors,
                vegetation_zero_max_arm_difference=gap, minimum_F_B=float(vertices.F_B.min()))


def run(source=DEFAULT_SOURCE, out=DEFAULT_OUT):
    source, out = Path(source), Path(out)
    paths = [source / "P1_original4096_isolated_timing_duration_80year.csv.gz",
             source / "P1_original32768_vegetation_predator_corners.csv.gz",
             source / "P1_within_timing_paired_vegetation_effects.csv"]
    effects, vertices = [pd.read_csv(p, dtype={"arm": str, "stage_design": str}) for p in paths[:2]]
    decomposition = decompose(effects)
    validation = verify_vertices(effects, vertices)
    summary, draws, labels, indices = summarize(decomposition)
    counts, transitions = sign_counts(decomposition)
    previous = pd.read_csv(paths[2])
    prior = previous[(previous.metric == "mean_log_F_B") &
                     (previous.contrast == "both_minus_neither")].set_index("timing")
    current = summary[(summary.kind == "timing") & (summary.term == "net")].set_index("contrast")
    replay_error = float((current.loc[list(TIMINGS), "mean"].to_numpy() -
                          prior.loc[list(TIMINGS), "mean"].to_numpy()).__abs__().max())
    require(replay_error < 1e-12, "P1 original net effect changed")
    out.mkdir(parents=True, exist_ok=True)
    decomposition.to_csv(out / "p1_all_256_background_decompositions.csv", index=False)
    summary.to_csv(out / "p1_decomposition_summary.csv", index=False)
    counts.to_csv(out / "p1_net_effect_sign_counts.csv", index=False)
    transitions.to_csv(out / "p1_background_sign_transitions.csv", index=False)
    # Preserve the previously reported intervals alongside their unchanged means.
    prior.loc[list(TIMINGS)].to_csv(out / "p1_original_net_effect_intervals.csv")
    transition_table = pd.crosstab(transitions.LS_sign, transitions.EL_sign).reindex(
        index=["negative", "zero", "positive"], columns=["negative", "zero", "positive"], fill_value=0
    ).fillna(0).astype(int)
    transition_table.to_csv(out / "p1_complete_sign_transition_table.csv")
    identity_error = float(np.abs(decomposition[list(TERMS[:3])].sum(axis=1) -
                                  decomposition.net).max())
    receipt = dict(
        status="POSTHOC_P1_COMPLETE_FACTORIAL_DECOMPOSITION_VERIFIED",
        source_commit=SOURCE_COMMIT, new_biological_simulations=0,
        source_backgrounds=256, timing_conditions=4, intervention_arms=4,
        original_scenarios=len(effects), original_vertices=len(vertices),
        bootstrap_resamples=BOOT, bootstrap_seed=SEED,
        bootstrap_indices_sha256=hashlib.sha256(indices.astype("<i8").tobytes()).hexdigest(),
        bootstrap_columns=len(labels), complete_contrasts=len(summary),
        source_input_sha256={str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in paths},
        analysis_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        decomposition_max_abs_error=identity_error, original_P1_mean_max_abs_error=replay_error,
        negative_to_positive=int(transitions.negative_to_positive.sum()),
        positive_to_negative=int(transitions.positive_to_negative.sum()),
        positive_shift=int((transitions["shift"] > 0).sum()),
        negative_shift=int((transitions["shift"] < 0).sum()),
        inference="Post-hoc algebraic explanation; pointwise source-bootstrap intervals; no field inference",
        g7_decision_changed=False, outcome_based_exclusions=0, **validation,
    )
    (out / "p1_decomposition_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(summary[summary.contrast == "EL_minus_LS"].to_string(index=False))
    print(counts.to_string(index=False))
    print(json.dumps({k: receipt[k] for k in ["status", "negative_to_positive", "positive_to_negative",
                                             "positive_shift", "decomposition_max_abs_error"]}))
    return receipt


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    cli.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = cli.parse_args()
    run(args.source, args.out)
