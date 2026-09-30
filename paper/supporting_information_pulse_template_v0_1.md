# Supporting Information

## Rainfall-associated chorus activation re-expresses persistent spatial structure in frog communities

This Supporting Information preserves secondary, falsification and alternative-mechanism analyses that are important for transparency but are not part of the main inferential spine.

The main article now focuses on:
1. multiscale expansion of the acoustically active community;
2. directional cross-dataset consistency of active-unit taxonomic deepening in NAAMP and FrogID;
3. exact species × stop incidence allocation benchmarked against both the original magnitude-matched uniform-activation null and a persistence-preserving stress test;
4. geographic, protocol-window and recorded acoustic-detection robustness.

Pairwise Sørensen stability is retained as secondary bounded context rather than as a title-level discovery because the equivalence margin was post hoc and the observed slope is not exceptional under the uniform-activation null.

Species-trait and response-trait analyses are retained here as falsification evidence. In particular, the proposed activation geometry was highly repeatable but failed a separately frozen placebo gate and is therefore **not** interpreted as a rainfall-specific response trait.

The analyses below were frozen and versioned before their own results were inspected where applicable. Their negative or non-headline results are retained explicitly to prevent outcome-dependent mechanism switching.

---

## S1. Analysis hierarchy and provenance

The original programme-level rainfall endpoint was frozen before the effect estimate was inspected. The metacommunity, matrix, functional and response-trait analyses were developed subsequently as post-opening mechanistic/community extensions.

For those extensions, the repository preserves:
- versioned contracts written before results were inspected;
- deterministic source hashes or pinned source versions;
- exact-consecutive-year sensitivities where applicable;
- exact algebraic identities for matrix decompositions;
- negative results and failed mechanism tests.

These safeguards do not convert post-opening questions into preregistered hypotheses. The main evidential claim rests on convergence among independently specified decompositions rather than on nominal significance of every extension.

---

## S2. Rain-recency timescale

The separately frozen rain-recency analysis used 7,848 eligible runs from 807 routes.

Run counts were:
- day 0: 2,255;
- day 1: 2,191;
- days 2–3: 2,020;
- days 4–7: 1,044;
- >=8 days: 338.

Within fixed route × seasonal-window strata, active-community richness relative to the >=8-day reference was:

| Recency bin | Difference in species | 95% CI | P |
|---|---:|---:|---:|
| day 0 | +0.654 | 0.448–0.860 | 5.08e-10 |
| day 1 | +0.544 | 0.350–0.739 | 3.86e-8 |
| days 2–3 | +0.411 | 0.227–0.596 | 1.26e-5 |
| days 4–7 | +0.381 | 0.202–0.561 | 3.11e-5 |

A stricter exact-consecutive-year dry-anchor sensitivity contained 289 pairs:

| Recency bin | Difference in species | 95% CI | P |
|---|---:|---:|---:|
| day 0 | +0.866 | 0.108–1.624 | .025 |
| day 1 | +0.450 | 0.109–0.790 | .0097 |
| days 2–3 | +0.416 | 0.091–0.741 | .012 |
| days 4–7 | +0.257 | -0.197–0.710 | .267 |

Therefore the association is not restricted to the calendar day of rain, but the data do not cleanly distinguish gradual post-rain decay from a contrast between recent-rain conditions and a sparse long-dry reference. We do not use “week-long pulse” as a headline inference.


---

## S3. Between-year turnover and nestedness

Matched wet–dry comparisons were also used to ask whether route-level compositional replacement increased with rainfall contrast.

The primary turnover coefficient was positive but imprecise (P = .104). In the exact-consecutive-year sensitivity, turnover increased with rainfall contrast (P = .0085). Nestedness-resultant change was unsupported in both the primary and exact-year analyses.

Because the primary turnover endpoint was not supported, We therefore do not headline compositional reassembly. These results are secondary to the within-run spatial decomposition of active stops, alpha, gamma and species × stop incidences.

---

## S4. Held-out response-diversity buffering test

A temporally held-out test estimated species wet/dry response signs in 2001–2007 and asked whether early response-sign diversity buffered route-level richness sensitivity in 2008–2015.

Early-period inputs:
- 16 estimable species;
- 846 eligible route × seasonal-window pools.

Validation set:
- 779 matched pairs;
- 177 routes.

Primary interaction:
- rainfall contrast × early response-sign diversity beta = **-0.954**;
- 95% CI = **-3.267 to 1.359**;
- P = **.419**.

Exact-consecutive-year sensitivity:
- 509 pairs;
- 144 routes;
- beta = +0.219;
- 95% CI = -2.352 to 2.789;
- P = .868.

The prespecified buffering prediction was therefore unsupported. Response diversity is present at the species level, but We do not claim that it stabilizes route-level active richness.


---

## S5. Alternative species-trait and context mechanisms

### S5.1 Body size

An initial pooled post-opening analysis suggested that smaller-bodied species had more positive wet-associated responses. Because body size is phylogenetically structured and the family-adjusted model was unstable, subsequent family-aware validation was treated as the stronger gate. The final family-stratified permutation did not authorize body size as the mechanism (P = .314).

We therefore do not claim that body size explains species rainfall responses.

### S5.2 Coarse hydroperiod coding

A prespecified ATraiU hydroperiod test was nonestimable because all 23 covered species were coded as using both temporary and permanent breeding waters. The available coarse binary coding therefore generated no among-species contrast.


The full receipt was produced in workflow run 36149886621 and is traceable through the artifact ID and digest stored in the summary.

### S5.3 Breeding-season breadth

Two separately versioned breeding-season encodings were evaluated and neither supported a mechanism.

**Phenology-filter encoding**
- n = 22 species;
- beta per month = +0.0262;
- 95% CI = -0.204 to 0.256;
- P = **.823**.

**Alternate continuous breadth encoding**
- n = 20 species;
- beta = -0.00123;
- 95% CI = -0.144 to 0.141;
- P = **.986**;
- Spearman rho = 0.168, P = .479.

The two null implementations reinforce the conclusion that breeding-season breadth, as available in the frozen transport, does not explain species rainfall-response differences.


### S5.4 Baseline recurrence and seasonal concentration

A temporally held-out episodic-participation test asked whether early-period acoustic recurrence or seasonal concentration predicted later wet-recruitment differences among species.

Across 28 cross-period matched species:
- baseline recurrence beta = +0.0639, 95% CI -0.259 to 0.387, P = **.698**;
- seasonal concentration beta = -0.00715, 95% CI -1.087 to 1.072, P = **.990**;
- combined episodicity Spearman rho = 0.080, P = .686.

Neither supplied a supported mechanism.


### S5.5 Historical route dryness

A held-out context analysis used 2001–2007 to define route-level baseline rainfall context and 2008–2015 for validation.

Primary rainfall-contrast × baseline-dryness interaction:
- n = 702 matched pairs across 117 routes;
- beta = +0.0247;
- 95% CI = -0.241 to 0.290;
- P = **.855**.

Exact-consecutive-year sensitivity:
- n = 480 pairs;
- beta = +0.148;
- P = .334.

