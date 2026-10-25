# NPS GLKN two-way fixed-effect comparison — explicitly post-hoc specification v0.1
Date: 2026-10-25.

**Status:** Additional NPS diagnostic fixed *after* reading the prior-site main (+0.4642) and weak-vs-strong (+0.3889) results. It is NOT independent confirmatory replication. Separate from the RC6 frozen Journal of Animal Ecology manuscript.

## Question

Does strictly earlier-year same-taxon strong chorus history still predict later strong activity **among taxa within exactly the same site × current year**, when we also control each species' **park × current year** propensity?

This is stricter for generic common-site confounding than the earlier NPS model that controlled prior other-taxon station hotness and broad hydroperiod classes; it still cannot distinguish conspecific attraction from *species-specific site suitability* such as emergent-plant architecture × species or slowly persistent demographic communities.

## Pinned source and data contract

- NPS 2016–2023 acoustic data, DOI 10.57830/2320505; original CSV SHA256 `b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2`.
- Reuse `fetch_csv`, `build_yearly`, `strict_prior_panel`, `informative_groups` in `research/scripts/nps_glkn_strict_history.py`. Keep the **same 1,815 park×site×taxon×year rows** and primary binary outcome annual maximum ManualCIV ≥2. Other observation/effort covariates must use only the target calendar year or strictly past years, not future. No plant/fish data in NPS.
- Add **two simultaneous sets of absorbed intercepts**: park × species × current year, and park × physical station × current year. The latter absorbs any **site-year common effects** such as generic site wetness, annual vegetative habitat state, broad waterbody type, common sound-recording context.
- Explanatory `own_prior_strong` uses earlier years only, so no same-year outcome leakage. The adjusted specification adds log(current manually scored species recordings), log(strictly prior recordings), prior years observed, `other_prior_strong_fraction` and an indicator of unobserved other-taxon history. Fixed hydroperiod broad class is absorbed by site×year FE; it must not be added again.
- Fit a two-way within-projected *linear probability* slope using deterministic alternating projection, checking numerical convergence and effective rank. Additional nuisance terms with exactly zero independent variation can be dropped with full disclosure, never drop the focal history predictor.
- For uncertainty, compute conservative diagnostic one-way cluster-robust standard errors by (a) physical station and (b) park×taxon trajectory; bootstrap is not needed if both are presented and 7 leave-one-park-out estimates also reported. These are *post-hoc* model diagnostics; no causal interpretation. Compare with same-sample one-way park×species×year FE using the exact same row-level covariates.
- Restricted comparison: only site×taxon×year observations with **any previously observed call** (CI≥1); prior CI≥2 versus prior CI=1, same two-way FE. This is a second post-readback sensitivity.
- Report all sample sizes, numbers of site×year and taxon×park×year cells, group variation, rank, convergence, year and park coverage, leave-park-out slopes, and invalid/estimability cases.

## Outcomes

**If coefficient remains positive**: historical calling signal is taxon-specific **even after shared site×year state is removed**. Species-specific microhabitat × taxon, past cohort availability, acoustic social context and differential monitoring still compete as explanations. This is not proof of plant-induced memory or wetland food-web interactions.

**If coefficient collapses**: generic site-year common wetland conditions can account for much of the prior history relationship; ecological memory interpretation should be demoted.

**If non-identifiable**: return non-estimable without inventing a coefficient.

## Separate macro ecology avenue

The openly licensed Girard, Robin & Wezel (2023) **85 fishpond** dataset (Zenodo 10.5281/zenodo.8158543) includes 134 pond records, macrophyte metrics, benthic invertebrates, net fish yield and years since last drying. It provides a distinct, *non-frog* waterbody structure/interaction benchmark. Explicitly do not present its plant–benthos correlations as effects on frog calling, or infer vegetative cause without interventions.
