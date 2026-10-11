#!/usr/bin/env python3
"""v3.6 synthetic-only identifiability and acoustic detection QA.

No NAAMP data, no Iowa native wet/dry and no frog responses are read.
The tests establish properties of hypothetical randomized site x night designs,
not an actual causal effect or a statistical power calculation.
"""
from __future__ import annotations

from itertools import combinations
from math import isfinite


def matrix_rank(rows: list[list[float]], tol: float = 1e-9) -> int:
    if not rows:
        return 0
    ncols = len(rows[0])
    if any(len(r) != ncols for r in rows):
        raise ValueError("ragged design matrix")
    a = [[float(z) for z in r] for r in rows]
    m = len(a)
    pivot_row = 0
    for col in range(ncols):
        if pivot_row == m:
            break
        best = max(range(pivot_row, m), key=lambda i: abs(a[i][col]))
        if abs(a[best][col]) < tol:
            continue
        a[pivot_row], a[best] = a[best], a[pivot_row]
        pivot = a[pivot_row][col]
        for j in range(col, ncols):
            a[pivot_row][j] /= pivot
        for i in range(pivot_row + 1, m):
            fac = a[i][col]
            for j in range(col, ncols):
                a[i][j] -= fac * a[pivot_row][j]
        pivot_row += 1
    return pivot_row


def build_plan(n_sites: int = 8, n_nights: int = 10, kind: str = "crossed"):
    """Deterministic toy assignments, not suggested field randomization sequences."""
    if n_sites < 2 or n_nights < 2:
        raise ValueError("must have crossed sites and nights")
    rows = []
    for site in range(n_sites):
        for night in range(n_nights):
            hist = site % 2
            sound = int((site * 31 + night * 17 + site * night * 13) % 7 < 3)
            water = int((site * 7 + night * 11 + site * night * 3) % 11 < 5)
            if kind == "sound_per_night":
                sound = night % 2
            elif kind == "water_per_site":
                water = site % 2
            elif kind == "perfect_sound_water_confounded":
                sound = water
            elif kind == "no_history_variation":
                hist = 0
            elif kind != "crossed":
                raise ValueError("unknown synthetic design kind")
            rows.append({"site": site, "night": night,
                         "history": hist, "sound": sound, "water": water})
    return rows


def design_matrix(rows: list[dict], term_names: tuple[str, ...]):
    sites = sorted({r["site"] for r in rows})
    nights = sorted({r["night"] for r in rows})
    if not sites or not nights:
        raise ValueError("no observations")
    out = []
    for r in rows:
        w, s, h = r["water"], r["sound"], r["history"]
        terms = {"water": w, "sound": s, "water_sound": w*s,
                 "history_sound": h*s, "history_water": h*w,
                 "history": h}
        out.append(
            [1.0] +
            [float(r["site"] == site) for site in sites[1:]] +
            [float(r["night"] == night) for night in nights[1:]] +
            [float(terms[name]) for name in term_names]
        )
    return out


def incremental_rank(rows: list[dict], terms: tuple[str, ...]):
    """Is each candidate estimable given site/night FE and previous terms?"""
    previous = ()
    baseline = design_matrix(rows, previous)
    last_rank = matrix_rank(baseline)
    summary = {"n_rows": len(rows),
               "n_sites": len({r["site"] for r in rows}),
               "n_nights": len({r["night"] for r in rows}),
               "base_rank": last_rank, "increments": {}}
    for term in terms:
        new = previous + (term,)
        rank = matrix_rank(design_matrix(rows, new))
        summary["increments"][term] = rank - last_rank
        previous, last_rank = new, rank
    summary["full_rank"] = last_rank
    return summary


def conditional_exact_k_probs(site_probs: list[float], k: int):
    """Independent Bernoulli site generator conditioned exactly on sum(Y)=k.

    This tests conditioning mechanics, NOT a valid null for every real frog system.
    """
    n = len(site_probs)
    if not n or not 0 <= k <= n:
        raise ValueError("invalid k")
    if any(not isfinite(p) or not 0 < p < 1 for p in site_probs):
        raise ValueError("site Bernoulli probabilities must be finite and in (0,1)")
    subsets = list(combinations(range(n), k))
    weights = []
    for subset in subsets:
        active = set(subset)
        value = 1.0
        for i, p in enumerate(site_probs):
            value *= p if i in active else 1 - p
        weights.append(value)
    total = sum(weights)
    if total <= 0:
        raise ValueError("numerical underflow: rescale or use log weights")
    return [(subset, w/total) for subset, w in zip(subsets, weights)]