The prespecified context-dependent amplification hypothesis was unsupported.


### S5.6 Compositional memory

A planned two-phase community-memory analysis required a dry–dry background family large enough to estimate ordinary compositional drift.

The separate frozen estimability audit found only:
- 338 total dry runs;
- 46 route-season strata with at least two dry runs;
- 40–53 candidate dry–dry pairs across 32–41 routes, depending on the frozen construction rule.

No candidate construction reached the required background gate. The memory-above-background endpoint is therefore **nonestimable**, not a negative effect estimate.


### S5.7 Early spatial niche breadth

A held-out response-trait hypothesis predicted that species with narrower early-period acoustic stop-use breadth would show stronger later wet recruitment.

The frozen directional prediction was falsified:
- 29 intersection species;
- pooled WLS beta = **+0.131**;
- 95% CI = 0.014–0.247;
- P = .028.

The observed pooled direction was opposite to the prediction, and the family-stratified permutation was unsupported:
- two-sided P = **.263**.

The opposite-direction pooled association is therefore not promoted as a mechanism.


### S5.8 Baseline spatial heterogeneity

A separate held-out hypothesis predicted that greater baseline among-stop acoustic beta diversity would strengthen later rainfall-associated gamma expansion.

The frozen positive-moderation support rule failed. In the full validation set (532 pairs, 106 routes), the interaction was actually opposite to prediction:
- gamma interaction beta = **-0.513**;
- 95% CI = -0.938 to -0.087;
- P = .018.

In the exact-consecutive-year sensitivity (365 pairs, 91 routes), the gamma interaction remained negative but was imprecise:
- beta = -0.354;
- 95% CI = -0.854 to 0.145;
- P = .165.

A secondary alpha interaction was negative in both the full validation (beta = -0.232, P = .0083) and exact-year subset (beta = -0.226, P = .0284). Because these directions were opposite to the frozen primary prediction, they are retained as secondary observations rather than promoted as a mechanism.


### S5.9 Functional trait space and rainfall-response alignment

A frozen four-axis AmphiBIO panel covered 93.2% of eligible run × species incidences and represented log body size, clutch size, offspring size and reproductive output.

Trait-covered richness increased with rainfall contrast:
- beta = **+0.2813**;
- 95% CI = 0.1516–0.4111;
- P = 2.14e-5.

However, mean pairwise functional distance did not show supported expansion:
- beta = **-0.0153**;
- 95% CI = -0.0434 to 0.0128;
- P = .285;
- richness-adjusted sensitivity P = .437.

Community-weighted means of all four traits showed no supported rainfall-associated shift after multiplicity correction.

Functional novelty balance was weakly positive in the full matched analysis:
- beta = +0.0419;
- P = .0422;

but the exact-consecutive-year sensitivity was imprecise:
- beta = +0.0483;
- P = .0640.

Among 24 response-eligible species with complete functional vectors, pairwise functional distance also failed to predict rainfall-response dissimilarity:
- Pearson r = **-0.0328**;
- 100,000 unrestricted response-label permutations: P = **.797**;
- within-family permutation sensitivity: P = **.739**.

These analyses do not identify a conventional life-history trait mechanism for the rainfall-associated community expansion.


### S5.10 Within-genus response heterogeneity

Adjusted wet-versus-dry species responses remained heterogeneous within operational genera after complex labels were excluded.

Among 26 species in seven genera:
- total heterogeneity Q = **141.68**, df = 25, P = 2.84e-18;
- within-genus Q = **66.41**, df = 19, P = 3.59e-7;
- between-genus Q = 75.26, df = 6, P = 3.39e-14;
- **46.9%** of total Q remained within genera.

Examples:
- *Hyla*: Q = 33.61, df = 5, P = 2.84e-6, with both positive and negative species;
- *Lithobates*: Q = 23.81, df = 6, P = 0.000565, with both positive and negative species;
- *Pseudacris*: Q = 3.89, df = 5, P = .566, with all six included species on the wet-associated side.

Broad genus identity therefore does not fully explain species-response heterogeneity. This is an operational genus decomposition rather than a phylogenetic comparative analysis.


---

## S6. Activation geometry: repeatability followed by placebo falsification

### S6.1 Why activation geometry initially appeared promising

Activation geometry was defined for wet-gain species × stop incidences as the opportunity-corrected log odds that a gain entered a stop that had been inactive in the paired drier survey rather than a stop that was already active. The offset was `logit(q)`, where `q` was the fraction of drier-run stops available in the inactive state.

Positive values were provisionally labelled “spatial-edge activators” and negative values “local taxonomic deepeners”.

The quantity showed strong reproducibility.

**Non-overlapping temporal validation**
- early period: 2001–2007;
- late period: 2008–2015;
- overlap species: 16;
- Spearman rho = **0.774**;
- P = **0.000439**;
- WLS late-on-early slope = **0.910**, 95% CI 0.816–1.003;
- 15/16 species retained the same sign, one-sided exact P = **0.000259**.

**Completely disjoint route-set validation**
- split A: 295 routes, 2,185 matched pairs;
- split B: 290 routes, 2,051 matched pairs;
- overlap species: 26;
- Spearman rho = **0.785**;
- P = **2.09e-6**;
- WLS B-on-A slope = **0.832**, 95% CI 0.542–1.122;
- 21/26 species retained the same sign, one-sided exact P = **0.00125**.

These results established that the species ordering was stable across time and route identities. They did **not**, however, establish that the ordering was specific to rainfall response.

### S6.2 Frozen placebo gate

**Reproducibility anchor.** Historical code supporting the falsification record, including the activation-geometry placebo, disjoint-route validation and AmphiBIO trait-audit scripts, is preserved on branch `history/pre-deep-cleanup-2026-09-28` at commit `cc6a71dfb3930af9f08b47311295806584abaeb1`.

Before reading placebo endpoints, a separate contract specified that activation geometry would remain in the title only if the wet-gain species ranking was **not** strongly reproduced by:

1. a reverse-direction dry-gain geometry;
2. wet-gain geometry in the bottom quartile of positive rainfall contrasts;
3. a baseline acoustic solitude tendency.

The same previously frozen strong-coupling criterion was reused: Spearman rho >= 0.60 with two-sided P < .05.

The fixed test family was the 16 species from the temporal-validation headline family. All 16 were estimable for every placebo quantity.

The gate failed decisively:

| Comparison with full wet-gain geometry | Spearman rho | P | Strong same-rank coupling? |
|---|---:|---:|---|
| reverse dry-gain geometry | **0.929** | 1.94e-7 | yes |
| low-rain-contrast wet geometry | **0.953** | 1.21e-8 | yes |
| opportunity-corrected baseline solitude geometry | **0.782** | 0.000341 | yes |
| raw singleton-calling fraction (descriptive) | **0.876** | 8.44e-6 | yes |

The low-rain-contrast placebo used the bottom quartile of the observed positive contrast distribution:
- cutpoint = **0.5596** on the frozen log rain-contrast scale;
- matched pairs = **1,065**.

