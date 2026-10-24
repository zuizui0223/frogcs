# 2001–2015 habitat × preceding-month water: ecological estimability audit (2026-10-24)

## Current state
**Source-verified, outcome-blind analysis complete.** USGS Annual NLCD Collection 1.2 and EC JRC/Google MonthlyHistory VER5-0 previous-calendar-month water have been linked to original NAAMP physical site visits. No acoustic `Counts.csv`, taxon-specific calling response, colonization, movement or breeding-success outcome has been accessed or estimated in this study. This does **not** modify the frozen RC6 Journal of Animal Ecology manuscript or `main`.

## Source integrity
- Official full JRC 2001–2015 compiled environment CSV SHA256 `bd291a4f42a9768a4dfc2d92c68050344bde4e5b2bbb0a923a1218399e96f81b` (matching full-panel audit receipt from [run 40061444450](https://github.com/zuizui0223/frogcs/actions/runs/40061444450)): 172,153 unique physical SiteID × survey year × strictly previous calendar month keys; 136,194 (79.1%) with >=50% actual observed 500-m pixels.
- USGS C1V2 original-year 500-m NLCD land cover: 64,779 QC site-years. Geometry-only NAAMP source calendar: 185,221 station visits, 18,778 distinct RunIDs, 1,145 distinct physical routes.
- **All 185,221 visits** independently joined exactly to both environmental datasets by original `RouteNumber × SiteID`, year and previous month, with no unmatched rows; original water input SHA256 was independently validated before this audit.
- JRC class 0 means no observation and is **never** assumed to be observed non-water; classes 1 and 2 are observed land/water. JRC is an annual satellite imagery *monthly composite* for the previous calendar month, **not** survey-night water depth/hydroperiod.

## Same-route-run spatial contrast (correct acoustic sampling topology)
- 14,638 survey **runs** spanning 1,132 physical routes met the prospective geography-only gate: at least 8 original NAAMP listening-station visits and at least 6 stations with >=50% valid 500-m JRC pixels.
- Within these runs, **5,918 / 14,638 (40.43%)** had >=5-percentage-point observed water-fraction contrast across stations (physical-route block-bootstrap 95% interval **37.34–43.72%**); **4,520 / 14,638 (30.88%)** had >=10-percentage-point contrast (95% interval **27.72–33.93%**).
- Median within-run maximum-minus-minimum JRC water fraction: **2.42 percentage points**. The route-run definition uses actual RunID, not route×monthly grouping; stops are sequential observations, not simultaneously monitored stations.
- **7,694 eligible runs** contained both stations with >=25% woody/emergent wetland vegetation and stations below that threshold. This provides within-run vegetation variation independent of frog outcomes.
- These are descriptive coverage/contrast statistics, not a test of frog chorus use or an estimate of local hydrological forcing.

## Same-site same-season interannual temporal contrast
- 28,354 distinct original physical site × previous-calendar-month groups have >=2 different survey years with >=50% observed JRC pixels.
- **1,771 (6.246%)** have >=5pp interannual water-range and **820 (2.892%)** >=10pp. A water-positive subset of 10,474 groups has **16.91%** >=5pp interannual contrast.
- Environmental variation is markedly related to mapped land-cover composition:

| Site-mean 500-m NLCD habitat stratum | Repeated site×month groups | >=5pp interannual JRC difference | Route-bootstrap 95% interval |
|---|---:|---:|---:|
| Open water >=10% | 2,256 | 1,109 (49.16%) | 45.74–52.23% |
| Woody+emergent wetland >=25%, NLCD open water <1% | 4,445 | 71 (1.60%) | 0.96–2.37% |
| Wetland vegetation <5%, open water <0.5% | 10,791 | 64 (0.59%) | 0.12–1.26% |
| Other | 10,862 | 527 (4.85%) | 3.85–5.96% |

The open-water minus vegetated-wetland descriptive contrast in detectable >=5pp interannual change was **47.56 percentage points** (route-bootstrap 95% interval **43.93–50.69 pp**). With a stricter >=80% pixel-visibility gate, the rates remain **35.3% (761/2,155)** versus **1.3% (54/4,272)**, respectively. **This is differential remote-sensing water detectability and mapped habitat structure, not evidence that water levels truly vary less in vegetated wetland breeding sites.**

Across season-matched repeated site groups, 94.7% of the descriptive sum of between-group mean-water-fraction variance and mean within-group interannual variance lay between groups. This is not an occupancy ICC, causal variance component, or population-level variance estimate: it is conditional on observed same-month repeated surveys.

## Seasonal missingness and mechanisms not excluded
At the unique physical site×previous-month grain, >=50% JRC pixel coverage was **11.6% for December**, **24.6% for January**, **65.8% for March**, **93.7% for May**, and **94.4% for June**. The source missingness is demonstrably season-dependent; any water-complete-only outcome model could alter the composition of survey dates/taxa.

Water under woody/emergent vegetation, tiny ephemeral ponds, shaded shallow breeding substrates and short rainfall-responsive inundation can be poorly classified by 30-m monthly satellite observations. Thus **absence of JRC open-water pixels cannot falsify local wetland hydrological filtering** in those habitats. Static NLCD habitat and monthly observed open-water **must remain separate covariates**.

## Next decision and rigorous scope
These source-only results establish that there is meaningful **within-run spatial water and vegetation contrast**, but sufficient temporally resolved water variation is habitat- and visibility-dependent. The next authorized research line is a **separate exploratory frog outcome study**, with its own *before-outcomes frozen* route/time-blocked design, source-access gate, detection controls, and explicit conditioning on species/route-night response magnitude. No frog claim or JAE RC6 revision is supported yet. Because previous frogcs analyses already inspected NAAMP outcomes, subsequent NAAMP fits are exploratory, **not** independent confirmation.

## Reproducibility
Independent notebook-free Python computations, joined original-year environmental tables, route-run source-unit audit, monthly/state/habitat coverage, repeated site×same-season tables, route-clustered bootstrap, and stricter >=80% coverage sensitivity are packaged in the downloadable environmental-identifiability archive for this turn. Aggregate values above are immutable analysis receipts; avoid pushing ~26 MB source tables into `main`.
