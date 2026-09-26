# Supporting Information — JAE RC6 v0.2

## Rainfall-associated expansion of frog active communities adds sites and species without detectable beta-diversity change

This Supporting Information preserves secondary, falsification and alternative-mechanism analyses that are important for transparency but are not part of the main inferential spine.

The main article now focuses on:
1. multiscale expansion of the acoustically active community;
2. practical equivalence of active-matrix fill;
3. exact species × stop boundary decomposition;
4. robustness to recorded acoustic detection conditions.

Species-trait and response-trait analyses are retained here as falsification evidence. In particular, the proposed activation geometry was highly repeatable but failed a separately frozen placebo gate and is therefore **not** interpreted as a rainfall-specific response trait.

The analyses below were frozen and versioned before their own endpoint readback where applicable. Their negative or non-headline results are retained explicitly to prevent outcome-dependent mechanism switching.

---

## S1. Analysis hierarchy and provenance

The original programme-level rainfall endpoint was frozen before effect readback. The metacommunity, matrix, functional and response-trait analyses were developed subsequently as post-opening mechanistic/community extensions.

For those extensions, the repository preserves:
- versioned contracts written before endpoint readback;
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

Therefore the association is not restricted to the calendar day of rain, but the data do not cleanly distinguish gradual post-rain decay from a contrast between recent-rain conditions and a sparse long-dry reference. RC6 does not use “week-long pulse” as a headline inference.

Authoritative files:
- `NAAMP_RAINFALL_PULSE_TIMESCALE_CONTRACT_V0_1.json`
- `NAAMP_RAINFALL_PULSE_TIMESCALE_SUMMARY_V0_1.json`
- `scripts/run_naamp_rainfall_pulse_timescale.py`

---

## S3. Between-year turnover and nestedness

Matched wet–dry comparisons were also used to ask whether route-level compositional replacement increased with rainfall contrast.

The primary turnover coefficient was positive but imprecise (P = .104). In the exact-consecutive-year sensitivity, turnover increased with rainfall contrast (P = .0085). Nestedness-resultant change was unsupported in both the primary and exact-year analyses.

Because the primary turnover endpoint was not supported, RC6 does not headline compositional reassembly. These results are secondary to the within-run spatial decomposition of active stops, alpha, gamma and species × stop incidences.

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

The prespecified buffering prediction was therefore unsupported. Response diversity is present at the species level, but RC6 does not claim that it stabilizes route-level active richness.

Authoritative files:
- `NAAMP_RESPONSE_DIVERSITY_BUFFERING_CONTRACT_V0_1.json`
- `NAAMP_RESPONSE_DIVERSITY_BUFFERING_SUMMARY_V0_1.json`
- `scripts/run_naamp_response_diversity_buffering.py`

---

## S5. Alternative species-trait and context mechanisms

### S5.1 Body size

An initial pooled post-opening analysis suggested that smaller-bodied species had more positive wet-associated responses. Because body size is phylogenetically structured and the family-adjusted model was unstable, subsequent family-aware validation was treated as the stronger gate. The final family-stratified permutation did not authorize body size as the mechanism (P = .314).

RC6 therefore does not claim that body size explains species rainfall responses.

### S5.2 Coarse hydroperiod coding

A prespecified ATraiU hydroperiod test was nonestimable because all 23 covered species were coded as using both temporary and permanent breeding waters. The available coarse binary coding therefore generated no among-species contrast.

Authoritative files:
- `NAAMP_HYDROPERIOD_FILTER_CONTRACT_V0_1.json`
- `NAAMP_HYDROPERIOD_FILTER_SUMMARY_V0_1.json`
- `scripts/run_naamp_hydroperiod_filter.py`

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

Authoritative files:
- `NAAMP_BREEDING_SEASON_FILTER_CONTRACT_V0_1.json`
- `NAAMP_BREEDING_SEASON_FILTER_SUMMARY_V0_1.json`
- `scripts/run_naamp_breeding_season_filter.py`
- `NAAMP_BREEDING_SEASON_BREADTH_CONTRACT_V0_1.json`
- `NAAMP_BREEDING_SEASON_BREADTH_SUMMARY_V0_1.json`
- `scripts/run_naamp_breeding_season_breadth.py`

### S5.4 Baseline recurrence and seasonal concentration

A temporally held-out episodic-participation test asked whether early-period acoustic recurrence or seasonal concentration predicted later wet-recruitment differences among species.

Across 28 cross-period matched species:
- baseline recurrence beta = +0.0639, 95% CI -0.259 to 0.387, P = **.698**;
- seasonal concentration beta = -0.00715, 95% CI -1.087 to 1.072, P = **.990**;
- combined episodicity Spearman rho = 0.080, P = .686.

