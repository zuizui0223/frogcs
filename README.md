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

**Rainfall-associated frog chorus activation shows higher-order spatial coherence and species-specific site recurrence**

Primary files:

- `paper/manuscript_pulse_template_v0_3.md` — current integrated manuscript
- `paper/manuscript_pulse_template_v0_2.md` — superseded integrated draft retained for audit
- `paper/supporting_information_pulse_template_v0_1.md`
- `revision/INTEGRATED_RESULTS_V0_1.json` — durable numeric synthesis for manuscript/figures
- `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_1.md`
- `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_2.md` — current gap/novelty/ecology/scale map
- `revision/HIGHER_ORDER_CHORUS_COHERENCE_SYNTHESIS_V0_2.md` — current scientific synthesis + stop rule
- `revision/TARGETED_LITERATURE_GAP_AUDIT_V0_1.md`
- `revision/FIGURE_REBUILD_SPEC_V0_1.md`
- `revision/PULSE_TEMPLATE_FIGURE_DATA_V0_1.json` — canonical figure inputs
- `revision/build_pulse_template_figures.py` — reproducible renderer
- `figures_pulse_template/` — canonical generated SVG/PNG figures

The frozen RC11 manuscript remains available as `paper/manuscript.md` and is not overwritten.

## Result in one paragraph

Across 4,236 matched wetter–drier NAAMP comparisons, recent-rain conditions were associated with expansion of the behaviourally active frog community, but the strongest result is not richness itself. Much of the CallingIndex increase came from previously silent species × site cells switching directly into overlapping or full chorus states. Recruited taxa showed excess participation at third-and-later sites, and exact within-pair conditioning on both recruited-taxon number and total incidence still showed greater within-taxon concentration toward the survey closer to rain (**β = 0.244, 95% CI 0.147–0.340**). The same result persisted with the same observer at the same physical sites, survived route-cross-fitted species-specific rainfall responses, strictly-prior species × SiteID history, dry-state persistence and the pre-existing held-out rain × history gate, and was not driven by one taxon or one state. Strong wet-state chorusing also preferentially reappeared at physical sites where that same taxon had chorused strongly before. The integrated interpretation is therefore **higher-order route-scale spatial coherence expressed on a recurrent species × site chorus template**, with the lower-level biological generator unresolved.

## Core evidence hierarchy

1. **Chorus-state switching** — 65.3% of CallingIndex slope from 0→positive activation; 87.1% of activation from 0→CI2/3; direct 0→CI3 positive and observer/site robust.
2. **Spatial depth** — excess begins at third-and-later occupied sites; 97.3% of that coefficient is carried by CI2/3.
3. **Exact higher-order coherence** — after exactly fixing target-new taxon number and total incidence within pair and direction, rain advantage still predicts excess within-taxon concentration.
4. **Robustness/falsification** — same-observer + same-SiteID, cross-fit species response, strictly-prior site history, dry persistence and the final held-out rain × history gate all fail to reproduce the higher-order concentration.
5. **Historical placement** — within the same pair and taxon, previously strong physical sites preferentially host later wet-state strong chorusing; the targeting strengthens toward the survey closer to rain.
6. **Breadth** — higher-order contributions are diffuse across taxa and all 21 leave-one-state-out estimates retain positive 95% confidence intervals, while state-specific effects remain heterogeneous.

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
