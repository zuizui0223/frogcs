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

This draft PR modifies **operational audit notes, manuscript/cover-letter wording, and Supporting Information Word table-rendering/QA only**. First, five repetitive Introduction phrases were shortened by 60 whitespace-delimited words, restoring the 8,000-word internal manuscript safety target (8,034 → 7,974). A second purely narrative alignment on 2026-10-16 reframed Abstract points 1 and 5 and the Discussion Conclusion around **one spatial-unit question** (with Q1 state change and Q3 recurrent-site placement supporting the focal Q2), and aligned the anonymous cover letter. It leaves all frozen quantitative endpoints, Materials and Methods, Results, references, figures, figure legends and SI unchanged. Latest draft counts: **7,989 manuscript words, 317 abstract words, 403 cover-letter words**. [Full single-question claim/wording ledger](RC6_CENTRAL_QUESTION_AND_CONCLUSION_ALIGNMENT_2026-10-16.md). No internal or journal word-count limit was relaxed.
The pre-existing pull-request trigger on
`.github/workflows/pulse_template_submission_pipeline.yml` rebuilds and checks
the anonymous submission package. **No biological analysis scripts, figure inputs,
numerical results or source NAAMP data were modified.**

### 2026-10-16: actual SI DOCX table bug corrected

Independent inspection of [artifact 12022169722](https://github.com/zuizui0223/frogcs/actions/runs/38846066120/artifacts/12022169722)
found **14 Markdown table blocks (136 pipe lines) in the original SI source but
zero Word tables in the generated Supporting_Information.docx**. All table
headers, separators and content were merely printed as pipe-delimited paragraphs.

Draft-only formatting fix:
- `scripts/submission/build_jae_anonymous_docx.py` now converts all SI Markdown
  grids to **genuine editable Word tables**, with cell word-wrap, repeated shaded
  header rows and row-splitting safeguards. Source SI Markdown bytes and all
  scientific interpretations remain unchanged; main manuscript has no tables.
- `scripts/submission/check_anonymous_si_tables.py` and both JAE workflow paths
  fail closed unless each of **14 tables / 122 actual data+header rows** retains
  identical original cell text and repeat-header markup.
- [SUCCESS workflow run 38854693187](https://github.com/zuizui0223/frogcs/actions/runs/38854693187):
  `table_count=14`, `total_table_rows=122`,
  `all_cells_exact_after_inline_markdown_cleanup=True`,
  `markdown_pipe_rows_in_word_paragraphs=0`.
- New audited [anonymous ZIP artifact 12026612177](https://github.com/zuizui0223/frogcs/actions/runs/38854693187/artifacts/12026612177):
  `sha256:dc736146b3599c16672f15dfa8b9089d95d339110d1c59244616d9df1c35f2d5`.
  The outer ZIP and every SHA256SUMS entry were independently verified. SI DOCX
  renders as 64 A4 pages with readable headers and no text falling outside the
  printable content bounds in LibreOffice PDF layout inspection.

This is a substantive **submission-format fix**, not a change to any frozen
acoustic estimate, comparison population, significance test or biological claim.

### Acceptance checks

- Full JAE pipeline finishes **SUCCESS**.
- Run SHA references the PR's test merge and the audited `main` source.
- New anonymous package has anonymous manuscript, SI, 5 figures, 400-word
  cover letter, and the reviewer-code archive.
- New manuscript count (including title page) still respects current JAE
  Research Article limit of 8,500 words; abstract ≤350; 8 alphabetized
  keywords; double-spacing and continuous line numbering.
- Compare output files against prior artifact. Expected changes: introduction/Abstract/Discussion wording, cover-letter opening, audit/specification contents and **true SI Word table formatting only**; **not** original frozen scientific results, Methods, Results, Markdown SI source or figures.
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
