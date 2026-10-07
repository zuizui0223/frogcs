# Remote-sensing hydrology mechanism closure — 2026-10-07

## Question

Can dynamic local wetland hydrology explain the established within-taxon multi-site concentration that remains after species rainfall response, strictly-prior SiteID propensity, dry-state persistence and total activation magnitude are represented?

## JRC MonthlyHistory visible open water

Primary 250-m result:
- 1,881 pairs, 366 routes, 20 states
- M0 residual = 0.174490
- M1 current-water residual = 0.182250
- fraction removed = -4.45%
- M1 residual remains above its simulated 95% upper bound

500-m sensitivity:
- 2,016 pairs, 371 routes, 20 states
- residual reduction = -0.07%
- not supported

100-m sensitivity:
- the same-sample M0 residual was already inside its null interval, so the subset is mechanism-uninformative.

JRC strong-chorus secondary:
- 1,000 informative pair x taxon clusters
- observed local-water difference at CI>=2 vs other stops = +0.000160
- permutation 95% interval = [-0.000798, +0.000831]
- P = 0.3596
- not supported.

JRC 12-month variability was coverage-inconclusive under the frozen completeness rule.

## MODIS DSWEmod partial/potential wetland

DSWEmod uses monthly 250-m DSWE classes and, unlike the JRC open-water metric, includes moderate-confidence and potential-wetland class 3 in the primary numerator.

Year 2004 was frozen as source-unavailable because the ScienceBase child TIFF is size 0 / HTTP 404 and the 2.04-GB parent ZIP does not support Range access. No frog result had been calculated before that source repair.

### 500-m primary sequence

Coverage:
- M1 current-state: 2,249 pairs, 372 routes, 19 states — gate PASS
- M3 full sequence: 1,649 pairs, 324 routes, 19 states — gate PASS

On the identical M3-complete sample:
- observed concentration beta = 2.558784
- M0 residual = 0.502156; null 95% [-0.197230, 0.224164]; P = 0.000999
- M1 current partial-wetland residual = 0.516837; null 95% [-0.210036, 0.196035]; P = 0.000999
- M2 + recent 3-month persistence residual = 0.506561; null 95% [-0.193356, 0.199021]; P = 0.000999
- M3 + 12-month hydroperiod variability residual = 0.530218; null 95% [-0.194326, 0.198577]; P = 0.000999

Residual decomposition relative to M0:
- current state: -2.92% removed
- recent persistence increment: +2.05%
- variability increment: -4.71%
- total through M3: -5.59% removed

Classification: **DSWEmod dynamic hydrology not supported as the principal concentration mechanism.**

### 250-m named sensitivity

- 2,246 pairs, 372 routes, 19 states
- M0 residual = 0.349605
- M1 residual = 0.341742
- residual removed = +2.25%
- both remain far above their null upper bounds, P = 0.000999

Thus the small positive change at 250 m is not mechanism closure and cannot replace the frozen 500-m primary.

## What this rules out

The concentration excess is not explained by the tested forms of remotely sensed surface hydrology:
- monthly visible open-water extent at 30-m Landsat/JRC scale;
- monthly partial/potential wetland fraction at 250-m MODIS DSWEmod scale;
- recent three-month persistence of partial-wetland state;
- recent twelve-month variability of partial-wetland state.

This conclusion is stronger than saying that 'weather was not enough': two distinct satellite water products and multiple temporal summaries failed under cross-fitted, same-SiteID, route-relative tests while conditioning on total activation magnitude.

## What remains open

Do not conclude that local wetland condition is irrelevant.

Still unresolved are hydrological or biological states not represented by these products:
- water depth rather than areal extent;
- water temperature;
- shallow water beneath dense/emergent vegetation;
- soil/substrate moisture;
- very small ephemeral pools below the relevant pixel/support scale;
- within-month or within-days hydrological transitions;
- demographic readiness / local abundance;
- social or behavioural state.

## Manuscript decision

Do not promote remote-sensing hydrology as the mechanism in the current paper.

The negative tests may be summarized as an additional limitation/robustness statement if space allows, but they do not justify expanding the main article around hydrology.

## Frozen DSWEmod secondaries

### Classes 1–4 sensitivity

Including the low-confidence class 4 did not rescue the mechanism:
- 2,249 pairs, 372 routes, 19 states
- M0 residual = 0.336522
- classes 1–4 M1 residual = 0.342747
- fraction removed = **-1.85%**
- both remain above the null upper 95% bound, P = 0.000999

Classification: **not supported**.

### Strong-chorus spatial bridge

Coverage:
- 1,211 informative pair × taxon clusters
- 263 routes
- 45 taxa

Observed mean DSWEmod_123 change at wet-survey CI>=2 stops minus other stops:
- observed = **-0.000441**
- permutation 95% = [-0.002297, +0.002384]
- upper-tail P = **0.646**

Classification: **not supported**.

Thus partial/potential wetland increase is not preferentially aligned with the established silence → strong-chorus spatial transition.

## Additional descriptive audit

Among 32 taxa whose current DSWEmod coefficients were estimable in both deterministic route folds, coefficient signs agreed in only 14/32. Cross-fold coefficient correlation was weak (Pearson r≈0.09; Spearman ρ≈0.08).

This is descriptive rather than a preregistered endpoint, but it gives no evidence for a nationally portable species-specific surface-hydrology sensitivity that could have been hidden by the concentration summary.

## Final closure

Do not further search JRC/DSWEmod radii, class combinations, temporal windows, or strong-chorus definitions for a favourable hydrology result.

The remaining landscape follow-up must change the biological hypothesis, not retune surface-water measurement. The next frozen line is NWI wetland-type × rainfall filtering.
