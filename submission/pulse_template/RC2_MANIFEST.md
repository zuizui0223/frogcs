# Integrated release candidate RC2

**Scientific release branch:** `release/jae-higher-order-rc2`  
**Submission candidate branch:** `submission/jae-higher-order-v2`  
**Frozen RC2 commit:** `726873b8a8063f661c2b8cfc34b533c4e44f5207`

## Why RC2 supersedes RC1

RC2 does **not** change the scientific manuscript, Supporting Information, figures or integrated results relative to RC1.

It adds/fixes submission and archive tooling:

- higher-order-specific Zenodo description;
- manuscript-matched citation/archive keywords;
- dummy-metadata renderer smoke test;
- fail-closed archive pipeline;
- archive/readiness documentation.

RC1 remains preserved as the first integrated scientific freeze.

## Validation

Manuscript QA workflow: **PASS**

Submission workflow run: `36786816335`  
Submission artifact: `frogcs-jae-pulse-template-scientific-submission`  
Artifact ID: `11130495524`  
Artifact size: **679,821 bytes**  
Artifact digest: `sha256:c9d3522a6388ca9eac0780fb040f57f905b5c6fecb0c03bbdb6ad745a462edc2`

The submission pipeline passed:

- integrated manuscript QA;
- dummy private-metadata renderer smoke test;
- anonymous manuscript/SI DOCX build;
- JAE formatting and anonymity checks;
- five-figure validation;
- anonymous scientific bundle assembly;
- SHA256 manifest generation;
- artifact upload.

## Scientific authority

RC2 freezes the integrated higher-order chorus paper:

- `paper/manuscript_pulse_template_v0_3.md`
- `paper/supporting_information_pulse_template_v0_1.md`
- canonical five-figure set under `figures_pulse_template/`
- `revision/INTEGRATED_RESULTS_V0_1.json`
- `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_2.md`
- `revision/HIGHER_ORDER_CHORUS_COHERENCE_SYNTHESIS_V0_2.md`

## Remaining human-only requirements

RC2 can be submitted scientifically, but the private initial-submission bundle still requires:

- final author order;
- affiliations;
- corresponding-author contact;
- CRediT roles where applicable;
- funding/acknowledgements;
- Conflict of Interest;
- Statement on Inclusion;
- approval confirmations.

Archive stage additionally requires:

- deliberately chosen repository license and actual `LICENSE`/`LICENSE.md`;
- persistent archive DOI.

No further same-data mechanism exploration is authorized on RC2.
