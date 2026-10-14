# Hydric state × site history: recovered evidence and inference boundary (2026-10-14)

**Status:** POST-HOC EVIDENCE AUDIT ONLY. Not a new prospective test, and not an amendment to the frozen Journal of Animal Ecology submission. The main branch and manuscript must not be changed on the strength of this audit.

## Question

Can the existing NAAMP results distinguish broad hydric activation from where taxon-specific strong choruses are re-expressed, and do hydric state and historical site use act additively or interactively?

The stronger causal reading ("rain does not matter; wet soil causes calling" or "soil wets historical sites first") is **not** established by the archived tests.

## Provenance and measurement

- Submission main commit reviewed: `0871da0c97d97e2a20156e75fda738d708c82883` (2026-10-06). Remains untouched.
- September 30 outcomes were recovered from completed **GitHub Actions job logs**, not from the filenames or the branch names alone.
- Predictor: Earthmover public **ERA5** `single/temporal` `swvl1` (soil layer 1, 0–7 cm; volumetric water, m³/m³), at the survey midpoint and the nearest **0.25° grid cell** to the route centroid. **Not ERA5-Land (~9 km)** and **not stop-scale local soil moisture**. `swvl2` was secondary.
- Contrast: swvl1 at the wetter-according-to-rain-recency survey minus swvl1 at the drier survey, z-standardized. The typical spatial support is tens of km; identical grid values may apply to many route stops.
- NAAMP uses operational taxon codes, including species complexes. Counts of 53 taxa must not be paraphrased as 53 independently verified biological species or independent phylogenetic replicates.

## Original results (coefficients use each archived model's units)

| Study and role | Sample | Key result | Decision under frozen rules |
|---|---|---|---|
| Soil moisture cue | 4,108 matched pairs; 564 routes | swvl1 change -> `strong_new_score` β=1.57279, CI [0.92286, 2.22273]; 72-hour rainfall-amount increment β=-0.13524, CI [-0.62657, 0.35609] | swvl1 positive; residual rain72 amount not supported |
| Same observer + stable SiteID | 3,021 pairs; 482 routes | soil β=1.62376, CI [0.82432, 2.42320] | swvl1 association persists |
| Spatial depth: route-new **strong** third+ | 4,045 pairs; 563 routes | soil β=0.26132, CI [0.10748, 0.41516] | positive |
| Spatial depth: route-new taxa count | same | soil β=0.10075, CI [0.03804, 0.16346] | positive; **not depth-exclusive** |
| Spatial depth: second-stop incidence | same | soil β=0.09958, CI [0.05016, 0.14901] | positive |
| Prior strong SiteID targeting, soil gate | 1,260 informative pair × taxon groups; 271 routes; 43 taxa | prior strong β=0.15079 [0.12949, 0.17208]; swvl1 × prior strong β=0.01019 [-0.00884, 0.02921] | recurrence positive; **gate interaction unsupported** |
| Joint prior-strong breadth + swvl1 -> third+ depth | 1,927 pair × recruited-taxon groups; 325 routes; 44 taxa | breadth β=0.62678 [0.48087, 0.77268]; soil β=0.13691 [0.03638, 0.23745]; interaction β=0.07289 [-0.02011, 0.16589] | **additive_two_axis**, not interaction |
| Same-observer subset of joint model | 1,472 groups; 278 routes; 43 taxa | interaction β=0.11190 [0.02032, 0.20347] | secondary sensitivity positive; **cannot override failed primary interaction** |
| State vs change | 4,045 pairs; 563 routes | wet-state β=2.28634; dry-state β=-2.61212; equal/opposite restriction P=0.216; dry coefficient=0 restriction P=1.42e-6 | **change_sufficient** *under these predeclared tests*, not proof of perfect equivalence |
| Rain × soil-wetting-sign discordance | 4,108 pairs; 564 routes | interaction β=0.19196 [-1.44632, 1.83025], P=0.818 | interaction unsupported |

### NAAMP-domain generality

- The exploratory generality audit found positive soil coefficients in the 2001–2008 **refit** (β=1.54991 [0.91150, 2.18832]) and the 2009–2015 **refit** (β=1.63651 [0.71967, 2.55336]).
- Deterministic disjoint-route subsamples and leave-one-state-out refits were also classified as supportive.
- **These are fit-stability and split-sample checks, not prospective future-year prediction:** each period was fitted with its own data, and no untouched independent external monitoring programme confirmed the effect.
- `swvl1` change and 72-hour precipitation contrast correlated (~0.598); the latter becoming nonsignificant conditional on swvl1 does not establish causal mediation or that rainfall has no other role.

## Two different ecological outcomes must stay separate

1. **Activation magnitude / spatial breadth:** route-new taxa count, strong acoustic activation, number of listening stops at which a newly active taxon calls. Route-level swvl1 changes are associated with several of these outcomes. No direct organism-level hydration is observed.
2. **Conditional allocation / recurring locations:** where calls occur **given a total response**, and whether prior strong species × SiteID locations are preferentially re-expressed. Strong historical targeting is supported; broad soil moisture × local-history amplification of that targeting is **not**.

The original JAE focal residual is a regression- and null-model-conditioned within-taxon concentration coefficient, **not** a raw independent concentration measure available for each species × route. A future species × route decomposition must use observation-level residuals or a proper hierarchical likelihood; it must not mechanically assign portions of the global coefficient to individual taxa/routes and fit those as noiseless endpoints.

## What these results cannot identify

- Causality: rainfall vs shallow-soil wetness vs unmeasured weather/season/pond hydroperiod; original data are observational and paired across survey runs.
- Fine-scale within-route wetness: ERA5 at route centroid does **not** measure 300-m wetland-edge moisture or differences among the ten stops.
- Adults moving from one terrestrial source population across wetlands; breeding success; spawning; abundance; philopatry or individual memory.
- Temporal sequence of sites becoming active: NAAMP ten-stop surveys are sequential snapshots, not continuous synchronized measurements.
- A true soil × historical-site interaction: two predeclared primary tests did not support it, notwithstanding one positive secondary subset.
- Independent validation from opportunistic recording locations alone.

## Auditable original run evidence

- [Swvl1 cue / rain72 adjusted, success, run 36665173015](https://github.com/zuizui0223/frogcs/actions/runs/36665173015).
- [Strong spatial depth, run 36666203384](https://github.com/zuizui0223/frogcs/actions/runs/36666203384).
- [Historical-site targeting interaction, run 36665528476](https://github.com/zuizui0223/frogcs/actions/runs/36665528476).
- [Joint soil + template depth, run 36666554909](https://github.com/zuizui0223/frogcs/actions/runs/36666554909).
- [State vs change, run 36666790776](https://github.com/zuizui0223/frogcs/actions/runs/36666790776).
- [Rain/soil discordance, run 36668721820](https://github.com/zuizui0223/frogcs/actions/runs/36668721820).
- [Within-NAAMP generality, run 36668353782](https://github.com/zuizui0223/frogcs/actions/runs/36668353782).
- [Survey-protocol sensitivity, run 36668480340](https://github.com/zuizui0223/frogcs/actions/runs/36668480340).

This ledger is meant to prevent the best exploratory result from being lost **and** prevent a non-supported interaction from becoming the next post-hoc story.

## Main-branch and evidence lock

Do **not** merge these claims into the submission paper, use them to reopen its frozen endpoint, or label new work on the same NAAMP rows an independent confirmation. The scientific next step is the separate design in `research/STATE_HISTORY_LANDSCAPE_TEST_PLAN_V0_1.md`.