Weighted regressions told the same story. Wet geometry was strongly predicted by reverse dry geometry (beta = 0.849), low-contrast geometry (beta = 0.920) and baseline solitude geometry (beta = 0.510).

### S6.3 Interpretation

The correct conclusion is therefore **not** that species possess a rainfall-specific activation geometry.

Instead, species have a stable acoustic co-occurrence/gain-placement tendency that appears in:
- wetter-direction gains;
- drier-direction gains;
- weak rainfall contrasts;
- ordinary singleton versus multispecies calling context.

The earlier temporal and disjoint-route repeatability results remain valid descriptively, but their stability is now better explained as a persistent species property that is not specific to rainfall direction.

Accordingly:
- activation geometry is removed from the title and main novelty claim;
- “spatial-edge activator” and “local taxonomic deepener” are not used as rainfall-response trait labels in the main article;
- geometry repeatability, route transfer and magnitude comparisons are retained here for auditability;
- no attempt is made to residualize, retune or redefine geometry after the failed gate.


---

## S7. Reconciliation with the earlier v0.4 conditional-multispecies result

An earlier repository manuscript version emphasized that rainfall did not detectably change the probability that an **already-active stop** contained multiple calling species.

The v0.4 activity-conditioned model used active stops as Bernoulli trials:
- response: stop has >=2 species versus exactly 1 species, conditional on >=1 caller;
- 8,043 runs;
- 61,650 active-stop trials;
- rain coefficient OR = **0.988**;
- 95% CI = 0.959–1.017;
- P = **.402**.

The current matched-pair alpha decomposition asks a related but **not identical** question. It first calculates a run-level fraction of active stops with >=2 species and then analyses the **wet-minus-dry change in that run-level fraction** across 4,236 matched route × seasonal-window pairs, with each matched pair contributing at the pair level.

For that matched estimator:
- rain-contrast beta for the >=2-species fraction component = **+0.02296**;
- 95% CI = 0.00461–0.04131;
- P = **.0142**.

The difference is therefore not a silent reversal of the same fitted model. The analyses differ in:
- observational unit and weighting: active-stop Bernoulli trials versus run-level fractions and matched-pair differences;
- exposure parameterization: pooled standardized dryness versus within-pair log rainfall-recency contrast;
- sample restriction: the current community analysis uses the complete ten-stop matched-run family;
- link/scale: conditional logistic odds versus pair-level difference in a run-level proportion.

Most importantly, the current local-alpha result does not depend mainly on the >=2 threshold. The exact decomposition of the active-stop mean-richness slope is:
- crossing from 1 to >=2 species: beta = **+0.02296**, about **28.9%** of the alpha slope;
- multiplicity beyond the second species: beta = **+0.05646**, about **71.1%** of the alpha slope.

Thus the main current result is broader than “more active stops become multispecies”. It is an increase in mean taxonomic depth among active stops, concentrated mostly above the two-species threshold.

Both results should be retained because they answer different estimands. The repository history makes that distinction auditable rather than treating the earlier null as if it never existed.


---

## S8. Additional interpretive boundaries

The analyses above concern acoustic activity. They do not establish:
- occupancy change;
- abundance change;
- colonization or extinction;
- dispersal among stops;
- demographic metacommunity connectivity;
- rainfall causality;
- physiological response half-lives.

Recorded hearing impairment, timeout, wind, traffic and MassNoiseIndex analyses constrain measured detection conditions as an explanation for the main multiscale pattern, but do not eliminate all unmeasured masking or species-specific detectability.

The frozen AmphiBIO functional panel covers body size, clutch size, offspring size and reproductive output. Null or weak relationships in that space do not establish that all ecological or physiological traits are irrelevant.

---

## S9. Endpoint policy

The activation-geometry placebo gate remains the final species-trait falsification for the species-trait analyses. It failed, so activation geometry is demoted rather than redefined.

No additional endpoint search is authorized to rescue activation geometry or replace it with another post-opening species trait in this manuscript.

Future mechanistic work should use independent data or independently sourced proximal traits and begin from a new frozen hypothesis family. The current article remains focused on the multiscale geometry of community expansion, matrix fill and beta diversity.


## Geographic generality audit


### Decision rule

The original matched model was refit 21 times, omitting one state per fit. PASS required every leave-one-state-out rainfall-contrast coefficient to remain positive for active-stop number, local alpha and route gamma. Strong PASS required all corresponding 95% confidence intervals to remain above zero. The audit achieved **strong PASS**.

| Omitted state | Active stops β [95% CI] | Local α β [95% CI] | Route γ β [95% CI] |
|---|---:|---:|---:|
| Delaware | 0.385 [0.237, 0.532] | 0.081 [0.023, 0.139] | 0.297 [0.173, 0.421] |
| Florida | 0.384 [0.240, 0.528] | 0.079 [0.023, 0.136] | 0.286 [0.165, 0.407] |
| Georgia | 0.414 [0.267, 0.561] | 0.088 [0.031, 0.146] | 0.303 [0.179, 0.427] |
| Indiana | 0.346 [0.196, 0.496] | 0.075 [0.014, 0.136] | 0.266 [0.136, 0.396] |
| Iowa | 0.378 [0.230, 0.526] | 0.074 [0.015, 0.133] | 0.287 [0.160, 0.414] |
| Kentucky | 0.381 [0.236, 0.526] | 0.080 [0.023, 0.136] | 0.288 [0.166, 0.410] |
| Maine | 0.401 [0.244, 0.558] | 0.079 [0.018, 0.141] | 0.293 [0.161, 0.426] |
| Maryland | 0.385 [0.233, 0.538] | 0.084 [0.023, 0.146] | 0.295 [0.165, 0.426] |
| Massachusetts | 0.433 [0.283, 0.583] | 0.096 [0.036, 0.156] | 0.329 [0.201, 0.458] |
| Mississippi | 0.372 [0.223, 0.522] | 0.050 [0.014, 0.085] | 0.218 [0.118, 0.318] |
| NewHampshire | 0.405 [0.255, 0.556] | 0.083 [0.024, 0.142] | 0.309 [0.183, 0.434] |
| NewJersey | 0.398 [0.253, 0.544] | 0.088 [0.029, 0.147] | 0.316 [0.190, 0.443] |
| NewYork | 0.394 [0.243, 0.545] | 0.079 [0.019, 0.139] | 0.300 [0.173, 0.428] |
| NorthCarolina | 0.357 [0.212, 0.503] | 0.070 [0.010, 0.129] | 0.244 [0.120, 0.369] |
| Pennsylvania | 0.362 [0.214, 0.510] | 0.080 [0.022, 0.138] | 0.282 [0.156, 0.408] |
| SouthCarolina | 0.377 [0.234, 0.520] | 0.074 [0.016, 0.132] | 0.262 [0.141, 0.382] |
| Tennessee | 0.385 [0.240, 0.531] | 0.083 [0.026, 0.139] | 0.292 [0.169, 0.414] |
| Texas | 0.386 [0.242, 0.530] | 0.080 [0.024, 0.136] | 0.286 [0.165, 0.408] |
| Vermont | 0.389 [0.244, 0.533] | 0.080 [0.023, 0.137] | 0.287 [0.165, 0.409] |
| Virginia | 0.351 [0.203, 0.498] | 0.081 [0.022, 0.139] | 0.270 [0.144, 0.396] |
| WestVirginia | 0.375 [0.231, 0.518] | 0.084 [0.026, 0.141] | 0.293 [0.169, 0.417] |


