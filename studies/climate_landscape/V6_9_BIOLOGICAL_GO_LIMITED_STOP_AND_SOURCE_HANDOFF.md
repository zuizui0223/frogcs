# v6.9 — biological GO / LIMITED / STOP decision after completed v6.5–v6.8 synthetic falsifications

**2026-10-11 JST. Independent draft PR #135 only.** This document closes further synthetic-mechanism proliferation and converts source discovery into a **source-first, biological-testability decision**. It is **not** an executed field investigation or a preregistration of all prior studies. Journal of Animal Ecology RC6/main remains unchanged.

## 1. Scientific current state (what is and is NOT established)

**Source-established:**
- CEWH Flow-MER has archived Murrumbidgee acoustic recordings and has reported real four-wetland frog detection/water-arrival work; the accessible nine-day Nap Nap interactive sequence is one named wetland only. None is a verified, authorized complete multi-wetland species×recording×local-water panel in this project.
- The public 2014–2022 frog source was audited at 673 rows; the separately university/ARDC-registered 2014–2024 product is not a validated acoustic panel. Its actual canonical `flow-mer-frogs` CKAN metadata endpoint returned HTTP 403; no animal rows were accessed from that newer product.
- The original MDMS `NAME` point-level mapping is verified, but official `DESCRIPTIO` means merely *optional description* and gives no physical parent-wetland unit. A monitoring **point** is not proof of an independently sampled wetland.
- Neither original source stage-specific tadpole field ID nor survey-opportunity denominator was obtained.

**New 2024–25 official source-governance evidence (reviewed 2026-10-12; not animal-data access):** [Murrumbidgee Area Flow-MER Annual Report 2024–2025 (dated 22 January 2026)](https://www.dcceew.gov.au/sites/default/files/documents/murrumbidgee-mer-annual-report-2024-25.pdf), printed pp. 22–23, 28 and 98, provides a more precise route to the original information missing above.

- **Authoritative original project field source:** the report explicitly identifies a central **Microsoft Access database** for Murrumbidgee Area project field records going back to 2014. Hydrology and other ancillary data are documented as versioned copies on **restricted project shared drives**, not necessarily in that same database. Governance roles include a **Lead Data Manager**, **Data Quality and Systems Analyst** and **Spatial Data Manager** (wetland polygons, location IDs and original linkages). Field records may have `evaluationCode` and `qualityCode` for deviations; whether these fields are defined for any *automated audio archive* is **NOT verified**. This identifies which roles to ask, not access rights or a verified crosswalk.
- **Hydrology exists at another documented source grain:** the 2024–25 report says depth loggers were deployed across **35 wetland sites**, and depth was processed into **daily water-depth time series** for that water year. The report's methods table also references 32 loggers for the evaluation approach; these distinct counts are **not reconciled** by this project. Neither nominal count establishes how many continuous, accurate, time-matched logger streams overlap the **12 historical long-term frog acoustic stations**. Do **not** conflate daily summaries with original logger timestamps or clock-matched recording opportunities.
- **2024–25 realized frog methodology, not the entire 2014–25 acoustic time series:** the same report describes **6 × 2-minute human listening surveys**, separate **2 × 20-minute adult visual surveys**, and **9 surveyed wetlands**; these must not be confused with the automatic 5-minute/hour archive. Tadpoles that cannot be separated between barking and spotted marsh frogs were assigned to a *Limnodynastes* species complex, explicitly maintaining the stage/taxon nonidentification concern. The 2024–25 reported procedure does **not** determine the actual acoustic-bout count for earlier years.
- **Separate shared audio stream:** the waterbird methods describe *raw audio shared* between NSW DCCEEW's Saving our Species southern bell frog programme and Flow-MER for 2024–25 bittern monitoring. This is a **source-custodian/referral lead** only; it does not authenticate overlap with the 2016–2025 frog-recogniser station archive or grant reuse rights.
- **Original governance barrier remains:** the report explicitly says research release is controlled by CSU policy, CEWH contractual terms, relevant ethics/partner agreements and sensitive-site restrictions. The then-new MDMS was **not yet available as of the report's 30 September 2025 writing date**; its present status has not been established from that historical statement.

**Practical decision:** obtain a *non-sensitive, versioned table/key inventory* from the Murrumbidgee project's **Lead Data Manager and Spatial Data Manager** through the existing CEWH enquiry, including original recorder↔logger↔wetland date-effective identifiers, separate acoustic opportunity/quality-code dictionaries and daily-versus-original water sampling grains. Do not request private database credentials or interpret a general central database statement as proof that raw autonomous recordings are stored there. The enquiry remains **UNSENT**, and the W/O/H/D/T/R gates are still **not cleared**.

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
