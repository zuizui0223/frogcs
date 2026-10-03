# RC5 release receipt

## Release identity

- release ref: `release/jae-multisite-rc5`
- submission ref: `submission/jae-multisite-v5`
- validated scientific source: `0dbc3b3724d428763c6176fcff939c0492c651d9`
- candidate lineage: `candidate/jae-multisite-rc5`
- manuscript: `paper/manuscript.md`
- Supporting Information: `paper/supporting_information.md`
- title: **Rainfall-associated frog chorus activation reveals recurrent within-taxon multi-site organization**

RC5 is the post-RC4 integrated candidate after the explicitly reopened and reclosed 2026-10-03 exploratory mechanism chain. It does not alter the RC4 principal comparator or its numerical result. It clarifies the ecological question, adds explicitly post-hoc structural diagnostics, foregrounds the monitoring consequence, and corrects the descriptive paired-data volume using the canonical pair constructor.

## Ecological question frozen in RC5

The reader-facing paper is organized around three natural-history questions:

1. **State change:** does recent-rain mainly amplify existing calling, or switch silent species × sites into substantial chorus?
2. **Spatial unit:** when a taxon becomes active, do route stops behave independently, or is activity organized across separated locations?
3. **Place selection:** when activity becomes spatially deep, is it uniform across the route, or preferentially expressed at recurrent taxon-specific chorus locations?

The preferred synthesis is:

> **On favourable nights, frog reproductive acoustic activity is organized at an intermediate spatial scale: broader than independent wetland responses, but more selective than a uniform route-wide switch. Spatially deep activity preferentially involves recurrent taxon-specific chorus locations.**

The shorthand “fast gate × slow template” is not the title-level or main reader-facing claim.

## Principal numerical evidence retained from RC4

- matched NAAMP comparisons: **4,236**
- routes: **585**
- states: **21**
- strictly-prior-history principal subset: **2,916**
- observed within-taxon concentration coefficient: **1.6503**
- principal comparator prediction: **1.3535**
- conditional residual: **0.2969**
- null residual 95% interval: **−0.1319 to 0.1187**
- plus-one upper-tail P: **0.000999**
- held-out rain × history prediction: **1.3323**
- historical strong-site targeting: **β = 0.1511**
- rain-selective full-chorus targeting: **β = 0.02449**

## Post-RC4 structural refinement

All items below are explicitly post-hoc exploratory NAAMP analyses.

- flexible measured weather removed only **11.4%** of the existing concentration residual;
- species-specific 72-h ERA5 rainfall amount removed only **6.5%** on the same weather-eligible sample;
- bounded residual dependence among dry-route-silent taxa was **rho_b = 0.285**;
- near stop-number lags 1–3: **0.296**;
- far lags 7–9: **0.272**;
- route-bootstrap near−far difference: **0.0247**, 95% CI **0.0101–0.0398**;
- a cross-fitted uniform species-night scalar shift reproduced concentration but overpredicted near/far dependence at about **0.475**;
- among **409** deep k≥4 clusters, exact-k placement preferentially overlapped strictly-prior strong-chorus SiteIDs (**β = 0.0266, P = 0.0020**);
- the direct deep−shallow contrast (**Δβ = 0.0297, P = 0.0210**) remains in Results/SI and is not an Abstract headline.

These diagnostics constrain spatial form but do not identify a unique hydrological, demographic, physiological or social mechanism.

## Monitoring implication

Post-hoc representative activation-model diagnostics showed:

- pair-clustered SE exceeded IID in **38/39** eligible taxa;
- median pair-cluster/IID SE ratio: **1.61×**;
- pooled route clustering increased the rainfall-effect SE **2.69×**.

This is not a reanalysis of published occupancy-trend estimators. It supports the narrower conclusion that ten acoustic stops need not provide ten independent pieces of behavioural-state information.

## Canonical data-volume reconciliation

Raw public NAAMP source:

- Runs.csv: **21,934** rows
- Stops.csv: **219,340** rows
- Counts.csv: **337,848** positive calling records
- three core files: **33.48 MB** uncompressed

Current eligible subset:

- **7,848** standardized ten-stop survey runs
- **78,480** stop visits
- **115,638** positive run × stop × taxon records

