# Frozen before new outcomes: NAAMP plant-associated within-year frog acoustic phenology

**Date 2026-10-23.** Post-hoc ecological research on the existing public 2001–2015 NAAMP × USFWS NWI 250-m vegetation/wetland crosswalk. Previous analyses already found robust positive PEM alpha/gamma acoustic richness, general interannual same-site recurrence in PEM and other wetland classes, and no verified PEM advantage in interannual stability or adjusted time-gap decay. This is NOT preregistration, an independent dataset, a forecasting project, a new literature review or a direct vegetation manipulation. The original JAE RC6 main/manuscript/SI/submission remain frozen.

## New ecological question: seasonal hierarchy, not prediction

**Within the SAME monitoring route, calendar year and EXACT same physical ten stations, does the acoustic frog taxon richness surplus at NWI-mapped emergent wetland sites change across the scheduled survey rounds 1–4?** Does the seasonal association reflect newly activated calling sites versus more additional taxa calling at already active sites, and do multi-stop equal-effort acoustic taxon-pool gamma differences show the same pattern?

The NAAMP `RunNumber` is a **within-year protocol-survey-round label**, not a uniform calendar date or directly measured vegetation phenophase across US States. Keep source date-of-year distributions, source observer IDs, local temperature and noise to contextualize the result. Do not call it a live-plant flowering/leaf-out effect.

## Source/population fixed before results

