# NAAMP spatial-dispersal POM gate — first genuine annual time-lag result

2026-10-31; run [#41210753759](https://github.com/zuizui0223/frogcs/actions/runs/41210753759) SUCCESS with 5/5 tests and true PR146 original site/source consistency checks. Old failed run #41210649500 stopped at YAML parsing (colon in an unquoted step label), fixed before real data analysis.

## Actual NAAMP acoustic result

- Source original: 4,248 monitoring sites and 63,180 completed acoustic site visits, PR146 commit c5ad81b1fb29a9bb92d742ee7004ae66a404dca9.
- Eligible for a strictly previous-calendar-year comparison of self + nearest and farthest documented *different* same-route stop, with repeated site and route-year support: **17,183 site×calendar-year outcomes, across 369 routes**.
- Weighted two-way site and route×year fixed effects, with own previous-year calling, nearest/farthest previous-year calling, current year air/noise/day-of-year covariates:
  - nearest previous calling coefficient **+0.005744**;
  - farthest previous calling coefficient **+0.002030**;
  - nearest − farthest **+0.003714**;
  - 399 route-resampled conditional score-bootstrap 95% interval **[−0.021255,+0.031107]**, includes zero.
- **Interpretation:** The source does not show a resolvable additional near-versus-far *previous-year acoustic association* after this particular statistical adjustment. This is not evidence that frog larvae/adults never disperse. NAAMP listening stops may hear more than one pond; an annual strong-call event is not colony immigration, juvenile survival or individual movement.

## Synthetic discrimination pilot on the same site-year mask

- A spatial shared-environment-without-movement model included stable site-level spatial correlation and serially correlated route×year shocks, plus previous site latent state.
- A second source-geometry model additionally imposed a **hypothetically strong 0.65 nearest-site latent coupling** with the same source annual survey counts. No wild movement rate is inferred.
- With 32 simulated source replicates per class, the prespecified nearest-minus-farthest score had **AUC 1.000**, and a 75% synthetic-training/25% holdout threshold produced **balanced accuracy 1.000**.
- This **only shows sensitivity to an artificially strong lagged coupling under two assumed source generators**. It does not rule out shared *time-varying local* environment, survey timing or adult acoustic detection as sources of similar spatial covariance in the field. AUC is a synthetic model-recovery measure, never a field mechanism posterior.

## What this rules out / does not rule out for the 96-structure plan

**Not supported:** Using this single empirical near−far temporal score as a strong source-verified observational constraint selecting a particular movement stage or migration fraction. The conditional interval spans 0, and no source observation of larvae/true migrant counts exists.

**Still reasonable:** Use whole-region-vs-route contrast and 2° spatial residual ICC as *descriptive multi-scale POM patterns*, with explicit shared-environment-only and environmental-spatial-autocorrelation nulls. Source previously measured 2° residual ICC ~0.133–0.134, route ICC ~0.369–0.371, but neither is direct movement evidence.

**Next model-recovery gate:** Evaluate weaker neighbour coupling and a **spatiotemporally structured local environmental process** with no organism movement. Inability to distinguish this environmental null from movement-like coupling means the migration axis should remain a sensitivity axis, not a posterior-selected causal mechanism.

A source-common 120-day seasonal predator +80-year finite-N dispersal simulator has NOT yet been used to generate the empirical 17,183 row annual acoustic target. In particular, the 8 synthetic ring patches and new 369 real-source routes should not be equated to actual occupied frog wetlands or directly treated as model-calibrated source geometry.

## Scientific reproducibility

- [Implementation](scripts/observed_neighbour_lag_dispersal_identifiability.py)
- [Five unit tests](scripts/test_observed_neighbour_lag_dispersal_identifiability.py)
- [Prespecified observational and synthetic-source contract](SPATIAL_DISPERSAL_NEIGHBOUR_LAG_PILOT_PROTOCOL_2026-10-31.md)
- [Verified actual source run and full 3-file result artifact](https://github.com/zuizui0223/frogcs/actions/runs/41210753759). Artifact contains observed coefficient/route-interval table, 64 simulated model recovery rows, and source receipt with original SHA256.
- Model-native PR146/148 and PR147 cohort/individual ABM are distinct mobility definitions and should not be blended without the original source-state bridge.
