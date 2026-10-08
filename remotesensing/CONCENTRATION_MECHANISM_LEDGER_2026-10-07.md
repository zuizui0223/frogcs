# Concentration-mechanism ledger — 2026-10-07

## Focal unexplained pattern

Primary endpoint:
- observed within-taxon concentration = 1.6503;
- principal comparator prediction = 1.3535;
- residual = 0.2969;
- simulated residual 95% = [-0.1319, 0.1187];
- plus-one P = .000999.

The comparator already represents:
- species-specific rainfall response;
- strictly-prior species × physical-SiteID propensity;
- dry-state persistence (a = 0.75);
- exact pair-level total wet-incidence matching.

The mechanism question is therefore not why activity increases in wet conditions, but why the added activity is allocated to the same taxa across multiple physical stops more strongly than these first-order components predict.

## Tested explanation classes

| Candidate mechanism | Direct test | Status | What is weakened |
|---|---|---|---|
| Uniform route-wide activation | Uniform activation null | Rejected | A single common route-night switch is insufficient |
| First-order species rain response | Cross-fitted species-response comparator | Included in M0 | Species-specific weather responsiveness alone is insufficient |
| Persistent local habitat/site quality | Strictly-prior species × SiteID propensity | Included in M0 | Stable site suitability alone is insufficient |
| Persistence of previously active cells | dry-state anchor a=0.75 | Included in M0 | Simple carry-over from dry-state occupancy is insufficient |
| Rain preferentially weighting historical sites | held-out rain × history gate | Rejected | Rain-selective use of recurrent sites does not close the residual |
| Exact route geometry / spatial spread | archived landscape-geometry line | Closed / non-support | Simple dispersion/fragmentation geometry is not the explanation |
| Visible monthly open-water change | JRC MonthlyHistory, 30 m | Non-support | Surface open-water extent at 100–500 m is not the principal generator |
| Partial / potential wetland state | MODIS DSWEmod classes 1–3, 250 m | Non-support | Including moderate-confidence and potential-wetland classes does not close the residual |
| Recent hydrological persistence | DSWEmod 3-month mean | Non-support | Sustained recent surface wetness does not close the residual |
| Surface-hydrology variability | DSWEmod 12-month SD | Non-support | Hydroperiod variability visible to monthly remote sensing does not close the residual |
| Surface water and strong-chorus placement | JRC and DSWEmod CI>=2 secondaries | Non-support | Remotely sensed surface-water increase does not preferentially locate strong chorus cells |
| Persistent NWI water-regime × rain filter | official NWI WATER_REGIME_NAME × rain, 2,028 pairs | **non-support, −0.18%** | Mapped hydroperiod regime did not reconstruct the concentration excess |
| NWI WETLAND_TYPE × rain filter | official nearest wetland type, same 2,028 pairs | **non-support, −1.37%** | Broad wetland class was not the missing rain-response filter |
| NWI wetland amount × rain filter | union polygon area in 500 m, 2,409 pairs | **non-support, −1.23%** | Mapped wetland area was not the missing capacity filter |
| E2 nighttime thermal filtering | MOD11A1 local night LST | **coverage-inconclusive** | Too few common-night, full-route scenes to evaluate thermal mechanism |
| E3 local vegetated/substrate moisture | Landsat C2L2 NDMI, frozen 500 m / 32 day / ≥70% QA | **formal response-blind pixel QA pending** | Final preauthorized abiotic test; no frog endpoint readback until coverage gate passes |

## Quantitative surface-hydrology closure

### JRC visible open water

250 m:
- 1,881 pairs, 366 routes, 20 states;
- M0 residual 0.17449;
- + current water residual 0.18225;
- fraction removed = -4.45%.

500 m:
- 2,016 pairs;
- fraction removed = approximately -0.07%.

Strong-chorus secondary:
- 1,000 informative pair × taxon clusters;
- P = .360.

### MODIS DSWEmod partial / potential wetland

500-m primary M3-complete sample:
- 1,649 pairs;
- 324 routes;
- 19 states.

Residual sequence:
- M0 = 0.50216;
- + current DSWEmod = 0.51684;
- + 3-month persistence = 0.50656;
- + 12-month variability = 0.53022.

Fraction removed:
- current = -2.92%;
- current + persistence + variability total = -5.59%.

Every model retained upper-tail P = .000999.

250-m current-state sensitivity:
- 2,246 pairs;
- residual reduction = +2.25%;
- residual remained far outside its null envelope.

Strong-chorus secondary:
- 1,211 clusters, 263 routes, 45 taxa;
- observed strong-minus-other DSWEmod difference = -0.000441;
- null 95% = [-0.002297, 0.002384];
- P = .646.

## What remains environmentally plausible

The negative remote-sensing results do **not** rule out wetland state in general.

They specifically weaken surface-area / partial-inundation explanations at monthly 30–250 m product support.

Remaining local environmental candidates include:
- water depth rather than water area;
- water temperature;
- soil or substrate moisture;
- small ephemeral pools below mapped support;
- inundation beneath dense canopy/emergent vegetation;
- chemistry, conductivity, pH or oxygen;
- fine-scale hydroperiod timing not represented by monthly composites.

## Non-environmental candidates that now rise in priority

NWI water-regime, type, and amount filters have also failed. Once the preauthorized E3 gate/test is classified, priority should shift toward processes that can create taxon-specific multi-site dependence without a corresponding remotely sensed surface-water pattern:

1. **demographic availability**
   - spatially structured local abundance or breeding-ready adults;
2. **latent reproductive state**
   - route-night taxon state shared across separated breeding sites;
3. **social / acoustic state dependence**
   - activation probability conditional on conspecific chorus state, not simple acoustic spillover;
4. **unmeasured taxon-specific habitat features**
   - substrate, vegetation architecture, fish/predator context, water chemistry.

## Decision rule

Do not search further remote-sensing radii, class combinations or species subsets after the closed JRC/DSWEmod results.

The NWI rain-filter suite is closed (2026-10-08). The only remaining frozen abiotic route is E3 Landsat NDMI under the separate official coverage/QA gate. Its metadata prerequisite passed (2,633 candidate pairs / 395 routes / 20 states), but that is NOT proof of pixel-level coverage. The E3 full QA run is https://github.com/zuizui0223/frogcs/actions/runs/37723985357. No new satellite indices or response-selected subsets are authorized. If E3 is unsupported or source-/coverage-inconclusive, stop abiotic endpoint searching and seek independent organism-level/local environmental data.

## 2026-10-08 follow-up: respiratory/acoustic state prediction distinction

A separate DSWEmod held-out predictor audit initially found a positive incremental 3-month-wetness gain for strong calling, but temporal training (2003, 2005–2009) to 2010–2015 validation did **not** transfer: log-loss gain = -0.003588 (95% route-bootstrap [-0.005858, -0.002186]). Therefore recent surface-water persistence must not be promoted as a temporally general predictor of reproductive readiness. This result has a different inference target from the unchanged higher-order concentration endpoint.