Across the 21 omissions, active-stop slopes ranged 0.346–0.433, local-alpha slopes 0.0496–0.0955 and route-gamma slopes 0.218–0.329. The smallest lower 95% confidence limits were +0.196, +0.0101 and +0.118, respectively. Thus no single sampled state controlled any headline association.

### State-specific heterogeneity

State-specific adjusted slopes were descriptive and were not part of the PASS rule. Nineteen states supported the route-clustered specification; Florida and Texas did not and are shown as NE. Positive slopes occurred in 16/19 estimable states for active-stop number and 13/19 for both local alpha and route gamma. Vermont had a wholly negative 95% confidence interval for active-stop number, and Massachusetts had a wholly negative interval for local alpha. No state had a wholly negative interval for route gamma. These patterns support geographic robustness of the pooled association but reject a claim of uniform state-level response.

| State | Active stops β | Local α β | Route γ β |
|---|---:|---:|---:|
| Delaware | 0.279 | 0.021 | -0.072 |
| Florida | NE | NE | NE |
| Georgia | -0.389 | -0.154 | -0.180 |
| Indiana | 0.772 | 0.138 | 0.537 |
| Iowa | 0.442 | 0.181 | 0.254 |
| Kentucky | 0.735 | 0.123 | -0.127 |
| Maine | 0.167 | 0.057 | 0.201 |
| Maryland | 0.371 | 0.033 | 0.195 |
| Massachusetts | -0.137 | -0.099 | -0.160 |
| Mississippi | 0.591 | 0.482 | 1.343 |
| NewHampshire | 0.209 | 0.024 | 0.013 |
| NewJersey | 0.220 | -0.064 | -0.177 |
| NewYork | 0.179 | 0.080 | 0.034 |
| NorthCarolina | 0.815 | 0.226 | 0.856 |
| Pennsylvania | 0.876 | 0.040 | 0.411 |
| SouthCarolina | 0.429 | 0.126 | 0.553 |
| Tennessee | 0.052 | -0.181 | -0.292 |
| Texas | NE | NE | NE |
| Vermont | -0.978 | -0.069 | 0.047 |
| Virginia | 1.033 | 0.066 | 0.631 |
| WestVirginia | 0.584 | -0.057 | 0.092 |


A secondary State random-intercept/random-slope model converged for active stops (population slope 0.381; state-slope SD 0.217) and local alpha (population slope 0.0760; state-slope SD 0.143, with a boundary warning). The route-gamma random-slope model did not converge and is therefore not used as inferential support. The leave-one-state-out gate remains the primary geographic-generality result.

**Interpretive boundary:** the audit establishes robustness to omission of any single sampled state, not a positive effect in every state, not equal effect sizes among states and not continental universality.


## Protocol-window sensitivity

The NAAMP national protocol specified that Gulf Coast and Great Plains routes should be conducted within three days of rainfall. After identifying this design feature, we froze a sensitivity contract before results were inspected to test whether the three headline associations were confined to comparisons entirely within that 0–3 day target window.

### Primary sensitivity: drier survey at least four days after rain

We required `dry_days_since_rain >= 4`, leaving 1,769 matched comparisons from 425 routes in 20 states. The original matched model and route-clustered covariance were unchanged.

| Response | n pairs | n routes | Rain-contrast β | 95% CI | P |
|---|---:|---:|---:|---:|---:|
| Active stops | 1,769 | 425 | 0.374 | 0.198 to 0.551 | 3.28 × 10^-5 |
| Local alpha | 1,729 | 419 | 0.0839 | 0.0140 to 0.154 | 0.0186 |
| Route gamma | 1,769 | 425 | 0.289 | 0.133 to 0.446 | 2.96 × 10^-4 |

The prespecified primary gate therefore achieved **strong PASS**: all three coefficients and all three 95% confidence intervals were positive.

### Secondary diagnostic: both surveys at least four days after rain

We next required `wet_days_since_rain >= 4`; because the wetter member necessarily has the smaller DaysSinceRain value, this places both members outside the 0–3 day window. Only 178 pairs from 111 routes in 18 states remained.

| Response | n pairs | n routes | Rain-contrast β | 95% CI | P |
|---|---:|---:|---:|---:|---:|
| Active stops | 178 | 111 | 1.333 | 0.494 to 2.173 | 0.00186 |
| Local alpha | 175 | 108 | 0.0861 | -0.106 to 0.278 | 0.379 |
| Route gamma | 178 | 111 | 0.196 | -0.441 to 0.832 | 0.547 |

All point estimates remained positive, but alpha and gamma were imprecise in this much smaller subset. This diagnostic was not assigned a PASS criterion and is not used to infer a long-duration rainfall effect.

**Interpretive boundary.** The primary sensitivity shows that the multiscale association is not confined to comparisons occurring entirely inside the national protocol's 0–3 day rain-target window. It does not eliminate programme scheduling, time-varying confounding, imperfect detection or other observational limitations, and it does not establish rainfall causality.


## Pre-submission inferential repair: uniform-activation null and Sørensen practical equivalence

### Uniform-activation null

The four-way incidence decomposition is an accounting identity, and a high boundary-crossing fraction can arise mechanically whenever overall activation increases. To provide an explicit comparator, we defined a uniform-activation null before final results were inspected.

Within each matched State × RouteNumber × RunNumber stratum, the candidate species pool was the union of species detected in any eligible run. Baseline species × StopNumber acoustic-detection propensities were estimated from unique drier-member runs only, with hierarchical shrinkage from the stratum mean to species means and then to species × stop cells. The primary shrinkage strength was κ = 2; κ = 1 and 5 were fixed sensitivities.

For each matched pair, the observed drier matrix was held fixed. One common additive shift on the log-odds scale was applied to all candidate species × stop probabilities, with that shift calibrated so the **expected** simulated wetter incidence count equalled the observed wetter incidence count for that pair. The null therefore conditions on response magnitude in expectation and tests the allocation of new acoustic participation through the matrix.

We generated 1,000 simulated wetter matrices for each smoothing specification. The primary four-dimensional vector contained the rainfall-contrast coefficients for corner expansion, spatial spread, taxonomic deepening and within-core rearrangement. The frozen omnibus statistic was the Mahalanobis distance from the simulated-null mean/covariance. Strong rejection required Monte Carlo P < .05 under κ = 1, 2 and 5.

The null was strongly rejected under all three specifications:

| κ | Monte Carlo P | Null mean boundary crossing | 95% null interval | Observed boundary crossing |
|---:|---:|---:|---:|---:|
| 1 | .000999 | 79.9% | 73.8–86.3% | 92.0% |
| 2 | .000999 | 80.9% | 74.2–87.4% | 92.0% |
| 5 | .000999 | 82.7% | 75.9–89.8% | 92.0% |

