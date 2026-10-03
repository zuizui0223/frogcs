# JAE submission readiness — post-RC4 main candidate

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
- release receipt: `submission/RC4_RELEASE_RECEIPT.md`

Historical manuscript drafts are retained in Git history and frozen release branches rather than duplicated in the canonical tree.

## JAE initial-submission checks

- [x] Research Article target
- [x] anonymized main-manuscript track
- [x] numbered English abstract
- [x] abstract ≤350 words — **312**
- [x] ≤8 alphabetized keywords — **8**
- [x] main manuscript below 8,500 words — current whitespace count **7,929**
- [x] separate Supporting Information
- [x] continuous line numbering and double-spaced anonymous DOCX validated
- [x] five reproducible main figures
- [x] data/archive statement present
- [x] historical RC4 anonymous scientific submission bundle builds successfully
- [ ] current post-RC4 main candidate scientific bundle — latest pipeline rerun pending after QA-safeguard restoration
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
- prospective WFTS execution under `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_4.md`.

**WFTS is not a submission gate for RC4.** The present paper is supported by the NAAMP discovery, robustness, falsification and breadth evidence already frozen in the canonical package. External confirmation is a future test of transferability, not missing evidence required to submit the current manuscript.

## Current claim safeguards

- [x] main inferential spine is restricted to state switching → deep within-taxon multi-site dependence → route-spanning but non-uniform taxon-night state → recurrent species × site template
- [x] FrogID, RC11 matrix allocation, exact N,K, raw recurrence, route topology and failed mechanism screens are routed to SI
- [x] principal comparator contains cross-fit species response + strictly-prior physical-site history + dry persistence + magnitude matching
- [x] title/public framing uses within-taxon multi-site organization / dependence structure, not higher-order interaction terminology
- [x] manuscript states cross-fitting is not independent confirmation
- [x] manuscript states no untouched NAAMP confirmation partition remains
- [x] Wisconsin lies outside the 21-state NAAMP discovery sample
- [x] WFTS outcome interpretation is frozen as support / informative non-replication of a half-discovery effect / inconclusive non-PASS

## Release authority

Historical frozen release authority:
- release: `release/jae-multisite-rc4`
- submission: `submission/jae-multisite-v4`
- validated scientific source: `bfcd5bcaaf08e9b35aa8684a6ed2e10bbe1d0beb`
- release receipt commit: `2b31c7b4363374110c8fb6098a2c0492f2e4c8e0`

Current `main` is a **post-RC4 candidate** containing the explicitly post-hoc extension and subsequent closure. Do not create a new release/submission ref until the current manuscript QA and anonymous scientific-bundle pipeline both pass on the same scientific HEAD.

Reserved next release names, to be created only after that gate:
- `release/jae-multisite-rc5`
- `submission/jae-multisite-v5`

Do not use the pre-existing `release/jae-v1-rc5`; that branch belongs to an older frog-chorus synchrony line.

Previous RC3 remains preserved at:
- `release/jae-multisite-rc3`
- `submission/jae-multisite-v3`

Original RC11 remains preserved at its frozen release/submission refs.

## Clean-integration automated validation

The canonical clean-main candidate `integration/jae-multisite-rc4-clean` has passed:

| Check | Run | Status |
|---|---:|---|
| manuscript/SI routing + JAE limits | **36819376056** | PASS |
| deterministic figure rebuild | **36818984683** | PASS |
| WFTS Daymet adapter QA | **36818980721** | PASS |
| WFTS v0.5 confirmatory-code QA | **36818948605** | PASS |
| anonymous RC4 submission pipeline | **36819400689** | PASS |
| restored RC4 analysis dependency smoke | **36819594549** | PASS |

Restored-analysis smoke coverage:
- **13** final exploration scripts compiled;
- **26** local module references resolved;
- **8** contract references resolved.

Clean scientific-bundle artifact from run 36819400689:
- name: `frogcs-jae-pulse-template-scientific-submission`
- artifact ID: `11142458770`
- size: **776,912 bytes**
- digest: `sha256:32d0ff1ab9e59e1f95ccd25bf642dd6eda9b28a69b52ef1c62a59346ed6a93fd`

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
