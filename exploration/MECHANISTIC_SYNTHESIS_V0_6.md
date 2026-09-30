# Mechanistic synthesis: rainfall gates a latent local chorus template

**Status:** exploratory synthesis only. The JAE submission authority remains `015a675324800f2e5ac9ab0985b080fe88adc375`; none of the analyses summarized here are merged into the frozen submission.

## One-sentence result

Recent rain does not simply make an already-active frog chorus louder. In NAAMP, it preferentially re-expresses historically used **species × physical-site acoustic states**, often at overlapping or full-chorus intensity, and the resulting **species-specific activation depth across stops** is sufficient to account for the boundary-biased species × stop geometry.

## Decision tree

### 1. Is the rainfall signal only amplification of callers already active?

No.

Across 4,236 matched comparisons, the CallingIndex rainfall coefficient was **2.841**. The dry-zero → wet-positive activation component was **1.855 (65.3%)**, whereas intensity change among cells positive in both surveys was only **0.196 (6.9%)**.

The result therefore reflects crossing an acoustic-activity boundary, not primarily louder calling inside an already-active core.

### 2. Could this be marginal detectability of weak calls?

Not as a sufficient explanation.

The dry-zero → wet-CI2/3 component had a rainfall coefficient of **1.615 (95% CI 0.493–2.737)** and carried **87.1%** of the total activation coefficient. New CI3 full choruses alone increased with rainfall contrast (**beta = 0.441, 95% CI 0.114–0.768**).

In the intersection of same-observer pairs and pairs retaining the same ten physical SiteIDs, new CI3 full-chorus activation remained supported (**beta = 0.514, 0.101–0.927; 3,115 pairs**).

Adjustment for recorded hearing impairment, major-noise timeout and wind likewise retained the CI2/3 recruitment signal.

### 3. Is the signal created by observer turnover or stop relocation?

No.

- Same-observer pairs retain the expansion and boundary allocation.
- **4,172 / 4,236 pairs (98.5%)** preserve the same SiteID at all ten StopNumbers.
- In those physically stable pairs the observed boundary-crossing share is about **93.1%**, with both primary null families rejected at the Monte Carlo minimum.

### 4. Are rainfall-associated “new” cells truly novel local states?

Mostly not.

Using only years before the focal comparison, the strong CI2/3 rainfall coefficient was **1.750**, while the recurrent component was **1.794** and the component with no prior route-season record was approximately zero (**−0.044**).

For strong recruitment:

- recurrent share of the rainfall coefficient: **~102.5%**;
- previously recorded at the same SiteID: **~84.4%**;
- previously CI2/3 at the same SiteID: **~70.0%**.

CI3 recruitment is likewise overwhelmingly recurrent.

The parsimonious acoustic interpretation is therefore **reactivation**, not one-off appearance of previously unseen local states.

### 5. Is “same-site recurrence” merely generic good-frog habitat?

No.

Within the *same focal pair and same species*, a prior CI2/3 record at a physical SiteID predicts wet-survey CI2/3 at that SiteID (**beta ~0.151, 95% CI 0.129–0.173**). The effect remains with the same observer (**~0.159, 0.134–0.183**).

When own-species memory and generic other-species site history are compared, the own-species signal remains strong whereas generic-site history is much weaker. Exact SiteID history is also more informative than merely being geographically close to a previously strong site.

Among estimable taxa, **19 / 20 species** have positive own-site template effects (sign-test **P ~2.0e-5**).

Thus the template is species-specific as well as local.

### 6. Is local memory just a rain-independent site-fidelity pattern?

Not entirely.

In a symmetric wet-versus-dry comparison using strictly prior site history, the local-memory effect is larger on the wet side. For CI3, the wet-minus-dry memory coefficient difference is about **0.0213**, with a route-cluster bootstrap 95% interval **0.0024–0.0349**.

Rainfall therefore appears to **selectively expose** an existing local template rather than merely reveal static site fidelity equally in both directions.

### 7. How long does this template last?

The evidence is suggestive but fails the prefixed formal coverage gate.

Descriptively:

- memory from **1–3 years** earlier: beta **~0.173**;
- memory from **>=4 years** earlier: beta **~0.101**;
- continuous log-lag effect: beta **~−0.135**.

