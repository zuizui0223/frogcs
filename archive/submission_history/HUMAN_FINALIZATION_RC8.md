# RC8 human finalization — one-file handoff

This is the only remaining submission-stage input path for the JAE RC8 package.

**Do not commit completed personal metadata to this public repository.**

Use:
- template: `submission/SUBMISSION_METADATA_TEMPLATE_V0_5.yml`
- renderer/validator: `scripts/render_submission_metadata.py`
- initial bundle: `.github/workflows/initial_submission_bundle.yml`
- final archive bundle: `.github/workflows/final_submission_bundle.yml`

## 1. Fill one private YAML file

Copy `submission/SUBMISSION_METADATA_TEMPLATE_V0_5.yml` to a private local file and replace all required placeholders.

Required before **initial submission**:

### Authors
For every author:
- final author order;
- given names;
- family names;
- display name;
- affiliation IDs;
- ORCID if available;
- contribution roles if there is more than one author.

JAE requires an Author Contributions statement for multi-author submissions. CRediT terms are accepted.

### Affiliations
For every affiliation:
- institution;
- department, if applicable;
- institutional postal address;
- city;
- country.

### Corresponding author
- author order number;
- e-mail;
- full postal address.

### Funding and acknowledgements
- funding source(s) and grant number(s), or explicitly `None`;
- acknowledgements, or explicitly `None`.

### Conflict of Interest
Give a complete statement. If there is no conflict, state that explicitly rather than leaving the field blank.

### Statement on Inclusion
This is required during JAE submission.

Because this project is a secondary analysis of existing North American monitoring data, the statement should truthfully describe:
- whether there was any new local data collection (there was not in RC8);
- whether scientists or stakeholders based in the study region contributed intellectually;
- how regional literature and contextual interpretation were considered;
- any limitation in regional representation that should be disclosed.

Do not claim collaboration or stakeholder engagement that did not occur.

### Submission confirmations
All six fields must be set to `true` before strict initial rendering:
- `all_authors_approve_submission`;
- `relevant_institutions_approve_submission`;
- `all_entitled_authors_included`;
- `not_under_consideration_elsewhere`;
- `work_original_and_acknowledged`;
- `legal_requirements_confirmed`.

These correspond to confirmations requested by the current JAE submission guidance.

## 2. Validate locally before uploading the secret

Run:

```bash
python scripts/render_submission_metadata.py \
  --metadata /PRIVATE/PATH/rc8_submission_metadata.yml \
  --strict \
  --stage initial \
  --outdir build/submission-metadata-check
```

A successful run produces:
- `JAE_TITLE_PAGE_FINAL.md`;
- `JAE_PORTAL_FIELDS.json`;
- `SUBMISSION_METADATA_VALIDATION.json`;
- `CITATION.cff`;
- `ZENODO_METADATA_FINAL.json`;
- `ARCHIVE_REFERENCE.txt`.

For the initial stage, repository license and archive DOI may remain unresolved. All author/contact/submission-confirmation fields must resolve.

## 3. Store the completed YAML as a private Actions secret

Create/update repository secret:

`JAE_SUBMISSION_METADATA_YAML`

Its value should be the full contents of the completed private YAML file.

The initial-submission workflow reads this secret at runtime and does not require committing the private metadata file.

## 4. Build the initial-submission bundle

Run the workflow:

**frogcs initial JAE submission bundle (RC8)**

It will:
1. run the frozen RC8 scientific-package audit;
2. validate the private metadata in strict initial mode;
3. render the title page and portal fields;
4. build the anonymous v1.0 main DOCX and RC8 SI DOCX;
5. assemble the RC8 initial-submission bundle;
6. write SHA-256 hashes for the bundle.

The manuscript/SI remain anonymous; identifying information is kept on the separate rendered title page.

## 5. Archive/final stage

After the reproducibility archive has a final DOI and license, run:

**frogcs final JAE submission bundle (RC8)**

Supply the published archive DOI as the workflow input. Archive-stage validation additionally requires:
- repository license;
- archive DOI.

The workflow inserts the DOI into the Data Availability statement and renders the final archive metadata/CITATION surfaces.

## Current non-human authority

Scientific/content inputs are already frozen:
- `MANUSCRIPT_JAE_V1_0.md`;
- `SUPPORTING_INFORMATION_JAE_RC8_V0_1.md`;
- `submission/COVER_LETTER_JAE_V0_10.md`;
- `figures_ecology_v1_0/`;
- `submission/RC8_STORY_FREEZE_V0_1.json`.

Do not edit scientific endpoints while completing human finalization.