Under the primary κ = 2 specification:

| Component | Observed share | Null mean | 95% null interval | Observed percentile |
|---|---:|---:|---:|---:|
| Corner expansion | 36.9% | 27.4% | 23.3–31.6% | 100.0% |
| Spatial spread | 15.2% | 22.9% | 17.4–28.4% | 0.40% |
| Taxonomic deepening | 39.9% | 30.5% | 25.4–36.2% | 99.8% |
| Within-core rearrangement | 8.0% | 19.1% | 12.6–25.8% | 0.20% |
| Boundary crossing | 92.0% | 80.9% | 74.2–87.4% | 99.9% |

Thus the important result is not that most gains lie outside the pre-existing core—uniform activation already predicts that. The empirical departure is the **excess** boundary crossing, concentrated in corner expansion and taxonomic deepening, together with a deficit of within-core rearrangement and spatial spread by already-participating species.

A secondary κ = 2 simulation compared pairwise Sørensen slopes. Uniform activation produced a mean rainfall-contrast slope of -0.00615 with a 95% null interval of -0.0130 to +0.00178. The observed slope was -0.00049, at the 91.5th percentile of that null distribution and still inside its 95% interval. Therefore the uniform-null rejection comes from incidence allocation, not from an unusual beta-diversity response.

Three implementation repairs were versioned before final results were inspected:
1. separation of the four-component geometry gate from the conditional Sørensen estimand;
2. retention of matched strata with empty candidate pools as exact zero-incidence matrices;
3. restriction of candidate-pool construction to strata represented in the frozen 4,236-pair dataset.

None changed the decision threshold or endpoint family.


### Pairwise Sørensen practical equivalence

Because the conventional Sørensen coefficient had already been inspected, this was explicitly defined as a **post hoc bounded robustness test**, not a preregistered equivalence analysis. Before the equivalence endpoint was read, the practical-equivalence margin was fixed at ±0.025 dissimilarity units per unit log-rainfall contrast.

Primary analysis:
- n = 4,007 pairs / 576 routes;
- β = -0.000492;
- 90% CI = **-0.0107 to +0.00968**;
- complete interval inside [-0.025, +0.025]: **PASS**.

Exact-consecutive-year sensitivity:
- n = 2,562 pairs / 491 routes;
- β = +0.00215;
- 90% CI = **-0.00973 to +0.0140**;
- complete interval inside [-0.025, +0.025]: **PASS**.

The equivalence claim applies only to the pairwise Sørensen rainfall-contrast slope within this fixed margin. It does not imply exact invariance or equivalence of every beta-diversity metric.


## Cross-dataset consistency of active-unit taxonomic depth

### Rationale and frozen decision rule

After the matrix analyses had been defined, we explicitly reopened one response component for an estimand-aligned comparison: **taxonomic depth within an acoustic sampling unit that was already active**. This was chosen because it has the same ecological interpretation in standardized NAAMP route stops and FrogID recordings. Earlier FrogID analyses had already shown a rain-associated ≥2-species signal, so the continuous-depth analysis is treated as a **cross-dataset consistency check**, not an independent or blinded validation. The unfreeze, endpoint definition and decision tree were versioned before the Australian continuous-depth endpoint was read.

The North American side was not refit. Its already-authorized result was the rainfall-contrast coefficient for mean species richness per active NAAMP stop:

- β = **+0.0794 species per active stop**;
- 95% CI = **+0.0231 to +0.1357**;
- P = **0.00569**.

Because every retained FrogID recording already contains at least one expert-validated frog species, the directly corresponding Australian response was

`excess richness = recording species richness - 1`.

The Australian sample and rainfall exposure were unchanged from the earlier timezone-repaired FrogID validation:

- **40,754 recordings**;
- **1,623** 0.25° ERA5 cells;
- **13,148 recorders**;
- deterministic FrogID sampling by SHA256(eventID);
- maximum coordinate uncertainty 25 km;
- coordinate-timezone-repaired event date/hour;
- rainfall exposure = z-score of log(1 + antecedent dry days), using complete local calendar days before the event, a 1-mm wet-day threshold and a 30-day cap.

Higher exposure values therefore mean **drier conditions farther from recent rain**.

The primary Australian model was

`excess_richness ~ dry_z + State × Month + year_z + sin(hour) + cos(hour)`

estimated by OLS with cluster-robust covariance by ERA5 cell. Cross-continental consistency was authorized only if the Australian dry-spell coefficient and its complete 95% CI were below zero while the already-frozen NAAMP active-alpha interval remained above zero. Strong consistency additionally required the Australian recorder-clustered and within-ERA5-cell continuous-depth sensitivities to have complete negative 95% intervals.

No pooled effect size was authorized because the rainfall exposures and sampling designs differ between systems.

### Primary Australian result

The primary Australian continuous-depth result strongly supported the frozen direction:

- β per 1 SD increase in log dry-spell exposure = **-0.08176 species**;
- cluster-robust SE = **0.00837**;
- 95% CI = **-0.09816 to -0.06535**;
- P = **1.54 × 10^-22**.

Thus Australian recordings that occurred farther from recent rain contained fewer additional species beyond the first, conditional on the recording already being acoustically active.

### Frozen sensitivities

Recorder-clustered inference gave the same point estimate:

- β = **-0.08176**;
- 95% CI = **-0.09490 to -0.06862**;
- P = **3.44 × 10^-34**.

The within-ERA5-cell analysis retained 40,020 recordings from 1,071 informative cells and was also fully negative:

- β = **-0.09984**;
- 95% CI = **-0.11822 to -0.08146**;
- P = **1.82 × 10^-26**.

The frozen cross-system decision therefore achieved **STRONG PASS**.

### Deeper multiplicity endpoints

Two secondary endpoints were specified before results were inspected but had no role in the pass/fail gate.

For recordings containing at least three species:

- n = **8,327**;
- OR per 1 SD increase in log dry-spell exposure = **0.8458**;
- 95% CI = **0.8115 to 0.8815**;
- P = **2.12 × 10^-15**.

For excess richness beyond two species:

- β = **-0.04833**;
- 95% CI = **-0.05997 to -0.03668**;
- P = **4.16 × 10^-16**.

These results are notable because the older NAAMP activity-conditioned binary >=2-species result was null (OR = 0.988, P = 0.402), whereas the current NAAMP depth decomposition places approximately 71% of its active-alpha slope beyond the second species. The Australian >=3 and beyond-two endpoints show the same deeper-multiplicity direction. We therefore interpret the cross-system agreement as applying to **continuous taxonomic depth**, not necessarily to the first 1-to-2-species threshold.

### Interpretation boundary

Authorized:

> Directional cross-dataset consistency in rainfall-associated taxonomic deepening within already-active acoustic units across NAAMP and FrogID datasets from North America and Australia.

Not authorized:

- worldwide or universal rainfall response;
- independent-replication language for the FrogID continuous-depth analysis;
- equality or pooling of North American and Australian effect sizes;
- identical ecological mechanism in the two systems;
- demographic recruitment, occupancy change or abundance change;
- replication of the North American four-component spatial matrix geometry in FrogID.

