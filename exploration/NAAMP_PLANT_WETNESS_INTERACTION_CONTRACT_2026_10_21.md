# Vegetation × historical wetness effect on frog calling-site allocation — new study contract
Date: 2026-10-21. **Separate user-directed exploratory work** beyond frozen JAE RC6.

## Biological question
Does a survey-month-inclusive three-month satellite wetness summary modify the spatial association between NWI mapped emergent wetlands and **which stops express a strong frog chorus**, after controlling for current water and static wetland availability? If it does, can that interaction explain any of the between-taxon checkerboard C-score excess while preserving marginal activity?

This hypothesis is motivated by two already-known findings but is **not an independent replication**:
1. Five NAAMP taxon units have positive cross-sectional NWI PEM associations with strong calling (BH q<0.05).
2. Pre-October 21 MODIS DSWEmod strong-chorus prediction found a positive out-of-**route** increment of three-month hydrology, but it **FAILED** 2003/2005–2009 → 2010–2015 temporal transfer (log-loss gain −0.003588, 95% CI −0.005858 to −0.002186). Do NOT describe this as a confirmed environmental-memory mechanism.

## Frozen environmental sources
- USGS NAAMP pinned Runs/Stops/Counts from ScienceBase original record; 7,848 eligible standardized 10-stop survey runs.
- Frozen full USFWS NWI coordinates/site buffer overlay from Actions **39450277196**, 5,147 retained station IDs over 501 routes; NWI PEM, mapped total wetland, woody wetland fractions within **250 m**. NWI is static/current available mapping, **not** historic plant species/cover measured at the frog-survey dates.
- Pre-existing (not retuned or re-extracted) MODIS monthly DSWEmod classes 1–3 run × physical SiteID metrics: Actions **37615425574**, artifact `naamp-dswemod-v02-reuse-result` (ID 11479971642), file `NAAMP_DSWEMOD_RUN_SITE_METRICS_V0_1.csv`. Primary *water* spatial support = frozen **500 m**, metrics `current_D_r500` and `recent_D_3m_r500`. This product can miss inundation beneath emergent vegetation, small pools, and within-month changes. Source years **2003 and 2005–2015**, excluding corrupt/unavailable 2004 before outcomes.
- Fixed current plant support = 250 m, water support = 500 m. No searches across support radii/classes/time lags.

## Source-only eligibility gate **before reading Counts outcomes**
- Valid NAAMP complete 10-stop runs with valid temperature; every stop uniquely identifies a source-validated `State×RouteNumber×SiteID` in the NWI overlay, and every run×SiteID has a DSWEmod valid current and survey-month-inclusive three-month value.
- Do not treat missing NWI or DSWEmod as absence.
- Sample must contain ≥600 complete route-runs, ≥100 routes, ≥12 states, ≥100 pre-2010 and ≥200 later years; and ≥80 runs having both within-route NWI PEM variability and positive DSWEmod recent3 value. Otherwise *coverage-inconclusive* without reading frog outcomes.
- A site is used only when station coordinates passed the pre-outcome NWI geometry exclusion (no post-hoc coordinate correction).

## Fixed response and two statistical questions

### A. Within-taxon choice of calling sites, conditional on strong activation
- Strong chorus (CI≥2) **primary**. CI≥1 descriptive secondary only.
- Each active taxon×route-run with exactly 10 observed positions contributes one **conditional fixed-k** likelihood (k strong-call stops; omit k=0 or k=10, record exclusions), which fixes each taxon's calling amount before predicting its placement.
- Fit species-specific conditional-logistic site weights in the *opposite* route fold (deterministic SHA256 State:RouteNumber from existing cross-fit code). Learn all taxa meeting **≥30 informative taxon-runs and ≥12 independent routes**; nonestimable taxa receive all-zero effects.
- Site predictors at ten stops:
  - W = mapped total wetland fraction (250m) ×10;
  - E = NWI PEM emergent fraction (250m) ×10;
  - D0 = current DSWEmod fraction (500m) ×10;
  - D3 = recent3 DSWEmod fraction (500m) ×10;
  - route D3 = mean of D3 over exactly ten site values, with no outcome dependence.
  - **interaction** E × route D3. This isolates modification of *where* strong calls appear with hydrological history without using other taxa as predictors. Route recent3 main effect is constant within the fixed-k run and is not independently estimable.
- Models on the **identical** complete-case route-runs:
  - **H0**: W + E + D0 + D3 (additive plant, current and recent wetness);
  - **H1**: H0 + E × route D3 (hydrological context-dependent expression of emergent-vegetation association).
- Fixed ridge penalty \(\lambda=3\), hard bounds \([-3,3]\) per predictor coefficient after above fixed scaling. Model training uses exact fixed-k likelihood over all \(\binom{10}{k}\) subsets.
- Primary evaluation: held-out negative log likelihood **per informative taxon-run** and H1−H0 log-score gain, route-cluster bootstrap (2,000 replicates, seed 2840274) on average taxon-run gain; evaluate within both route folds.
- Crucial temporal transfer: fit H0/H1 **only on years 2003, 2005–2009**, test in **2010–2015**, using taxa observable in the early-training sample only. Report the same H1−H0 gain on future years. Do not replace split if failed.
- Interpretation of positive cross-route, negative temporal or vice versa must remain **mixed**, not a stable mechanism.

### B. Checkerboard sufficiency
- Use **same retained strong CI≥2 survey matrices** and their frozen C-score from Actions 39436588431. Never replace the prespecified matrix eligibility after reading outcomes.
- Compare H0 and H1 as weights in a Metropolis–Hastings Curveball model with **identical observed taxon row totals and stop column totals**. Use prior weighted sampler, fixed 199 draws per matrix, burn 40×n_taxa, thin 8×n_taxa, seed 2840275. No re-selection of taxa with strongest effects.
- Calculate mean observed C-score, H0 and H1 null means, route-clustered CI for improvement H1−H0 and remaining excess. Report upper-tail plus-one MC P (minimum 1/200=0.005). Flag insufficient mixing if >20% of baseline-informative matrices yield zero C-score exploration. Two folds separately.
- For biological positive claim, require **both** route-fold held-out log-score gain CI >0 AND H1−H0 checkerboard C-score gain CI>0. To claim "explains checkerboard" additionally require H1-adjusted residual CI overlapping 0 and within the simulated 95% envelope; otherwise it is only partial.

## Strict limitations
This is a **post-hoc observational test** within an already-explored archive. A successful NWI × DSWEmod interaction would not establish aquatic plant species identity, hydrological causation, spawning, abundance, individual habitat choice, or frog–frog social interactions. DSWEmod recent3 is the mean of the **survey calendar month and the previous two months**, NOT an exposure ending strictly before the survey day. The survey-month composite may contain observations later than the frog survey and must NOT be interpreted as a causal antecedent or leak-free prospective forecast. These summaries are strongly spatially aggregated and do not measure submerged water among plant stems. Wetland NWI temporal mismatch is material. Do not modify the RC6 paper, SI, or journal submission package in this branch.

## Code and outputs
- Source-only preflight `exploration/run_naamp_plant_wetness_source_preflight_v0_1.py` (no Counts)
- Gated outcome analysis `exploration/run_naamp_plant_wetness_conditional_null_v0_1.py`
- GitHub Actions artifacts and immutable JSON result receipt. If source file hash or sample membership differs, abort rather than guess/repair.
