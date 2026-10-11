# v6.9 — biological GO / LIMITED / STOP decision after completed v6.5–v6.8 synthetic falsifications

**2026-10-11 JST. Independent draft PR #135 only.** This document closes further synthetic-mechanism proliferation and converts source discovery into a **source-first, biological-testability decision**. It is **not** an executed field investigation or a preregistration of all prior studies. Journal of Animal Ecology RC6/main remains unchanged.

## 1. Scientific current state (what is and is NOT established)

**Source-established:**
- CEWH Flow-MER has archived Murrumbidgee acoustic recordings and has reported real four-wetland frog detection/water-arrival work; the accessible nine-day Nap Nap interactive sequence is one named wetland only. None is a verified, authorized complete multi-wetland species×recording×local-water panel in this project.
- The public 2014–2022 frog source was audited at 673 rows; the separately university/ARDC-registered 2014–2024 product is not a validated acoustic panel. Its actual canonical `flow-mer-frogs` CKAN metadata endpoint returned HTTP 403; no animal rows were accessed from that newer product.
- The original MDMS `NAME` point-level mapping is verified, but official `DESCRIPTIO` means merely *optional description* and gives no physical parent-wetland unit. A monitoring **point** is not proof of an independently sampled wetland.
- Neither original source stage-specific tadpole field ID nor survey-opportunity denominator was obtained.

**Software/synthetic-established only:**
- [v6.5 CI SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38107674794): known artificial null, water-only, injected acoustic-carryover and combined regimes are distinguishable under favorable complete-water simulation.
- [v6.6 CI SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38107962770): omitted artificial slow water creates *positive prior-calling prediction* despite exactly zero direct calling effect.
- [v6.7 CI SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38108587827): synthetic noisy/missing local depth leaves spurious lag gains.
- [v6.8 CI **SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38108980247): four artificial sensors with shared error do not reliably remove false lag information. Signed median improvements under ZERO direct calling carryover: oracle **−0.001700**, four independent loggers **+0.000644**, four rho=0.75 **+0.006490**, four fully shared **+0.008675**, one noisy **+0.010257**. The entire pre-frozen v6.8 GitHub Actions log reproduces the previous independent local readout exactly.

These synthetic numbers are **not** real effect sizes, empirical confidence intervals, Type I error rates, or information that any frog species possesses memory, fidelity, social feedback or increased reproductive success.

## 2. Ecological hypotheses conditional on genuine source access

**Q-A. Hydrological path dependence:** Among true independent wetlands, **at comparable present measured local depth**, are calibrated frog calling occurrence/intensity and taxon composition associated with rising versus receding local depth, antecedent drying and water-arrival history, after season/solar time and recording quality are accounted for?

**Q-B. Extra previous acoustic prediction:** After *adequately measuring* recent and accumulated **local wetland** hydrological history (with sensor uncertainty), plus stable species×wetland propensity and detection error, does **strictly previous completed wetting-episode** acoustic use improve forecasts on later untouched episodes? The honest endpoint is **incremental held-out prediction**, not biological memory causation.

**Q-C (requires an additional study):** Does reproductive payoff / tadpole survival differ at recurrent acoustic sites? This cannot be answered by calling records alone; requires authenticated field-stage species/effort linkage, appropriately lagged offspring outcomes, and independent breeding-event denominators. The existing pooled/within-point tadpole table sign reversal is only exploratory table-level association.

The original independent study's strongest immediate question is Q-A; Q-B is supportable **only as a predictive test with environmental-confounding sensitivity**, not as an identified cause. A genuine causal history/social facilitation mechanism would require intervention, justified natural experiment or additional designs, not simply a positive lag coefficient.

## 3. Final source-first gate, with no arbitrary success thresholds

