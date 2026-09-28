# Private JAE metadata setup

The final submission workflow is designed so that names, postal address and email do **not** need to be committed to this public repository.

## Canonical source

Copy:

`submission/SUBMISSION_METADATA_TEMPLATE_V0_7.yml`

Fill every human field locally.

Before use, confirm:

- author order;
- affiliations;
- corresponding-author contact details;
- CRediT roles;
- acknowledgements and funding;
- Conflict of Interest statement;
- Statement on inclusion;
- all three approval booleans;
- repository/archive license.

The archive DOI can be left blank in the secret because the final workflow overwrites it with the DOI entered at dispatch time.

## Validate locally

Install PyYAML and run:

`python scripts/submission/render_submission_metadata.py --metadata <your-private-file.yml> --strict --outdir build/submission-metadata`

Strict mode refuses unresolved placeholders, false approval declarations, invalid author/affiliation references, an invalid DOI, missing license, or missing required JAE submission statements.

## Store as a GitHub Actions secret

Create a repository Actions secret named:

`JAE_SUBMISSION_METADATA_YAML`

Paste the complete YAML contents as the secret value.

Do not commit the completed private YAML to a public branch.

## Build the private-metadata initial-submission bundle

After populating `JAE_SUBMISSION_METADATA_YAML`, run:

**Actions → frogcs initial JAE submission bundle → Run workflow**

The active initial-submission workflow:

1. materializes the private metadata only inside the temporary runner;
2. validates required human submission fields in strict mode;
3. renders the title page and portal-field summary;
4. rebuilds the anonymous manuscript and Supporting Information DOCX files;
5. assembles generic journal-facing filenames plus a separate internal audit folder;
6. creates SHA-256 checksums and uploads one bundle artifact.

The archive DOI may remain blank for the initial double-anonymized submission. DOI insertion and public archive finalization should be done only when the archive is actually minted.

The secret contents are not intentionally printed to logs.
