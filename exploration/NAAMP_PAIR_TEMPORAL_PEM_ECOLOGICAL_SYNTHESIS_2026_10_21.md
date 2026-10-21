# Ecological persistence and aquatic-plant context of frog-pair calling patterns — 2026-10-21

## Main result

**Partner-specific frog acoustic spatial associations persist even when the positive and negative partners are recorded in the very same ten-stop survey run.** This strengthens the prior persistent pair-network finding against broad route/night/geographic sample-composition explanations. Two candidate PEM-specific pair moderators, however, failed stricter epoch/coverage robustness; there is still no evidence identifying a direct interspecific interaction or an irreducible three-taxon mechanism.

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

## C. Follow-up falsification of the two PEM-moderation candidates (2026-10-21)

Both candidate pairs were selected *after* observing their original full-period signed PEM-context contrasts. We froze the two names and tested the original 250m NWI PEM category without refitting any habitat coefficient or optimizing the location buffer. The original species×stop incidence margins, site richness and original C-scores were preserved in an independent 199-draw Curveball re-simulation.

**Outcome:** both full-period contrasts replicate their previous magnitudes and signs under a new deterministic MCMC seed, but **neither passes the stricter predeclared robustness criteria**. This is a failure of temporal information and balanced spatial coverage, not evidence for a zero biological effect.

