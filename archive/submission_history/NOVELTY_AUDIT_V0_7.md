# Novelty audit v0.7 — RC8 boundary-biased active-community expansion

## Reviewer-safe central advance

Rainfall effects on frog calling, acoustic activity and observed richness are established. Short-term acoustic-community composition and beta diversity are established. Wetting and inundation effects on frog richness and community composition are established. Even a high fraction of new detections falling outside a previously active matrix is not, by itself, surprising: a simple increase in detection probabilities will mechanically create many such boundary gains.

RC8 therefore makes a narrower claim than RC7:

> **Rainfall-associated expansion is more boundary-biased than expected under a uniform increase in baseline acoustic propensities, while pairwise Sørensen differentiation remains practically stable within a fixed margin.**

That statement has an explicit comparator.

Under the primary frozen uniform-activation null:
- expected boundary crossing = **80.9%**;
- 95% null interval = **74.2–87.4%**;
- observed boundary crossing = **92.0%**;
- four-component omnibus Monte Carlo P = **.000999**.

The null was rejected under all three frozen smoothing specifications (κ = 1, 2, 5; P = .000999 each).

The observed allocation is not simply “more of everything”:
- corner expansion: **36.9% observed vs 27.4% null mean**;
- spatial spread: **15.2% vs 22.9%**;
- taxonomic deepening: **39.9% vs 30.5%**;
- within-core rearrangement: **8.0% vs 19.1%**.

The result is therefore an empirical bias toward **route-new taxonomic participation**, not just a mechanically high boundary-crossing percentage.

## What prior work already owns

RC8 does not claim novelty for:
- rainfall-sensitive frog calling;
- lagged rainfall effects on calling activity or observed richness;
- fine-temporal acoustic-community composition;
- beta diversity of frog calling assemblages;
- inundation-driven richness or composition changes;
- joint alpha–beta–gamma responses to precipitation;
- species × site matrices or additive incidence decompositions.

Relevant comparison classes remain:
- Xie et al. (2017): rainfall-associated calling activity and species richness;
- Sugai et al. (2021): short-timescale calling-assemblage composition and beta diversity;
- Sarker et al. (2022): inundation-associated richness, chorusing and composition;
- broader precipitation–alpha/beta/gamma literature in other systems.

## What RC8 adds

### 1. A familiar activation response is benchmarked against a direct null

The main question is no longer “does most incidence growth cross a boundary?” because the answer is partly forced by expanding activity.

Instead:

> **Does the observed allocation differ from what a common activation shift would generate, after conditioning on the observed activation magnitude?**

The frozen null:
- preserves observed dry matrices;
- estimates dry-side species × stop acoustic propensities;
- applies one common log-odds activation shift;
- calibrates each pair to its observed wet incidence total in expectation;
- recomputes the exact four incidence components 1,000 times.

This makes the structural claim falsifiable.

### 2. The deviation is biologically interpretable

Uniform activation predicts substantial boundary crossing already, but too much of its incidence growth remains in:
- spatial spread by route-existing species;
- within-core rearrangement.

Observed rain-associated expansion instead shows:
- more corner expansion than expected;
- more taxonomic deepening than expected;
- less spatial spread than expected;
- much less within-core rearrangement than expected.

The simplest ecological reading is **excess recruitment of route-new acoustic participants**, both at newly active and already-active sites.

That is stronger than “the active community got bigger”.

### 3. Practical non-homogenization is now bounded, not inferred from P > .05

Pairwise Sørensen has a fixed post hoc practical-equivalence margin of ±0.025 slope units.

Primary:
- β = -0.00049;
- 90% CI = **-0.0107 to +0.00968**;
- PASS.

Exact consecutive-year:
- β = +0.00215;
- 90% CI = **-0.00973 to +0.0140**;
- PASS.

Therefore RC8 may use **practical stability / without practical homogenization** specifically for the pairwise Sørensen slope within this bound.

This does not establish exact invariance or equivalence of every beta metric.

### 4. Uniform activation is rejected by allocation, not by beta diversity

Under the uniform null, the expected Sørensen slope was slightly negative:
- null mean = -0.00615;
- 95% null interval = -0.0130 to +0.00178.

Observed = -0.00049, inside that null interval.

Thus RC8 does **not** claim that the beta response itself uniquely distinguishes the system from uniform activation.

The distinguishing information lies in **where incidences enter the matrix**.

This separation is conceptually important and guards against bundling every result into one mechanism.

### 5. Geographic and protocol-window robustness remain intact

The RC7 robustness structure is unchanged:
- every one of 21 leave-one-state-out refits retains CI-positive footprint/alpha/gamma slopes;
- the primary 3-day protocol-window sensitivity retains CI-positive effects in 1,769 pairs / 425 routes / 20 states.

These results establish broad robustness without implying state-level uniformity or rainfall causality.

### 6. Mechanism remains deliberately unresolved

Activation geometry failed its rain-specific placebo gate and stays demoted.

The uniform-null rejection does not rescue that trait and does not prove heterogeneous activation thresholds.

Independent literature makes threshold heterogeneity, inundation and hydric physiology plausible, but these remain Discussion hypotheses.

## Why the result is surprising

A uniform activation process was deliberately allowed to know:
- which species and stops are usually detected;
- the dry-side spatial structure;
- the candidate species pool;
- the total wet activation magnitude in expectation.

Even with those advantages, it predicted only about 81% boundary crossing and roughly 19% within-core rearrangement.

The data instead show 92% boundary crossing and 8% within-core rearrangement.

So the surprising fact is not that environmental activation creates new rows and columns. It is that **the real matrix opens more aggressively at taxonomic boundaries than a magnitude-matched uniform activation process does**.

## Remaining novelty risks

1. The null is an acoustic observation-process null, not a demographic null.
2. Rejecting one uniform-activation model does not identify a unique biological mechanism.
3. The candidate-pool and shrinkage choices matter; that is why κ = 1, 2, 5 were frozen as sensitivities.
4. Sørensen equivalence is post hoc with a pre-readback margin, not an originally preregistered equivalence hypothesis.
5. The effect concerns behaviourally realized acoustic participation, not occupancy or abundance.

## Preferred one-sentence novelty statement

> **A familiar rainfall–calling response expands the active frog community in a way that cannot be reproduced by uniformly increasing baseline species × site activation: route-new taxonomic participation is overrepresented, within-core rearrangement is underrepresented, and pairwise Sørensen differentiation remains practically stable within a fixed margin.**
