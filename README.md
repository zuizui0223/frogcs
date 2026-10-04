# frogcs — RC5 integrated frog chorus analysis

## Current paper

**Rainfall-associated frog chorus activation reveals recurrent within-taxon multi-site organization**

Current validated release/submission refs:

- `release/jae-multisite-rc5`
- `submission/jae-multisite-v5`
- validated RC5 scientific source: `0dbc3b3724d428763c6176fcff939c0492c651d9`
- release receipt: `submission/RC5_RELEASE_RECEIPT.md`

Historical RC4 remains preserved at:
- `release/jae-multisite-rc4`
- `submission/jae-multisite-v4`

RC3 and the original RC11 submission remain preserved in their historical release/submission refs; they are not duplicated in this cleaned integration tree.

**Provenance note:** RC5 contains an explicitly post-hoc exploratory extension opened on **2026-10-03** and closed again the same day after targeted common-cause, route-night-scale and recurrent-site tests. These additions are not independent confirmation. The closure authority is `revision/NAAMP_POST_REOPENING_CLOSURE_2026-10-03.md`; no further same-data lower-level mechanism families are authorized.

**Operational status (2026-10-04):** RC5 is complete as a NAAMP-only submission package. WFTS acquisition is **parked**. No WFTS request email is required, scheduled, or part of the RC5 submission path.

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

The 4,236 wetter–drier comparisons are built from **6,074 unique nights**, **60,740 fixed-stop visits** and **88,737 positive species × stop calling records** across the 53 paired-analysis taxa.

Rain exposure is much lower-dimensional than the frog response:
- primary NAAMP `DaysSinceRain`: one value per eligible survey night;
- post-hoc ERA5 72-h rainfall: **7,559 run-level sums**, derived from **544,248 hourly precipitation values** (72 per run);
- ERA5 coverage: **2,835/2,916** principal-history pairs (97.2%).

Full counting and caveats:
- `revision/DATA_VOLUME_AUDIT_2026-10-03.md`

## Main ecological interpretation

The discovery is not simply that frogs call more after rain.

The ecological question is not only how many local units respond to a favourable night, but **how those activations are allocated across taxa and places after first-order response has been represented**. The NAAMP pattern falls between independent local responses and a uniform route-wide switch: activity is over-concentrated within taxa and selectively re-expressed at recurrent taxon-specific chorus locations.

The general hypothesis is:

> **Short environmental pulses may affect ecological organization not only through how many local units respond, but through how activation is allocated across persistent spatial structure.**

This is a conceptual generalization from the NAAMP system, not a new statistical theorem, universal law or identified lower-level mechanism.

## Main text versus Supporting Information

The current paper is organized around **one primary endpoint**:

> conditional within-taxon multi-site concentration among taxa acoustically recruited on wetter surveys, after species-specific rainfall response, strictly prior physical-site propensity, dry-state persistence and total activation magnitude are represented.

Two biological analyses interpret that endpoint rather than competing with it as co-equal headline outcomes:

1. **state change** — whether the activity entering the endpoint is weak amplification or silence→strong-chorus switching;
2. **place selection** — whether the excess is expressed arbitrarily or preferentially at recurrent taxon-specific chorus locations.

The principal 2,916-pair comparator is the inferential centre. The held-out rain × history gate and breadth analyses bound its robustness and generality. Reader-facing authority: `revision/CURRENT_ENDPOINT_PAPER_SPINE_V0_2.md`.

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
- `revision/CURRENT_ENDPOINT_PAPER_SPINE_V0_2.md`
- `revision/NOVELTY_AND_GENERAL_PRINCIPLE_AUDIT_V0_2.md`
- `revision/CURRENT_ENDPOINT_PAPER_SPINE_V0_1.md` — superseded
- `revision/THREE_QUESTION_ECOLOGICAL_SPINE_V0_1.md` — superseded reader-facing structure retained for provenance
- `revision/RESEARCH_QUESTION_EVOLUTION_2026-10-03.md`
- `revision/TARGETED_LITERATURE_GAP_AUDIT_V0_3.md`
- `revision/MULTISITE_CHORUS_COHERENCE_SYNTHESIS_V0_2.md`
- `submission/SUBMISSION_READINESS.md`
- `submission/RC5_RELEASE_RECEIPT.md`

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

## Optional prospective external confirmation — parked

Wisconsin Frog and Toad Survey (WFTS) remains a prepared external candidate, but it is **not part of the evidence required for RC5, not a submission gate, and not a current required task**. The request/contact documents are retained only as dormant planning artifacts so that the prospective design is not lost. They should be used only if external replication is explicitly reopened later.

Important boundaries:

- Wisconsin is not one of the 21 NAAMP discovery states;
- response-blind structural eligibility must pass before frog outcomes are loaded;
- the primary endpoint/comparator is frozen;
- the real-data authority is `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_4.md`;
- the primary implementation is `scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py`;
- after the primary result is frozen, a separately frozen secondary sequence tests Daymet common-environment sufficiency, bounded route-night dependence, far-lag persistence and clustered uncertainty under `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_4.md`;
- secondary results cannot rescue, downgrade or retune the primary WFTS classification.
- v0.4 additionally freezes exact-k deep historical-template alignment and the deep-versus-shallow coupling contrast before WFTS frog outcomes.
- the authorized real-data files are byte-locked by `revision/WFTS_REAL_DATA_EXECUTION_LOCK_V0_1.json`; lock QA run **37129985326** passed.
- the receipt → schema-only → mapping freeze → weather → structural preflight → primary → secondary execution order is fixed in `revision/WFTS_REAL_DATA_EXECUTION_HANDOFF_V0_1.md`.
- the complete synthetic preflight → primary → common-environment secondary → recurrent-site secondary chain passed in run **37130556855**; the QA artifact is **11276592978**.
- fail-closed guard QA passed in run **37153969280**: insufficient structural coverage stops before response access, and any post-preflight runs/matrix byte drift is rejected.
- pre-receipt readiness is frozen in `revision/WFTS_PRE_RECEIPT_READINESS_RECEIPT_V0_1.json`.
- if this external test is explicitly reopened, there are currently **no internal pre-receipt scientific or implementation blockers**; the external dependency would be acquisition of the existing station-level WFTS export plus route/station lineage metadata.
- contact routing was reverified on 2026-10-04 and is retained in `revision/WFTS_CONTACT_ROUTE_VERIFICATION_2026-10-04.md` for possible future use; no contact is currently required.

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

The integrated NAAMP result remains post-opening and exploratory at manuscript level. Prospective external confirmation would be valuable future evidence, but it is not required to justify or submit RC5.