| Gate | Original source evidence required, ideally metadata first | If missing |
| --- | --- | --- |
| **W — physical unit** | date-effective **independent wetland unit ←→ recorder/location/logger** crosswalk; moved stations and multiple devices within one wetland; year continuity | No independent wetland count, multilateral chorus allocation or wetland-cluster inference |
| **O — acoustic denominator** | all scheduled/attempted **recording intervals** with VALID/MISSING/UNCERTAIN quality, standardized effort, confirmed valid no-calls and method version | No legitimate silence or activity probability; recordings cannot be treated as independent visits |
| **H — local water** | original depth/inundation **same-wetland time series**, accurate clocks, vertical datum/dry thresholds, continuous past hydroperiod, calibration precision, sensor moves, missingness and cross-sensor agreement/error | No credible water-path vs acoustic-history discrimination; river flow or annual raster is not substitute |
| **D — taxon detection** | species-specific labels/classifier version and independent hand-validation with false positive/negative patterns across water/rain/noise and seasons | Do not treat classifier non-detection as frog silence or chorus intensity |
| **T — independent temporal support** | actual **distinct wetlands × separate wetting/drying events × calendar years** with valid overlap, within-wetland same-depth rising and falling, strictly earlier episode histories; report counts, do not impose `k≥4` borrowed from NAAMP | Report `NO_PHASE_OVERLAP` or `NO_INDEPENDENT_HISTORY`; do not upgrade one-site clips or four publicly exposed pilot wetlands |
| **R — source rights** | data owner/custodian, usage permissions, data version, safe site aliases, permissible derived public outputs | No acquisition or downstream publication until authorized |

The gate decides **identifiability and ethical access**, not a cherry-picked sample size. Real precision/power must be evaluated from verified actual coverage and prespecified endpoints later; the artificial 180×24 source-free simulations are not power results for Flow-MER.

## 4. Triage when original source metadata arrive

- **GO for Q-A, CONDITIONAL Q-B:** all W/O/H/D/T/R pass, depth/phase support exists. Freeze classification cutoffs, lag duration, episode segmentation, calibration and *calendar folds* using original metadata and source protocols **before opening frog call outcomes**. Compare M0 current water, M1 cumulative/path hydrology, M2 prior-call forecast with unchanged held-out population, but report sensor uncertainty and unmeasured-state caveats.
- **LIMITED:** independent wetland/recordings and classifier pass, but only broad gauge/annual wetness, no paired depth or phase. Study calling chronology/detection and environmental association descriptively; **no Q-A causal/hysteresis claim, no Q-B separate acoustic-state claim**.
- **LIMITED single site:** only Nap Nap-like one-wetland time series; study within-site acoustic time and water timing descriptively, not 12-wetland organization or landscape-scale spatial history.
- **STOP:** uncertain physical wetland membership, absence of valid recording negatives, unknown classifier noise, no overlap/independent episodes, or no source rights. Preserve the source audit; do not invent hydrological joins or rebuild frog outcomes from public aggregate Y/N data.

**Important:** even after GO, observational M2–M1 gain **does not prove memory/adaptation**. The downstream report must label predictive information versus identified biological mechanism explicitly.

## 5. Single real next action, explicitly unsent

The [one existing metadata-only CEWH inventory request](V6_0_CEWH_ACOUSTIC_HYDROLOGY_SOURCE_INVENTORY_REQUEST_UNSENT.md) now includes logger model, accuracy/datum, calibration, gaps, and shared instrument error documentation alongside recorder/wetland identity, audio opportunity/classifier and rights. **No email was sent**; any contact requires a separate author decision, verified recipient and author identity. No private observations requested at this stage.

**Project scientific status:** `FUTURE_HYDROLOGICAL_HYSTERESIS_FEASIBILITY_UNVERIFIED; PAST_CHORUS_PREDICTIVE_GAIN_NOT_EMPIRICALLY_TESTED; CAUSAL_BIOLOGICAL_MEMORY_NOT_IDENTIFIED; NEW_SOURCE_REQUIRED`.

**Do not reopen NAAMP, retune JAE RC6, create more post-hoc synthetic branches, or merge this source-validation PR into the submission branch.**
