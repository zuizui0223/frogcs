# v6.4 — prospective ecological discriminator: water-path hysteresis vs taxon-specific acoustic carryover

**2026-10-11 JST — independent draft PR #135 ONLY.** Proposed **future** design; no new frog response data or depth loggers have been accessed. This design is written after the existing NAAMP results and after public reports of the four-wetland 2026 pilot, so it is **NOT a preregistration predating those already-published observations**. JAE RC6/main remains locked.

## Ecological question — beyond the already demonstrated inundation response

> **At the same locally measured depth, do frogs express different calling states while water is rising versus receding, and does acoustic use in *previous independent wetting episodes* predict those differences after local hydrological history and persistent species–wetland propensity are represented?**

Three mutually informative ecological pictures:

1. **Instantaneous depth sufficiency:** current local water state, season, diel/solar phase, weather, observation quality and stable species–wetland propensity adequately explain calling. There is no reproducible phase/history gain.
2. **Hydrological hysteresis:** at comparable present depth, the rising and falling limbs, time since inundation and antecedent dry interval help forecast calls. The *hydrological path* matters, without invoking individual memory or unexplained biological persistence.
3. **Additional acoustic carryover:** after depth, hydrological *path*, species–wetland stable propensity and effort are represented, strictly prior episode-specific chorus history improves later-episode forecasts of **which wetlands express activity**. This supports an extra predictive state variable, **not** individual philopatry, acoustic social facilitation, adaptive fitness or fixed causal mechanism.

### Why the distinction is not an automatic novelty claim