- Start with exactly 7,848 standardized ten-stop source run-nights and the existing previously source-only response-blind NWI overlay of 5,147 physical SiteIDs; 6,236 NWI/environment-complete nights, 499 source physical monitoring routes, 20 US States (source GIS Actions #39450277196). The exact source loader, taxon list (including complexes) and CI>=1 and CI>=2 definitions are unchanged.
- For each State×RouteNumber×SurveyYear, retain one unique visit per `RunNumber` 1..4; if source contains duplicates for a round-year cell, drop that ambiguous round **without inspecting frog calls**. Keep route-year groups with at least two distinct remaining rounds. Require exactly identical ordered physical `SiteID` ten-stop lists across **all** retained rounds; reject site-relocated route-years rather than treating different stations as one seasonal habitat. Report every exclusion.
- Within each identical route-year group, compare only listening stops **already mapped as any NWI wetland** (mapped total wetland fraction>0), and require ≥2 stops in mapped NWI PEM emergent category and ≥2 mapped wetland stops with no PEM polygon overlap. Exactly the same physical sites and mapped categories are compared across rounds. NWI category 0 is not proof of botanical plant absence. Selection must use route/time/NWI only, never whether frogs called.
- Every eligible run contributes the zero-inclusive, per-stop:
  `C_alpha = mean_{wetland PEM+} #taxon units − mean_{wetland PEM0} #taxon units`,
  `C_activation = mean 1{>=1 call taxon} difference`,
  `C_extra = mean max(0,#taxa−1) difference`, exactly `C_alpha = C_activation + C_extra`.
- `C_gamma` is an **exact no-replacement rarefaction** difference of expected taxon pool size when drawing m=min(n_PEM,n_nonPEM) of 2–5 physical listening stops in each same-night habitat stratum. A taxon with k positive sites among n contributes 1−comb(n−k,m)/comb(n,m) to expected gamma. Previous gamma implementation is imported without retuning. Both silence and all original taxon labels retained.
- Main outcomes in exact inferential family: (1) **CI>=1 alpha surplus primary**, (2) CI>=2 alpha surplus, (3) CI>=1 rarefied gamma surplus, (4) CI>=2 rarefied gamma surplus. Four tests, BH adjustment. No choosing taxon subsets, States, plant buffer radius, Year, round thresholds or sex/observer post-readback.

## Hierarchical geography and year fixed effects

Let `h` be one **physical route × one calendar year**, whose ordered 10 physical stations are fixed. Fit an exact within-h de-meaned **categorical** survey-round regression (round1 is reference), for each C endpoint. Prespecified covariates:
- D_2, D_3, D_4: indicators survey round 2, 3, 4;
- `temp_PEMminus_nonPEM`: instantaneous same-night station-group mean air temperature (°C) difference;
- `sound_PEMminus_nonPEM`: instantaneous same-night acoustic noise/masking index difference.

This isolates how the mapped vegetation-associated acoustic richness/pool contrast **changes within a physical route-year** across the protocol survey rounds, controlling mapped geography, route-year weather and observed site-group contrasts. It does NOT hold true plant cover constant across the years nor observe a plant change; NWI is mapped static.

Equal total weight per **physical monitoring route** over all eligible repeated nights (routes, not nights/stops, are independent inference clusters). Route-sandwich covariance with finite-cluster adjustment, t(df=G−1) 95% intervals for round2–round1/3–round1/4–round1 and robust Wald-F(3,G−1) for the single **omnibus round effect** of each endpoint. Require ≥50 independent physical routes, ≥5 States, ≥100 informative route-year groups, and identifiable full rank of all five model columns; individual round-comparison coverage (both rounds recorded in same physical route-year) must cover ≥20 independent routes for each of 2vs1,3vs1,4vs1, otherwise mark omnibus as nonidentifiable rather than promote a sparse round4 contrast.

Run **4,999 physical-route 3-vector score sign flips** after weighted Frisch–Waugh–Lovell nuisance removal under the three-round-coefficient null (the route vector includes all repeated route-year records). Report the Monte Carlo plus-one omnibus p. This is an observational cluster-symmetric reference, NOT randomized vegetation assignment. Report 20-State-cluster omnibus F with df=(3,19) as a geographic uncertainty sensitivity, not an automatic substitute for route inference.

BH across **exactly four frozen omnibus tests** (including both calling strengths and alpha/gamma); classify `exploratory_route_robust_withinyear_PEM_phenological_heterogeneity` only if primary any-call alpha omnibus has route F P<.05, 4-test BH q<.05, route-vector score signflip p<.05, and State-level F P<.05. Otherwise `not_supported_by_joint_withinyear_multilevel_gates`. Lack of support never justifies choosing an early/late threshold after readback.

## Hierarchical accounting and temporal stability

Compute identical model matrices for `C_activation` and `C_extra`, and verify the **exact vector identity** for every round coefficient:
`β_alpha,round = β_activation,round + β_extra,round`.
Only describe these components; no new significance-test family. Report observed equal-route mean contrasts by rounds 1,2,3,4 and date-of-year median/IQR, sample nights and routes, and categorical effect confidence intervals.

Same observer as a **predeclared sensitivity**: within each route×year group retain it only if two or more rounds have the same nonmissing ObserverTrackingID; use at most one observer per group chosen deterministically as the most common among eligible rounds (tie: lexical observer token), rather than selecting on frog outcomes. Refit identical design only if ≥40 routes, ≥75 informative route-years and full categorical rank. Observer-sensitive results are descriptive and cannot independently establish seasonal plants or frog ecology.

Also fit a simple within-route-year **continuous linear trend in round number** (one round-number coefficient replacing D_2,D_3,D_4), same temperature/noise nuisance, for interpretive direction only. Do not use this linear alternative to rescue a nonsignificant categorical omnibus or declare seasonal adaptation.

## Boundaries and reproducible delivery

Static NWI categories may correlate with hydroperiod, permanent water, fish/predator presence, vegetation and detection, none of which is directly time matched or jointly measured. Acoustic richness is not occupancy, population fitness or direct frog-frog interactions. Survey rounds intentionally follow season, but across States the DOYs vary, so phenological ecology is exploratory. If calendar DOY is non-monotonic within some route-year despite round order, report the exception rate and avoid an absolute phenology claim.

Add source-grounded Python analysis `exploration/run_naamp_vegetation_withinyear_round_hierarchy_v0_1.py`, frozen QA workflow `.github/workflows/naamp_vegetation_withinyear_round_hierarchy.yml`, aggregate result and a compact ecological synthesis to the isolated exploration branch only. Third-party raw datasets are downloaded into GitHub Actions and not committed. JAE RC6 and `main` stay untouched.
