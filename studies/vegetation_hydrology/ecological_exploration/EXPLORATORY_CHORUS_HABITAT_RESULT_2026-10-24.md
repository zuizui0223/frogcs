# NEW exploratory frog chorus placement × vegetation/water: first actual outcome result (2026-10-24)

## Status and evidence hierarchy
**Executed SUCCESS:** [GitHub Actions run 40078227644](https://github.com/zuizui0223/frogcs/actions/runs/40078227644), artifact `exploratory-exact-k-frog-habitat-location-audit-not-independent-replication` (ID **12554441079**). Previous run 40078164736 failed at the *pre-outcome unit-test stage* because a guard-test symbol was misnamed; the guard was corrected without changing model assumptions, and all **7/7 pre-outcome tests passed** before `Counts.csv` readback. Dataset source hashes for Runs, Stops, Counts and full JRC water were verified. The annual NLCD C1V2 source was rebuilt from the original 15 SHA/receipt-pinned source artifacts.

**Interpretation:** this is a NEW post-hoc **exploratory secondary test using the already analysed NAAMP monitoring programme**, not independent confirmation and not a re-estimate/reopening of the frozen RC6 JAE manuscript. All work is isolated in `research/chorus-habitat-conditional-exploration-2026-10`. No modifications to `main` or the submitted manuscript.

## Frozen target
- NAAMP full canonical source: **4,236 matched wetter–drier pairs** (each same State × RouteNumber × RunNumber, adjacent observed years with unequal DaysSinceRain); original 10-stop survey framework and site coordinate QC.
- Exclude **64** pairs whose wet/dry 10 physical SiteIDs changed or were incomplete; exclude **380** more pairs at geography-QC-held physical sites; retained eligible spatial support before taxon filters is 3,792 pairs.
- Analyze a taxon acoustically unrecorded at all ten drier stops and with **k=2..9** CI2/3 strong-chorus stops on the wetter revisit. Exactly condition on `k`; enumerate `choose(10,k)` alternative placements. Focal sample: **1,088 taxon × matched-pair placement groups**, **333 distinct physical routes**, **44 original operational taxon label tokens** (not a claim about 44 biological species). Route folds: deterministic SHA256 5-fold; ridge penalty 1.0 fixed.
- M0: strictly-prior species × physical-site strong-chorus probability transformed to a smoothed logit. Prior history includes only surveys preceding BOTH members of the focal matched pair; coefficients trained on other route folds.
- M1: M0 + 500m annual USGS NLCD Collection 1.2 woody/emergent wetland vegetation fraction and open-water land-cover fraction, centred within the ten stations. Predicts *spatial placement conditional on the number of strong stops*, **not rainfall effect or total amount of calling**.
- M2: same model plus strictly **previous-calendar-month** JRC 500m observed-water fraction, only in complete ten-site valid imagery cases; compare M0/M1/M2 on identical complete-case focal groups. The month is not the survey-night water level.

## Frozen-primary held-out route predictive finding
| Route-fold heldout exact-k log probability | Mean per focal group |
|---|---:|
| M0 (historical acoustic physical site propensity) | **−4.308707** |
| M1 (M0 + habitat) | **−4.302777** |
| M1 − M0 | **+0.005930** |
| Physical-route-cluster bootstrap 95% interval | **−0.007765 to +0.018551** |

**Decision: positive point estimate, but no supported route-heldout predictive increment from the coarse 500m habitat covariates.** The interval spans zero. This is not an equivalence/non-effect finding, and it does not refute fine-scale breeding microhabitat filtering.

The historical-acoustic-site baseline coefficient remained positive across the five training folds (M0 coefficients approximately **0.79–0.88**), consistent with site recurrence already documented in RC6, **not independent evidence**. The habitat wetland coefficient was positive in all five training fits (approximately 0.55–0.96), but its direction is **exploratory**: those training fits share data and the primary held-out incremental benefit is not established. Do not elevate coefficient signs into a universal biological mechanism.

## Strict same-sample JRC prior-month water secondary
- **883 focal placement groups, 291 routes** had all ten source JRC stations valid; **28.31%** of groups had >=5-percentage-point among-station water fraction spread. These pass predeclared M2 estimability gates.
- Same-sample M1−M0: **+0.001939** (descriptive).
- Additional JRC model M2−M1: **−0.0000741 per focal group**; physical-route bootstrap **95% interval −0.0004534 to +0.0002898**. No supported incremental predictive value of previous-month satellite-visible surface water.
- Five heldout fold training estimates for the water coefficient are small/mixed in sign (about −0.077 to +0.191); do not interpret as proof that actual temporary breeding-water availability is unimportant.

## Biological meaning and limits
**The supported new statement is restricted:** In this post-hoc NAAMP placement sample, broad retrospective annual mapped wetland/open-water cover and a monthly *visible* water proxy did **not demonstrate a dependable out-of-route gain beyond strictly prior local acoustic history** when spatial allocation was conditioned on `k`. Historical acoustic use of physical sites is a competitive predictor for later expression. A slow physical-site template might encode persistent habitat suitability, demography, local detectability and breeding-ground familiarity; no unique cause is identified.

This does **not** say that rainfall is causal, vegetation irrelevant, frogs migrate among stops, site fidelity is individual memory, or that all sites call at once. Satellite data (30m monthly) are especially weak for small, short-lived or vegetated/shaded breeding pools. Roadside route sampling, acoustic detection, season-dependent image observation completeness and use of retrospectively constructed NLCD maps all limit inference. The previous frogcs conditional concentration residual is a separate statistical endpoint: **M3 residual structure has not been rerun here**, so do not claim that the original residual has been eliminated or survived all environmental controls.

## Decision for further research
Do **not** respecify habitat radius, set response-dependent thresholds or iterate new weather windows to chase significance in the same NAAMP dataset. The highest-value next discriminating evidence would be spatially distributed, *event-dated local wetland inundation / water depth* together with frog calls and fine-scale vegetation structure, or an independent frog monitoring programme with those covariates. Consider a descriptive spatial history × habitat mediation simulation only if independently prespecified; do not promote post-hoc exploratory differences as confirmatory.
