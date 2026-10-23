# Exact source-derived descriptive temporal Sørensen ratios — NAAMP wetland vegetation

**2026-10-23: ecology-only fallback/QA from an already-validated complete numerical aggregate, not a new route-level hypothesis test.** This file was computed directly from the original independently verified [2-site × 2-round spatial–seasonal acoustic gamma aggregate](./NAAMP_WETLAND_SPACETIME_ACOUSTIC_GAMMA_AGGREGATE_2026_10_23.json), based on the original 2,869 survey rounds /1,115 route-years/274 physical routes/20 States. It is not independent biological data, nor evidence of plant causality or animal-to-animal interactions.

## Exact expected-incidence identity and scope

Let G21 be the **physical-route-equal** expected frog acoustic taxon pool from exactly two randomly chosen physical sites in one of two survey rounds, averaged across the same source observation pairs. Let G22 be the similarly route-equal expected taxon pool from the same sites **pooled across both survey rounds**. For original source subpopulation and same two observations, mean expected shared taxon count `a=2×G21−G22`, total taxon labels unique to exactly one round `b+c=2×(G22−G21)`. The temporal Sørensen **ratio of pooled expected counts** is

`(b+c)/(2a+b+c) = (G22−G21)/G21`.

**It is NOT the mean of per-route-year Sørensen values**, NOT an independent two-sample statistical test and NOT an estimator of relative demographic turnover. One cannot derive a route-cluster interval or Simpson replacement vs nestedness without underlying taxon-by-round incidence, which the aggregate intentionally does not contain.

| Calling threshold | Habitat | G21 | G22 | Expected shared a | Expected early-only + later-only | Pooled temporal Sørensen |
|---|---|---:|---:|---:|---:|---:|
| CI≥1 | PEM | 2.31095 | 3.88583 | 0.73607 | 3.14977 | **0.68149** |
| CI≥1 | other | 2.01406 | 3.44405 | 0.58406 | 2.86000 | **0.71001** |
| CI≥2 | PEM | 1.39202 | 2.44467 | 0.33938 | 2.10529 | **0.75620** |
| CI≥2 | other | 1.20217 | 2.12594 | 0.27840 | 1.84754 | **0.76842** |

**PEM−other source descriptive pooled-ratio contrasts:** CI≥1 **-0.02852** (−2.85 percentage points); CI≥2 **-0.01222** (−1.22 percentage points). These do not prove negative or non-significant change in pair-level turnover or nestedness. The more conservative beta replacement versus nestedness analysis is separately predeclared and requires the complete underlying NWI×NAAMP route-year source.

## Provenance and blocker

Original verified source = `exploration/NAAMP_WETLAND_SPACETIME_ACOUSTIC_GAMMA_AGGREGATE_2026_10_23.json`; source Actions #39909729800 (successful immutable original artifact consistency QA). The new full route-level temporal beta analysis is `exploration/run_naamp_pem_temporal_beta_turnover_v0_1.py`. Source-free enumerative beta QA passed but the initial real-data Actions run #39916111616 failed to fetch the **non-expired** original NWI geography artifact #12278539157 due an Azure-hosted ZIP transfer error after five retries. It cannot correctly infer six source-specific route cluster P-values until this input transport is restored. No analysis result or P value is imputed.

**Limits:** source USFWS NWI 250m mapped wetland/PEM polygons are not 2001–15 live botanical plant species or temporal macrophyte structure; acoustic presence is not occupancy/fitness; an index decomposition cannot establish frog-frog competition, predator mediation, or causal ≥3-species interactions. Original frozen JAE RC6 and main are unchanged.
