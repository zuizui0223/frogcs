# v7.1 — FIRST ACTUAL public frog acoustic assemblage recurrence result (2019–2023)

**2026-10-13 JST. Ecological description from ORIGINAL published positive-detection rows, not synthetic data and not causal hydrology.** Independent frogcs draft PR #135; Journal of Animal Ecology RC6/main unchanged. Pre-outcome analysis and units [frozen before inspecting `scientific.name` similarity values](V7_1_PUBLIC_PAM_SEASONAL_RECURRENCE_FROZEN_ANALYSIS.md).

## Original open-data provenance

- [Hoefer et al. 2026 Zenodo v2.0, open published data and code](https://zenodo.org/records/21634473); original [GitHub v.2.0 dataset and data dictionary](https://github.com/cheloniax/repo_PAM_frogs/tree/v.2.0/data).
- Exact input `frog_data_season.csv` pinned to original Git blob `e5a419574be5e3f9922989f9aa6001fbb7f09d01`, file SHA-256 `07a825f7b3269b7d15a353c11a099bceecafef4a5d9a5ffb8a80126bc18d4bc5`.
- [Prior source-only actual schema/season/year quality check, Actions 38350097992 — SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38350097992). This demonstrated **13,577 detection rows**, 6 public study sites, 4 plots per site, **4 author seasons**, and data across **2019–2023**. All rows in this file have `assessment.method=PAM.all`, not the observer- or period-matched alternative. The source dictionary uses `Sampling.trip` but actual CSV uses `sampling.trip`; this analysis relies on the original `date` and `season`, not undocumented interpretation of trip codes.
- [**Actual predeclared empirical analysis Actions 38350418671 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38350418671). All original source rows are downloaded/used in memory by `scripts/analyze_public_hoefer_seasonal_recurrence_v71.py`, only an [aggregate reproducible JSON result](receipts/HOEFER_2026_REAL_SEASONAL_RECURRENCE_V71.json) is retained; no site/taxon labels, coordinates or raw rows were published in this result.

**Observed input grain:** the published rows are **positive frog detections**, not 13,577 independent surveys. After deduplicating the published species names within `site × plot × season × calendar-year`, there are **216 nonempty detected-assemblage cells**, spanning **24 site–plot keys**, **72 site–plot×year keys**, **95 site–plot×season keys**, and **34 distinct detected species labels**. Cell detected richness ranges **1–12** species (median **4**); the number of *dates with any positive frog detection* ranges **1–91** per cell (median **15**). These positive dates are NOT a valid all-recording effort denominator. No unlisted/empty cell is given a pseudo-negative.

## Frozen Jaccard similarities — actual source detections

Site-level averages are **equal-weight across six original sites**, not pseudo-independent counts of species records/pairs. Each binary Jaccard index compares *the detected species lists* `|intersection| / |union|` for the same two positive cells.

| Comparison, all eligible positive cells | Pairs | Mean site-averaged Jaccard |
| --- | ---: | ---: |
| **A:** same site, same plot, same author season, **adjacent calendar years** | **118** | **0.473504** |
| **T:** same site, same plot and calendar year, **different seasons** | **246** | **0.442195** |
| **P:** same site, same season and year, **different plots** | **262** | **0.460211** |

**Primary frozen contrast: A − T = +0.031310** in similarity units. This is a modest, positive descriptive difference, but only **3/6 sites** have positive site-level contrasts. Descriptive 5000-draw **site-resampling** 95% interval: **[−0.008629, +0.074230]**, **crosses zero**; site differences range **[−0.022435, +0.111987]**. It is therefore **NOT robust evidence that within-plot seasonal assemblage recurrence dominates within-year seasonal turnover generally**.

**Secondary:** `P − T = +0.018016`, 3/6 sites positive, interval **[−0.034404, +0.077003]**. This is likewise not consistent site-level evidence of spatial assemblage structure dominating seasonal turnover.

These interval summaries have only six site clusters, not a random experimental study design; do not treat their numerical 95% coverage as a calibrated population-level probability or publish confirmatory P values.

## Predeclared positive-date-support sensitivity, not genuine effort correction

Require both compared cells to have **≥5 distinct calendar dates with at least one positive detection**. As fixed before seeing the result, this filters low-positive-activity cells without proving complete audio recording opportunity coverage.

| Comparison (same definitions) | Eligible pairs | Mean site-averaged Jaccard |
| --- | ---: | ---: |
| A, adjacent-year same-season | 87 | 0.507866 |
| T, within-year different-season | 184 | 0.472239 |
| P, same-year different-plot | 198 | 0.483948 |

Primary **A − T = +0.035627**, positive in 5/6 sites, descriptive site-bootstrap interval **[+0.010964, +0.068929]**. **Do NOT promote this selected sensitivity's positive interval into an effort-adjusted discovery.** Positive detection dates are affected by source recording amount, vocal activity and detection probability; conditioning on them can create selection bias. The unrestricted primary result has only 3/6 positive sites and includes zero in its interval.

Secondary **P − T = +0.011709**, positive in 2/6 sites, interval **[−0.030198, +0.057868]**; not robust.

## Supported ecological statement versus interpretation boundary

**Supported:** Across a real five-year public Australian PAM dataset, detected frog assemblage lists have moderate similarity (site-average Jaccard roughly **0.44–0.47**) across interseasonal, annual same-season, and within-site between-plot contrasts. The predeclared annual same-season recurrence advantage is **small and heterogeneous among the six sites**. Source date support strongly varies across source cells, and conditional screening changes site-level sign consistency.

**NOT supported:** No test here estimates occupancy, actual wetland species absence, dispersal, observed frog memory, breeding success, frog calling intensity, solar/clock effects, wetland inundation timing, or site-specific hydrological trajectories. FrogID/NAAMP and the CEWH Murrumbidgee source are separate sampling systems; none may be called a replication of this survey. No matching source wetland depth or valid all-interval recording opportunity ledger is available in this Zenodo table.

**Key reason to stop at description:** detection-only `PAM.all` rows lack explicitly recorded complete negative acoustic opportunities per season/plot and observation quality/calibration. Comparisons may reflect variation in recording availability, conditions and species detectability, even within source site. Publication-level `season` and `date` are used verbatim; year/season are not independent assigned treatments. Cross-year pair counts and within-year seasonal pair counts involve correlated, overlapping cells; source **site** is the comparison cluster, not each pair or row.

## Decision for frogcs

The public-only path has produced a **genuine empirical, method-constrained ecological result** without requesting external data or retuning the JAE paper, but it does **not** identify Q-A (matched-depth rise/fall) or Q-B (past frog calling forecast *beyond local water history*). Their W/O/H/D/T/R source-identity/effort/hydrology gates remain **not cleared**. It would be scientifically incorrect to promote this mild recurrent seasonal similarity into strong spatial relay, memory, adaptation or water-causal mechanism.

Keep the [CEWH metadata-only request](V6_0_CEWH_ACOUSTIC_HYDROLOGY_SOURCE_INVENTORY_REQUEST_UNSENT.md) **UNSENT**. Future public-only work should first look for independently exposed **recording effort manifests or measured wetland water series**, not generate more synthetic worlds, arbitrary taxon-specific tests or repeated inaccessible API attempts.

**Permanent receipt:** [v7.1 actual published input and aggregate similarities](receipts/HOEFER_2026_REAL_SEASONAL_RECURRENCE_V71.json). The source study must be cited as Hoefer et al. 2026 and the source license checked before reproducing raw rows/recordings; no raw data are redistributed in frogcs.
