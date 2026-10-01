# Frog chorus response to rainfall — integrated revision track

## Branch status

This branch is a **post-freeze integrated revision** built from the frozen JAE RC11 submission plus explicitly versioned post-freeze mechanism analyses.

The frozen submission authority remains unchanged on:

- `main`
- commit `015a675324800f2e5ac9ab0985b080fe88adc375`
- `release/jae-v1-rc11`
- `submission/jae-v1`

Nothing in this branch retroactively converts post-freeze analyses into preregistered tests.

## Current integrated manuscript

**Rainfall-associated frog chorus activation shows within-taxon multi-site coherence and species-specific site recurrence**

Primary files:

- `paper/manuscript_pulse_template_v0_4.md` — current integrated manuscript
- `paper/manuscript_pulse_template_v0_3.md` — superseded RC2-era draft retained for audit
- `paper/supporting_information_pulse_template_v0_2.md` — current SI
- `revision/INTEGRATED_RESULTS_V0_2.json` — current numeric synthesis
- `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_2.md` — current evidence hierarchy
- `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_3.md` — current gap/novelty/ecology map
- `revision/MULTISITE_CHORUS_COHERENCE_SYNTHESIS_V0_1.md` — current synthesis + stop rule
- `revision/PROSPECTIVE_EXTERNAL_REPLICATION_SPEC_V0_1.md` — frozen external-confirmation specification
- `revision/WFTS_EXTERNAL_REPLICATION_ELIGIBILITY_V0_1.md` — outcome-blind WFTS design/data-access audit
- `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_3.md` — frozen Daymet/rainfall and confirmatory analysis implementation
- `revision/WFTS_DATA_REQUEST_TEMPLATE_V0_1.md` — outcome-blind raw-data request template
- `revision/WFTS_CANONICAL_SCHEMA_V0_1.json` — frozen canonical WFTS input schema
- `scripts/wfts/` — prospective confirmatory analysis core + synthetic QA fixture generator
- `revision/TARGETED_LITERATURE_GAP_AUDIT_V0_1.md`
- `revision/FIGURE_REBUILD_SPEC_V0_2.md`
- `revision/PULSE_TEMPLATE_FIGURE_DATA_V0_1.json` — canonical figure inputs
- `revision/build_pulse_template_figures.py` — reproducible renderer
- `figures_pulse_template/` — canonical generated SVG/PNG figures
- `submission/pulse_template/` — integrated cover letter, metadata template and submission-readiness checklist
- `.github/workflows/pulse_template_submission_pipeline.yml` — integrated anonymous/private bundle builder
- `.github/workflows/pulse_template_archive_pipeline.yml` — fail-closed archive metadata builder
- `submission/pulse_template/ARCHIVE_READINESS.md` — license/DOI/archive checklist

The frozen RC11 manuscript remains available as `paper/manuscript.md` and is not overwritten.

## Integrated release authority

Current integrated release candidate:

- `release/jae-higher-order-rc2`
- `submission/jae-higher-order-v2`
- frozen commit `726873b8a8063f661c2b8cfc34b533c4e44f5207`

RC2 includes the same scientific manuscript/results as RC1 plus corrected higher-order Zenodo/CITATION metadata tooling and a validated metadata-renderer smoke test.

Historical RC1 remains preserved at:

- `release/jae-higher-order-rc1`
- `submission/jae-higher-order-v1`

Release manifests are stored under `submission/pulse_template/`.

## Result in one paragraph

