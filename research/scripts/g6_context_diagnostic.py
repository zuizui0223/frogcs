"""Describe frozen G5 predictions by observed vegetation and suitability context.

No fitting, source selection, intervention prediction, or new direct four-sign
test occurs here. Block intervals condition on the supplied predictions; they
describe a retrospective diagnostic, not independent mechanism validation.
"""
from __future__ import annotations

from numbers import Integral

import numpy as np
import pandas as pd


BACKGROUNDS = ("uniform", "target_group")
MODELS = (
    "env_add", "env_all", "flex_add", "flex_all",
    "flex_prior_00", "flex_prior_11",
)
BASELINES = ("flex_add", "flex_prior_00", "flex_all", "env_add")
CANDIDATE = "flex_prior_11"
MIN_SITES, MIN_ROUTES, MIN_BLOCKS, MIN_VISITS = 20, 5, 3, 200


def _validated_copy(wide: pd.DataFrame) -> pd.DataFrame:
    metadata = (
        "site", "background", "route", "spatial_block", "V",
        "caudata_tertile", "odonata_tertile", "n_completed", "k_strong",
    )
    if not isinstance(wide, pd.DataFrame):
        raise ValueError("wide must be a pandas DataFrame")
    if not wide.columns.is_unique:
        raise ValueError("Duplicate input column names")
    missing = set(metadata + MODELS).difference(wide.columns)
    if missing or wide.empty:
        raise ValueError(f"Missing diagnostic rows or required columns: {sorted(missing)}")
    d = wide.loc[:, metadata + MODELS].copy()
    if d[list(metadata)].isna().any().any():
        raise ValueError("Missing source metadata")
    if set(d.background) != set(BACKGROUNDS):
        raise ValueError("Both original uniform and target_group backgrounds are required")
    if d.duplicated(["site", "background"]).any():
        raise ValueError("Duplicate source site/background rows")
    for column in ("site", "route", "spatial_block"):
        if d[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Empty source identifier: {column}")
    for column, allowed in (
        ("V", {0, 1}), ("caudata_tertile", {0, 1, 2}),
        ("odonata_tertile", {0, 1, 2}),
    ):
        if not d[column].isin(allowed).all():
            raise ValueError(f"Invalid predictor labels: {column}")
        d[column] = d[column].astype(int)
    for column in ("n_completed", "k_strong"):
        try:
            values = d[column].to_numpy(dtype=float)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Non-numeric source counts: {column}") from exc
        if (not np.isfinite(values).all()
                or not np.equal(values, np.floor(values)).all()
                or np.any(values > np.iinfo(np.int64).max)):
            raise ValueError(f"Nonfinite or non-integer source counts: {column}")
        d[column] = values.astype(np.int64)
    if (d.n_completed.le(0).any() or d.k_strong.lt(0).any()
            or (d.k_strong > d.n_completed).any()):
        raise ValueError("Counts must satisfy n > 0 and 0 <= k <= n")
    try:
        probabilities = d[list(MODELS)].to_numpy(dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("Non-numeric frozen probabilities") from exc
    if (not np.isfinite(probabilities).all()
            or np.any(probabilities <= 0) or np.any(probabilities >= 1)):
        raise ValueError("All frozen probabilities must be finite and strictly inside (0, 1)")
    d[list(MODELS)] = probabilities

    common = ["route", "spatial_block", "V", "n_completed", "k_strong"]
    first = d[d.background.eq(BACKGROUNDS[0])].set_index("site")
    second = d[d.background.eq(BACKGROUNDS[1])].set_index("site")
    if set(first.index) != set(second.index):
        raise ValueError("Unpaired site sets across backgrounds")
    if not first[common].equals(second.loc[first.index, common]):
        raise ValueError("Source observation metadata differs between backgrounds")
    return d.reset_index(drop=True)


def _strata():
    """Enumerate all planned cells, including cells absent in the source."""
    yield "all", "all", {}
    for v in (0, 1):
        yield "V", f"V{v}", {"V": v}
    for v in (0, 1):
        for s in (0, 1, 2):
            yield "V_S", f"V{v}_S{s}", {"V": v, "caudata_tertile": s}
    for v in (0, 1):
        for s in (0, 1, 2):
            for o in (0, 1, 2):
                yield "V_S_O", f"V{v}_S{s}_O{o}", {
                    "V": v, "caudata_tertile": s, "odonata_tertile": o,
                }


def _interval(draws: np.ndarray, supported: bool) -> tuple[float, float]:
    valid = np.isfinite(draws)
    if not supported or not valid.any():
        return np.nan, np.nan
    lo, hi = np.quantile(draws[valid], [0.025, 0.975])
    return float(lo), float(hi)


def analyze_contexts(
    wide: pd.DataFrame, bootstrap: int = 999, seed: int = 20261106,
) -> dict[str, pd.DataFrame]:
    """Return scores, gains, V1-minus-V0 heterogeneity, and cell support.

    ``wide`` has one row per original site/background and one probability
    column per member of ``MODELS``. Counts and physical-site metadata must
    match across the two backgrounds. Predictor tertiles may differ.

    All intervals reuse one multinomial resampling of the complete spatial
    block universe. Invalid cell denominators are counted explicitly. Cells
    below any support minimum retain point estimates, with interval endpoints
    set to NaN. Empty cells retain zero contribution to the whole-data gain.
    """
    if not isinstance(bootstrap, Integral) or isinstance(bootstrap, bool) or bootstrap < 1:
        raise ValueError("bootstrap must be a positive integer")
    if not isinstance(seed, Integral) or isinstance(seed, bool) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    bootstrap = int(bootstrap)
    d = _validated_copy(wide)
    blocks = sorted(d.spatial_block.unique(), key=lambda value: (type(value).__name__, str(value)))
    block_lookup = {value: index for index, value in enumerate(blocks)}
    n_blocks = len(blocks)
    weights = np.random.default_rng(int(seed)).multinomial(
        n_blocks, np.full(n_blocks, 1.0 / n_blocks), size=bootstrap,
    )
    scores, gains, heterogeneity, support = [], [], [], []
    model_index = {model: i for i, model in enumerate(MODELS)}

    for background in BACKGROUNDS:
        g = d[d.background.eq(background)].reset_index(drop=True)
        n = g.n_completed.to_numpy(dtype=float)
        k = g.k_strong.to_numpy(dtype=float)
        p = g[list(MODELS)].to_numpy(dtype=float)
        loss = -(k[:, None] * np.log(p) + (n - k)[:, None] * np.log1p(-p))
        brier = k[:, None] * (1 - p) ** 2 + (n - k)[:, None] * p ** 2
        block_index = g.spatial_block.map(block_lookup).to_numpy(dtype=int)
        total_visits = float(n.sum())
        total_block_visits = np.bincount(block_index, weights=n, minlength=n_blocks)
        total_draw_visits = weights @ total_block_visits
        if np.any(total_draw_visits <= 0):
            raise AssertionError("A full-source bootstrap draw has no visits")
        v_results = {}

        for partition, stratum, labels in _strata():
            mask = np.ones(len(g), dtype=bool)
            for column, value in labels.items():
                mask &= g[column].to_numpy() == value
            cell = g.loc[mask]
            visits = int(n[mask].sum())
            strong_events = int(k[mask].sum())
            sites = int(mask.sum())
            routes = int(cell.route.nunique())
            cell_blocks = int(cell.spatial_block.nunique())
            supported = bool(sites >= MIN_SITES and routes >= MIN_ROUTES
                             and cell_blocks >= MIN_BLOCKS and visits >= MIN_VISITS)
            common = dict(
                background=background, partition=partition, stratum=stratum,
                V=labels.get("V", np.nan),
                caudata_tertile=labels.get("caudata_tertile", np.nan),
                odonata_tertile=labels.get("odonata_tertile", np.nan),
                sites=sites, routes=routes, blocks=cell_blocks, visits=visits,
                strong_events=strong_events, supported=supported,
                min_sites=MIN_SITES, min_routes=MIN_ROUTES,
                min_blocks=MIN_BLOCKS, min_visits=MIN_VISITS,
            )
            support.append(common.copy())
            observed_rate = strong_events / visits if visits else np.nan
            for candidate, mi in model_index.items():
                predicted_rate = float(n[mask] @ p[mask, mi] / visits) if visits else np.nan
                scores.append(dict(
                    **common, candidate=candidate,
                    observed_rate=observed_rate, predicted_rate=predicted_rate,
                    residual=observed_rate - predicted_rate,
                    nll_per_visit=float(loss[mask, mi].sum() / visits) if visits else np.nan,
                    brier_per_visit=float(brier[mask, mi].sum() / visits) if visits else np.nan,
                ))

            block_visits = np.bincount(block_index[mask], weights=n[mask], minlength=n_blocks)
            draw_visits = weights @ block_visits
            valid_cell = draw_visits > 0
            for baseline in BASELINES:
                difference = loss[:, model_index[baseline]] - loss[:, model_index[CANDIDATE]]
                point_numerator = float(difference[mask].sum())
                point_gain = point_numerator / visits if visits else np.nan
                block_difference = np.bincount(
                    block_index[mask], weights=difference[mask], minlength=n_blocks,
                )
                draw_difference = weights @ block_difference
                gain_draws = np.divide(
                    draw_difference, draw_visits, out=np.full(bootstrap, np.nan), where=valid_cell,
                )
                contribution_draws = draw_difference / total_draw_visits
                low, high = _interval(gain_draws, supported)
                contribution_low, contribution_high = _interval(contribution_draws, supported)
                invalid_gain = int((~np.isfinite(gain_draws)).sum())
                invalid_contribution = int((~np.isfinite(contribution_draws)).sum())
                gains.append(dict(
                    **common, baseline=baseline, candidate=CANDIDATE,
                    gain_per_visit=point_gain,
                    full_total_weighted_contribution=point_numerator / total_visits,
                    gain_ci_low=low, gain_ci_high=high,
                    contribution_ci_low=contribution_low, contribution_ci_high=contribution_high,
                    invalid_gain_draws=invalid_gain,
                    invalid_contribution_draws=invalid_contribution,
                    valid_gain_draws=bootstrap - invalid_gain,
                    valid_contribution_draws=bootstrap - invalid_contribution,
                    bootstrap_repetitions=bootstrap,
                ))
                if partition == "V":
                    v_results[(baseline, labels["V"])] = (point_gain, gain_draws, common)

        for baseline in BASELINES:
            gain0, draws0, context0 = v_results[(baseline, 0)]
            gain1, draws1, context1 = v_results[(baseline, 1)]
            paired_draws = draws1 - draws0
            eligible = context0["supported"] and context1["supported"]
            low, high = _interval(paired_draws, eligible)
            invalid = int((~np.isfinite(paired_draws)).sum())
            heterogeneity.append(dict(
                background=background, baseline=baseline, candidate=CANDIDATE,
                gain_v0=gain0, gain_v1=gain1,
                difference_v1_minus_v0=gain1 - gain0,
                ci_low=low, ci_high=high, invalid_draws=invalid,
                valid_draws=bootstrap - invalid,
                supported_v0=context0["supported"], supported_v1=context1["supported"],
                v0_sites=context0["sites"], v1_sites=context1["sites"],
                v0_visits=context0["visits"], v1_visits=context1["visits"],
                bootstrap_repetitions=bootstrap,
            ))

    gain_table = pd.DataFrame(gains)
    for (background, baseline), rows in gain_table.groupby(["background", "baseline"], sort=False):
        whole = float(rows.loc[rows.partition.eq("all"), "gain_per_visit"].iloc[0])
        for partition in ("V", "V_S", "V_S_O"):
            rebuilt = float(rows.loc[rows.partition.eq(partition), "full_total_weighted_contribution"].sum())
            if not np.isclose(whole, rebuilt, rtol=1e-12, atol=1e-13):
                raise AssertionError(f"Global gain is not conserved: {background}/{baseline}/{partition}")
    return {
        "scores": pd.DataFrame(scores),
        "gains": gain_table,
        "heterogeneity": pd.DataFrame(heterogeneity),
        "support": pd.DataFrame(support),
    }
