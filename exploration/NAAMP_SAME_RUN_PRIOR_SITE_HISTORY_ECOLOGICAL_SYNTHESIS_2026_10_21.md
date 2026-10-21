# Frog acoustic partner choice versus historic SiteID use — 2026-10-21

## Main ecological inference

**A frog community's paired, partner-dependent acoustic configuration is partly predicted by each taxon's strictly earlier-year use of physical sites, but the partner-specific residual remains after that first-order control.**

This is a **post-hoc exploratory NAAMP observation**, not a demonstration of frog-to-frog attraction, avoidance or an irreducible three-species biological interaction. It is stronger than comparing separate species pairs in different regions because both partner relations are measured in the same route-run, at exactly the same ten sampled listening stops and with the same total observed frog species richness per stop.

The physical-site history can reflect true persistent habitat quality, spatially autocorrelated individuals, predator/fish context, long-term species occupancy, seasonality, detection, or past biotic interactions; it is **not a marked-individual memory or pure abiotic habitat variable**.

## Established prior facts and target

- Original matched NWI+PEM fixed-fixed null: 3,659 CI1–3 (any calling) and 1,766 CI2–3 (strong) survey matrices, each retaining the exact observed taxon-positive stop counts, stop frog richness and survey source.
- Same-route-run candidate contrast previously succeeded: `Lithobates clamitans` (central species, C) has higher adjusted site covariation with `Lithobates catesbeianus` (P) than with `Anaxyrus fowleri` or `Hyla versicolor` (N) **on the very same survey**.
- This extension tests whether **strictly previous year** species×physical-SiteID calling history explains the residual signed `C×P` versus `C×N` pair contrast `D`.

## Model sequence and empirical coverage

For a target year, use only earlier-year surveys from exactly the same State × RouteNumber × RunNumber (seasonal round). Require at least **2 strictly earlier route-season surveys and 8 of the ten physical SiteIDs represented in prior observations** before a route-run enters this analysis. No same-year or later frog count is used to construct historical preferences.

- Prior site probability is smoothed with four historical pseudo-visits around the previous seasonal route-species calling rate, then converted to **demeaned per-site log odds capped at ±3**.
- **N0:** frozen species-specific cross-fitted NWI wetland and PEM mapping coefficients;
- **N1:** N0 + site-history log odds, fixed coefficient 1.0, with no fit to current-year target frog outcomes;
- **Nhalf:** N0 + half historical log odds as a fixed sensitivity; **no outcome-based re-tuning**.
- Each route-run has the exact same observed frog row/column margins in all three weighted Metropolis–Hastings Curveball simulators, **199 draws per matrix, 40×n burn, 8×n thinning**. Synthetic fixed-margins/detailed-balance QA PASS.
- The original **3,659/1,766** observed C-scores were individually checked against the frozen NWI reference. History-complete NWI matrices retained **1,979 (CI1–3)** and **967 (CI2–3)**. Among the full 6,236 source-eligible NWI runs, 3,307 had enough prior-season SiteID support; 2,929 failed the predeclared history coverage gate without reference to current calling results.

The same sample is used for each N0/N1/Nhalf comparison within a particular trio. Historic information is not a simultaneous plant census; both underlying NWI mapping and original NWI first-order coefficients are temporally mismatched to one or more survey years.

Weighted-null pair-contrast variation was observable in **261/271 (96.3%)** of the *A. fowleri* primary triple matrices and **349/413 (84.5%)** of the *H. versicolor* primary triple matrices. Thus both main estimates pass the separately frozen ≥80%-variable null diagnostic. The strong-chorus *H. versicolor* sensitivity varies in only **72/95 (75.8%)** and is separately non-confirmatory; 199 MCMC draws do not turn hard incidence margins into independent site experiments.

## Main primary CI1–3 result: historical site use explains **some, not all**, paired contrast

| Central C = `L. clamitans`, P = `L. catesbeianus` | Against `A. fowleri` N | Against `H. versicolor` N |
|---|---:|---:|
| Same-run sample | **271 runs; 102 routes; 12 states** | **413 runs; 131 routes; 13 states** |
| N0 (NWI-only): `D` | +0.06009 | +0.04433 |
| Nhalf: `D` | +0.05456 | +0.03894 |
| N1 (NWI + historic use): `D` | **+0.04816** | **+0.03352** |
| N1 D 95% route CI | **+0.03662 to +0.05969** | **+0.02637 to +0.04067** |
| Historic site use removed from N0 D | **19.9%** | **24.4%** |
| Paired N0−N1 reduction 95% route CI | **+0.00842 to +0.01545** | **+0.00751 to +0.01411** |
| N1 signed full contrast BH q (2 fixed trios) | **2.82×10⁻¹⁶** | **8.30×10⁻²⁰** |

