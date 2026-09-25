# Ecological argument spine v0.2 — rainfall-pulse community reassembly

## Working title

**Rainfall-associated richness gains accompany species-selective reassembly of active frog communities**

## Biological question

Rainfall-driven frog calling is established. The ecological question is:

> **When rainfall increases acoustic activity, does it amplify the same assemblage or rapidly reorganize which species constitute the active community?**

The paper is therefore about short-timescale community dynamics, not the detection process.

## Design

Central system: standardized NAAMP only.

Matched comparison:
- same State × RouteNumber × RunNumber;
- complete 10-stop, temperature-qualified runs;
- adjacent observed years;
- wetter vs drier orientation from DaysSinceRain;
- pair-level adjustment for temperature difference, day-of-year difference and year gap.

Primary dataset:
- 4,236 wet–dry pairs;
- 585 routes;
- 21 states;
- 7,848 eligible runs.

Exact consecutive-year sensitivity:
- 2,693 pairs.

## Claim 1 — wetter matched runs have richer active communities

Primary richness-gain slope:
- β = **+0.2859 species / unit log-rain contrast**;
- 95% CI **0.1646–0.4072**;
- P = **3.81 × 10^-6**.

Exact consecutive-year:
- β = **+0.3009**;
- 95% CI **0.1447–0.4572**;
- P = **1.60 × 10^-4**.

This establishes a community-level response beyond “more total calling”: more species constitute the active assemblage under wetter matched conditions.

## Claim 2 — richness gain is not simple nested addition

Nestedness:
- primary P = 0.279;
- exact consecutive-year P = 0.711.

Turnover:
- primary β = +0.01264, P = 0.104;
- exact consecutive-year β = **+0.01840**;
- 95% CI **0.00470–0.03211**;
- P = **0.00850**.

Therefore the wet assemblage is not simply the dry assemblage plus extra species. The strict consecutive-year sensitivity supports compositional replacement.

## Claim 3 — reassembly is strongly species-selective

Raw species family:
- 29 eligible species;
- χ² = **165.45**, df = 28;
- P = **1.91 × 10^-21**;
- FDR 5%: 9 wet-recruited, 3 dry-retained.

Pair-covariate-adjusted responses:
- 29/29 estimable;
- Q = **144.01**, df = 28;
- P = **1.46 × 10^-17**;
- raw vs adjusted Spearman ρ = **0.997**;
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

This is the strongest evidence against a uniform community-wide activation model.

## Secondary trait result — body size is not the mechanism authority

AmphiBIO pooled association:
- raw species response β(log body size) = **-0.3353**, P = **5.17 × 10^-7**;
- adjusted species response β = **-0.3670**, P = **1.23 × 10^-6**;
- Spearman ρ = **-0.517**, P = **0.00687**.

But family-stratified permutation:
- 26 species;
- 5 families;
- observed within-family slope = **-0.1889**;
- 100,000 permutations;
- two-sided P = **0.314**;
- negative-tail P = **0.151**.

Therefore:
> body size is a pooled cross-species correlate, not a family-robust mechanism.

It belongs in a secondary Results paragraph / Supplement, not the title, abstract conclusion or central mechanism.

## Supporting mechanism from earlier decomposition

The prior NAAMP decomposition remains useful as support:
- rain increases P(any calling stop);
- rain increases run-level active species richness;
- P(>=2 | >=1 active) is null;
- plug-in residual is null;
- fixed-marginal shuffle residual is null;
- pairwise network density is null.

This says the rainfall response is expressed more strongly in **active-community participation/membership** than in residual co-calling among already-active species.

## Role of FrogID

FrogID is not required for the main ecology article.

Recommended:
- supplementary contextual analysis only;
- do not use it to define the ecological claim.

## Ecological synthesis

> **Short rainfall pulses are associated with richer but compositionally different active frog assemblages. Species responses are highly non-uniform and remain so after matched-pair environmental adjustment, indicating rapid species-selective reassembly rather than uniform activation of a fixed assemblage.**

General implication:

> **Behaviourally realized communities can be reorganized by short environmental pulses on timescales much shorter than occupancy change.**

## Hard boundaries

Do not claim:
- rainfall changes occupancy or abundance;
- wet-only species colonized;
- dry-only species went extinct;
- classical environmental filtering through establishment/persistence;
- body size is a proven or family-robust mechanism;
- hydroperiod preference is directly tested;
- rainfall causality;
- breeding success increased.

Use:
- acoustically active assemblage;
- active-community richness;
- species-selective reassembly;
- short environmental pulse;
- temporal turnover;
- species-specific wet/dry response.
