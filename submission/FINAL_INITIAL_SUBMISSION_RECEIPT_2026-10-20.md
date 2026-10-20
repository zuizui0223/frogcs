# Current initial-submission receipt — 2026-10-20

## Authority and scope

This receipt **supersedes** `submission/FINAL_INITIAL_SUBMISSION_RECEIPT_2026-10-06.md` for the **current initial-submission file bundle**. The 2026-10-06 receipt remains preserved as historical provenance.

The 2026-10-20 change is a **copy-edit to restore the manuscript 8,000-word safety guard** after the October 6 abstract uncertainty polish. It changes no underlying observations, numerical results, focal endpoints, comparator, evidence hierarchy, or inferential boundaries.

- source manuscript commit: `ee204d09c745c955de7b78790f3b4cf99745eac3`;
- changed submission input: `paper/manuscript.md` only;
- source branch: `main`;
- WFTS: specified but **not pursued**; no data requested or analysed;
- independent replication: remains untested;
- same-data NAAMP analysis: remains closed.

## Verified word counts

Counts from the exact current GitHub source using whitespace-separated tokens, as implemented by the manuscript and pipeline QA:

- anonymous manuscript: **7,991 words** (local QA safety guard: ≤8,000);
- five-point Abstract: **277 words** (pipeline limit: ≤350);
- title-page template: **158 words** before completed private author information;
- current combined count: approximately **8,149 words** (8,500-word article limit; approximately **351 words** of remaining margin before adding final private author metadata);
- anonymous cover letter: **400 words**;
- keywords: **8**, alphabetized.

## Verified GitHub Actions and artifact

GitHub Actions on `ee204d09c745c955de7b78790f3b4cf99745eac3`:

- workflow: **JAE submission pipeline**;
- run: [39425635411](https://github.com/zuizui0223/frogcs/actions/runs/39425635411);
- event: push to main;
- conclusion: **SUCCESS**;
- scientific-bundle job: **SUCCESS**;
- private-bundle job: **SKIPPED** (expected: final private author metadata was not supplied);
- standalone manuscript QA: **SUCCESS** for the same source commit.

Current anonymous scientific submission artifact:

- name: `frogcs-jae-pulse-template-scientific-submission`;
- artifact ID: **12264629523**;
- size: **1,245,562 bytes**;
- digest: `sha256:e748d23811f9439018d47fb0f32cbbe65362617aee7b79f587d90dc68f57315f`;
- created: **2026-10-20 12:52:20 UTC**;
- source workflow run: **39425635411**;
- source commit: `ee204d09c745c955de7b78790f3b4cf99745eac3`.

The 2026-10-06 artifact (ID 11410907633) is **superseded for current initial submission**. Do not submit files from mixed artifact versions.

## Unchanged scientific conclusion

Among 2,916 prior-site-history NAAMP pairs, the frozen within-taxon multi-site concentration was 1.6503 observed versus 1.3535 under the principal comparator (conditional residual 0.2969, plus-one P = 0.000999). State-blocked and temporal-block analyses provide post-hoc within-programme transferability, **not independent confirmation**. The future-rain negative control restricts temporal-specificity claims about the auxiliary 72-hour rainfall amount analysis.

## Outstanding author-controlled inputs

Only final author names/order and affiliations, corresponding-author contact, contribution roles, funding/acknowledgements, Conflict of Interest, approval of the Statement on Inclusion, and final author/institutional approvals remain before submission. Do not infer or publicly commit private author contact details.

License/release/Zenodo DOI and archive metadata remain separate pre-publication finalization items, not blockers for the initial submission under the current repository handoff.
