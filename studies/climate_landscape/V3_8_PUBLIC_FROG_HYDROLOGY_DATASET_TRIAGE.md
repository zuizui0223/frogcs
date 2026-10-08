# v3.8 — Public multi-wetland frog data source audit: what can actually be tested?

**Date:** 2026-10-08. **Status:** source-backed data-discovery triage, not a new frog biological result. The frozen JAE RC6 manuscript and numeric outputs remain unchanged. No public frog-response values or original Iowa stop-event wet/dry have been downloaded or analysed in this branch.

## 1. Answer to the immediate question

A real open-access **frog calling × precipitation × hydrology** time series EXISTS. It is suitable for a limited within-system observational feasibility analysis without awaiting Iowa native wet/dry records, but it is **not** an untouched multi-route/10-stop reproduction of the frogcs spatial-configuration result.

### Candidate A — Nebraska 2015–2017 multimodal time series (highest near-term value)

Official published data: [Brinley Buckley et al. 2020 Mendeley Data v1](https://data.mendeley.com/datasets/p6nbn2hyz9), **DOI 10.17632/p6nbn2hyz9.1**, CC BY 4.0; [Data in Brief 2020](https://doi.org/10.1016/j.dib.2020.106581); [Ecological Indicators 2021](https://doi.org/10.1016/j.ecolind.2020.107171).

Published sampling: two physically distinct environments in the Central Platte River Valley, **a wet meadow and a forested slough**; `Pseudacris maculata`; spring 2015, 2016, 2017; acoustic recorders captured one minute out of each 20 minutes and time-lapse habitat imagery was available. The source article reports 472 total observed site recording days (227 wet meadow, 245 slough), with some days excluded/missing. Public daily tabular data describe calling `count` (continuous 0–1 activity index), `missing`, `PRCP` (daily precipitation), `PRCP1`, `PRCP7`, temperature, wind, vegetation and `HYDRO`.

**Nonnegotiable measurement warning:** the dataset's `HYDRO` values are **wet-meadow fractional image inundation at one site**, but **Platte River streamflow at the other** (both scaled 0–1). They are not two calibrated measurements of the same variable. Never fit a pooled “one-unit hydrology effect” across sites without acknowledging this construct mismatch; a pooled effect could reflect measurement type/habitat rather than a universal water-state response. Assess within-site relationships separately first, if individual original values can be source-verified.

**Potential but not yet executed questions:** do rainfall and directly observed meadow inundation provide separately predictive information for daily calling within a wet meadow, after season/temperature and historical time block? Does a corresponding streamflow association exist in the slough, reported as a distinct environmental construct? Is any candidate interaction sign stable across within-site years, with blocked temporally held-out scoring? How much of the rain association remains after local water state is added? **These are associative questions, not randomized rainfall mechanisms or causal mediation.**

**Hard stops:** only two wetlands, one taxon, daily aggregated calling, no repeat independent sites representing a full 10-stop route, no measured rain *sound* or randomized playback, and only three breeding seasons. Therefore cannot identify frogcs's within-taxon **deep k≥4 placement**, a route-wide shared taxon-night latent state, a landscape relay, true individual movement, or prior strong-chorus selection across many separate wetlands. A two-wetland daily comparison is a **source-to-mechanism exploratory pilot**, not spatial replication.

**Data status:** publication and DOI/field glossary verified from source, but the underlying CSV rows have **not** been read. The actual public file list is separately queried by `scripts/preflight_public_mendeley_metadata_v38.py` via Mendeley’s [documented public-files metadata endpoint](https://data.mendeley.com/api/docs/) at `api.data.mendeley.com/datasets/publics/p6nbn2hyz9/files?version=1`. This tool intentionally checks only filenames, bytes and official metadata, never downloads response values. A successful CI execution only proves *metadata access*, not scientific data completeness.

### Candidate B — Québec, 180 ponds, eDNA + acoustic detections (availability control, not rain mechanism)

[Original 2017–2018 Dryad dataset](https://doi.org/10.5061/dryad.8cz8w9gr1) for *Pseudacris maculata* surveys at **180 ponds** in southeastern Québec. Files publicly listed include `detectData-eDNA-Acoustic.csv`, `detectData180eDNA.csv`, `siteCovariateData180eDNA.csv` and `README.txt`. This might assist the critical **calling silence ≠ animal absence** distinction by triangulating eDNA and acoustic detection. However, public dataset-page metadata do **not** establish date-matched rain/water-level or repeated same-night acoustic chorus intensity suitable for the frogcs spatial interaction.

**Gate:** inspect README/header/protocol before even treating this as an acoustic state series. If eDNA/call data are cross-sectional and not time-matched, use only for occurrence/detection context, not a rain-triggered chorus allocation model.

### Candidate C — Great Lakes Coastal Wetland Monitoring frog data (wetlands & repeated surveys, temporal cue limited)

[Tozer et al. Dryad data](https://doi.org/10.5061/dryad.hmgqnk9v8) / [programme protocols](https://greatlakeswetlands.org/Sampling-protocols). Wetland surveys used 1–6 fixed point counts per sampled wetland, points >500m apart, ~3 visits spaced at least 15 days apart in the breeding season. Crucially, the protocol avoided **persistent or heavy precipitation**. Consequently those survey records are useful for site-level occurrence/long-term monitoring and possibly spatial association, but not a direct test of immediate heavy-rain sound-triggered calling. Multiple stops within the **same wetland** should not be represented as independent ponds; frog types were grouped in some call identifications.

### Candidate D — 488 wetland hydroperiod/occupancy sites (physical opportunity, no sound endpoint)

[Dare et al. 2026 Dryad](https://doi.org/10.5061/dryad.9cnp5hr0r) includes hydroperiod model output and breeding occupancy for **488 sites**, with observational wetland depth/soil-moisture inputs. It tests broad ecological water-availability/occupancy processes but does **not**, by the dataset description, supply a synchronized frog calling intensity series. This is independent evidence for the WATER-LOCAL ecological possibility, not a replication of a rain-vocalization interaction.

### Candidate E — Australian frog PAM 2026 (acoustic detection QA, hydrology unconfirmed)

[Hoefer et al. 2026 Zenodo v2](https://zenodo.org/records/21634473) includes plot/site frog detections, a species call-validation data file and seasonal PAM, with **115 example call validations for 50 species** described in the repository. Excellent possible background for detection limits and site-varying acoustic sampling, but the catalog description alone does not establish matched per-site current water level or rain-sound records. Do not infer a hydrology panel from an acoustic validation dataset.

## 2. What can and cannot be combined

**Scientific separation is essential.** Do not merge Nebraska two-site acoustic/hydrology responses with Québec eDNA/occupancy site rows, Great Lakes visit datasets or multi-species Australian PAM outcomes as though they measured the same populations, same observation windows, same CallingIndex, or a common independent rainfall treatment. They are candidate **independent tests of different pieces of the causal problem**, not a synthetic spatial replication from unrelated databases.

Two-stage possible programme:

1. **Near-term, modest, source-backed:** Nebraska original-file audit, and only if source/time coverage permits, freeze a within-site rainfall × hydrology observational design with blocked year validation and explicit future-rain negative control *before looking at corresponding frog response values*. Water and rain may be physically coupled; lead/lag predictive separation is **not** causal identification.
2. **Real frogcs spatial explanation:** independent repeated 4+ physically separate breeding wetlands with synchronized acoustic activity, event-specific local wetness and true pre-evaluation history. If no such source is confirmed, retain v3.7's multi-pond Stage-0 prospective field feasibility rather than claiming an external spatial replication.

### Exact no-go criteria for calling it a frogcs replication

All of the following must be positively verified from actual data/protocol; otherwise no replication claim:
- A spatial frame of **multiple independent physical breeding wetlands**, with site IDs/coordinates and a prospectively fixed **k/depth** resolution.
- Same taxon observed at multiple sites over comparable rain/phenology windows and repeated years, with genuinely measured **no calling**, not skipped/masked/missing recording windows.
- Prior taxon×site strong activity defined from an **earlier, independent** time partition, adequate site-to-site variation and sufficient events to avoid structural zero comparisons.
- Rain/weather or water-state exposures defined and frozen before evaluation, no switching across incompatible hydrology constructs.
- Marginal calling and conditional site-configuration endpoints treated separately; exact-k conditioning is **predictive**, not a controlled causal effect.
- Out-of-block validation and a fixed informativeness rule, including explicit fail-closed result when route/wetland breadth is too small.
- Sound/recording contamination and local biological availability addressed as far as data permit.

## 3. Source/data authority and next decisions

- **Confirmed now:** journal articles, public dataset landing pages, DOI, described variable names and published design limitations.
- **Not yet confirmed:** raw Mendeley file object IDs/content hash/header; per-site actual hydrology and call completeness; any new rain × water effect sizes; a three-way rain × water × site-history interaction.
- **Explicitly not done:** any new actual frog outcome extraction, model fitting, same-data RC6 reopen, field treatment, public-record request, data custodian contact, or Iowa-native W/D access.

The near-term novel achievement would be a **credible external small-system ecological test** with clear limitation—not a substitute for the main multi-site paper's empirically still-unidentified causal generator. An inconclusive source feasibility result is a valid stop rather than a reason to pick advantageous locations after outcome readback.