- [Sarker et al. (2022), *The effect of inundation on frog communities and chorusing behaviour*](https://doi.org/10.1016/j.ecolind.2022.109640) already found different species' chorus durations increasing or decreasing after water arrival in Gwydir; the 2026 Murrumbidgee programme public report also described dry-versus-watered calling differences. A generic before/after wetting or taxon-heterogeneous response is **not new**.
- [Longer-term Nebraska paired acoustic/inundation monitoring](https://www.sciencedirect.com/science/article/pii/S1470160X20311109) already associates calling phenology with hydropattern, season and precipitation. Even phase-sensitive observations are not necessarily novel until a stricter matched-depth, repeated-episode comparison is established.
- Our specific **paired depth rising vs receding and previous-episode acoustic residual** contrast is a prospective target, not verified to be absent from every prior study and not claimed as a novel discovery yet.

## 1. Required original record grains BEFORE any new frog outcome read

Each planned analysis key requires:
- **Physical wetland:** source-authenticated independent `wetland_id`, date-effective `recorder_id`↔`logger_id` crosswalk, metadata on station moves and sensor multiple membership. 12 recorders ≠ proven 12 independent wetlands.
- **Recording opportunity:** `recorder × timestamp_start/end × VALID/MISSING/UNCERTAIN × minutes × noise quality × classifier_version`; preserve legitimate no-calling VALID opportunities, never turn missing clips into non-detection.
- **Wetland local depth:** `logger × timestamp × numeric water depth / instrument datum × calibrated resolution/uncertainty × quality × actual dry threshold`; river-gauge ML/day, CEW annual frequency and vegetation plots are not stand-ins for local depth.
- **Ecological event:** local wetting onset and independent rising/falling cycles from hydrological records alone, after resolution and sampling frequency are documented and **before** animal outcome inspection; overlapping hydro episodes must not be counted as independent.
- **Species acoustic classifier:** original taxon annotations with confusion/error by wet/dry, rain/water noise and time of day, including manual validation on a panel independent from evaluation periods; measures are acoustic, not egg/tadpole or NAAMP CI2/3 scores.
- **Usage rights:** permission for source derived files and safe pseudonymized wetland/time output.

If any essential identity/effort/hydrology/detection/right element is missing, fail closed; descriptive Nap Nap 2020 remains a **one-wetland illustration**, not multiple-wetland verification.

## 2. Three models and two non-interchangeable contrasts

Let (Y_{s,w,t}) denote **calibrated acoustic calling occurrence or intensity per eligible standardized recording interval** for species (s), physical wetland (w) and time (t). Outcome metric and recording-standardisation must be documented *before* inspecting those source responses.

**M0 — current-water and persistent propensity baseline**
- Same-wetland local current depth/inundation, season and solar time, weather, recording duration/quality, species terms and a regularized **species × physical wetland propensity** estimated only from the training years.
- Never estimate site/taxon fixed propensity using evaluation-year acoustic detections.

**M1 — past-water path / hydrological hysteresis**
- All M0 predictors plus hydrology-only **backward-looking** depth rate-of-change (rising / falling / stable), time since local inundation, previous dry spell duration, depth trajectory and rewetting episode descriptors.
- Compare M1 vs M0 at *same-depth overlap* between rising and falling observations. If the two phases do not overlap in actual local depth and solar/seasonal covariates, the hysteresis contrast is **not identified** and should be reported `NO_COMPARABLE_PHASE_SUPPORT`.
- This is observational conditional predictive evidence, not a randomized depth-phase causal effect; unmeasured thermal/social changes can track phase.

**M2 — additional past acoustic state**
- All M1 predictors, **plus** a strictly prior, episode-specific, species × wetland chorus-use feature (e.g., a prior completed wetting episode's standardized chorus activity), estimated from earlier eligible training intervals and never including same/current episode or held-out/future labels.
- Use the **same historical data budget** for M1 and M2, and ensure M1 includes comparable episode hydrology. A mere “ever chorused here” or historical site mean duplicating a fitted species×wetland propensity is **not** genuine new information.
- Prefer residualized prior acoustic activity versus M1's train-fold expected probability, with its construction also frozen and cross-fitted within historical training folds; test this as **temporal information**, not as an individual memory mechanism.

**Primary information gains (direction unknown):**
- (Delta_1 = Score(M1)-Score(M0)), hydrological path beyond present depth.
- (Delta_2 = Score(M2)-Score(M1)), lagged acoustic information beyond hydrological path and persistent propensity.
- Higher score must mean better by definition (e.g., negative mean log loss; select one in advance). All comparisons computed on **exactly the same eligible held-out wetland×episode outcomes**.

Do **not** use an observed active-site count `k` to estimate the causal effect of watering, as `k` can itself be affected by local hydrology. An exact-`k` conditional placement check remains secondary purely **predictive**.

## 3. Prospective data split and pseudo-replication protection

- Freeze data roles from non-outcome station/event/quality metadata first. **Rolling-origin** years/whole hydrological episodes; no clips from a test event in model training or calibration.
- The 2026 publicly described **four-wetland pilot** has **aggregate results previously exposed**. Declare a separate exploratory status for those exposed site-periods; do not call them a completely unseen confirmation set.
- Aggregate predictive score differences at the **independent physical wetland × distinct hydrological episode** level, with uncertainty resampled by wetland/catchment-event, not by individual 5-minute clip.
- Need multiple independent wetting/recession events and comparable depth values within individual wetlands; 12 recorder devices and thousands of five-minute clips do not themselves establish effective replication. If few independent episodes/years or only four already-described sites exist, downgrade to a descriptive pilot.
- Control season, circadian/solar phase, water-event duration and recorder noise: classifier false negatives can depend on wet/dry status and hydrophone/water sounds.
- Choose water-phase smoothing, acceptable sensor gaps, phase-decision noise threshold, matched-depth bands and minimum effort **from original sensor sampling/calibration metadata prior to frog readback**, not to maximize statistical significance. A sensor-standard-based `stable` class must not be forced into rising or falling.
- Report negative (Delta_1) or (Delta_2), poor phase overlap and uncertain hydrology with equal prominence. Do not switch endpoints/models after outcome exposure.

## 4. Decision table — what the data could actually establish

| Metadata+source conditions | Admissible science |
| --- | --- |
| no original physical wetland or source opportunity ledger | descriptive dataset-source audit only; STOP |
| wetland, quality, species detection present, but no same-wetland logger | species calling and season/site descriptive patterns only; no matched-water mechanism |
| matched depth, but only one water limb / no repeated comparable depth | depth-associated calling only; NO phase hysteresis test |
| repeated matched rising/falling plus valid calls, but no independent wetting histories | M1 vs M0 possible as *exploratory* conditional hydrology, M2 not independently tested |
| sufficiently repeated, independently identified wetland×episode panels + validated detection, strict historical folds and rights | M1/M0 and M2/M1 genuinely testable (predictive, observational) |
| negative or inconsistent out-of-year gains | no evidence that these historical features improve predictions in that frame; not universal absence of frog history effects |

## 5. Evidence and project boundary

No observations have been downloaded or modeled in v6.4. The historical acoustic archive exists, but the paired physical-unit/valid-opportunity/wetland-specific logger table and usage rights are **not obtained**. The university/ARDC registered `2014–2024` frog-abundance source returned official CKAN 403 on the verified canonical slug in v6.3 and cannot be silently used as a new sound-level dataset. The existing single metadata-only CEWH enquiry is **UNSENT**.

**Work to do only after authorised source inventory:** source-only metadata eligibility gates, then freeze source-specific numeric QC thresholds, then access original species-call responses under approved rights; never reverse that order. JAE RC6 remains frozen at main `0871da0c97` and is not changed by this independent experiment design.


## 6. Executed implementation QC — synthetic only

- CI: [GitHub Actions **38107413290 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38107413290).
- Code: [`scripts/preflight_hydro_hysteresis_acoustic_history_v64.py`](scripts/preflight_hydro_hysteresis_acoustic_history_v64.py), standard-library only.
- Synthetic example uses **two invented wetlands**. One has a sensor-defined depth bin encountered while **rising and falling**; the other does not have matched rising/falling depths. The code counts **one** potentially informative synthetic wetland-depth stratum, but flags independent wetting episode/solar/seasonal comparability as **NOT VERIFIED**.
- Hydrological phase uses **only the preceding measurement**, and a source-defined maximum instrument gap. It rejects missing depth/phase tolerances rather than selecting convenient thresholds after seeing frog outcomes.
- A prior chorus score is accepted only if its complete acoustic episode ended **before both the target date and the frozen training cutoff**. A future evaluation-period episode is rejected; missing past history remains **missing**, never silently mapped to no calling.
- No real acoustic score, water-depth value, station identifier, wetland ID, 2014–24 frogs resource, or sensitive source location was accessed. The test supports correct code behavior **only**, not hydrological hysteresis or acoustic carryover in real frogs.

**Scientific status at v6.4:** `SOURCE_INVENTORY_NEEDED; HYSTERESIS_NOT_TESTED; ACOUSTIC_HISTORY_NOT_TESTED`. The next evidential step is still an approved, source-authenticated independent wetland/recorder/logger/effort/classifier manifest. The previous metadata-only custodian request is UNSENT.
