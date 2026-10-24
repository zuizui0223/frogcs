# Environment-only prospective route-panel selection — transparent exploratory design
Date: 2026-10-24

## Mission / boundary
Turn the frog chorus spatial-history identification problem into an actionable **independent field-monitoring candidate panel** rather than repeatedly fitting the already-studied NAAMP frog outcomes. This is a source-only design prototype, **not** site access permission, a field survey, independent frog validation or causal identification. The earlier paper RC6 and `main` are frozen. No `Counts.csv` is read. Thresholds are environmental follow-up heuristics motivated by the 15-year source-only audit; they are NOT a pre-NAAMP preregistration.

## Authoritative source data
1. Original USGS Annual NLCD Collection 1.2 2001–2015 500m site-year categorical buffer table, SHA256 `137ad705641e39b1a43acfb0d1c5c4aef1fce7024ccb788fb1efc67510a2c67a`.
2. EC JRC/Google previous-calendar-month GSW MonthlyHistory VER5-0 500m water, SHA256 `bd291a4f42a9768a4dfc2d92c68050344bde4e5b2bbb0a923a1218399e96f81b`. JRC 0=no satellite observation, NOT dry water state. Use coverage ≥50% for primary environmental audit, ≥80% for sensitivity.
3. Accepted physical NAAMP coordinates SHA256 `2dbd226a117e5d2c9c10dbd6340fb86a07320b2925aaca3249c8a307a5071afc`. Data represent historical U.S. monitoring sites, **not necessarily accessible contemporary ponds**.

## Environmental information score (descriptive, not Fisher information)
Within each physical RouteNumber × preceding-calendar-month, identify adjacent *observed survey years* with ≥6 of the same physical SiteIDs having valid satellite coverage both years. Retain the **earliest eligible pair per route × calendar month**. Let site-specific difference `d_i = JRCwater_{i,t2} - JRCwater_{i,t1}`. Define `E_rm = Σ_i(d_i - mean(d))²`. This is environmental *site-relative contrast energy*, NOT directly ecological Fisher information, a water-effect coefficient, frog power, or an effect size.
Average `E_rm` across a route's eligible months for **one E_r per route** (do not treat repeated route-months as independent). Summarize concentration over routes (top decile, top 1%, `N_eff=(Σ E_r)²/Σ E_r²`), with sensitivity to (a) ≥80% satellite visibility, (b) exactly one-year gaps, and (c) at least 8 matched stations.
Ranking is *environment-only but selected after examining the environment distribution*; neither percentiles nor model variants may be claimed independently pre-registered. Do not use frog `Counts.csv` to select sites.

## Candidate route categories for independent field validation
Use only routes with exactly 10 accepted physical sites, max pairwise coordinate separation ≤25km, 500m wetland vegetation (woody + emergent) vs NLCD mapped open water measured across actually surveyed years, and ≥1 spring (preceding month March–June) cross-year JRC matched contrast with ≥6 common observed stations.

Select at most **10 routes per category**, at most **2 routes per state** within category, then stop (report shortage rather than relax rules). Deterministic tie-breaking by SHA256(RouteNumber) ascending.

- **A: satellite-visible variable water** — route environmental contrast `E_r` in top **10%** of all rank-audited routes, route wetland-vegetation range ≥25 percentage points. Order candidates by `E_r` descending. This is a positive-visibility comparator, not proof of true hydroperiod.
- **B: vegetated-wetland sensor-blind candidate** — `E_r` at or below median; ≥2 physical sites with 500m mean woody/emergent wetland ≥25% and mapped open water <1%; route wetland vegetation range ≥25pp. Order by number of blind wetland sites descending, then `E_r` ascending. Here JRC lack of water changes MUST NOT be interpreted as true water constancy; this is precisely the validation target.
- **C: low wetland/openwater comparator** — route mean 500m wetland vegetation <5% and mean openwater <1%; `E_r` at or below median. Order by `E_r` ascending. This is a LAND-COVER comparator, not proven no local ponds or no frogs.

All categories are *habitat/remote-observation contrasts*, not biological "treatment" arms. The route-level panel must expose counts and selection attrition (exact10, acceptable span, spring-history, category, state cap) and full 10 site coordinates per selected route. Do not infer contemporary route accessibility or landowner permission.

## Prospective site × event observational protocol (future, not performed)
For each selected route, verify access and actual wetland existence *on site* before treating it as an eligible field route. Sample all 10 original stations at matched repeated visits within the same breeding season, ideally ≥2 pairs of relative-to-rain opportunities, plus observer/detection controls. Measure directly at each event: water depth (cm, calibrated local datum), under-vegetation flood presence and flooded area fraction, water temperature, dominant vegetation cover, wind/noise, microphone calibration and exact acoustic timestamp. Missing local water must stay missing, not 0.
Do not use casual weather forecasts as a substitute for observed local water. Balanced repeated visits are required to separate site-fixed and event-common effects.

**Primary information gate before frog outcomes**: For actual field water `W_{it}`, calculate the two-way fixed-effect residual `W_it - mean_t(W_it) - mean_i(W_it) + overall_mean(W)` for complete site×event panels; require nontrivial variance after removing all site and event means. In two-occasion pairs, equivalently use the non-uniform vector `ΔW_i - mean_jΔW_j` across ≥6 matched stations. The threshold is a measurement precision/variability issue; do not equate <5pp JRC pixel difference with no wetland change.

If independent acoustic outcomes are eventually available, freeze a new taxon/detection/conditional-k model and geography/time splits **before** seeing them. A route-common rainfall shift can affect total call magnitude while cancelling from conditional spatial placement. No simultaneous calling or individual site memory is inferable from sequential NAAMP stops.

## Outputs
Route candidate registry + all-site CSV, source/selection audit JSON, source-only sensitivity summary and a machine-readable field observation schema. Repository receives only small derived tables and scripts, not bulk satellite source data or original acoustic outcomes.
