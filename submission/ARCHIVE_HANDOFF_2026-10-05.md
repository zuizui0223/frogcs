# RC6 archive handoff — 2026-10-05

## Current state

The scientific package is closed. Archive finalization is the remaining repository-side step before a persistent archive DOI can be inserted into the final publication metadata. Under current JAE/BES guidance, this archive DOI is **not treated as a blocker for initial submission**; the permanent archive must be completed before publication/final acceptance processing.

As of 2026-10-05:

- the repository has **no GitHub Release object**;
- no root `LICENSE` file is present;
- no root `CITATION.cff` is present;
- `submission/metadata.template.yml` still contains author/contact placeholders;
- `repository.license` is still `[CONFIRM LICENSE]`;
- `repository.archive_doi` is empty;
- the manuscript Data Availability section correctly says that the code and derived package **will be archived in Zenodo at finalization**.

These are archive/finalization metadata gaps, not scientific-evidence gaps and not, by themselves, initial-submission blockers.

## Archive source

The archive should be built from the final closed RC6 state after the repository-status cleanup is merged.

Scientific reference point:
- validated RC6 scientific source: `ea2bea7fd9ac8856f880a7f3302e193fa19705bd`

Project-closure authorities:
- `submission/RC6_FINAL_PROJECT_CLOSURE_2026-10-05.md`
- `revision/WFTS_NOT_PURSUED_2026-10-05.md`
- `revision/LANDSCAPE_LINES_CLOSED_2026-10-05.md`

The archive may include later provenance/status cleanup provided it does not alter the frozen manuscript/SI scientific results.

## Initial submission can proceed before archive minting

The current manuscript already contains a Data Availability statement identifying the public source datasets and stating that the code/derived analysis package will be archived in Zenodo at finalization.

For initial JAE submission, the remaining blockers are author-side metadata and approvals, not the Zenodo DOI itself.

Current policy basis checked 2026-10-05:
- JAE Author Guidelines: https://besjournals.onlinelibrary.wiley.com/hub/journal/13652656/author-guidelines
- BES data archiving policy: https://besjournals.onlinelibrary.wiley.com/hub/data_archiving_policy

## Required human metadata before archive minting

Complete `submission/metadata.template.yml` outside the public repository if private contact details should remain private.

Required fields:

1. final author names and order;
2. affiliations;
3. corresponding-author email/postal address;
4. ORCID values if used;
5. CRediT roles;
6. funding/acknowledgements;
7. Conflict of Interest statement;
8. Statement on Inclusion approval;
9. repository/archive license choice;
10. final author/institutional approvals.

Do not infer or auto-fill these from repository history.

## License decision

No license is currently declared at repository root.

A license must be chosen explicitly before archive-stage metadata validation. The repository mixes code, manuscript/provenance text, figures and derived summaries, while raw third-party datasets are not redistributed. The chosen licensing scheme therefore needs author approval rather than being inferred automatically.

Once chosen:

- add the corresponding root license file(s);
- set `repository.license` in the private/final metadata YAML to the archive-facing license label;
- keep third-party source-data exclusions explicit.

## Metadata renderer already available

`scripts/submission/render_submission_metadata.py` already supports the final archive workflow.

With completed metadata it renders:

- `JAE_TITLE_PAGE_FINAL.md`;
- `ZENODO_METADATA_FINAL.json`;
- `CITATION.cff`.

At archive stage the renderer requires both:

- a non-empty repository license;
- a valid archive DOI.

Therefore the expected order is:

1. finalize authors/approvals/license;
2. create the final GitHub release/archive source;
3. create the Zenodo record and obtain the persistent DOI;
4. insert that DOI into the final metadata YAML;
5. run the archive-stage metadata renderer;
6. place the DOI in the title page/Data Availability text if required by the final journal package;
7. retain the generated Zenodo metadata and `CITATION.cff` with the archived release.

## Zenodo boundary

No Zenodo DOI has been minted from this repository yet.

Do not invent a DOI or substitute the NAAMP/FrogID source-data DOIs for the analysis-repository DOI.

The source-data DOIs remain:

- NAAMP: `10.5066/F7G44NG0`;
- FrogID description/dataset citation: `10.3897/zookeys.912.38253`.

## Submission consequence

RC6 does **not** need more NAAMP analysis, WFTS work or landscape exploration.

For **initial submission**, only author-side metadata/approval completion remains.

For **pre-publication archive finalization**, the remaining repository-side items are:

- explicit license choice;
- final release/archive creation;
- Zenodo DOI minting;
- final archive metadata/CITATION generation.

After those are supplied, the existing metadata pipeline can generate the final archive-facing title-page, Zenodo and citation files without reopening the scientific analysis.
