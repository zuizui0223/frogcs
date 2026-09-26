# Supporting Information — JAE RC6 v0.1

## Rainfall-associated expansion of frog active communities has repeatable species-specific spatial geometry

This Supporting Information preserves secondary, falsification and alternative-mechanism analyses that are important for transparency but are not part of the main inferential spine.

The main article focuses on:
1. multiscale expansion of the acoustically active community;
2. practical equivalence of active-matrix fill;
3. exact species × stop boundary decomposition;
4. temporally repeatable species activation geometry;
5. the distinction between conventional functional traits and empirically derived response traits.

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

A prespecified ATraiU hydroperiod test was nonestimable because all 23 covered species were coded as using both temporary and permanent breeding waters. The available coarse binary coding did not generate informative among-species contrast.

### S5.3 Breeding-season breadth

A prespecified breeding-season breadth test was unsupported (P = .823).

### S5.4 Baseline recurrence and seasonal concentration

Temporally held-out tests asked whether species that were more recurrent locally or more seasonally concentrated in the early period showed stronger later rainfall responses.

- baseline recurrence: P = .698;
- seasonal concentration: P = .990.

Neither supplied a supported mechanism.

### S5.5 Historical route dryness

A historical route-dryness interaction was unsupported (P = .855).

### S5.6 Compositional memory

A planned dry–dry background comparison for compositional memory was nonestimable because no candidate design passed the frozen dry–dry sample-size gate. No memory-above-background claim is authorized.

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

A separate held-out hypothesis predicted that greater baseline among-site heterogeneity would expose more latent diversity under recent-rain conditions. The frozen positive-moderation support rule failed. Opposite-direction secondary patterns were therefore not promoted to the main mechanism.

---

## S6. Response magnitude versus activation geometry

RC6 distinguishes two response coordinates:

1. **response magnitude** — how strongly and in which direction a species shifts between wetter and drier paired surveys;
2. **activation geometry** — conditional on wetter-run gains, whether those gains enter newly active versus already-active stops.

A frozen cross-period diagnostic used early activation geometry (2001–2007) to predict independently rebuilt late response magnitude (2008–2015).

Among 16 overlap species:
- Spearman rho = **0.415**;
- P = **.110**;
- frozen strong-coupling criterion |rho| >= 0.6 and P < .05: **not met**.

Precision-weighted regression was nevertheless positive:
- beta = **+0.354**;
- 95% CI = 0.204–0.503;
- P = 3.36e-6.

Spatial-edge activators had a weighted mean late response of +0.184 log-odds, whereas local deepeners had -0.050.

The two coordinates are therefore treated as **conceptually distinct but partially coupled**. RC6 does not claim statistical independence or orthogonality.

Authoritative files:
- `NAAMP_RESPONSE_GEOMETRY_VS_MAGNITUDE_CONTRACT_V0_1.json`
- `NAAMP_RESPONSE_GEOMETRY_VS_MAGNITUDE_SUMMARY_V0_1.json`
- `SPECIES_RESPONSE_TRAIT_FRAMEWORK_V0_1.md`

---

## S7. Additional interpretive boundaries

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

## S8. Endpoint policy

No additional endpoint search is authorized to rescue rejected mechanisms.

Future mechanistic work should prioritize:
- independently sourced proximal response traits, such as developmental timing, breeding microhabitat, call energetics or physiological water balance;
- phylogenetically explicit validation of activation geometry;
- independent monitoring systems that can estimate the same multiscale matrix quantities.

The current paper treats activation geometry as an empirically derived response trait because its temporal repeatability passed the frozen gate; it does not retrofit failed static traits into the explanation.
