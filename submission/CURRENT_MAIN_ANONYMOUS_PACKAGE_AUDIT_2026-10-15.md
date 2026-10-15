# Journal of Animal Ecology — current-main anonymous package audit, 2026-10-15

**Purpose:** trigger the existing read-only JAE submission workflow on a draft
PR to verify the latest source on `main`, WITHOUT merging any scientific
changes, overwriting the previously pinned successful bundle, requesting new
WFTS records, or reopening the NAAMP/landscape hypotheses.

## Why the 2026-10-06 artifact cannot automatically serve as the latest source

The successful anonymous bundle attached to
[workflow run 37458881761](https://github.com/zuizui0223/frogcs/actions/runs/37458881761)
(artifact 11410907633, digest
`sha256:aa76a41a97058e63ba96845cfc7586363efbc5700dc1623ca5076fac486b54ba`)
was produced from scientific source `e5eb94885346a1c0c3247a14eed0c847d3c3d775`.
It was still present and unexpired when inspected on 2026-10-15.

The current `main` is `0871da0c97d97e2a20156e75fda738d708c82883`,
five commits later. Direct Git-blob comparison found changes to:

1. `paper/manuscript.md`: Abstract point 5 adds the monitoring-uncertainty
   finding; Figure 3 legend adds a comparability caution. **Both are
   presentation of previously recorded results, not re-estimation.**
2. `provenance/CURRENT_RESULTS.json` and
   `revision/INTEGRATED_RESULTS_V0_3.json`: environmental literature audit
   enlarged without new NAAMP outcome analysis.
3. `provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json`: updated references
   to the environmental audit and prospective study.
4. `scripts/submission/build_anonymous_reviewer_bundle.py`: includes
   additional frozen audit/specification files.

Therefore the older **successful** artifact is *not byte-equivalent to what the
current `main` submission workflow would package*. It is not acceptable to
claim unchanged bytes solely because the numerical endpoint is unchanged.

## Audit-only draft PR with minimal copy-edit

This draft PR modifies **the present audit note and five short, purely verbal cuts in the manuscript Introduction (−60 whitespace-delimited words)**. The frozen numerical endpoint, Abstract, Results, Discussion, references and figure legends remain unchanged by this copy-edit. The internal manuscript limit was found to be **8,000 words**, against the latest source count **8,034**; Introduction-only deduplication leaves **7,974** words and does not weaken the internal QA threshold.
The pre-existing pull-request trigger on
`.github/workflows/pulse_template_submission_pipeline.yml` is intended
to rebuild/QA the current main manuscript and reviewer-code bundle.
All scientific, formatting and anonymization scripts remain untouched.

### Acceptance checks

- Full JAE pipeline finishes **SUCCESS**.
- Run SHA references the PR's test merge and the audited `main` source.
- New anonymous package has anonymous manuscript, SI, 5 figures, 400-word
  cover letter, and the reviewer-code archive.
- New manuscript count (including title page) still respects current JAE
  Research Article limit of 8,500 words; abstract ≤350; 8 alphabetized
  keywords; double-spacing and continuous line numbering.
- Compare output files against prior artifact. Expected changes: two
  manuscript text passages plus audit/specification contents, not original
  frozen scientific results.
- Keep **both** artifact records and disclose which exact bundle was used
  for any actual submission.

### Explicit non-authorized actions

- Do not merge the draft audit PR merely to trigger a workflow.
- Do not submit to ScholarOne without separately confirmed author identity,
  author order, corresponding author, CRediT, funding/acknowledgments,
  conflicts, Inclusion statement, and submission approvals.
- Do not infer author identity or contribution from GitHub or account history.
- Do not treat an archive DOI as required before the initial submission;
  complete final archival license/DOI before publication.
- Do not reopen WFTS (specified-not-pursued) or NAAMP landscape experiments.
- Do not promote post-2026-10-06 2,422-pair exploratory geometry studies to
  the original RC6 manuscript.

**Reference authorities:** `submission/FINAL_INITIAL_SUBMISSION_RECEIPT_2026-10-06.md`,
`submission/SUBMISSION_READINESS.md`, `revision/WFTS_NOT_PURSUED_2026-10-05.md`,
`revision/LANDSCAPE_LINES_CLOSED_2026-10-05.md`.
