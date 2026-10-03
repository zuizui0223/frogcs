# Common-cause falsification synthesis v0.1

Date: 2026-10-03

## Provenance boundary

The original same-data mechanism sequence ended under its prespecified stopping rule. That rule was explicitly reopened on 2026-10-03. Everything in this note that was run after reopening is **post-hoc exploratory falsification**, not independent confirmation and not part of the original prespecified evidence sequence.

## Question

Could the NAAMP within-taxon multi-site concentration be a trivial consequence of a species-wide environmental switch acting across all ten route stops on a given night?

## Stage 1 — flexible measured route-night environment

Fixed contract: `exploration/NAAMP_FLEXIBLE_COMMON_ENVIRONMENT_NULL_CONTRACT_V0_1.json`

Population: 2,916 strictly-prior-history pairs, 439 routes, 20 states.

The cross-fitted species model allowed nonlinear `log(1 + DaysSinceRain)`, nonlinear temperature, first and second annual harmonics, a rain-recency × temperature interaction, State and RunNumber effects, strictly-prior species × physical-SiteID history, dry-state persistence and matched total wet incidence.

Result:
- observed concentration β = **1.6503**
- existing principal-null prediction = **1.3535**
- flexible-environment prediction = **1.3872**
- residual: **0.2969 → 0.2631**
- fraction of existing residual removed = **11.4%**
- flexible-null residual 95% interval = **−0.1307 to 0.1276**
- upper-tail **P = 0.000999**

Nonlinear rain recency, temperature, season and their tested interaction explain only a small fraction of the concentration residual.

## Stage 2 — actual antecedent rainfall amount

A separate earlier NAAMP analysis had already established that antecedent rainfall amount is biologically informative for strong activation: the 72-h ERA5 rainfall-amount effect on the strong-new-chorus score was β = **0.741** (95% CI **0.386 to 1.097**) while DaysSinceRain remained positive.

Fixed concentration contract: `exploration/NAAMP_RAIN_AMOUNT_COMMON_ENVIRONMENT_NULL_CONTRACT_V0_1.json`

Weather/prior-history intersection: **2,835** pairs, **428** routes, **20** states.

Same-sample comparison:
- observed concentration β = **1.7136**
- linear species-response null prediction = **1.3960**
- linear conditional residual = **0.3176**
- 72-h rainfall common-environment prediction = **1.4166**
- rainfall conditional residual = **0.2970**
- fraction of same-sample residual removed = **6.5%**
- rainfall-null residual 95% interval = **−0.1305 to 0.1378**
- upper-tail **P = 0.000999**

Actual antecedent rainfall amount clearly helps explain whether strong activation occurs, but it explains very little of the residual allocation of that activity across multiple stops within the same taxon.

## Other measured atmospheric cues already examined

Earlier branch-preserved analyses provide useful negative controls:

- **Current light rain:** no supported independent effect on strong activation.
- **Surface pressure / pressure fall:** no supported independent effect once rain recency and 72-h rainfall amount are represented.
- **Humidity:** no supported individual effect; a joint humidity+pressure test contained some information, but rain recency remained positive.
- **AnuraSet external threshold exercise:** did not provide a robust general replication of a threshold-dominant recent-rain response.

These analyses do not exhaust environmental common causes. Local hydroperiod, water level, soil moisture, small-scale rainfall heterogeneity and other unmeasured route-night variables remain possible.

## Stage 3 — direct conditional-independence diagnostic

Fixed contract: `exploration/NAAMP_SPECIES_ROUTE_NIGHT_RESIDUAL_DEPENDENCE_CONTRACT_V0_1.json`

Using the fixed stop-specific probabilities from the strongest 72-h-rainfall + prior-history comparator:

Coverage:
- 2,835 focal pairs
- 18,769 species × route-night clusters
- 187,690 species × stop cells

Standardized within-species route-night residual correlation:
- observed **ρ_resid = 0.4159**
- independent-Bernoulli null mean ≈ **0.00002**
- null 95% interval = **−0.00343 to 0.00343**
- upper-tail **P = 0.000999**

Thus conditional independence among the ten stop outcomes is strongly rejected under the tested measured-environment + historical-site comparator.

A simple ten-stop exchangeable-correlation translation gives a design-effect heuristic ≈ **4.74** and effective-stop-count heuristic ≈ **2.11 of 10**. These are heuristic translations, not the exact design effect of a particular occupancy estimator.

## Biological interpretation now supported

> **A frog species' acoustic state on a given route-night behaves as a shared landscape-scale state: after measured rainfall amount, nonlinear rain recency, temperature, season, historical physical-site use, dry-state persistence and total activity are represented, calling outcomes at separated stops remain strongly positively dependent within the same species and night.**

This establishes the **scale of dependence**, not its unique lower-level cause.

Still unresolved:
- unmeasured shared hydrology or microclimate;
- synchronized breeding state;
- demographic/availability state shared across a route;
- social facilitation;
- other latent route-night processes.

Not established:
- individual movement among stops;
- literal simultaneity among sequential NAAMP stops;
- rainfall causality;
- social transmission;
- a universal anuran mechanism.

## Monitoring implication

The direct ecological result implies that stop number is not automatically equal to independent information. The historical NAAMP occupancy literature itself treated route stops as spatial replicates and noted that nesting within routes could induce dependence affecting trend precision.

A separate fixed post-hoc diagnostic directly compares model-based IID uncertainty with species × route-night clustered uncertainty for a representative stop-level activation regression:
- contract: `exploration/NAAMP_MONITORING_INDEPENDENCE_IMPACT_CONTRACT_V0_1.json`

That SE comparison determines whether the monitoring implication is presented quantitatively or only as a methodological consequence.

## Current decision

The common-cause test does **not** support pivoting the paper to “species-specific rainfall thresholds explain the pattern.”

The stronger direction is:

1. retain the ecological discovery as **species-by-route-night landscape-scale dependence**;
2. show that the strongest measured common environmental triggers explain little of the allocation residual;
3. use the direct SE comparison to decide how strongly to elevate the monitoring-design implication;
4. keep WFTS as the prospective confirmation, with the already frozen secondary common-environment diagnostic in `revision/WFTS_PROSPECTIVE_COMMON_ENVIRONMENT_DIAGNOSTIC_V0_1.json`.