def historical_overlap_distribution(site_probs, k, historical_sites):
    rows = conditional_exact_k_probs(site_probs, k)
    if any(i < 0 or i >= len(site_probs) for i in historical_sites):
        raise ValueError("out-of-range history SiteID index")
    h = set(historical_sites)
    return sum(p * len(set(subset) & h) for subset, p in rows)


def synthetic_tests():
    names = ("water", "sound", "water_sound", "history_sound", "history_water")

    # Positive crossed assignment. All terms add rank after site+night FE.
    crossed = incremental_rank(build_plan(kind="crossed"), names)
    assert all(crossed["increments"][x] == 1 for x in names), crossed

    # Sound played across all ponds on the same night aliases night FE.
    # Its interaction with a varying historical-site attribute MAY be estimable.
    nightly = incremental_rank(build_plan(kind="sound_per_night"),
                               ("water", "sound", "history_sound"))
    assert nightly["increments"]["sound"] == 0, nightly
    assert nightly["increments"]["history_sound"] == 1, nightly

    # Water fixed at each pond aliases site FE; cannot identify its main effect.
    site_fixed = incremental_rank(build_plan(kind="water_per_site"),
                                  ("water", "sound"))
    assert site_fixed["increments"]["water"] == 0, site_fixed

    # Sound and water assigned identically: no separated treatment contrast.
    confounded = incremental_rank(build_plan(kind="perfect_sound_water_confounded"),
                                  ("water", "sound", "water_sound"))
    assert confounded["increments"]["water"] == 1
    assert confounded["increments"]["sound"] == 0
    assert confounded["increments"]["water_sound"] == 0

    # If history never varies between sites, history x treatment cannot be tested.
    no_history = incremental_rank(build_plan(kind="no_history_variation"),
                                  ("water", "sound", "history_sound", "history_water"))
    assert no_history["increments"]["history_sound"] == 0
    assert no_history["increments"]["history_water"] == 0

    # History is by construction a site-level characteristic; main effect is
    # always absorbed by site FE even when history x randomized cue is estimable.
    history_main = incremental_rank(build_plan(kind="crossed"), ("history",))
    assert history_main["increments"]["history"] == 0

    # Exact-k null: same total activity is NOT the same spatial placement.
    equal = conditional_exact_k_probs([0.5] * 4, 2)
    assert len(equal) == 6
    assert abs(sum(p for _, p in equal) - 1) < 1e-12
    assert all(abs(p - 1/6) < 1e-12 for _, p in equal)
    q = [0.85, 0.85, 0.15, 0.15]
    expected = historical_overlap_distribution(q, 2, {0, 1})
    assert 1 < expected < 2
    assert expected > historical_overlap_distribution([0.5]*4, 2, {0, 1})
    # Post-treatment k is a selection variable, not a randomized treatment.
    # Sound affects site 2 only. Site 1 marginal call probability is unchanged,
    # yet selecting observations with exactly k=1 creates a large change in
    # site-1's conditional fraction. Do NOT interpret that as suppression of
    # site 1 caused by sound.
    p_control = [0.2, 0.2]
    p_sound = [0.2, 0.8]
    assert p_control[0] == p_sound[0]
    control_site1_given_one = historical_overlap_distribution(p_control, 1, {0})
    sound_site1_given_one = historical_overlap_distribution(p_sound, 1, {0})
    assert abs(control_site1_given_one - 0.5) < 1e-12
    assert sound_site1_given_one < 0.07
    assert control_site1_given_one > sound_site1_given_one

    for bad_probs, bad_k in (([1.,0.2],1),([0.5,0.5],3)):
        try:
            conditional_exact_k_probs(bad_probs,bad_k)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid fixed-k input accepted")

    # Same actual 20 calls in each arm. Detection drops under masking, so
    # naive recorded-count contrast is biased even when true effect is zero.
    real_calls_control = real_calls_rain_sound = 20
    detected_control = real_calls_control * 1.0
    detected_rain_sound = real_calls_rain_sound * 0.6
    assert real_calls_control == real_calls_rain_sound
    assert detected_rain_sound < detected_control
    print("PASS: 6 treatment identifiability contrasts, exact-k site allocation,")
    print("      detection-masking and post-treatment-k selection counterexamples, invalid-input guards.")
    print("SYNTHETIC ONLY: no frog outcomes, field treatment, sound recordings or sample-size power.")


if __name__ == "__main__":
    synthetic_tests()
