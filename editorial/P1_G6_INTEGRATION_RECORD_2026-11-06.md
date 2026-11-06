# P1–G6 manuscript integration — source and review record

**6 November 2026. Integrated coauthor-review draft: completed local source, structure and reproducibility checks; not submitted to a journal.**

The [main manuscript](MAIN_TEXT_R1_R4_SUBMISSION_CANDIDATE_2026-11-05.md) and [Supplementary Information](SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md) now connect the observed acoustic association to fixed mechanistic predictions, their vegetation-context correspondence, controlled developmental mechanisms and population consequences. The central result remains that a mechanism's ability to generate an interaction signature does not establish its demographic benefit. P1's early-arrival plus prolonged-aquatic-duration reversal is retained as the main mechanistic discriminator and Figure 3.

## 1. Authoritative versions joined

| Layer | Source | Immutable source head |
|---|---|---|
| P1 manuscript, Supplement, four-figure assembly and 44-claim auditor | [PR165](https://github.com/zuizui0223/frogcs/pull/165) | `ac53197127bb1196589b09f1d49038fad66f8dc5` |
| G4 support and G5 fixed-shape geographic prediction | [PR166](https://github.com/zuizui0223/frogcs/pull/166) | `e963b2bf8f8522117f7ac1cf6c10389f1766fbb2` |
| G6 retrospective decomposition and complete replay evidence, including G4/G5 | [PR167](https://github.com/zuizui0223/frogcs/pull/167) | `c6756ed18ca44dd43b9eec5d5d92b6a4f8f4d7a0` |

The integration branch starts at PR167 and merges the PR165 head, preserving both histories. No biological kernel, source model, G4/G5/G6 result, G6 analysis program or original numerical panel was changed by this editorial integration. The bodies of both P1 main-text sections and Supplementary Methods S8–S9 are unchanged from PR165; the P1 Results heading was clarified. Original R1 route-bootstrap estimates and intervals remain intact.

## 2. Scientific connection and its limits

| Evidence | Integrated role | Claim boundary |
|---|---|---|
| R1: 4,248 locations | Establishes the caudate-conditioned odonate-suitability versus adult-calling pattern | SDM suitability and calling are not measured predator abundance, predation or aquatic cohort size |
| G4/G5: fixed observation operator and geographic holdouts | Makes the model-to-observation comparison explicit; retains positive source-11 coefficients in all five folds and positive pooled point gains | One corner misses support; the robust primary prediction gate fails; a simple environmental baseline predicts better |
| G6: saved predictions, no refitting | Locates positive primary point gains in the 506 locations with recorded landscape flooded vegetation; compares observed and modelled rank contrasts with the same operator | Retrospective diagnosis; vegetation-specific gains and paired V1−V0 intervals include zero; no vegetation intervention or independent field validation |
| R2/R3: matched vegetation mechanisms | Retains four-sign compatibility increasing from 3.52% to 14.06%, positive factorial compatibility and redistributed predator-hazard share alongside lower mean frog cohorts | Conditional model interventions, with a historically selected rate region; compatibility is not a field likelihood |
| P1: independent arrival × aquatic-duration intervention | Retains the abundance response changing from negative in late-arrival settings to clearly positive under early arrival plus long aquatic duration, while signature gains decline | Early arrival and long duration are distinguished; all four compatibility gains remain positive; field breeding phenology was not estimated |
| R4: 24,576 stochastic 80-year arms | Retains positive factorial occupancy and positive context-2 net effects alongside an uncertain pooled net occupancy benefit | Context 2 jointly changes S arrival and duration; immigration remains on; occupancy and frog abundance are different outcomes |

Exact estimates, intervals, denominators and source links are in the main text and Supplement. Main-text vegetation-specific rank contrasts cite **Supplementary Table S3e**; Supplementary Figure S1 C–D depicts the pooled rank contrasts. G6 block uncertainty does not replace R1 route uncertainty or the original G5 intervals.

## 3. Review package

| Item | Current state |
|---|---|
| Main file | **4,866 whitespace-delimited words**, including abstract, headings, captions and status material |
| Abstract | **137 words**; the Ecology Letters alternative matches the main abstract exactly |
| Supplement | **5,929 words**, nine main Methods sections; G6 in S3d, Tables S3d/S3e and Supplementary Figure S1 |
| Main figures | **Four unchanged composite PNGs**, assembled from nine original audited panels; Figure 3 is P1 and Figure 4 is R4 |
| Supporting documents | Cover-letter draft, journal abstracts, submission strategy and figure-source record synchronized to the integrated story |

Counts use the repository auditor's whitespace convention, not an asserted final journal-specific count. Earlier 135/4,406 counts in historical records refer to PR165 and are labelled as such. The alternative GEB structured abstract contains 264 words including its seven headings; its exact survey-year metadata remains unresolved.

The [four-figure record](FOUR_FIGURE_SOURCE_ASSEMBLY_RECORD_2026-11-06.md) links every review image. All four PNGs match the original receipt, and visual inspection found their labels, intervals and panel content intact. The original archive from [Actions run 42169682447](https://github.com/zuizui0223/frogcs/actions/runs/42169682447), artifact `13479644364`, has SHA256 `45a64e6fbf176870f127b99053d7d802b8073d98fd2c35c7686b83443ecf1d31`.

## 4. Verification completed before publication

1. **Research regression suite: 177 tests passed in 21.002 seconds.** The source suite used the pinned external acoustic module already required by the G5 tests. No biological analysis was refitted for this editorial task.
2. **G6: all eight tables replayed from the unchanged bundled source predictions.** The exact added CI step passed locally with numerical tolerances `rtol=1e-12`, `atol=1e-14`, zero refits, original R1 points reproduced, and the original G4/G5 failure gates preserved. This verifies computation, not an independent biological validation.
3. **Manuscript: all 16 structural and preservation checks passed.** These include abstract/main lengths, figure inventory, nine Methods sections, source cross-links, key inferential boundaries, unchanged P1 section bodies and unchanged SI S8–S9. Relative links and source-preservation hashes are recorded in the [integration QA receipt](../research/results/p1_g6_editorial_integration_20261106/integration_QA_receipt.json).
4. **Archived 44-claim source QA retained and rechecked.** The [original claim table](../research/results/p1_g6_editorial_integration_20261106/source/pr165_claim_qa/source_claim_checks.csv) and [historical receipt](../research/results/p1_g6_editorial_integration_20261106/source/pr165_claim_qa/submission_source_QA_receipt.json) are unchanged from [Actions run 42169682353](https://github.com/zuizui0223/frogcs/actions/runs/42169682353), artifact `13480184326`, ZIP SHA256 `539089cd34204847b95ed75baf640918bd31bd2759606b4ca5252de6423f9141`. All 44 archived values pass the current targets. This local recheck is distinguished from a new recomputation from all six original result archives.
5. **Independent scientific review completed.** A separate read-only audit reviewed the main text, SI, four main images, G6 image and supporting editorial documents. Its one material cross-reference issue was corrected from pooled Figure S1 to vegetation-specific Table S3e and rechecked; no material numerical, interpretation or positive-result-preservation issue remains in that review's scope.

The [source-claim CI workflow](../.github/workflows/research_submission_claim_source_QA_20261105.yml) now targets an integration PR based on the G6 branch. It downloads all six original numerical archives, recomputes the 44 headline claims against the integrated manuscript, and separately replays all eight G6 tables. Its remote result is reported on the PR after execution; this pre-publication record does not assert that a future run has passed.

## 5. Remaining author and submission work

Bibliography completion, author details and approval, data/code access and permission arrangements, final journal-specific counting/formatting, and production-size figure review remain. These are submission tasks, not reasons to discard the completed conditional model result. Independent biological calibration and direct pond-scale field testing remain future research. The manuscript, cover letter and alternative journal framing have not been submitted or sent.