Neither supplied a supported mechanism.

Authoritative files:
- `NAAMP_CROSSPERIOD_EPISODIC_RECRUITMENT_CONTRACT_V0_1.json`
- `NAAMP_CROSSPERIOD_EPISODIC_RECRUITMENT_SUMMARY_V0_1.json`
- `scripts/run_naamp_crossperiod_episodic_recruitment.py`

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

Authoritative files:
- `NAAMP_CONTEXT_DEPENDENT_PULSE_CONTRACT_V0_1.json`
- `NAAMP_CONTEXT_DEPENDENT_PULSE_SUMMARY_V0_1.json`
- `scripts/run_naamp_context_dependent_pulse.py`

### S5.6 Compositional memory

A planned two-phase community-memory analysis required a dry–dry background family large enough to estimate ordinary compositional drift.

The separate frozen estimability audit found only:
- 338 total dry runs;
- 46 route-season strata with at least two dry runs;
- 40–53 candidate dry–dry pairs across 32–41 routes, depending on the frozen construction rule.

No candidate construction reached the required background gate. The memory-above-background endpoint is therefore **nonestimable**, not a negative effect estimate.

Authoritative files:
- `NAAMP_TWO_PHASE_COMMUNITY_MEMORY_CONTRACT_V0_1.json`
- `NAAMP_TWO_PHASE_COMMUNITY_MEMORY_SUMMARY_V0_1.json`
- `scripts/run_naamp_two_phase_community_memory.py`
- `DRY_DRY_BACKGROUND_ESTIMABILITY_AUDIT_CONTRACT_V0_1.json`
- `DRY_DRY_BACKGROUND_ESTIMABILITY_AUDIT_SUMMARY_V0_1.json`
- `scripts/audit_dry_dry_background_estimability.py`

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

Authoritative files:
- `NAAMP_SPATIAL_NICHE_BREADTH_RESPONSE_CONTRACT_V0_1.json`
- `NAAMP_SPATIAL_NICHE_BREADTH_RESPONSE_SUMMARY_V0_1.json`
- `scripts/run_naamp_spatial_niche_breadth_response.py`

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

Authoritative files:
- `NAAMP_LATENT_SPATIAL_HETEROGENEITY_CONTRACT_V0_1.json`
- `NAAMP_LATENT_SPATIAL_HETEROGENEITY_SUMMARY_V0_1.json`
- `scripts/run_naamp_latent_spatial_heterogeneity.py`


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

Authoritative files:
- `NAAMP_FUNCTIONAL_COMMUNITY_EXPANSION_SUMMARY_V0_1.json`
- `NAAMP_FUNCTIONAL_RESPONSE_DECOUPLING_SUMMARY_V0_1.json`
- `scripts/run_naamp_functional_community_expansion.py`
- `scripts/run_naamp_functional_response_decoupling.py`

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

Authoritative files:
- `NAAMP_SPECIES_RESPONSE_WITHIN_GENUS_CONTRACT_V0_1.json`
- `NAAMP_SPECIES_RESPONSE_WITHIN_GENUS_SUMMARY_V0_1.json`
- `scripts/run_naamp_species_response_within_genus.py`

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

Authoritative files:
- `NAAMP_SPECIES_ACTIVATION_GEOMETRY_REPEATABILITY_SUMMARY_V0_1.json`
- `NAAMP_SPECIES_ACTIVATION_GEOMETRY_ROUTE_SPLIT_SUMMARY_V0_1.json`
- `NAAMP_RESPONSE_GEOMETRY_VS_MAGNITUDE_SUMMARY_V0_1.json`
- `NAAMP_ACTIVATION_GEOMETRY_PLACEBO_CONTRACT_V0_1.json`
- `NAAMP_ACTIVATION_GEOMETRY_PLACEBO_SUMMARY_V0_1.json`
- `scripts/run_naamp_activation_geometry_placebo_gate.py`

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

Authoritative files:
- `MANUSCRIPT_JAE_V0_4.md`
- `NAAMP_MECHANISM_DECOMPOSITION_RECEIPT_V0_1.json`
- `NAAMP_WITHIN_ACTIVE_DEPTH_SUMMARY_V0_1.json`
- `scripts/run_naamp_mechanism_decomposition.py`
- `scripts/run_naamp_within_active_depth_decomposition.py`

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

The activation-geometry placebo gate is the final species-trait falsification for RC6. It failed, so activation geometry is demoted rather than redefined.

No additional endpoint search is authorized to rescue activation geometry or replace it with another post-opening species trait in this manuscript.

Future mechanistic work should use independent data or independently sourced proximal traits and begin from a new frozen hypothesis family. The current article remains focused on the multiscale geometry of community expansion, matrix fill and beta diversity.
