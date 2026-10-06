# RC6 initial-submission handoff — 2026-10-05

## Status

Final pre-submission correction receipt: `submission/FINAL_PRE_SUBMISSION_AUDIT_2026-10-05.md`

Final initial-submission receipt: `submission/FINAL_INITIAL_SUBMISSION_RECEIPT_2026-10-06.md`

The scientific and technical initial-submission package is complete.

Canonical scientific-bundle source:
- commit: `3c7677e14866f70f922ff09d2fd398d6e5d74279`
- JAE pipeline run: **37406142401**
- artifact ID: **11387327485**
- digest: `sha256:018dbab97284978ec69cb37736ba111b4b38b4f76f0c490406a0976c892c8226`

Later repository commits may update receipts or workflow triggers only; they do not alter the canonical submission inputs.

The manuscript, Supporting Information, figures and scientific endpoints are closed. A finite public-data scale validation was subsequently completed and reclosed: blocked State/time transferability supported the conditional spatial-allocation result, while a future-rain negative control limited temporal interpretation of the 72-h rainfall-amount covariate. No further NAAMP analysis, WFTS work or landscape exploration is required for initial submission.

## Technical checks

The final submission-facing packaging PR passed:

- integrated manuscript QA — **SUCCESS** within JAE pipeline run **37406142401**
- JAE submission pipeline — **SUCCESS** (run **37406142401**)
- build pulse-template figures — **SUCCESS**
- RC4 restored-analysis reproducibility smoke — **SUCCESS**
- WFTS real-data authority lock — **SUCCESS**
- WFTS frozen full-chain QA — **SUCCESS**
- WFTS fail-closed guard QA — **SUCCESS**
- WFTS confirmatory/secondary/weather/schema/route QA — **SUCCESS**

The WFTS checks are historical-design integrity checks only. WFTS is not being pursued and contributes no evidence to RC6.

## Current JAE-facing files

- anonymous manuscript: `paper/manuscript.md`
- Supporting Information: `paper/supporting_information.md`
- title-page template: `paper/title_page.template.md`
- optional anonymous cover letter: `submission/cover_letter.md`
- figures: `figures_pulse_template/`
- private human-metadata template: `submission/metadata.template.yml`
- metadata renderer: `scripts/submission/render_submission_metadata.py`
- submission readiness: `submission/SUBMISSION_READINESS.md`

## Word-count margin

Current counts before final human metadata:

- anonymous main manuscript: **7,980 words**
- current title-page template: **158 words**
- current combined count: approximately **8,138 words**
- JAE Research Article limit: **8,500 words**

Approximate remaining margin before final title-page metadata: **362 words**.

Keep final author names, affiliations, acknowledgements, contributions and other title-page additions concise enough to remain within this margin.

## Cover letter

The cover letter is optional and anonymous.

Current cover letter:
- **400 words**
- below the current **500-word** JAE limit
- contains no author-identifying information

## Anonymous reviewer-code access

The scientific submission pipeline now generates `Reviewer_Code.zip`, containing the main analysis scripts, frozen specifications, selected result receipts and deterministic figure inputs without Git history or author-identifying repository metadata. Identity tokens are scanned automatically.

Preferred review workflow:
- attach `Reviewer_Code.zip` directly as an anonymous reviewer/supplementary file in the journal submission system;
- if the journal interface requires a URL instead of a file, upload this exact ZIP to an anonymous/restricted repository service before submission;
- do **not** give reviewers the public GitHub URL containing the account name.

## Human decisions still required before initial submission

Do not infer these from Git history, email addresses, repository ownership or prior drafts.

### 1. Final authorship

Confirm:
- final author set;
- author order;
- exact display names;
- whether the submission is single-author or multi-author.

### 2. Affiliations

For each author confirm:
- department/division;
- institution;
- postal address;
- city;
- country.

### 3. Corresponding author

Confirm:
- which author is corresponding author;
- email;
- postal address.

### 4. ORCID

Optional unless otherwise required by the submission system. Use only explicitly confirmed ORCID identifiers.

### 5. Author Contributions / CRediT

Required for a multi-author manuscript.

Confirm the roles for each author. Do not infer contributions from commit history.

### 6. Funding and acknowledgements

Explicitly confirm either:
- the relevant funder/grant/acknowledgements; or
- that there is none.

The public template intentionally contains confirmation placeholders rather than assuming "None".

### 7. Conflict of Interest

Provide an explicit final Conflict of Interest statement.

### 8. Statement on Inclusion

The current draft is:

> This study is a secondary analysis of publicly released amphibian-monitoring datasets from the United States and Australia; the authors conducted no new local field sampling. We cite the monitoring programmes and dataset creators whose work made these analyses possible and interpret the results within the scope of their sampling designs. No additional local stakeholder or community engagement was undertaken for this secondary-data analysis.

All authors should approve the final wording.

### 9. Submission approvals

Confirm:
- all authors approve the submitted version;
- relevant institutions approve submission where required;
- all entitled authors are included;
- the manuscript is not under consideration elsewhere;
- the work is original and acknowledgements are complete;
- applicable legal/conservation/welfare requirements are satisfied.

## Private metadata workflow

Do **not** commit private contact details to the public repository unless intentionally public.

Recommended workflow:

1. copy `submission/metadata.template.yml` locally or store completed YAML in the existing GitHub Actions secret workflow;
2. fill only confirmed metadata;
3. run the metadata renderer with strict initial-submission validation;
4. generate the final title page and portal fields;
5. check the final combined word count remains below 8,500;
6. upload the anonymous manuscript/SI plus the separate title page in the journal system.

## Archive DOI boundary

A Zenodo/repository DOI is **not treated as an initial-submission blocker** under the current JAE/BES workflow. The manuscript already contains a Data Availability statement and identifies Zenodo as the intended final archive.

Before publication/finalization, complete:
- explicit repository/archive license choice;
- final GitHub release/archive source;
- Zenodo persistent DOI;
- final `CITATION.cff` and Zenodo metadata.

Archive instructions:
- `submission/ARCHIVE_HANDOFF_2026-10-05.md`

## Scientific stop

Do not reopen the analysis to improve the paper before submission.

Permitted work is limited to:
- demonstrable bug correction;
- deterministic reproducibility checks;
- citation/reference correction;
- non-substantive copy-editing/formatting;
- human metadata and submission form completion;
- later archive finalization.

Any future external replication or landscape study is a separate project decision, not unfinished RC6 work.