**Both individual signed partner residuals remain supported in the N1 null on the same complete case sample:**

- `A. fowleri` trio: `C×P` residual **+0.03304** (95% CI +0.02585 to +0.04024) and `C×N` residual **−0.01511** (−0.02191 to −0.00832).
- `H. versicolor` trio: `C×P` **+0.02628** (+0.02175 to +0.03080); `C×N` **−0.00725** (−0.01220 to −0.00230).

Thus retained D is not simply a difference in which residual has the larger magnitude; **the two signs are opposite** in both primary comparisons.

### Transfer checks

- A/ B **geographically disjoint route folds** have positive N1 D in both focal trios.
- Retrospective **2001–2009 and 2010–2015** strata both have route CIs excluding zero for N1 D:
  - `A. fowleri`: early **+0.05219** (CI +0.03545 to +0.06894; 68 runs), later **+0.04680** (+0.03241 to +0.06120; 203 runs).
  - `H. versicolor`: early **+0.03595** (+0.02323 to +0.04867; 164 runs), later **+0.03192** (+0.02334 to +0.04049; 249 runs).
- NWI species weights were trained on the opposite route fold over *both* time periods, so these retrospective year summaries are **not independent temporal validation**. The focal species were selected because previous NAAMP screens identified them; these are not independent discovery/confirmation samples.

### Independent evidence that site-history covariate itself matters

Using **all informative taxon×survey matrices** that pass the prior-site coverage gate, not just the selected focal trios, the strictly earlier species×SiteID history predicts held-out *same-survey fixed-k calling-site choices*:

- CI1–3: **+0.47328 nats per taxon×run**, route-bootstrap 95% **+0.42988 to +0.51443**, 9,153 informative taxon×runs across 344 routes;
- CI2–3: **+0.39790 nats**, CI **+0.35290 to +0.44138**, 3,900 taxon×runs across 273 routes.

A major part of site-specific frog calling is genuinely predictable from prior-years observations, which makes it especially important that the **partner difference still remains** after representing this predictor. These log-scores are conditional on a taxon already calling somewhere on that route-run (its observed row total), **not** predictions of route-wide occurrence or reproductive success.

## Strong-call CI2–3 secondary boundary

- `A. fowleri` trio: **34** history-complete runs/22 routes, **below frozen ≥60 runs/25-route gate**; do not claim survival or disappearance.
- `H. versicolor` trio: **95** runs/50 routes; D remains **+0.01732** (route CI +0.00101 to +0.03364), but the `L. clamitans × H. versicolor` *negative signed component* is **−0.00433** (CI −0.01351 to +0.00485) and does not individually exclude zero. Therefore the strong-call test **does not** meet the predeclared full opposite-sign pair criterion. The main affirmative result is **CI1–3**, not CI2–3.

## Hierarchical conclusion and next discriminating biological test

The validated layers are:
1. First-order mapped aquatic-plant context predicts some frog taxa's acoustic locations.
2. Strictly earlier physical-site history has powerful out-of-sample site-placement information.
3. **Second-order partner identity structure persists in the same route-night after both first-order components are represented.**
4. Global irreducible 3-taxon co-calling excess was not robust, and present results remain **two pairwise associations in a shared survey**, not causally irreducible third-order interactions.

The next independent evidence must resolve **site-night plant architecture, water depth/temperature, predator fish/odonate larvae and fine-scale acoustic timing**. If frog social signalling is the mechanism, co-located continuous recorders with controlled heterospecific playback are much more informative than further buffer searches on the same archive. If pond predation mediates co-presence, repeated fish/invertebrate and egg/tadpole surveys could distinguish it from simple hydrological sorting.

No frog-to-frog avoidance or attraction is proven; the outcome is **acoustic co-detection** at sequentially visited fixed survey stops, and absence of a calling record is not occupancy absence.

## Traceable execution

- Frozen prior hypothesis: `exploration/NAAMP_PARTNER_SWITCH_PRIOR_SITE_HISTORY_NULL_CONTRACT_V0_1.md`.
- Script: `exploration/run_naamp_same_run_prior_site_history_null_v0_1.py`.
- Numeric full proof: `exploration/NAAMP_SAME_RUN_PRIOR_SITE_HISTORY_RESULT_V0_1.json`.
- [Successful workflow 39603785733](https://github.com/zuizui0223/frogcs/actions/runs/39603785733) with original immutable source artifacts; result artifact ID **12346753041**.
- [Original same-run trio 39597933440](https://github.com/zuizui0223/frogcs/actions/runs/39597933440).
- All work resides in the independent exploration branch; **RC6 frozen research paper, SI, journal submission, author artefacts and main are unchanged**.
