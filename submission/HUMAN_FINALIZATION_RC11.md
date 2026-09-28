# Human finalization guide — JAE RC11

RC11 scientific content is frozen and machine-validated. The remaining submission blockers are administrative metadata, not scientific analyses.

## Already complete

- anonymous main manuscript: `MANUSCRIPT_JAE_V1_3.md` / generated DOCX
- anonymous Supporting Information: `SUPPORTING_INFORMATION_JAE_RC11_V0_1.md` / generated DOCX
- figures and legends
- cover letter
- novelty audit and reviewer attack matrix
- RC11 story freeze
- same-observer reviewer robustness
- JAE word-count / abstract / anonymity checks
- scientific submission bundle manifest

## Human-only fields still required

- final author names and order
- full affiliation addresses
- corresponding-author details
- CRediT contributions if applicable
- funding and acknowledgements
- Conflict of Interest statement
- Statement on Inclusion
- all-author and relevant-institution approval
- originality/legal confirmations
- archive license and final archive DOI when required

## Private metadata workflow

The repository supports rendering private submission metadata from the GitHub Actions secret `JAE_SUBMISSION_METADATA_YAML`. The RC11 private-metadata bundle should be run only after that secret is populated with the final approved author metadata.

Until then, use the RC11 scientific bundle as the canonical review package. Do not insert identifying author information into the anonymous manuscript or Supporting Information.
