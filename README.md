# frogcs — RC4 integrated frog chorus analysis

## Current paper

**Rainfall-associated frog chorus activation reveals recurrent within-taxon multi-site organization**

Historical frozen release/submission refs:

- `release/jae-multisite-rc4`
- `submission/jae-multisite-v4`
- validated RC4 scientific source: `bfcd5bcaaf08e9b35aa8684a6ed2e10bbe1d0beb`
- release receipt: `submission/RC4_RELEASE_RECEIPT.md`

Current `main` is the **post-RC4 submission candidate** containing the explicitly post-hoc 2026-10-03 refinement and its second closure. A new release ref should be cut only after manuscript QA and the anonymous scientific-bundle pipeline both pass for the same current scientific HEAD.

RC3 and the original RC11 submission remain preserved in their historical release/submission refs; they are not duplicated in this cleaned integration tree.

**Provenance note:** RC4 remains the frozen historical release authority. Current `main` contains an explicitly post-hoc exploratory extension opened on **2026-10-03** and closed again the same day after targeted common-cause, route-night-state and historical-template tests. These additions are not independent confirmation. The closure authority is `revision/NAAMP_POST_REOPENING_CLOSURE_2026-10-03.md`; no further same-data lower-level mechanism families are authorized.

## Biological result

Across **4,236** matched wetter–drier NAAMP comparisons, recent-rain conditions are associated with rapid switching from acoustic silence into strong chorus states. The unusual spatial component is a **deeper-than-expected within-taxon multi-site tail**: marginal depths 4–10 exceed both activation nulls, whereas the second and third stops do not.

The principal ecological test uses **2,916** pairs with strictly prior physical-site history. Observed within-taxon concentration was **1.6503** versus **1.3535** under a comparator that already contained:

- route-cross-fitted taxon-specific rainfall response;
- strictly-prior species × physical-site use;
- dry-state persistence;
- matched total wet incidence.

The conditional residual was **0.2969**, outside the simulated 95% range (**−0.1319 to 0.1187**, plus-one **P = 0.000999**). A stronger held-out rain × history gate still predicted only **1.3323**.

Strong wet-state chorusing also preferentially reappeared at species-specific historically strong sites (**β = 0.1511**), and that targeting strengthened toward the survey closer to rain (**β = 0.02449**).

Post-reopening falsification showed that flexible measured weather removed only **11.4%** of the concentration residual and actual 72-h rainfall amount only **6.5%** on a common sample. A repaired bounded residual-dependence coefficient was **rho_b = 0.172** overall and **0.285** among taxa silent across the drier route (both P = 0.000999). Dependence persisted from stop-number lags 1–3 (**0.296**) to lags 7–9 (**0.272**). A cross-fitted uniform species-night scalar state reproduced concentration but overpredicted near/far dependence (~**0.475**), showing that the state is not a whole-route all-or-none switch. Among **409** deep k≥4 clusters, the non-uniform active subset aligned with strictly-prior strong-chorus SiteIDs beyond exact k and fixed q site propensity (**β = 0.0266**, P = **0.0020**).

## Data scale

The public NAAMP source release contains **21,934 run rows**, **219,340 stop rows** and **337,848 positive calling records**. Current filters retain **7,848 standardized survey nights** and **78,480 fixed-stop visits**.

The 4,236 wetter–drier comparisons are built from **6,075 unique nights**, **60,750 fixed-stop visits** and **88,743 positive species × stop calling records** across the 53 paired-analysis taxa.

Rain exposure is much lower-dimensional than the frog response:
- primary NAAMP `DaysSinceRain`: one value per eligible survey night;
- post-hoc ERA5 72-h rainfall: **7,559 run-level sums**, derived from **544,248 hourly precipitation values** (72 per run);
- ERA5 coverage: **2,835/2,916** principal-history pairs (97.2%).

Full counting and caveats:
- `revision/DATA_VOLUME_AUDIT_2026-10-03.md`

## Main ecological interpretation

The discovery is not simply that frogs call more after rain.

The ecological question is **what spatial unit organizes reproductive acoustic activity on favourable nights**. The NAAMP pattern falls between two simple extremes: route stops do not behave as fully independent local responses, but a taxon also does not switch uniformly across the whole route. Instead, route-spanning activity is spatially selective and is disproportionately re-expressed at recurrent taxon-specific chorus locations.

The general hypothesis is:

> Environmental pulses may reveal how behavioural activity is distributed across persistent spatial structure that is difficult to see when animals are inactive.

