# Private JAE metadata setup

The final submission workflow is designed so that names, postal address and email do **not** need to be committed to this public repository.

## Canonical source

Copy:

`submission/SUBMISSION_METADATA_TEMPLATE_V0_2.yml`

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

`python scripts/render_submission_metadata.py --metadata <your-private-file.yml> --strict --outdir build/submission-metadata`

Strict mode refuses unresolved placeholders, false approval declarations, invalid author/affiliation references, an invalid DOI, missing license, or missing required JAE submission statements.

## Store as a GitHub Actions secret

Create a repository Actions secret named:

`JAE_SUBMISSION_METADATA_YAML`

Paste the complete YAML contents as the secret value.

Do not commit the completed private YAML to a public branch.

## Final DOI workflow

After the archive DOI is minted, run:

**Actions → frogcs final JAE submission bundle → Run workflow**

Enter the published DOI.

The workflow then:

1. materializes the private metadata only inside the temporary runner;
2. inserts the real DOI into that private metadata;
3. validates all human submission fields in strict mode;
4. generates the final JAE title page, Zenodo metadata, CITATION.cff, archive citation and portal-field summary;
5. inserts the DOI into a generated copy of the manuscript Data Availability section;
6. reruns the scientific manuscript guard;
7. regenerates the anonymous DOCX;
8. regenerates and verifies both figures;
9. creates SHA-256 checksums;
10. uploads one final submission artifact.

The secret contents are not intentionally printed to logs.
