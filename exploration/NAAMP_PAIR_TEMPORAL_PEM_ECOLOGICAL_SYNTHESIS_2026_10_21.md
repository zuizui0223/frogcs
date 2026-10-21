# Ecological persistence and aquatic-plant context of frog-pair calling patterns — 2026-10-21

## Main result

**The residual acoustic relationship between selected *pairs* of frog taxa is more persistent across survey years than a simple one-time composition anomaly.** Yet mapped emergent wetland vegetation modifies only a small fraction of the candidate pair associations, and the three widely supported pairs of interest do **not** show a BH-supported mapped-PEM moderation signal.

This is a post-hoc observational extension of the already explored USGS NAAMP 2001–2015 survey archive; it does **not** identify competition, facilitation or trophic interaction and is **not** independent temporal validation because the historical NWI habitat coefficients were trained across both year blocks. Submission RC6 is unchanged.

## Prior context (locked before the present study)

- Independent prior model result: 5 taxon units showed strong calling-site associations with mapped NWI PEM emergent wetland area, but NWI+PEM habitat filters left a large fixed-margin checkerboard residual.
- A previously frozen same-matrix scan found **43 of 127** eligible primary species-pair signed deviations after BH plus fold consistency, and **14 of 57** for strong calling. No robust 3-taxon global co-calling motif excess. Source: `exploration/NAAMP_PLANT_CONDITIONED_FROG_PAIR_NETWORK_RESULT_V0_1.json`, [run 39528330890](https://github.com/zuizui0223/frogcs/actions/runs/39528330890).
- Pair effect units are the difference in **fraction of stops where both taxa were acoustically detected**, between observed and the species/stop-incidence-preserving NWI weighted-null expectation. Positive means more same-stop joint detection; negative means less. This does not measure encounter, physical co-presence of individuals or simultaneous signaling.

## A. Retrospective temporal stability of signed pair edges

Fixed outcome: CI1–3 first, CI2–3 secondary, NWI 250m mapped wetland+PEM. Exactly the previous **3,659 route-runs / 478 routes**, and **1,766 / 398** for CI2–3. Weighted Curveball keeps **all** taxon detected-stop totals and stop-level taxon richness exactly unchanged, 199 draws per matrix, route-crossfit species PEM preference coefficients fixed.

Predeclared early period **2001–2009**, late **2010–2015**:

| Target | CI1–3 | CI2–3 |
|---|---:|---:|
| Early-survey study runs | 1,573 | 643 |
| Late-survey study runs | 2,086 | 1,123 |
| Pairs meeting early coverage/mixing gates | 85 | 35 |
| Early BH-supported pair associations | **19** | **2** |
| Early-discovered pairs also eligible in late period | 18 | 2 |
| Late BH-supported, sign-stable pairs (both geographic folds) | **14** | **2** |

Of 14 stable CI1–3 pairs, 4 are positive co-detection and 10 are negative segregation. Among all 14, **Lithobates clamitans** and **L. catesbeianus** each participate in several links, consistent with the prior whole-period degree pattern. Their status as *associational network connectors* is not ecological keystoneness.

### Three fixed motivating contrasts

| Pair | Early effect | Late effect | Late BH q | Strong-call result |
|---|---:|---:|---:|---|
| `Lithobates catesbeianus` × `L. clamitans` | **+0.03130** | **+0.03449** | 9.32×10⁻⁴⁶ | Stable **positive** (early +0.02419; late +0.02145, q=2.12×10⁻⁷) |
| `Anaxyrus fowleri` × `L. clamitans` | **−0.01501** | **−0.01393** | 1.62×10⁻⁶ | Stable **negative** (early −0.01810; late −0.01526, q=5.94×10⁻⁵) |
| `Hyla versicolor` × `L. clamitans` | **−0.00688** | **−0.00811** | 0.00115 | **Not** significantly stable for strong CI2–3 |

The different positive/negative signs of pairs sharing `L. clamitans` suggest **partner-specific spatial organization** under the fixed-null model. Although `H. versicolor` and `L. clamitans` both previously had positive associations with mapped PEM for strong calls, their any-call detections are more segregated than expected, in **both year strata**. Same plant association clearly does not entail same spatial use.

**Important inference limit:** the previous species-specific NWI environmental coefficients were fitted using all years (but cross-fitted across routes); therefore year-block consistency of *pair residuals* is informative retrospective stability, **not** fully independent early-trained → late-tested mechanism confirmation.

## B. Does mapped emergent vegetation modify pair residuals?

For only the route-runs with at least 2 mapped-PEM-overlap and 2 non-overlap stations, compute pair-specific observed minus weighted-null **same-stop joint detection rates within each group**; test *PEM residual minus non-PEM residual* across independently clustered routes. NWI no mapped polygon does **not** imply actual absence of plants in a wetland. Importantly this difference measures *conditional association* over first-order plant affinity already accounted for in the weighted null.

- CI1–3: **2,142** mixed-PEM survey runs across **274** routes. **121** eligible pair tests, 2 passed BH q<0.05 and geographic-fold sign checks.
- CI2–3: **1,029** mixed-PEM survey runs across **231** routes; **57** eligible pair tests, **zero** supported under the same rule.

Two candidate CI1–3 moderation effects:

| Taxon pair | PEM-overlap residual | Nonoverlap residual | PEM − nonPEM | 95% route CI | BH q | Study strength |
|---|---:|---:|---:|---|---:|---|
| `Gastrophryne carolinensis` × `Hyla chrysoscelis` | −0.06099 | +0.05179 | **−0.11278** | −0.17145 to −0.05411 | 0.01995 | 45 mixed-PEM joint-positive runs, **20 routes** |
| `Hyla gratiosa` × `Lithobates sphenocephalus` | +0.07846 | −0.02901 | **+0.10747** | +0.04755 to +0.16738 | 0.02655 | 34 runs, **15 routes** |

These observations are especially interesting because **none of the four taxa belongs to the five primary BH-positive *individual* PEM-associated taxon units**. A pair's acoustic coupling can be vegetation-context dependent even if neither individual's continuous-cover slope was statistically supported by the earlier screen. That is a **new hypothesis-generating interaction layer**, not identified biotic facilitation/competition or proof that plants cause the pattern. Each moderation candidate is based on a relatively small number of mixed-habitat routes; **neither** gained confirmation in the strong CI2–3 endpoint (one did not meet its secondary coverage gate).

The three fixed temporally stable motivating pairs did not have a supported measured-PEM-context change:

- `H. versicolor` × `L. clamitans`: PEM minus nonPEM residual **−0.00931** (95% CI −0.02523 to +0.00660), BH q **0.745**; relationship remains negative across years.
- `L. catesbeianus` × `L. clamitans`: **+0.00554** (−0.01122 to +0.02230), BH q **0.863**.
- `A. fowleri` × `L. clamitans`: **−0.00705** (−0.02671 to +0.01261), BH q **0.845**.

That distinction is ecologically useful: stable **pair identity** signals can be present without a detectable interaction with the mapped emergent wetland category. A PEM-dependent two-species contrast could reflect **unmeasured abiotic gradients** or third-party fish/insect abundance; do not equate a statistical moderator with a mechanistic mediator.

## Hierarchical interpretation

Observed order of support in the current NAAMP + mapped vegetation study:

1. **Taxon × plant-habitat association**: some individual taxa's strong acoustic recording locations show positive NWI PEM associations.
2. **Persistent taxon-pair acoustic organization**: specific positive/negative co-detection residuals remain after preserving row/column margins, NWI filter, multiple-testing adjustment and retrospective year stratification.
3. **Plant-context modification of selected pair links**: 2/121 CI1–3 pairs have candidate moderation but limited 15–20 route coverage; 0/57 CI2–3 pairs. Thus a broad vegetation-driven network reorganization is *not* supported.
4. **Irreducible three-taxon biological interactions**: neither inferred nor required by global triplet tests; no full experimental measurement of the third party (fish, insects, tadpoles, social calls).

**Do not conflate step 3 with a verified third-species-mediated interaction.** These are acoustically detected links across spatial sampling stops, not observed predator/prey or social contacts.

## Next best biological discriminator

Rather than additional NWI radius tuning, collect replicated same-night data on plant species and actual vegetation structure, water depth, fish and odonate predator presence, chorus playback responses, and concurrently monitored species' sub-minute vocalization histories. Focus observation on positive connectors such as bullfrog–green frog and negative edges such as `H. versicolor`–green frog; they are explicit hypotheses for an environmental vs social effect test.

## Reproducibility

- Full source-only NWI crosswalk: [workflow 39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- Frozen NWI-weighted fixed-row/column null: [workflow 39516056663](https://github.com/zuizui0223/frogcs/actions/runs/39516056663).
- Prior whole-period BH pair graph: [workflow 39528330890](https://github.com/zuizui0223/frogcs/actions/runs/39528330890).
- New temporal + PEM moderation workflow: [workflow 39592028334](https://github.com/zuizui0223/frogcs/actions/runs/39592028334), **SUCCESS**, source artifact ID **12341634243** (`result.json`, run-year NWI QA CSV for each endpoint).
- Extracted full output highlights: `exploration/NAAMP_PAIR_TIME_PEM_SUMMARY_V0_1.json`.
- Exact PEM-positive/negative residual breakdown from an immutable saved source artifact: `exploration/NAAMP_PAIR_PEM_CONTEXT_DETAIL_V0_1.json`; [audit workflow 39592995660](https://github.com/zuizui0223/frogcs/actions/runs/39592995660) **SUCCESS**.
- All output exploratory; underlying NWI plants are time-mismatched mapping classes, and first-order habitat model coefficients include both year periods. No changes to the RC6 manuscript, SI, submission, protected release, or result claim ledger.
