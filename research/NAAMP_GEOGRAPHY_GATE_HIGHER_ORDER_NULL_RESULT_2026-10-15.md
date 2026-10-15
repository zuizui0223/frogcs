# NAAMP original high-order concentration survives exact physical SiteID source gate

**Date:** 2026-10-15  
**Scope:** geographically/source-quality restricted **reuse of the original NAAMP panel**. Post hoc sensitivity, **not** an independent ecological replication and **not** an Annual NLCD mechanism test. Frozen JAE \`main\` unchanged.

## 1. Before-reading selection and exact physical matching

Original NAAMP 2001–2015 survey metadata and source coordinates, SHA256-pinned, reproduce:
- full conventional matched design: **4,236 pairs, 585 routes, 21 states**;
- strictly prior physical-SiteID-memory population: **2,916 pairs, 439 routes, 20 states**;
- gross-geometry + exactly-ten-source-SiteID eligible routes: **2,422 matched pairs, 358 routes, 20 states**.

Additional survey-to-geometry source audit (done **without Counts.csv**):
**all 2,422/2,422 geography-eligible survey pairs have exactly the same ten physical SiteIDs as the public USGS coordinate table**. Overlap histogram: \`{"10": 2422}\`. No physical relocation/300-m positional truth is independently certified.

[Source-only all-2,422 SiteID match run](https://github.com/zuizui0223/frogcs/actions/runs/38725438609); [source-only original route and pair listing](https://github.com/zuizui0223/frogcs/actions/runs/38725438609/artifacts/11967662330).

Retained geography is not uniform by state: Kentucky retains 1/26 pairs, Indiana 124/233, Iowa 77/120, South Carolina 147/148. All 20 focal states remain, but pooled estimates do not justify universal state-level generality.

## 2. Descriptive original higher-order coefficient

[Original JAE higher-order route-cluster sensitivity](https://github.com/zuizui0223/frogcs/actions/runs/38725955346) reproduces the original observed higher-order coefficient **1.6503201354367818** using the original regressors/rain direction and archived matrix metric.

| Selection | Pairs | Routes | Higher-order β | Route-cluster 95% CI |
|---|---:|---:|---:|---|
| Original prior-site-history sample | 2,916 | 439 | 1.6503 | [0.3266, 2.9740] |
| **Exact 10 source-coordinate SiteIDs** | **2,422** | **358** | **1.7184** | **[0.1584, 3.2785]** |
| Excluded by source geography | 494 | 81 | 1.1463 | [-0.5000, 2.7925] |

This is an **observational** rain-contrast coefficient; the subgroup estimates have different state composition. No supported difference between retained and excluded populations is established.

[Archived descriptive result and coefficients](https://github.com/zuizui0223/frogcs/actions/runs/38725955346/artifacts/11968497139).

## 3. Strictly unchanged original crossfit species + historical-site null

The original \`exploration/run_naamp_higher_order_crossfit_species_history.py\` analysis was imported unchanged into the source-quality script \`research/scripts/naamp_exact_siteid_crossfit_hoc_null_v0_1.py\`:
- species-specific rain slopes trained out of route using the original hash-based fold assignments and all original training survey runs, without geographic subset retuning;
- original strictly prior species × SiteID probability matrix and dry-state persistence anchor \`ANCHOR=0.75\`;
- original \`KAPPA=2\` specification and wet total cell-probability offset calibrated to observed wet cell count;
- original \`B=1000\` Monte Carlo replicates, fixed seed \`2840223+102000\`;
- residualized rain-contrast design with temperature, day-of-year, year gap, state and run-number controls;
- regressed simulated higher-order slopes on simulated route-new-species and extra-stop slopes to obtain the **conditional excess** under the original comparator. This is the JAE-consistent null family, not the newer distinct exact-(K,N) allocation model.

All 2,916 original observed higher-order slopes were independently reproduced (β=1.6503), and the original archived full-sample null receipt is quoted below. The **restricted subset's Monte Carlo null is recomputed** at its own design, not copied from the original 2,916-pair output.

| Same original model | Original 2,916 pairs | Exact SiteID 2,422 pairs |
|---|---:|---:|
| Observed higher-order β | 1.6503 | **1.7184** |
| Null-predicted β | 1.3535 | **1.4478** |
| Conditional unexplained β | **+0.29685** | **+0.27063** |
| Null 95% residual interval | [-0.13185, +0.11871] | **[-0.14487, +0.13956]** |
| Upper-tail Monte Carlo p | 0.000999 | **0.000999** |
| Excess beyond null 95% | Yes | **Yes** |

The reported p-value is the minimum resolvable value for this finite set of 1,000 simulations; it must not be reported as zero or as a new independent confirmatory probability.

[Successful original-null run for the strict 2,422 pairs](https://github.com/zuizui0223/frogcs/actions/runs/38726385727), [original complete JSON artifact](https://github.com/zuizui0223/frogcs/actions/runs/38726385727/artifacts/11968532683).

**Result:** Higher-order within-taxon concentration conditional on lower-order species breadth and route-new species remains above the frozen species-shift + local prior-site-history + dry-persistence comparator under an independent source/geometry restriction. This is **evidence for descriptive robustness to the location-source gate**, not an explanation by any terrestrial variable.

## 4. Explicit boundaries and next decision

What this supports:
- The focal higher-order NAAMP effect is not confined to the 81 routes excluded by coordinate-source eligibility; the 358-location cohort still gives a positive observed β and positive conditional residual with the original null family.
- The source-eligible 358 routes retain all 20 focal states and the same ten geometric SiteIDs within all included pairwise surveys.
- The original JAE's unexplained concentration remains a valid **question** for terrestrial-habitat explanatory testing. No mechanism has been identified.

What it does **not** support:
- Any new causal or direct hydric/moisture inference: the original shallow ERA5 soil water is a coarse route-level environmental correlate, not a 300-m station measurement.
- Forest patch connection causes frog movement, species interactions, or synchronized chorusing.
- Independent biological replication, unique identification of a mechanism, 300-m accurate geolocation, or year-to-year station physical constancy.
- Confirmation of a C1V2 landcover/environment predictor: official raw landcover plus confidence pixels have **not** been obtained; MRLC WCS2 returned server-side time errors.

**Next admissible data action** is the already-frozen 10-site \`Delaware:210302\` source-only MRLC Viewer AOI [GeoJSON](aoi/NAAMP_Delaware_210302_source_only_C1V2_request.geojson) and original \`StopNumber->SiteID\` table [workflow artifact](https://github.com/zuizui0223/frogcs/actions/runs/38724734319/artifacts/11967790799). Verify matched 2012 Annual NLCD Collection 1.2 \`Land Cover\` and \`Land Cover Confidence\` categorical numeric GeoTIFFs, original provenance, raster CRS/pixel size and historic site precision **before** testing forest-connected pair effects against the generic same-taxon pair model.

**Status:** Keep frozen JAE submission branch untouched. Analysis executed and read-only result archived on \`research/state-history-hydric-synthesis-v1\`.