Reactivation after intervening sampled silence is also positively associated with prior same-site strong chorus. However, the old-memory and dormant-memory tests did not meet their minimum route-count gates, so a formal “multi-year persistence” headline is not authorized.

### 8. What creates the species × stop boundary geometry?

The key variable is **activation depth**, not exceptional stop placement.

Rainfall-associated route-new species do not become exceptional simply because more species are recruited or because more species reach a second stop. The excess appears at **third and later occupied stops**:

- route-new species coefficient: **0.185**;
- second-stop coefficient: **0.132**;
- third-plus-stop coefficient: **0.473**;
- fourth-plus-stop coefficient: **0.363**.

The third-plus component exceeds both the uniform and persistence-preserving null ranges.

However, after conditioning on species identity and each recruited species' realized wet-side occupied-stop count **k**, the remaining stop placement is not exceptional (omnibus **P ~0.179** and **0.212** under the two history/persistence placement comparators).

Therefore the matrix anomaly is generated mainly by **how spatially deep an activated species becomes**, not by a special geometric arrangement once that depth is fixed.

Historical route-scale strong-chorus breadth predicts later wet-side depth (**beta ~0.635, 95% CI 0.489–0.780**) and has a positive interaction with rainfall contrast (**beta ~0.165, 0.045–0.285**), although the smaller same-observer and exact-year versions did not pass their prefixed coverage gates.

## Mechanisms tested and not sufficient

The following explanations were tested and are not sufficient to account for the main pattern:

- a common uniform activation shift;
- a persistence-favouring common activation shift;
- transferable species-specific rainfall shifts alone;
- observer turnover;
- physical relocation of NAAMP stops;
- measured hearing impairment, interruption noise, wind or traffic;
- CI1-only weak-call detectability;
- simple facilitation toward stops where other species were already chorusing;
- an exclusively immediate 0–1-day rain response;
- NWI hydroperiod as the primary strong-chorus mediator;
- broad Palustrine versus Riverine/Lacustrine NWI class as the primary mediator;
- generic site quality instead of species-specific site history;
- local-memory weighting alone;
- a single cross-fit rain × local-memory gate;
- unusual geographic placement conditional on activated-species stop depth.

## Mechanistic ceiling

The strongest defensible interpretation is:

> **Rain acts as a temporal gate over a latent, species-specific local chorus template. Historically used species × site combinations are selectively re-expressed under wetter conditions, often at substantial chorus intensity. The matrix-level consequence depends chiefly on how deeply each activated species expands across the ten-stop route.**

What the data **do not** distinguish is whether the persistent template represents:

1. a continuously present local population whose males are intermittently acoustically active;
2. persistent species-specific microhabitat or breeding-site suitability that is reused across years;
3. some mixture of population persistence and habitat recurrence.

The proximal rain-associated gate also remains unresolved: hydration, actual water-level/inundation change, reproductive/endocrine readiness, other atmospheric cues, or correlated prey/weather conditions remain candidates.

## Generality

### Within NAAMP

The pooled signal is geographically robust: deleting any one of the 21 states retains a positive, CI-supported strong-activation coefficient. But state-specific effects are heterogeneous: only about **68%** of estimable state slopes are positive and about **32%** are individually CI-supported; the random-slope SD is large relative to the pooled slope.

Thus this is a robust regional pattern, **not the same effect everywhere**.

### Across taxa

The species-specific local-template effect is broadly positive among estimable NAAMP taxa, and route-new spatial-depth contributions are not dominated by one or two species.

### Outside NAAMP

Cross-continental universality is **not established**. Existing public external datasets either fail to provide an effort-complete multi-location species × site matrix or do not reproduce the prefixed NAAMP threshold-dominance rule.

Published Korean monitoring of *Dryophytes suweonensis* independently shows that sites known active in 2014 can become acoustically silent in later years and sometimes recover, which is qualitatively compatible with latent local acoustic states, but it is not yet a rainfall-gate replication.

## Stop rule

No further post-readback NAAMP mechanism model should be added unless it tests a qualitatively new falsifiable alternative. The next high-value evidence is:

1. an independent, effort-complete multi-site acoustic time series;
2. direct survey-night hydrology / water-level data; or
3. individual-level mark-recapture / telemetry linking acoustic recurrence to persistent local populations.

