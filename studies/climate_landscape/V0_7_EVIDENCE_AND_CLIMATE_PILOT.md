# Independent NAAMP frog climate × landscape project — v0.7

**Date: 2026-10-08. Scientific status: response-blind climate pilot created; ecological outcome stage NOT executed. No change to the RC6 JAE manuscript.**

## 1. Previously inaccessible external empirical evidence now checked

The pinned 2001–2015 USGS NAAMP metadata-only cohort was successfully downloaded and checksum-verified in GitHub Actions (e.g. run [37728431320](https://github.com/zuizui0223/frogcs/actions/runs/37728431320)). The log reports 7,848 standardized ten-stop surveys, 78,480 surveyed stop opportunities, 8,223 distinct route×SiteID keys, and 29,986 consecutive-year same-season **stop comparison opportunities**, not independent route-level replicates. No Count.csv was read. The earlier upload step in that run silently failed because `${RUNNER_TEMP}` remained a literal string in an Actions `with.path:` parameter; a subsequent revision switched to `${{ runner.temp }}`, with `if-no-files-found: error`. Until a corrected run/artifact completes, the detailed receipt is available from the successful job log but not as a durable artifact.

Of 78,480 surveyed site events, 75,849 match a coordinate source record, 74,861 pass geometry-only QC and zero are independently verified against historical physical-site documentation. Thus the new *30 m site-level* satellite overlay and acoustic spatial-allocation effect remain blocked. The usable climate pilot below does not pretend that route centroids verify historical stations.

## 2. New empirical Landsat scanline/pixel-QA risk

The frozen E3 real Landsat STAC metadata covers 3,811 survey runs across 395 routes, but the underlying E3 cohort had previously been selected by a frog-informed workflow. It is an engineering feasibility population, not the source of a new unbiased frog–climate estimate. We retrieved and read the three E3 18-run Landsat pixel-QA pilot artifacts (first candidate per run only) and dated all strict metadata longitudinal scene pairs relative to the USGS 2003-05-31 Landsat 7 SLC failure date.

- Strict >=5-year comparison: 123 candidate routes. **76** use LE07 on both sides *after* scanline corrector failure; **37** compare LE07 *before vs after* SLC failure; only **10** use LT05 instead. All 113 LE07 candidate pairs include at least one post-failure scene. No LE07 long-gap pair is entirely pre-failure.
- Strict early (2001–05) vs late (2011–15): 58 candidate routes; 21 both post-failure LE07, 32 LE07 mixed, 5 LT05.
- Strict adjacent-year: 1,421 candidate pairs / 316 routes; 820 pair scenes have at least one SLC-off LE07 image (789 both post, 31 mixed), 22 both LE07 pre-failure, 429 LT05 and 150 LC08.
- First-candidate quality pilot: 18 hash-selected runs; 12 had successful cloud/reflectance QA evaluation, of which **3** passed >=70% valid pixels at all 10 stops; 9 failed, 6 additional runs had source HTTP errors. These 18 are too few and preselected to estimate whole-sample QA yield.

The complete machine-readable [receipt](receipts/LANDSAT_SLC_OFF_PILOT_QA_AUDIT_V0_1.json) was calculated directly from source metadata and actual QA pilot artifacts; **no NDMI changes, annual NLCD pixels, frog calling responses or climate effects** were calculated. The SLC result reinforces that a two-scene Landsat NDMI difference is not a reliable primary measurement of decadal terrestrial transitions in this sample.

## 3. Actual Daymet climate screening — newly executable route-level lane

Created `scripts/daymet_route_climate_pilot.py` and `.github/workflows/climate_landscape_daymet_route_pilot.yml` to fetch real Daymet daily `prcp,tmin,tmax` for a **predeclared, outcome-blind and geographically spread route-scale screening sample**. The script:

1. Reads only SHA256-pinned USGS `Runs.csv`, `Stops.csv`, and the coordinate table, and retains the exact standardized 2001–2015 non-skipped ten-stop opportunities; no frog taxon / CallingIndex or land use is read.
2. Requires at least eight geometry-pass coordinate records, >=5 observed survey years and >=8-year repeat span, without calling geometry-pass "field verified". Selects **at most one route per state**, then 12 states, with a stable SHA256 seed unrelated to frog/temperature outcomes.
3. Uses a *median of the geometry-pass station coordinates* solely to query approximately 1-km Daymet route-scale gridded climate. This is **not** approved for a 30-m landscape overlay or station-level microclimate claims.
4. Requests the complete daily period **1981–2015**, checks all 365 entries per year (including leap-year Feb 29, excluding leap-year Dec 31), and fails on missing, duplicate, negative precipitation or physically invalid values. Preserves raw response hashes.
5. Computes the fixed 1981–2000 reference, Theil–Sen 1981–2015 descriptive temperature/precipitation slopes **not available to earlier survey outcomes as predictors**, and separate past-only five-complete-year climate states for each 2001–2015 focal year. If downloading fails midway, emits a status-marked partial receipt; partial series are not acceptable for inference.
6. Uploads only sampled route geometry metadata and climate screening summaries (not the full original USGS source tables or frog call responses).

**Synthetic tests passed:** source- and outcome-blind sample selection, Daymet leap-calendar parsing, hard-fail missing days, invalid date and rainfall, historical-baseline and pre-survey leakage control. This source-only climate route pilot can establish *whether long-term warming/precipitation signals actually occur at the monitored routes*, but it cannot by itself tell whether frogs adjusted to them.

## 4. Biology: inference still blocked, and how to adjudicate

The biological question remains whether long-term warmth/drought and terrestrial conversion cause strong-calling activity to diminish or **be redistributed among physically verified breeding-season acoustic sites**, with or without lag. Total taxon×route event strong chorus intensity must be modelled separately from within-route fixed-K location allocation; route-constant climate main effects are mathematically unidentifiable in conditional fixed-K site-allocation likelihood. Temporal lag/legacy requires pre-conversion and multiple post-conversion observations of the **same physical station**. Short-term wetness already showed limited predictive benefit for CI>=2 in previous DSWEmod work, but the broader surface-water mechanism was negative. Neither result demonstrates a climate-change effect or a reproductive-success effect.

**Near-term evidence gate:** source-checked Daymet route-series receipts; then externally verified stationary SiteIDs and official Annual NLCD Collection 1.2 matched-pixel changes with valid-pixel class/confidence checks; only then freeze and execute taxon calling comparisons with held-out temporal and spatial blocks. If verification or paired-pixel coverage is too small, report infeasibility, not a relaxed outcome-selected sample.