The actual 4,236 matched comparisons, verified by the manuscript's canonical `build_runs + pair_runs` functions, use:

- **6,074 unique survey runs**
- **60,740 stop visits**
- **88,737 positive run × stop × taxon records**
- **53 positive taxon labels**

Canonical RunID-set SHA256:
`a1ae266d8e87599a4b19d0eb0cded5f4ec82ef177909456efdbfbe97aa7cdff2`

ERA5 72-h rainfall coverage:

- **7,559** weather-linked runs
- **544,248** sampled run-hour precipitation values
- **2,835 / 2,916** principal-history pairs

Authority:
- `audit/NAAMP_CANONICAL_PAIR_VOLUME_CHECK_V0_1.json`
- `audit/NAAMP_DATA_VOLUME_AUDIT_RECEIPT_V0_1.json`

## Main/SI routing frozen in RC5

Main:
1. silence → strong-chorus state switching;
2. deeper-than-expected multi-site tail;
3. principal species-response + prior-site-history comparator;
4. held-out rain × history sensitivity;
5. recurrent taxon-specific physical-site targeting;
6. broad but heterogeneous taxonomic/geographic support;
7. concise post-hoc monitoring implication.

SI/defence layer:
- RC11 matrix-allocation analyses;
- uniform/persistence-only nulls;
- exact N,K diagnostic;
- raw recurrence;
- route topology;
- FrogID directional evidence;
- trait/context and activation-geometry falsifications;
- flexible-weather and 72-h-rain common-cause falsification;
- bounded residual dependence and near/far diagnostics;
- observer/detection/calibration/stop-night hotness checks;
- latent/scalar-state diagnostics;
- exact-k deep-placement and deep−shallow contrast details;
- numerical/Monte-Carlo stability audits.

## Automated validation

### Manuscript/SI QA
Run **37128665685** — **SUCCESS**

Validated scientific source:
`0dbc3b3724d428763c6176fcff939c0492c651d9`

### Anonymous scientific submission pipeline
Run **37128665645** — **SUCCESS**

Artifact:
- name: `frogcs-jae-pulse-template-scientific-submission`
- artifact ID: **11275981516**
- size: **1,005,169 bytes**
- digest: `sha256:64d3d1b4fd768d08a33481aa96084b882b6be31aeb550546688ea6e9069169c7`

### Canonical data-volume audit
Run **37128735161** — **SUCCESS**

Canonical pair-constructor reconciliation was separately verified in run **37128517668** and reproduces:
- 7,848 eligible runs;
- 4,236 pairs;
- 585 routes;
- 6,074 unique pair-side runs;
- 88,737 positive pair-side calling records.

### Prospective WFTS deep-template QA
Run **37105487275** — **SUCCESS**

The synthetic fixture correctly permits an inconclusive secondary result when the fixed informativeness gate fails; secondary classification cannot alter the frozen primary WFTS result.

## Exploration and confirmation boundary

The historical research path is documented in:
- `revision/RESEARCH_QUESTION_EVOLUTION_2026-10-03.md`

The current three-question reader-facing spine is:
- `revision/THREE_QUESTION_ECOLOGICAL_SPINE_V0_1.md`

The reopened NAAMP mechanism-analysis line is closed again under:
- `revision/NAAMP_POST_REOPENING_CLOSURE_2026-10-03.md`

No new same-data lower-level mechanism family or outcome-driven retuning is authorized.

Prospective external authority:
- `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_4.md`

No WFTS frog-response outcome was inspected to define the frozen secondary spatial prediction.

## Inferential boundary

RC5 does not claim:
- rainfall causality;
- acoustic zero = physical absence;
- literal simultaneity/synchrony among sequential stops;
- individual movement;
- individual memory or philopatry;
- occupancy/colonization change;
- spawning or reproductive success;
- exact geographic-distance decay;
- a unique lower-level mechanism;
- universal anuran generality;
- independent confirmation within NAAMP.

## Release immutability rule

After RC5 refs are created, scientific endpoints, principal comparator, reader-facing three-question spine, title-level claim, data-volume counts, main/SI routing and WFTS v0.4 interpretation rules are frozen for RC5.

Only demonstrable bug correction, non-substantive copy-editing, private human metadata completion, archive/license/DOI finalization and journal-format packaging corrections are permitted on descendant submission refs.