FrogID lacks fixed ten-stop spatial matrices, so the uniform-activation geometry test described above remains a specifically North American analysis.


---

## Persistence-preserving uniform-activation stress test

### Motivation

The primary uniform-activation null estimates dry-history species × stop probabilities with hierarchical shrinkage toward species means. A reviewer-facing concern is that this may make stable cells too exchangeable and thereby inflate expected within-core rearrangement. We therefore added one separately specified stress test before results were inspected. No observed component definition, matched sample, covariate specification or magnitude-matching target was changed.

### Frozen construction

The candidate species pool remained the full eligible-run union within each State × RouteNumber × RunNumber stratum. Historical cell probabilities were estimated from unique drier-member runs only, but hierarchical species-level shrinkage was removed:

`p_hist = (y_cell + 0.5) / (n_dry_runs + 1)`.

Each matched pair then received a direct anchor to its observed dry species × stop state:

`p_anchor = (1 - a) p_hist + a I(dry-present)`.

The primary anchor weight was **a = 0.75**; **a = 0.50** and **0.90** were frozen sensitivities. At a = 0.90, dry-present cells begin close to one and dry-absent cells close to zero before the common activation shift, deliberately favouring strong temporal persistence.

For each pair, one additive log-odds shift was applied to all anchored cells and solved so that the expected wet incidence count matched the observed wet incidence count. We generated 1,000 simulations per anchor weight and tested the same four-component rainfall-coefficient vector by Mahalanobis distance. Strong rejection required Monte Carlo P < 0.05 at all three anchor weights. The allocation-centred title additionally required observed boundary crossing to exceed the primary a = 0.75 upper 95% null bound.

### Results

The persistence-preserving null was strongly rejected at all three frozen anchor weights:

| Anchor weight | Omnibus P | Null boundary mean | 95% null interval | Observed boundary |
|---|---:|---:|---:|---:|
| 0.50 | .000999 | 78.7% | 73.2–84.3% | 92.0% |
| 0.75 | .000999 | 77.9% | 73.4–82.8% | 92.0% |
| 0.90 | .000999 | 77.6% | 72.9–82.3% | 92.0% |

Under the primary a = 0.75 stress test:

- corner expansion: **36.9% observed vs 28.6% null mean**;
- spatial spread: **15.2% vs 19.3%**;
- taxonomic deepening: **39.9% vs 30.1%**;
- within-core rearrangement: **8.0% vs 22.1%**.

Thus stronger preservation of pair-specific dry cell identity does not explain the observed allocation. If anything, the persistence-favouring null predicts slightly less boundary crossing and more within-core rearrangement than the original κ = 2 null.

**Interpretive boundary:** rejection shows that the observed allocation is not reproduced by a common activation shift even when the null strongly preserves dry species × stop identity. These comparators still apply one common activation shift; we did not fit a null with species-specific shifts, which would test whether species-level response heterogeneity alone can reproduce the boundary allocation. The analyses therefore do not identify a unique biological mechanism. Preferential recruitment of combinations rare under dry conditions, including activation of temporary or intermittently suitable wet sites, is a plausible discussion-level hypothesis only.


---

## Robustness-method details moved from the main text

### Geographic generality audit

After the primary scientific story had been defined, we conducted an explicitly versioned pre-submission audit of geographic generality because broad spatial coverage does not by itself establish that a pooled effect is independent of one influential region. The audit contract and an estimability repair were committed before results were inspected. The three already-authorized headline responses—active-stop number, local alpha richness and route gamma richness—were refit 21 times, each time omitting one state while retaining the original covariates, State and RunNumber fixed effects for the remaining observations, and route-clustered covariance. The prespecified PASS criterion required all leave-one-state-out rainfall-contrast coefficients to remain positive for all three responses; strong PASS required every corresponding 95% confidence interval to remain above zero.

We also estimated state-specific slopes using the same covariates except the State term. These slopes were descriptive and were not used for the PASS decision; states for which route-clustered inference was not estimable were explicitly flagged. A secondary State random-intercept/random-slope model quantified heterogeneity where it converged. No state-specific significance threshold was used as a criterion for generality.

### Protocol-window sensitivity

Because the national NAAMP protocol targeted surveys within three days of rain in Gulf Coast and Great Plains programmes, we froze a post hoc design-sensitivity analysis before reading its endpoints. We refit the three existing headline responses with the original matched model after requiring the drier member of each pair to have DaysSinceRain >= 4. This primary subset therefore excluded comparisons occurring entirely within the protocol-target 0–3 day window. The prespecified PASS criterion required positive rainfall-contrast coefficients for active-stop number, local alpha richness and route gamma richness; strong PASS required all three 95% confidence intervals to remain above zero. A stricter secondary diagnostic required the wetter member also to have DaysSinceRain >= 4, so both surveys lay outside the target window. Because that restriction was expected to remove many immediate-rain contrasts, it had no PASS criterion.

### Recorded detection-condition robustness

Because acoustic community metrics can be affected by hearing conditions, we prespecified a reviewer-robustness analysis using survey-quality fields recorded by NAAMP. Regional programmes recorded ambient hearing impairment either as a yes/no `Noise` field or with the Massachusetts noise index. We standardized a stop as hearing-impaired when `Noise = 1` or, when the Massachusetts index was available, when `MassNoiseIndex >= 2`; indices 0–1 were treated as not materially impairing sampling. We also used `TimeOut`, which records major noise interruptions during which the listening period was paused, and the mean of valid start- and end-of-run Beaufort wind codes.

For each eligible run we calculated the fraction of sampled stops with recorded hearing impairment, the timeout fraction and mean wind. Primary robustness models added wet-minus-dry differences in these three quantities to the matched-pair models for active-stop count, local alpha richness and route gamma richness. The primary detection-quality sample required at least eight valid stop-level noise and timeout records per run and valid start/end wind in both members of the pair. Prespecified sensitivities additionally adjusted for mean stop-level car counts where at least eight values were available and, in programmes using it, replaced the binary impairment fraction with mean Massachusetts noise index. These analyses constrain measured acoustic detection conditions as an explanation but do not constitute a complete detection model.

### Same-observer sensitivity

Observer turnover could in principle create apparent recruitment if different observers differ in their ability to detect infrequently calling species. We therefore first audited the frozen public NAAMP run schema without inspecting outcome contrasts. The field `ObserverTrackingID` was nonempty in all 21,934 run records and contained 2,301 unique identifiers. We then froze a same-observer reviewer-robustness contract before results were inspected and restricted the existing wetter–drier matched design to pairs in which both runs had the same nonempty `ObserverTrackingID`.

The restriction retained **3,152 of 4,236 pairs (74.4%)**, spanning **500 routes and 542 observer identifiers**. All three headline rainfall-contrast coefficients remained positive with 95% confidence intervals excluding zero: active-stop number β = **0.352** (95% CI 0.179–0.525), richness per active stop β = **0.098** (0.028–0.169; 3,071 estimable pairs), and route richness β = **0.319** (0.171–0.466).

