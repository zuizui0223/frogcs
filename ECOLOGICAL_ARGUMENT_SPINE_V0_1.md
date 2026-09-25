# Ecological argument spine v0.1 — rainfall-pulse community filtering

## Working title

**Rainfall pulses increase frog active-community richness through species-selective reassembly**

Alternative if body-size robustness survives within-family testing:

**Rainfall pulses selectively reassemble frog acoustic communities along a body-size gradient**

## Biological question

Short-term rainfall effects on frog calling are well known. The ecological question here is different:

> **When rainfall increases community acoustic activity, does it simply activate the same assemblage more strongly, or does it change which species constitute the active community?**

This turns the paper from a weather-detection study into a pulse-driven community-assembly study.

## Empirical design

Use standardized NAAMP runs only for the central ecological article.

For each **State × RouteNumber × RunNumber** stratum:
- retain complete 10-stop, temperature-qualified runs;
- pair adjacent observed years;
- orient each pair as wetter versus drier by DaysSinceRain;
- compare active species composition within the same route and same seasonal survey window.

Primary matched dataset:
- 4,236 wet–dry pairs;
- 585 routes;
- 21 states;
- 7,848 eligible runs.

Exact consecutive-year sensitivity:
- 2,693 pairs.

The matched design holds place and sampling window much more tightly than the original cross-sectional rain model.

## Claim 1 — rainfall contrast increases active-community richness

Primary:
- β(rain contrast → wet-minus-dry richness) = **+0.2859 species**;
- 95% CI **0.1646 to 0.4072**;
- P = **3.81 × 10^-6**.

Exact consecutive years:
- β = **+0.3009**;
- 95% CI **0.1447 to 0.4572**;
- P = **1.60 × 10^-4**.

This is not merely “frogs call after rain”: within the same route and seasonal window, the **number of species constituting the active assemblage** increases with rainfall contrast.

## Claim 2 — richer wet assemblages are not simple nested additions

A pure nested-recruitment model predicts wet assemblage = dry core + extra species.

That prediction is not supported:
- nestedness-component slope: P = 0.279 primary;
- P = 0.711 exact consecutive-year sensitivity.

Compositional replacement is non-negligible:
- Simpson turnover slope P = 0.104 primary;
- exact consecutive-year β = **+0.01840**;
- 95% CI **0.00470 to 0.03211**;
- P = **0.00850**.

Interpretation:
> rainfall-associated richness gain is accompanied by **active-community reassembly**, not only species addition.

## Claim 3 — reassembly is species-selective

Raw discordant-pair family:
- 29 eligible species;
- species × wet/dry heterogeneity χ² = **165.45**, df = 28;
- P = **1.91 × 10^-21**;
- FDR 5%: 9 wet-recruited, 3 dry-retained.

Pair-covariate-adjusted species responses:
- all 29 species estimable;
- residual heterogeneity Q = **144.01**, df = 28;
- P = **1.46 × 10^-17**;
- raw vs adjusted rank concordance ρ = **0.997**;
- FDR 5%: 5 wet-associated, 3 dry-associated.

Adjusted wet-associated examples:
- *Gastrophryne carolinensis*;
- *Hyla squirella*;
- *Hyla chrysoscelis*;
- *Pseudacris crucifer*;
- *Pseudacris maculata*.

Adjusted dry-associated:
- *Hyla cinerea*;
- *Lithobates catesbeianus*;
- *Lithobates palustris*.

This rejects a uniform community-wide activation model.

## Claim 4 — species selectivity follows a body-size gradient

AmphiBIO exploratory finite trait screen:
- 26/29 species matched for body size;
- log body size β = **-0.3353**;
- 95% CI **-0.4662 to -0.2044**;
- P = **5.17 × 10^-7**.

Using pair-covariate-adjusted species responses:
- β = **-0.3670**;
- 95% CI **-0.5153 to -0.2187**;
- P = **1.23 × 10^-6**;
- Spearman ρ = **-0.5168**, P = **0.00687**.

Leave-one-family-out slopes are negative wherever estimable.

**Pending authority:** within-family permutation test. Until that test closes, body size is a strong secondary result rather than the article title.

Ecological mechanism:
smaller anurans have greater surface-area-to-volume ratios and generally greater mass-specific evaporative water-loss constraints. A rainfall pulse may therefore release hydric constraints more strongly for smaller species, transiently changing the composition of the acoustically active assemblage.

This is a **hydric-filter hypothesis**, not yet a direct physiological measurement.

## Claim 5 — older participation/association results become mechanism support

The old v0.4 decomposition should move behind the community-assembly story:

- rain increases P(any calling stop);
- rain increases active-pool richness;
- P(>=2 | >=1 active) is null;
- independence residual is null;
- fixed-marginal shuffle residual is null;
- pairwise network density is null.

These results support a community-filter interpretation:
the rainfall response primarily changes **which sampling units and species enter the active assemblage**, not pairwise co-calling structure within active stops.

## Role of FrogID

FrogID is no longer a central pillar of the main ecological article.

Recommended placement:
- Supplementary cross-system contrast;
- brief Discussion paragraph only.

Reason:
FrogID is conditioned on already-active recordings and estimates a different response. Keeping it central pulls the manuscript back toward observation-process inference, which is not the desired ecological paper.

## Ecological synthesis

The target conclusion is:

> **Rainfall pulses do not simply raise frog acoustic activity uniformly. Within standardized communities, wetter conditions increase active-species richness while selectively changing species membership; smaller-bodied species are disproportionately associated with the wet side of this reassembly.**

More general:

> **Environmental pulses can act as transient trait filters that reorganize the realized active community on timescales much shorter than changes in occupancy or regional species pools.**

## Hard boundaries

Do not claim:
- rainfall changes occupancy;
- rainfall changes abundance;
- wet-only species colonized the route;
- dry-only species went locally extinct;
- body size is proven causal;
- hydroperiod preference is directly measured;
- breeding success increased;
- rainfall causality from observational data.

Use:
- acoustically active assemblage;
- active-community richness;
- species-selective reassembly;
- short-term environmental filter;
- body-size gradient;
- hydric-filter hypothesis.
