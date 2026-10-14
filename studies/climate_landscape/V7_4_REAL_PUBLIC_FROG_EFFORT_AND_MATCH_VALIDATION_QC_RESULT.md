# v7.4 — REAL public source QA of acoustic recording effort and manual match annotations

**Completed 2026-10-13 JST. This is NOT another search for positive frog ecology effects.** Independent draft PR #135, frozen JAE RC6/main unchanged. [Pre-data QC contract](V7_4_PUBLIC_RECORDER_EFFORT_AND_MANUAL_MATCH_SOURCE_QC_CONTRACT.md) was committed before new `MANUAL.ID` validation rows were examined. Source [Hoefer et al. (2026) Zenodo v2.0](https://zenodo.org/records/21634473) is the separate open eastern Australian frog survey; its preprint is not necessarily peer-reviewed. This does NOT authenticate any CEWH Murrumbidgee recorder/logger join.

**[Actual source-check CI 38410943930 — SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38410943930)** · [reproducible hash-pinned Python script](scripts/audit_public_hoefer_effort_and_manual_validation_v74.py) · [aggregate-only JSON result](receipts/HOEFER_2026_REAL_ORIGINAL_EFFORT_VALIDATION_QC_V74.json). All **three original source Git blobs** independently verified: original [authors' R code](https://github.com/cheloniax/repo_PAM_frogs/blob/v.2.0/scripts/R_code_biodiversityFrogs.qmd) SHA1 `93c6e051ce446f76ac0730f52693bea9ebfc3963`; public `frog_data_season.csv` SHA1 `e5a419574be5e3f9922989f9aa6001fbb7f09d01`; manual match table `frogs_PAM_daily_all.csv` SHA1 `f2f7a5426be57e98387f06055c9361377f007ad4`. All original rows read in the CI runner memory, no identifiable data or animal detections redistributed.

## A. Author-supplied monitoring-day denominators exist, BUT not at the needed recorder×time grain

The original author code defines **six site-level all-period `T_days` values** in the PAM accumulation calculation (R lines **1191–1199**, also repeated under `site_vals` at line 1217), and **24 site×season `max_days` values** in the seasonal iNEXT calculation (lines **1360–1389**). Both independent site-total declarations were verified to agree with each other. Site names were used internally for arithmetic but are NOT exported in the anonymized receipt.

| Exactly as encoded in the original R script | Summed days across six source sites |
| --- | ---: |
| Whole-period `T_days`, six site totals | **4,951** |
| Four author season-specific `max_days` per site, 24 rows | **4,875** |
| **Whole-period total minus season-specific aggregate** | **+76** |

Only **1/6** sites reconciles exactly; **5/6** differ. Original site-level differences, sorted without site identifiers: **0, +1, +2, +6, +20, +47 days**. The difference is **not** direct proof of missing records, data fabrication or a statistical error; the two source calculations may use different inclusion/period definitions, boundary handling or some other author-specific method not documented in the printed lines. The calculations must not be silently "repaired" by distributing 76 days among plots, seasons or unobserved dates.

The released **13,577 frog detections** had at least one positive frog record on **41–300 distinct calendar dates per site×season** (median **130**); comparing these positive dates with source `max_days` yields a min/median/max ratio of **0.216 / 0.7836 / 1.0000** across the 24 site×season groups, and no source positive-day count exceeded its published `max_days`. There are **95/96** plot×season categories with at least one positive frog record. These are **detection-positive dates**, NOT all valid negative/zero recording opportunities; *neither the differences nor the ratios measure calling probability, occupancy or actual uptime.*

**Correct source-availability statement:** site-level and site×season **author-defined observation-day limits are publicly available**, so the earlier shorthand that this source has "no effort information" was too broad. However, there is still **NO authenticated `site × plot × calendar timestamp × valid/missing/no-call` opportunity ledger** in the inspected detection CSV or author R definitions. Such a ledger would be necessary to standardize the v7.1–v7.3 within-site plot-by-season Jaccard comparisons or infer absences.

## B. The separate human validation table is large and demonstrates candidate prefiltering, NOT final published detection sensitivity

From the source [`data/frogs_PAM_daily_all.csv`](https://github.com/cheloniax/repo_PAM_frogs/blob/v.2.0/data/frogs_PAM_daily_all.csv) and [original dictionary](https://github.com/cheloniax/repo_PAM_frogs/blob/v.2.0/data/ReadMeDataFiles.txt), the only published columns in this validation table are `MANUAL.ID` (TRUE/FALSE/UNSURE/missing), `template`, and `eucledian.distance` (the authors' spelling). These are *acoustic match candidates*, not unique site×date×frog observation records, nor a survey-opportunity manifest.

| Candidate manual matching label | Source rows |
| --- | ---: |
| **TRUE**: matches example frog call | **13,609** |
| **FALSE**: does not match example frog call | **237,535** |
| **UNSURE** | **105** |
| **Missing label** | **32** |
| **Total candidate rows** | **251,281** |

Among **251,144** candidate rows assigned TRUE/FALSE, the TRUE share is **0.05419 (5.419%)**. **DO NOT call this "5.4% frog classifier accuracy," "5.4% precision of the final 13,577 published species detections," or "94.6% erroneous ecological observations".** The candidate-generation threshold, day sampling frame, manual-labelling enrichment and final authors' filtering are different target populations.

- **115** original example-call templates, **78** with ≥1 manually confirmed TRUE (and also ≥1 FALSE), **37** with FALSE candidates but **zero validated TRUE**.
- **70** templates have ≥5 confirmed TRUE and ≥5 confirmed FALSE, but this is *not* an independently checked per-species holdout or recall estimate.
- Original R code lines **135–140** remove `UNSURE` and missing labels and select **only templates that ever produced a TRUE** before fitting/summarizing Euclidean match quality. Thus reported template-level models are **conditional on previous confirmed positives**.
- Crucially the candidate file has **no `site`, `plot`, `date`, `scientific.name`, file ID or source event ID**. It cannot be reliably row-joined to `frog_data_season.csv`'s **13,577 positive frog species detections**. Superficial similarities in counts (13,609 TRUE manual candidate labels vs 13,577 final detections) are NOT evidence those are exactly the same events. Never substitute candidate-label aggregate rates for source species-specific false positives or calibration.

The author's R heading "Recall calculations Embeddings" includes `glm(MANUAL.ID ~ eucledian.distance)` and draws from manual true/false candidate match-distance distributions. In the inspected source, this estimates candidate correctness conditional on the candidate sample (or discrimination among candidate matches), **not full ecological vocalization recall across all recordings**, which would require known true calls including missed detections.

## C. Scientific consequence for v7.1–v7.3 and STOP

Source quality **undermines any strong inference**, rather than changing the original computed Jaccard descriptions:

1. **Preserved observation:** the source's positive species-list Jaccard contrasts v7.2 and v7.3 were actually calculated, using exact published frog species labels and 6 sites as clusters. No previous numerical result was silently refitted.
2. **No stronger claim:** the +0.0350 v7.3 water-proximity grouping difference, null-containing six-site interval and site-fixed 3^6 structural comparison remain **descriptive**, not evidence of water-caused habitat sorting. Repeatedly screening until a threshold produces a positive result is not valid.
3. **Minimum missing original resource:** time-stamped recorder operating/recording quality and actual attempted valid non-detection opportunities by plot and season-year; additionally an authoritative record/template/version-specific crosswalk if attempting to correct detected taxon lists. The source-authorised site total/season maximum days do not supply either.
4. **Data-access policy:** this project has read only legitimately public GitHub-tagged files. No audio, private coordinates, raw species/site values, or human correspondence was transmitted, stored or committed to the frogcs results. CEWH source-specific hydrology Q-A/Q-B remains **BLOCKED** and enquiry **UNSENT**.

**Final public-data QA decision:** `SOURCE_POSITIVE_LISTS_REPRODUCIBLE; SITE_LEVEL_AND_SEASON_LEVEL_EXPOSURE_SUMMARIES_PRESENT_BUT_NOT_RECORDER_LEDGER; SITE_TOTAL_VS_SEASON_SUM_76_DAY_DIFFERENCE_UNRECONCILED; CANDIDATE_VALIDATION_NOT_ROW_JOINABLE; NO_CAUSAL_OR_EFFORT_CORRECTED_FROG_COMMUNITY_RESULT`. Stop source-free refinements on this collection. This is a useful audit of *what the original public data can establish*, not a new predictive effect or biological memory claim.