The matrix geometry was also retained. The observed component shares were **34.6% corner expansion, 12.8% spatial spread, 44.6% taxonomic deepening and 8.0% within-core rearrangement**, giving **92.0% boundary crossing**. Under the primary magnitude-matched uniform-activation null (κ = 2), expected boundary crossing was **80.3%** (95% interval 73.0–87.1%) and the four-component omnibus was rejected (Monte Carlo P = 0.001). The same conclusion held at κ = 1 and 5 (both P = 0.001); observed boundary crossing remained above every frozen 95% interval.

The persistence-preserving stress test gave the same result. At the primary 0.75 dry-state anchor, expected boundary crossing was **79.1%** (73.3–84.9%) versus 92.0% observed, with omnibus P = 0.001. Anchors 0.50, 0.75 and 0.90 all rejected the comparator (P ≤ 0.002), and the observed boundary share exceeded every corresponding 95% interval. The prefrozen classification was therefore **observer robust**. This analysis does not establish that observers are interchangeable, but it shows that between-observer turnover is not required to generate the expansion or boundary-allocation result within the large same-observer subset.




---

## S10. Calling-state decomposition and direct full-chorus activation

### S10.1 Provenance and question

These analyses were conducted after the RC11 matrix results were known. The CallingIndex decomposition was developed during post-freeze mechanism exploration. The direct 0→CallingIndex 3 endpoint was fixed in `exploration/NAAMP_NEW_FULL_CHORUS_ACTIVATION_CONTRACT_V0_1.json` before that endpoint was read.

The question was whether rainfall-associated recruitment was confined to marginal CallingIndex 1 detections or included direct entry from acoustic silence to overlapping/full chorus states.

CallingIndex semantics were retained from NAAMP:
- CI1: individual calls distinguishable, no overlap;
- CI2: calls overlap but individuals remain distinguishable;
- CI3: continuous/full chorus, individuals not distinguishable.

### S10.2 Decomposition

Across the frozen 4,236 matched pairs, the total rainfall-associated CallingIndex coefficient was **2.8410**. Activation from CallingIndex 0 to any positive state contributed **1.8549**, or **65.3%** of the total. Direct 0→CI2/3 activation contributed **1.6150**, or **87.1%** of the activation coefficient.

Direct 0→CI3 activation was positive:

- full sample: **β = 0.4406**, 95% CI **0.1136–0.7675**;
- same-observer + identical physical SiteID subset (3,115 pairs): **β = 0.5141**, 95% CI **0.1008–0.9273**.

The robust subset simultaneously holds observer identity and physical listening-site identity constant. These results concern acoustic chorus state, not exact caller abundance or reproductive success.

### S10.3 Recorded detection-condition robustness

For the combined strong activation endpoint (0→CI2/3), adjustment for recorded hearing impairment, major-noise timeout and wind gave **β = 1.6225**, 95% CI **0.4587–2.7864**.

These analyses constrain measured acoustic conditions but do not make dry acoustic zeros equivalent to confirmed biological absence.

## S11. Spatial depth of recruited route species

### S11.1 Exact decomposition

The post-freeze spatial-depth analysis was fixed before endpoint readback in `NAAMP_ROUTE_NEW_SPATIAL_DEPTH_CONTRACT_V0_1.json`.

For every species absent from the entire dry route and present in the wet route, (k) was the number of wet stops occupied. Extra spatial participation was decomposed into:

- second-stop incidence: one incidence for every species with (k≥2);
- third-and-later incidence: (max(k-2,0));
- fourth-and-later incidence: (max(k-3,0)).

The prefixed spatial-depth criterion required third-and-later incidence to exceed the upper 95% range under both the primary κ=2 uniform-activation null and the primary a=0.75 persistence-preserving null.

### S11.2 Results

The second-stop coefficient was **β = 0.132** and was not exceptional under either primary null.

By contrast:

- third-and-later incidence: **β = 0.473**, above both primary-null 95% ranges, with plus-one Monte Carlo **P = 0.000999** under each;
- fourth-and-later incidence: **β = 0.363**, also above the null ranges.

The third-and-later coefficient was carried almost entirely by substantial chorus states:

- CI2/3 share in the full sample: **97.3%**;
- CI2/3 share in the same-observer + same-physical-site subset: **95.4%**.

CI1-only spatial deepening was not supported.

### S11.3 Higher-order spatial coherence conditional on recruitment and total spread

After the existing conditional-spread and third-and-later results were known, we fixed a distinct higher-order test before reading its endpoint in `NAAMP_HIGHER_ORDER_SPATIAL_COHERENCE_CONTRACT_V0_1.json`. The interpretation for both PASS and FAIL outcomes was also frozen before endpoint readback in `HIGHER_ORDER_SPATIAL_COHERENCE_DECISION_NOTE_V0_1.md`.

For each route-new species occupying (k) wet stops, define (e=max(k-1,0)). We calculated

`higher_order_within_species_mass = choose(e,2) = e(e-1)/2`.

This statistic is zero for (k≤2) and grows convexly for (k≥3). For example, if three recruited taxa collectively contribute three extra-stop incidences, allocating them as one extra stop to each taxon gives mass 0, whereas allocating all three extra incidences to one taxon gives mass 3. Thus it distinguishes deep within-taxon concentration from the amount of recruitment or spread itself.

For each primary null family, 1,000 simulated coefficient triplets were generated:

1. route-new-species gain;
2. total extra-stop incidence;
3. higher-order within-species mass.

Across the 1,000 simulations we fitted

`higher_beta = intercept + b1 * new_species_beta + b2 * extra_stop_beta`.

The primary statistic was the observed higher-order coefficient minus the null prediction evaluated at the observed route-new-species and extra-stop coefficients. Support required this conditional residual to exceed the upper 95% simulated residual bound under **both** null families.

Observed first-order coefficients were:

- route-new-species gain: **β = 0.1847**;
- extra-stop incidence gain: **β = 0.6043**.

The observed higher-order coefficient was **β = 1.5240**.

Under the κ=2 uniform-activation null:

- predicted higher-order β at the observed first-order coefficients: **1.1384**;
- observed conditional residual: **0.3856**;
- null residual 95% interval: **−0.0984 to 0.0959**;
- plus-one upper-tail **P = 0.000999**.

Under the a=0.75 persistence-preserving null:

- predicted higher-order β: **0.7836**;
- observed conditional residual: **0.7404**;
- null residual 95% interval: **−0.0805 to 0.0824**;
- plus-one upper-tail **P = 0.000999**.

The prefixed classification was therefore **higher-order spatial coherence supported**.

A separate conditional route-topology analysis had already shown that adjacent-stop links increased with rainfall contrast (**β = 0.4194**) and remained above the upper conditional residual range under both primary nulls after conditioning on total extra-stop spread (both **P = 0.000999**).

These tests establish non-independent spatial expression at the route scale. They do **not** establish literal simultaneity because stops were surveyed sequentially, nor do they identify movement, hydrological connectivity, social facilitation or a causal rainfall mechanism.

## S12. Historical recurrence of apparent wet-state recruitment

### S12.1 Route-new incidence recurrence