This is a conceptual generalization from the NAAMP system, not a universal law or an identified lower-level mechanism.

## Main text versus Supporting Information

The main paper is organized around three ecological questions:

1. **state change** — amplification versus silence→strong-chorus switching;
2. **spatial unit** — independent wetland responses versus organized multi-site expression;
3. **place selection** — uniform route spread versus preferential use of recurrent taxon-specific chorus locations.

The principal comparator, held-out rain × history gate and breadth analyses answer or bound those questions.

Supporting Information contains the defence/falsification layer:

- earlier RC11 four-component matrix allocation;
- uniform and persistence-only activation nulls;
- exact N,K combinatorial diagnostic;
- raw recurrence percentages;
- route-topology corroboration;
- FrogID directional consistency;
- trait/context mechanism screens;
- activation-geometry placebo falsification;
- protocol, detection and observer sensitivities;
- post-reopening flexible-weather and 72-h-rain common-cause falsification;
- bounded species × route-night residual co-dependence;
- dry-route-silent, far-lag and same-observer dependence diagnostics;
- specieswise monitoring-uncertainty diagnostics.

## Current canonical files

- `paper/manuscript.md`
- `paper/supporting_information.md`
- `paper/title_page.template.md`
- `figures_pulse_template/`
- `provenance/CURRENT_RESULTS.json`
- `provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json`
- `revision/INTEGRATED_RESULTS_V0_3.json`
- `revision/EVIDENCE_CLAIM_LEDGER_V0_1.md`
- `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_3.md`
- `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_4.md`
- `revision/THREE_QUESTION_ECOLOGICAL_SPINE_V0_1.md`
- `revision/RESEARCH_QUESTION_EVOLUTION_2026-10-03.md`
- `revision/TARGETED_LITERATURE_GAP_AUDIT_V0_3.md`
- `revision/MULTISITE_CHORUS_COHERENCE_SYNTHESIS_V0_2.md`
- `submission/SUBMISSION_READINESS.md`
- `submission/RC4_RELEASE_RECEIPT.md`

Historical manuscript drafts are retained in Git history and frozen release branches rather than duplicated in the current tree.

## Reproducibility and QA

Current automated checks:

- `.github/workflows/pulse_template_manuscript_qa.yml` — manuscript/SI routing, wording and JAE limits;
- `.github/workflows/build_pulse_template_figures.yml` — deterministic five-figure rebuild;
- `.github/workflows/pulse_template_submission_pipeline.yml` — anonymous DOCX, formatting/anonymity audit and submission bundle;
- `.github/workflows/wfts_daymet_code_qa.yml` — prospective weather adapter QA;
- `.github/workflows/wfts_confirmatory_code_qa.yml` — prospective external-confirmation code QA.

The original RC11 analysis scripts under `scripts/naamp/` remain because they support the baseline and reviewer-defence analyses.

Post-freeze analyses that generated the integrated multi-site result remain auditable on their frozen `exploration/*` branches. The final contracts/scripts needed for the RC4 claim have also been selectively restored here; the full exploration history is intentionally not duplicated.

## Prospective external confirmation

Wisconsin Frog and Toad Survey (WFTS) is the first external candidate.

Important boundaries:

- Wisconsin is not one of the 21 NAAMP discovery states;
- response-blind structural eligibility must pass before frog outcomes are loaded;
- the primary endpoint/comparator is frozen;
- the real-data authority is `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_4.md`;
- the primary implementation is `scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py`;
- after the primary result is frozen, a separately frozen secondary sequence tests Daymet common-environment sufficiency, bounded route-night dependence, far-lag persistence and clustered uncertainty under `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_4.md`;
- secondary results cannot rescue, downgrade or retune the primary WFTS classification.
- v0.4 additionally freezes exact-k deep historical-template alignment and the deep-versus-shallow coupling contrast before WFTS frog outcomes.

A non-PASS is classified prospectively as either:

- `informative_nonreplication_of_half_discovery_effect`, or
- `inconclusive_nonpass`.

This prevents a low-precision non-significant result from being mislabeled as biological non-replication.

## Inferential boundaries

The paper concerns **observed reproductive acoustic activity**.

It does not establish:

- rainfall causality;
- acoustic zero = biological absence;
- literal synchrony among sequential route stops;
- movement among sites;
- individual memory or philopatry;
- occupancy/colonization change;
- spawning or reproductive success;
- a unique lower-level mechanism;
- universal anuran generality.

The integrated NAAMP result remains post-opening and exploratory at manuscript level. Prospective external confirmation remains the decisive next test.