| Pair | Full CI1–3 PEM minus unmapped residual | 2001–2009 | 2010–2015 | Balanced 3–7 sites each | Formal classification |
|---|---:|---|---|---|---|
| `Gastrophryne carolinensis` × `Hyla chrysoscelis` | **−0.10552**, 95% CI −0.16454 to −0.04650; 45 runs, 20 routes | 10 runs/9 routes; **underpowered** (direction −0.15316 descriptive only) | **−0.09191**, CI −0.15290 to −0.03092; 35 runs/18 routes | −0.11791, CI −0.20632 to −0.02951; 23 runs/10 routes | **fragile post-hoc candidate** |
| `Hyla gratiosa` × `Lithobates sphenocephalus` | **+0.10176**, CI +0.04477 to +0.15875; 34 runs, 15 routes | 7 runs/7 routes; **underpowered** (+0.06775 descriptive) | **+0.11058**, CI +0.03510 to +0.18606; 27 runs/13 routes | 21 runs/**7 routes**, **underpowered** (+0.09521 descriptive) | **fragile post-hoc candidate** |

Leaving one State out at a time retained the original contrast sign in **4/4** State omissions for the first pair, **3/3** for the second. However, the study data span only three or four States, and almost all early-period pairs fall below the pre-fixed minimum. Strong-call (CI2–3) secondary contrasts are **underpowered** for both candidates, notwithstanding a descriptive negative trend for the first pair.

**Updated inference:** `PEM × species-pair` is a *hypothesis-generating candidate layer*, **not** an independently supported ecological interaction level. Do not publish the originally discovered two BH-positive moderator tests as a demonstrated vegetation-driven species relationship after the robustness gate fails.

The partner-specific **pairwise acoustic network** remains a materially stronger finding: 14 year-stratified CI1–3 pair links and 2 strong-call links were retained under the separately frozen retrospective test. Those links are still not demonstrated direct biological interactions.

New reproducibility: `exploration/NAAMP_PEM_MODERATOR_EPOCH_ROBUSTNESS_CONTRACT_V0_1.md`; `exploration/NAAMP_PEM_PAIR_EPOCH_ROBUSTNESS_RESULT_V0_1.json`; [successful workflow 39594685501](https://github.com/zuizui0223/frogcs/actions/runs/39594685501) (artifact 12344076046).

---

## D. Falsification of route/night sample-composition confounding: same-survey partner contrast

**New finding, 2026-10-21.** Earlier associations of different pairs might have arisen because the positive and negative pairs occur in different regions, seasons, or species communities. To test that alternative, retain *only those individual route-runs in which all three taxa were recorded at least once*. Compare the SAME `L. clamitans` individual species label's residual joint calling with its positive versus negative partner over the **same ten site columns**. This is a comparison of two *pairwise* edges conditional on a shared three-species survey, **not a third-order interaction coefficient**.

Focal central species `Lithobates clamitans`, positive partner `Lithobates catesbeianus`; fixed negative partners `Anaxyrus fowleri` and `Hyla versicolor`, chosen from the previously BH-supported full-record network and fixed before this new common-run result readback.

Each frozen route-run matrix preserves all species positive-stop counts, stop taxon richness, and original observed C-score. Null means come from 199 new NWI+PEM-weighted Curveball draws under the *previously frozen opposite-route-fold species/site model*; no habitat coefficient is refit and no alternative taxon is added after observing results.

| Same-run comparison (CI1–3) | Surveys/routes/States | Residual `L. clamitans × L. catesbeianus` | Residual `L. clamitans × negative partner` | **Paired partner residual difference** (95% route CI) |
|---|---:|---:|---:|---:|
| Negative partner `A. fowleri` | **538 / 175 / 14** | **+0.03750** (CI +0.03160 to +0.04339) | **−0.01655** (CI −0.02182 to −0.01129) | **+0.05405** (CI **+0.04516 to +0.06295**), BH q=1.05×10⁻³² |
| Negative partner `H. versicolor` | **744 / 198 / 15** | **+0.03579** (CI +0.03135 to +0.04024) | **−0.00962** (CI −0.01346 to −0.00577) | **+0.04541** (CI **+0.03911 to +0.05170**), BH q=4.44×10⁻⁴⁵ |

Both comparisons show positive differences across geographic A/B route folds. On the same separately defined triples, the signed differences are positive with 95% CIs excluding zero in **both** 2001–2009 and 2010–2015 splits. Leave-one-State-out point estimates remain positive for **14/14** and **15/15** State omissions. However, the NWI first-order species coefficients were trained on both year periods, so none of these is a fully independent temporal test.

**Strong-chorus secondary (CI2–3):**
- `L. clamitans` + `L. catesbeianus` versus `A. fowleri`: **72 shared surveys / 48 routes**, same-run positive residual +0.03356 and negative residual −0.02083, paired difference **+0.05440** (CI +0.03561 to +0.07318); both component signed CIs exclude 0 and the contrast passes the frozen decision rule.
- Versus `H. versicolor`: **171 surveys / 81 routes**; paired difference +0.02357 (CI +0.01025 to +0.03688), but the `L. clamitans × H. versicolor` negative component = −0.00338 (CI −0.01074 to +0.00398), **not** independently supported for strong-only calls. Do not headline this secondary as a robust positive-and-negative edge reversal.

**Biological interpretation:** a partner-dependent **observational co-calling configuration** survives matching the actual survey route/night, recorded species context, total species/station activity margins and measured NWI plant/habitat effects. This makes a purely regional composition artifact less plausible. It **does not** prove that a calling green frog senses, attracts, facilitates or avoids either partner: finer stop-specific hydrology, predator/larval biotic contexts, phenological signal, species call detectability and sequential listening times remain possible common causes. The separate 3-taxon centered-moment null result still stands. This is **two pairwise effects observed together**, not proof of an irreducible third-order biological interaction.

Files: `exploration/NAAMP_SAME_RUN_PARTNER_SWITCH_CONTRACT_2026_10_21.md` and `exploration/NAAMP_SAME_RUN_PARTNER_SWITCH_RESULT_V0_1.json`. Executed: [GitHub Actions 39597933440](https://github.com/zuizui0223/frogcs/actions/runs/39597933440), **SUCCESS**, artifact 12345635297.

---

## E. Does strict prior species×SiteID use explain same-night partner contrast?

**Completed new first-order falsification (2026-10-21).** Read previously frozen opposite-route NWI+PEM weights; for every tested species compute its past same-physical-site calling log odds using **only earlier survey years in the same route/season**. Require ≥2 prior seasonal survey runs and ≥8 previously visited physical SiteIDs before including a route-run. No current target year responses enter history, and no history effect strength is tuned after seeing the result.

CI1–3 exact **same complete samples** with 199 weighted fixed-row-and-column Curveball draws under each model:

| Same-run central frog `L. clamitans` positive partner `L. catesbeianus` versus | Eligible runs/routes | NWI-only contrast D | NWI + prior SiteID D (route 95% CI) | Original residual removed |
|---|---:|---:|---|---:|
| Negative `A. fowleri` | 271 / 102 | +0.06009 | **+0.04816** (+0.03662 to +0.05969) | **19.9%** |
| Negative `H. versicolor` | 413 / 131 | +0.04433 | **+0.03352** (+0.02637 to +0.04067) | **24.4%** |

In **both** target comparisons, the residual **positive** central-to-bullfrog and **negative** central-to-other-frog pair effects remain individually distinguishable from zero, and the D contrast remains positive in two geographic folds and both retrospective year strata. The fixed 0.5-history-strength secondary did not close the contrasts either. Historical sites substantially predict frog location itself (+0.473 nats/taxon×run for CI1–3, route bootstrap 95% +0.430 to +0.514), so their partial explanatory power is biologically and statistically meaningful.

**Strong CI2–3 caveat:** the `A. fowleri` trio had only 34 eligible surveys and failed the coverage gate. The `H. versicolor` trio had 95 surveys and positive D (+0.01732, CI +0.00101 to +0.03364), but the negative central-to-Hyla component had a CI that included zero. Hence the full opposite-signed effect is supported for **any calling**, not as an independently robust CI2–3 generalization.

Result and QA: `exploration/NAAMP_SAME_RUN_PRIOR_SITE_HISTORY_ECOLOGICAL_SYNTHESIS_2026_10_21.md` and `exploration/NAAMP_SAME_RUN_PRIOR_SITE_HISTORY_RESULT_V0_1.json`, [GitHub Actions 39603785733](https://github.com/zuizui0223/frogcs/actions/runs/39603785733) (SUCCESS).

**Updated hierarchy:** static mapped plant preferences and past species×SiteID use jointly explain a portion of the acoustic placement, but cannot recover all residual partner-specific structure in the present same-survey CI1–3 sample. This is a **partial failure of the tested first-order generator**, not proof of current interspecific competition, biological facilitation or an irreducible 3-way interaction.

---

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