The recurrent-activation analysis was fixed before endpoint readback in `NAAMP_RECURRENT_ACTIVATION_MEMORY_CONTRACT_V0_1.json` and restricted to physically stable pairs.

Leave-pair-out history classified focal route-new wet incidences as same-site recurrent, route-only recurrent or one-off within the State × RouteNumber × RunNumber stratum.

The rainfall-associated recurrent share was **98.1%**. In a stricter classification using only runs before the focal pair, the recurrent share was **98.9%**. The strictly-prior one-off/no-prior component was approximately zero (**β = 0.0094**, 95% CI **−0.1412–0.1600**).

These raw shares are descriptive because the probability of having some previous record increases with monitoring duration.

### S12.2 Direct full-chorus recurrence

For focal cells switching from 0→CI3:

- leave-pair-out any-history recurrent share of the new-CI3 coefficient: **98.1%**;
- leave-pair-out same-physical-site recurrent share: **90.4%**;
- strictly-prior same-site recurrent share: **82.6%**.

A prior record at the same SiteID may reflect stable habitat suitability, repeated breeding-site use or other persistent spatial structure; it does not prove continuous occupancy or return of the same individuals.

## S13. Within-species historical site targeting

The local-targeting analysis was fixed before endpoint readback in `NAAMP_LOCAL_CHORUS_MEMORY_TARGETING_CONTRACT_V0_1.json`.

Focal species were absent from all ten dry stops, present in the wet survey and recorded somewhere on the route in a strictly prior year. The unit was pair × species × physical SiteID. The predictor was whether that same species had previously reached CI2/3 at the SiteID.

Both predictor and response were demeaned within pair × species, so the coefficient compares sites for the **same species in the same focal pair**.

Results:

- prior strong SiteID → wet CI2/3: **β = 0.1511**, 95% CI **0.1291–0.1731**;
- prior strong SiteID → wet CI3: **β = 0.0778**, 95% CI **0.0619–0.0937**;
- same-observer primary result: **β = 0.1589**, 95% CI **0.1344–0.1833**.

This identifies repeated spatial placement of strong acoustic activity. It does not identify individual memory or philopatry.

## S14. Rain-selective historical targeting

A historical site may be repeatedly favourable even without rain selectivity. The directional placebo analysis in `NAAMP_RAIN_SELECTIVE_LOCAL_MEMORY_CONTRACT_V0_1.json` therefore mirrored wet-target and dry-target directions within each matched pair.

For each direction, the endpoint was the CI3 rate among historically strong candidate cells minus the CI3 rate among non-recurrent candidate cells. Target-rain advantage was +rain_contrast for the wet direction and −rain_contrast for the dry direction, and both endpoint and predictor were demeaned within pair.

The primary coefficient was positive:

- **β = 0.02449**, 95% CI **0.00700–0.04198**;
- same-observer sensitivity: **β = 0.03067**, 95% CI **0.01331–0.04804**.

Thus proximity to rain selectively strengthens full-chorus placement at sites with a prior strong record beyond generic recurrence.

## S15. Nested mechanism-null sequence

### S15.1 Rationale

The integrated manuscript does not infer a mechanism from a single null rejection. Instead, post-freeze exploration evaluated an ordered set of increasingly structured generative comparators. Each comparator was fixed before its own endpoint readback. The final escalation path was itself governed by `MECHANISM_DECISION_TREE_V0_1.json`.

### S15.2 Sequence

| Null family | Population | Plus-one Monte Carlo P | Decision |
|---|---:|---:|---|
| Uniform activation | 4,236 pairs | 0.000999 | rejected |
| Persistence-preserving activation | 4,236 pairs | 0.000999 | rejected |
| Route-cross-fit species-specific rainfall shifts | full eligible sample | 0.001998 | rejected |
| Strictly-prior local species × SiteID history | 2,916 pairs | 0.000999 | rejected |
| Joint cross-fit species + prior local history + dry persistence | 2,916 pairs | 0.000999 | rejected |
| Final held-out rain × local-history gate | 2,916 pairs | 0.000999 | rejected; stop mechanism escalation |

Under the final held-out null:

- observed boundary-crossing share = **0.9213**;
- null boundary mean = **0.8138**;
- observed taxonomic-deepening share = **0.3988**;
- null taxonomic-deepening mean = **0.3158**;
- observed within-core share = **0.0787**;
- null within-core mean = **0.1862**.

### S15.3 Final stopping rule

The prefixed decision tree required stopping after rejection of the held-out rain × local-history gate. It explicitly prohibited additional trait fishing, same-data site-specific rainfall coefficients, relaxed gates or further mechanism models.

The authorized interpretation is therefore **structured state-dependent re-expression with an unresolved lower-level generator**, not identification of a unique mechanism.

## S16. Taxonomic and geographic breadth of strong activation

Strong activation was distributed across the species pool:

- species represented: **57**;
- species with positive strong-activation contributions: **28**;
- largest positive contributor: **13.9%** of positive mass;
- top five contributors: **49.2%**;
- HHI of positive contribution shares: **0.074**;
- removing any single species left the total coefficient positive.

Geographically, removing each state in turn left the total strong-activation coefficient positive with a positive 95% CI.

State-specific effects were nevertheless heterogeneous:

- estimable states: **19**;
- positive point estimates: **13/19**;
- entirely positive 95% CIs: **6/19**;
- random-slope population estimate: **1.65**;
- state-slope SD: **3.46**.

The result is therefore programme-scale robust but not spatially homogeneous.

## S17. Integrated provenance hierarchy

The integrated manuscript deliberately distinguishes three evidence classes.

### S17.1 Frozen RC11 evidence

Includes:
- 4,236 matched-pair design;
- active-stop, active-stop alpha and route-gamma associations;
- exact four-component species × stop decomposition;
- κ-based uniform-activation null;
- persistence-preserving null;
- detection-condition, protocol-window, same-observer and geographic robustness;
- FrogID active-unit taxonomic-depth consistency.

### S17.2 Post-freeze analyses fixed before their own endpoint readback

Includes:
- direct 0→CI3 endpoint;
- route-new spatial-depth decomposition;
- conditional extra-stop coherence and adjacent-stop linkage;
- higher-order within-taxon spatial coherence conditional on both recruitment and total spread;
- recurrent-activation decomposition;
- direct full-chorus recurrence;
- within-pair × species historical-site targeting;
- directional rain-selective historical targeting;
- cross-fit species-specific shift null;
- strictly-prior local-history null;
- joint species + history + dry-persistence null;
- held-out rain × local-history gate.

These tests are protected against retuning after their own readback but remain post-opening relative to the original manuscript.

### S17.3 Descriptive or non-gating diagnostics

Includes raw recurrence percentages, memory-age diagnostics that failed their prefixed route-count gate, and candidate-mediator analyses without an authorized mechanism classification.

### S17.4 Manuscript-level interpretation

The integrated paper is therefore a transparent synthesis of frozen and post-freeze evidence. The central biological pattern is stronger than RC11's original boundary-allocation description, but it is not presented as a prospectively preregistered fast-gate × slow-template hypothesis.
