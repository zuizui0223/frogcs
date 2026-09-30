# Archive readiness — integrated multi-site chorus paper

## Current authority

Current frozen integrated authority remains:

- release: `release/jae-higher-order-rc2`
- submission: `submission/jae-higher-order-v2`

RC3 scientific files are currently on:

`revision/pulse-template-synthesis-v1`

Prospective RC3 refs, to be created **only after manuscript QA, figure rendering and scientific-bundle validation pass**, are:

- `release/jae-multisite-rc3`
- `submission/jae-multisite-v3`

They are not treated as existing authority before that validation.

## RC3 scientific distinction

RC3 changes the inferential hierarchy from RC2:

- the exchangeable exact N,K null is secondary;
- the principal comparator preserves cross-fit species response + strictly-prior physical-SiteID history + dry persistence;
- public terminology is within-taxon spatial concentration / multi-site coherence;
- cross-fitting is explicitly not independent confirmation;
- no untouched NAAMP confirmation partition remains;
- a prospective external replication specification is frozen.

## Archive pipeline

Workflow:

`.github/workflows/pulse_template_archive_pipeline.yml`

The workflow is already configured for the **prospective** RC3 source:

`release/jae-multisite-rc3`

Until that branch is actually created after validation, archive execution should fail rather than silently fall back to RC2.

## Human decisions still required

### Repository license

No repository license has been selected.

Do **not** archive until the authors deliberately choose a license and add the corresponding `LICENSE` or `LICENSE.md` file.

### Private metadata secret

Populate:

`JAE_PULSE_TEMPLATE_METADATA_YAML`

using:

`submission/pulse_template/metadata.template.yml`

Archive-stage strict validation requires:
- final author names/order;
- affiliations;
- corresponding-author details;
- CRediT roles where applicable;
- funding and acknowledgements;
- Conflict of Interest;
- Statement on Inclusion;
- all approval booleans true;
- repository license;
- archive DOI.

## Archive outputs

When RC3 exists and all human requirements are met, the workflow generates:

- `ZENODO_METADATA_FINAL.json`
- `CITATION.cff`
- `ARCHIVE_REFERENCE.txt`
- `SUBMISSION_METADATA_VALIDATION.json`
- `SOURCE_MANIFEST.json`
- selected repository license
- `SHA256SUMS.json`

## Separation rule

Archive preparation does not modify:
- frozen original `main`;
- `release/jae-v1-rc11`;
- `submission/jae-v1`;
- RC1 or RC2 integrated release branches.

RC3 will become current only after its own validated release manifest is written.