Across 4,236 matched wetter–drier NAAMP comparisons, recent-rain conditions were associated with expansion of the behaviourally active frog community, but the strongest result concerns **how multi-site activity is allocated within recruited taxa**. Most activation entered directly at overlapping/full chorus states, and the unusual spatial component emerged at third-and-later sites. The principal comparator uses 2,916 pairs with strictly prior physical-site history and combines route-cross-fitted species rainfall responses, prior species × SiteID propensity, dry-state persistence and matched total wet incidence. It predicted within-taxon concentration β = **1.353** versus **1.650 observed**; the conditional residual was 0.297 beyond the null 95% interval (−0.132 to 0.119; P = 0.000999). A held-out rain × history gate still predicted only 1.332. Strong wet-state chorusing also preferentially reappeared at species-specific physical sites with prior strong chorus (β = **0.151**), and that targeting strengthened toward the survey closer to rain (β = **0.0245**). The exact N,K-conditioned exchangeable diagnostic (β = 0.244) is retained only as a secondary combinatorial check because it does not preserve taxon-specific spatial breadth or prior site use.

## Core evidence hierarchy

1. **Chorus-state switching** — 65.3% of CallingIndex slope from 0→positive activation; 87.1% of activation from 0→CI2/3; direct 0→CI3 positive and observer/site robust.
2. **Spatial depth** — the second occupied site is ordinary; the excess begins at third-and-later sites and is 97.3% CI2/3.
3. **Principal spatial comparator** — cross-fit species response + strictly-prior SiteID history + dry persistence predicts 1.353 versus 1.650 observed (P = 0.000999).
4. **Stronger sensitivity** — adding a held-out rain × history gate predicts 1.332 and remains insufficient (P = 0.000999).
5. **Historical placement** — prior strong physical SiteIDs preferentially host later wet strong chorus within the same pair and taxon; targeting strengthens toward rain.
6. **Breadth with heterogeneity** — contributions are diffuse across taxa and robust to state omission, while state-specific effects vary strongly.
7. **Confirmation status** — cross-fitting prevents route leakage but is not independent confirmation; no untouched NAAMP confirmation partition remains. Prospective external replication is required.

## Inferential boundaries

The study concerns **acoustic reproductive activity**, not abundance, occupancy, colonization, spawning or reproductive success.

Do not infer:

- literal simultaneity or synchrony among route stops;
- individual movement among sites;
- individual memory or philopatry as the mechanism;
- hydrological connectivity or social facilitation;
- causal rainfall forcing;
- worldwide or universal anuran response;
- identification of a unique lower-level generator.

## Provenance classes

The integrated paper distinguishes:

- **frozen RC11 evidence**;
- **post-freeze analyses fixed before their own endpoint readback**;
- **descriptive/non-gating diagnostics**.

The post-freeze mechanism escalation is stopped. No new trait fishing, relaxed gates, same-data site-specific rainfall coefficients or new lower-level mechanism families are authorized for this integrated track.

## Repository layout

- `paper/` — frozen RC11 and integrated revision manuscripts/SI
- `revision/` — gap audit, evidence hierarchy and figure specification for the integrated paper
- `scripts/naamp/` — frozen NAAMP analysis base
- `scripts/frogid/` — FrogID consistency analysis
- `exploration/` — versioned post-freeze contracts, scripts and receipts retained for auditability
- `provenance/` — frozen RC11 specifications/results
- `submission/` — frozen RC11 submission package

## Frozen submission reproducibility

For reproduction of the original RC11 submission, use `main`, not this revision branch:

- `provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json`
- `provenance/CURRENT_RESULTS.json`
- `.github/workflows/reproduce_current_results.yml`
- `.github/workflows/submission_pipeline.yml`

Historical development remains available in release/history branches and ordinary Git history.


## Prospective external confirmation status

First candidate: **Wisconsin Frog and Toad Survey (WFTS)**

Current status:

**DESIGN_ELIGIBLE / DATA_ACCESS_PENDING**

Official design documentation confirms permanent 10-station traditional routes, repeated annual survey periods, five-minute listening and the compatible CI1–3 calling scale. Wisconsin is external to the 21-state discovery dataset, although WFTS is historically linked to USGS/NAAMP protocol development.

No WFTS concentration outcome has been inspected.

The weather exposure, canonical schema, route folds, coverage gate, principal comparator, simulation count and decision rule are frozen before response-data access.
