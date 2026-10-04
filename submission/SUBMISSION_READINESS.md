# RC5 JAE submission readiness

## Current canonical scientific package

- manuscript: `paper/manuscript.md`
- Supporting Information: `paper/supporting_information.md`
- title page template: `paper/title_page.template.md`
- figures: `figures_pulse_template/`
- numerical synthesis: `revision/INTEGRATED_RESULTS_V0_3.json`
- evidence ledger: `revision/EVIDENCE_CLAIM_LEDGER_V0_1.md`
- evidence hierarchy: `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_3.md`
- gap/claim map: `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_4.md`
- literature novelty lock: `revision/TARGETED_LITERATURE_GAP_AUDIT_V0_3.md`
- closest-prior-study audit: `revision/CLOSEST_PRIOR_STUDIES_AUDIT_V0_1.md`
- scientific stop rule: `revision/MULTISITE_CHORUS_COHERENCE_SYNTHESIS_V0_2.md`
- release receipt: `submission/RC5_RELEASE_RECEIPT.md`

Historical manuscript drafts are retained in Git history and frozen release branches rather than duplicated in the canonical tree.

## JAE initial-submission checks

- [x] Research Article target
- [x] anonymized main-manuscript track
- [x] numbered English abstract
- [x] abstract ≤350 words — **307**
- [x] ≤8 alphabetized keywords — **8**
- [x] main manuscript below 8,500 words — current whitespace count **7,899**
- [x] separate Supporting Information
- [x] continuous line numbering and double-spaced anonymous DOCX validated
- [x] five reproducible main figures
- [x] data/archive statement present
- [x] historical RC4 anonymous scientific submission bundle builds successfully
- [x] current RC5 anonymous scientific submission bundle builds successfully — run **37128665645**, artifact **11275981516**
- [ ] final authors/order
- [ ] final affiliations
- [ ] corresponding-author details
- [ ] CRediT roles
- [ ] funding/acknowledgements
- [ ] Conflict of Interest
- [ ] Statement on Inclusion
- [ ] repository license
- [ ] persistent archive DOI
- [ ] final author/institutional approvals

## Scientific stop

The original same-data stop was explicitly reopened on **2026-10-03** for a finite post-hoc falsification chain and is now **closed again** under `revision/NAAMP_POST_REOPENING_CLOSURE_2026-10-03.md`.

No new NAAMP lower-level mechanism family or outcome-driven retuning is authorized.

Permitted remaining work:
- correction of demonstrable bugs, with affected claims re-audited if endpoints change;
- deterministic reproducibility and previously frozen numerical/implementation QA;
- non-substantive copy-editing, figures and metadata;
- archive/license/DOI finalization;
- optional prospective WFTS execution under `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_4.md` **only if external replication is explicitly reopened**; it is not required for RC5 submission.

**WFTS is not a submission gate for RC5.** The present paper is supported by the NAAMP discovery, robustness, falsification and breadth evidence already frozen in the canonical package. External confirmation is a future test of transferability, not missing evidence required to submit the current manuscript.

## Current claim safeguards

- [x] main inferential spine is restricted to state switching → intermediate spatial organization across separated stops → preferential expression at recurrent taxon-specific chorus locations
- [x] FrogID, RC11 matrix allocation, exact N,K, raw recurrence, route topology and failed mechanism screens are routed to SI
- [x] principal comparator contains cross-fit species response + strictly-prior physical-site history + dry persistence + magnitude matching
- [x] title/public framing uses within-taxon multi-site organization / dependence structure, not higher-order interaction terminology
- [x] manuscript states cross-fitting is not independent confirmation
- [x] manuscript states no untouched NAAMP confirmation partition remains
- [x] Wisconsin lies outside the 21-state NAAMP discovery sample
- [x] WFTS outcome interpretation is frozen as support / informative non-replication of a half-discovery effect / inconclusive non-PASS

## Release authority

Current validated RC5 scientific source:
- validated scientific source: `0dbc3b3724d428763c6176fcff939c0492c651d9`
- manuscript QA: run **37128665685** — PASS
- anonymous scientific bundle: run **37128665645** — PASS
- artifact ID: **11275981516**
- artifact digest: `sha256:64d3d1b4fd768d08a33481aa96084b882b6be31aeb550546688ea6e9069169c7`
- release receipt: `submission/RC5_RELEASE_RECEIPT.md`

RC5 refs:
- `release/jae-multisite-rc5`
- `submission/jae-multisite-v5`

Historical RC4 remains preserved:
- `release/jae-multisite-rc4`
- `submission/jae-multisite-v4`

Do not use the pre-existing `release/jae-v1-rc5`; that branch belongs to an older frog-chorus synchrony line.

Previous RC3 remains preserved at:
- `release/jae-multisite-rc3`
- `submission/jae-multisite-v3`

Original RC11 remains preserved at its frozen release/submission refs.

## RC5 automated validation

| Check | Run | Status |
|---|---:|---|
| manuscript/SI routing + JAE limits | **37128665685** | PASS |
| anonymous scientific submission pipeline | **37128665645** | PASS |
| canonical NAAMP data-volume audit | **37128735161** | PASS |
| canonical pair-volume reconciliation | **37128517668** | PASS |
| WFTS prospective deep-template QA | **37105487275** | PASS |

RC5 scientific-bundle artifact:
- name: `frogcs-jae-pulse-template-scientific-submission`
- artifact ID: **11275981516**
- size: **1,005,169 bytes**
- digest: `sha256:64d3d1b4fd768d08a33481aa96084b882b6be31aeb550546688ea6e9069169c7`

The private metadata bundle remains intentionally pending until final human metadata are supplied.

## Prospective external confirmation — future, non-blocking

WFTS real-data authority:
- `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_4.md`
- `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_5.md`
- `scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py`
- `revision/WFTS_PROSPECTIVE_DEEP_TEMPLATE_ALIGNMENT_V0_1.json`
- `scripts/wfts/run_wfts_deep_template_alignment_v0_1.py`

The v0.4 authority leaves the primary replication unchanged and prospectively adds the NAAMP-derived secondary prediction that exact-k historical-template coupling is stronger for deep k≥4 than shallow k=1–3 activation. Synthetic QA for that secondary path has passed. No WFTS frog-response outcome was inspected to create or test these rules.

## Revision-stage note

A graphical abstract should be prepared only if required at revision stage; it is not part of the present initial-submission scientific bundle.
