# RC4 clean-main integration receipt

## Purpose

This receipt records the cleaned integration of the validated RC4 scientific package onto the minimal RC11-era `main` tree.

The goal is **not** to merge the entire 313-commit post-freeze development history into `main`. Historical drafts, intermediate mechanisms and superseded specifications remain recoverable through Git history and frozen release/submission branches.

## Canonical RC4 state integrated here

- manuscript: `paper/manuscript.md`
- Supporting Information: `paper/supporting_information.md`
- title page template: `paper/title_page.template.md`
- five reproducible figure pairs: `figures_pulse_template/`
- canonical current results: `provenance/CURRENT_RESULTS.json`
- canonical analysis specification map: `provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json`
- versioned numerical synthesis: `revision/INTEGRATED_RESULTS_V0_3.json`
- evidence/claim ledger: `revision/EVIDENCE_CLAIM_LEDGER_V0_1.md`
- current evidence hierarchy: `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_3.md`
- novelty/gap map: `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_4.md`
- literature novelty lock: `revision/TARGETED_LITERATURE_GAP_AUDIT_V0_2.md`
- synthesis/stop rule: `revision/MULTISITE_CHORUS_COHERENCE_SYNTHESIS_V0_2.md`
- current WFTS prospective authority/specification and v0.5 implementation
- current submission cover letter, metadata template and readiness record

## Historical clutter intentionally not duplicated

The canonical tree does not re-add:
- manuscript v0.1–v0.4 copies;
- SI v0.1–v0.2 copies;
- earlier WFTS analysis implementations v0.1–v0.4;
- RC1–RC3 development manifests;
- the full post-opening exploration tree;
- obsolete RC11 contents of `CURRENT_RESULTS` / `CURRENT_ANALYSIS_SPECIFICATIONS` (the canonical paths are recreated with RC4 contents);
- obsolete RC11 submission/reproduction workflows.

Those materials remain in frozen refs and Git history.

## Restored post-freeze reproducibility core

Only final contract/receipt/script sets required to audit the RC4 claim were restored under `exploration/`.

Current restored set:
- 13 final analysis scripts;
- associated frozen contracts and available receipts;
- principal species-response + prior-site-history comparator;
- held-out rain × history gate;
- same-observer/site multi-site robustness;
- direct full-chorus activation;
- spatial-depth decomposition;
- exact N,K diagnostic;
- historical-site targeting;
- rain-selective targeting;
- taxonomic breadth;
- geographic breadth.

Static dependency smoke passed with:
- **13** scripts compiled;
- **26** local module references resolved;
- **8** explicit contract references resolved.

## Clean-integration validation

| Check | Run | Result |
|---|---:|---|
| manuscript/SI routing + JAE limits | 36819376056 | PASS |
| deterministic figure rebuild | 36818984683 | PASS |
| WFTS Daymet adapter | 36818980721 | PASS |
| WFTS v0.5 confirmatory code | 36818948605 | PASS |
| canonical anonymous submission bundle | 36819400689 | PASS |
| restored-analysis dependency smoke | 36819594549 | PASS |

Canonical clean-bundle artifact:
- name: `frogcs-jae-pulse-template-scientific-submission`
- artifact ID: `11142458770`
- digest: `sha256:32d0ff1ab9e59e1f95ccd25bf642dd6eda9b28a69b52ef1c62a59346ed6a93fd`

## Release provenance

RC4 scientific source:
- `bfcd5bcaaf08e9b35aa8684a6ed2e10bbe1d0beb`

RC4 frozen release receipt commit:
- `2b31c7b4363374110c8fb6098a2c0492f2e4c8e0`

Frozen refs:
- `release/jae-multisite-rc4`
- `submission/jae-multisite-v4`

The clean-main integration changes repository canonicalization, not scientific endpoints or numerical conclusions.

## Main-merge boundary

A merge of this clean integration is allowed to:
- replace canonical paper/SI/title-page files with RC4;
- replace obsolete RC11 canonical QA/submission machinery with RC4 QA;
- add the final RC4 reproducibility core;
- add prospective WFTS confirmation machinery.

It does **not** authorize:
- new same-data mechanism exploration;
- changing the principal comparator;
- changing main/SI claim routing;
- strengthening the manuscript beyond the frozen dependence-structure framing;
- changing the prospective WFTS decision rule after response access.
