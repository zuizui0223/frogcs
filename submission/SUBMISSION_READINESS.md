# RC4 JAE submission readiness

## Current canonical scientific package

- manuscript: `paper/manuscript.md`
- Supporting Information: `paper/supporting_information.md`
- title page template: `paper/title_page.template.md`
- figures: `figures_pulse_template/`
- numerical synthesis: `revision/INTEGRATED_RESULTS_V0_3.json`
- evidence ledger: `revision/EVIDENCE_CLAIM_LEDGER_V0_1.md`
- evidence hierarchy: `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_3.md`
- gap/claim map: `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_4.md`
- literature novelty lock: `revision/TARGETED_LITERATURE_GAP_AUDIT_V0_2.md`
- scientific stop rule: `revision/MULTISITE_CHORUS_COHERENCE_SYNTHESIS_V0_2.md`
- release receipt: `submission/RC4_RELEASE_RECEIPT.md`

Historical manuscript drafts are retained in Git history and frozen release branches rather than duplicated in the canonical tree.

## JAE initial-submission checks

- [x] Research Article target
- [x] anonymized main-manuscript track
- [x] numbered English abstract
- [x] abstract ≤350 words — **349**
- [x] ≤8 alphabetized keywords — **8**
- [x] main manuscript below 8,500 words — approximately **6,455**
- [x] separate Supporting Information
- [x] continuous line numbering and double-spaced anonymous DOCX validated
- [x] five reproducible main figures
- [x] data/archive statement present
- [x] anonymous scientific submission bundle builds successfully
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

No further same-data mechanism search is authorized for RC4.

Permitted remaining work:
- non-substantive copy-editing;
- private human metadata completion;
- archive/license/DOI finalization;
- prospective WFTS execution only after its response-blind eligibility gate passes.

## RC4 claim safeguards

- [x] main inferential spine is restricted to state switching → within-taxon multi-site dependence → recurrent species × site placement
- [x] FrogID, RC11 matrix allocation, exact N,K, raw recurrence, route topology and failed mechanism screens are routed to SI
- [x] principal comparator contains cross-fit species response + strictly-prior physical-site history + dry persistence + magnitude matching
- [x] title/public framing uses within-taxon multi-site organization / dependence structure, not higher-order interaction terminology
- [x] manuscript states cross-fitting is not independent confirmation
- [x] manuscript states no untouched NAAMP confirmation partition remains
- [x] Wisconsin lies outside the 21-state NAAMP discovery sample
- [x] WFTS outcome interpretation is frozen as support / informative non-replication of a half-discovery effect / inconclusive non-PASS

## Release authority

Current:
- release: `release/jae-multisite-rc4`
- submission: `submission/jae-multisite-v4`
- validated scientific source: `bfcd5bcaaf08e9b35aa8684a6ed2e10bbe1d0beb`
- release receipt commit: `2b31c7b4363374110c8fb6098a2c0492f2e4c8e0`

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

## Prospective external confirmation

WFTS real-data authority:
- `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_2.md`
- `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_5.md`
- `scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py`

No WFTS response outcome was inspected to create the current support/informative/inconclusive rule.

## Revision-stage note

A graphical abstract should be prepared only if required at revision stage; it is not part of the present initial-submission scientific bundle.
