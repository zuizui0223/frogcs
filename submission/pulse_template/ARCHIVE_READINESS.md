# Archive readiness — integrated multi-site chorus paper

## Frozen source

- release candidate: `release/jae-multisite-rc3`
- submission candidate: `submission/jae-multisite-v3`
- both were created from the same validated integrated revision head
- scientific anonymous bundle: PASS

## Archive pipeline

Workflow:

`.github/workflows/pulse_template_archive_pipeline.yml`

Default source ref:

`release/jae-multisite-rc3`

The workflow intentionally fails closed until all archive-stage requirements are present.

## Human decisions still required

### Repository license

No repository license has been selected.

Do **not** archive until the authors deliberately choose a license and add the corresponding `LICENSE` or `LICENSE.md` file.

The archive metadata must use the same license identifier.

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
- all approval booleans set true;
- repository license;
- archive DOI.

### Archive DOI

The metadata renderer requires a syntactically valid persistent archive DOI at `--stage archive`.

## Archive outputs

When all requirements are met, the workflow generates and validates:

- `ZENODO_METADATA_FINAL.json`
- `CITATION.cff`
- `ARCHIVE_REFERENCE.txt`
- `SUBMISSION_METADATA_VALIDATION.json`
- `SOURCE_MANIFEST.json`
- selected repository license
- `SHA256SUMS.json`

The source manifest records the exact archived git commit and SHA256 digests of the central manuscript, SI, results and figure-input files.

## Important separation

Archive preparation does not modify:

- frozen original `main`;
- `release/jae-v1-rc11`;
- `submission/jae-v1`;
- integrated `release/jae-higher-order-rc1`.

Any archive-helper changes after RC1 belong on the revision track only.


## RC3 scientific distinction

RC3 changes the inferential hierarchy from RC2:
- the exchangeable exact N,K null is secondary;
- the principal comparator preserves taxon-specific rainfall response and strictly-prior SiteID history;
- public terminology is within-taxon multi-site concentration/coherence;
- independent confirmation remains outstanding and must be external.
