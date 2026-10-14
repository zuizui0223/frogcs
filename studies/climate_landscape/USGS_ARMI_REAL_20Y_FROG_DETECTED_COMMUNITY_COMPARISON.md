# REAL USGS public frog calling: 2003–08 vs 2024 matched-site detected assemblages and historical observer baseline

**2026-10-14 JST — Original open federal field-survey observations, actually executed on source-pinned CSVs; not simulated, not a species-occupancy trend analysis, not a new discovery of *Acris blanchardi* recolonization.** Independent frogcs draft PR #135; JAE RC6/main untouched and CEWH water-history enquiry UNSENT.

## 1. Genuine original release files, different observation periods

| Original USGS dataset | Source records | Source Site codes | Authentic SHA256 |
|---|---:|---:|---|
| [Roth, Burner & Sadinski 2003–08, ver.1.1 April 2026](https://doi.org/10.5066/P1X9UBHV) | **10,189** species-line records | **744** | `33bb028cf148a685d8af5a579786ce94bde045fa68d00f8c395713c6c06ae32b` |
| [Roth et al. 2024, ver.1.1 April 2026](https://doi.org/10.5066/P19ZCGWM) | **1,934** species-line records | **343** | `dafd388c7ccb79e08dbadd37a25c604473a8caf4ff5c8318532740acb56a04e4` |

Original official FGDC dictionaries provide `Site`, `Site_original`, `Observer`, `Method`, `Arrival_time`, `Species`, and `Number_heard`. The source code `Number_heard=NA` denotes **no anurans heard**; the source also permits ranges and `Unknown` numbers for genuinely heard frog calls. The scripts inspect the source entirely in runner memory; **no original site coordinate, observer identity, detailed field record or species-name list is in this repository output**.

Real source-only validation predated biological outcomes: [original release/field grain CI 38492599752](https://github.com/zuizui0223/frogcs/actions/runs/38492599752); [FGDC definitions, geospatial/method audit CI 38492813806](https://github.com/zuizui0223/frogcs/actions/runs/38492813806). [Analysis/eligibility fixed BEFORE opening old/new frog species-list outcomes](USGS_ARMI_PUBLIC_FROG_20Y_MATCHED_EPOCH_OBSERVER_FROZEN_CONTRACT.md).

## 2. GENUINE field identity QA prevents false ecological turnover

Official `Site` labels match exactly between eras at **298** candidate locations; median coordinate pairs agree within **10 m at 293**, while **5** names are physically separated by **>500 m** (worst **8.224 km**). One additional 2024 site label has a **>100 m internal coordinate inconsistency**, so **292 source-site candidates** pass all fixed restrictions (same literal `Site` ID; cross-era coordinate displacement ≤10 m; each-era within-label coordinate max spread ≤100 m). The legacy `Site_original` has **306** exact aliases, **301** spatially close, but these aliases are *not substituted post hoc* for `Site`.

This is source-ID and geospatial **consistency**, not an externally custodian-certified wetland ecology population crosswalk, randomized re-survey or independent pond replicate.

Original study design also differs markedly across eras. Historic 2003–08 has **3,230 Site×Date×Observer source keys** across 744 sites, 16 observer labels and Ear/Microphone/Unknown methods. The 2024 source has **797 keys** across 343 sites and 2 observer labels. The historical source contains **615** explicit no-anuran rows, which map after key quality filtering to **607 valid no-frog observer events**; the 2024 source has **220** explicit no-frog observer events. In the 2024 data 2 timestamp-specific source events were excluded due to one ambiguous observer-day; older original data had **140** same-observer-day events affected by changing times or methods and excluded from this comparison.

Original observed taxon name vocabularies differ (**14** historic labels, **10** in 2024, **9** shared exactly). The original taxonomic labels are compared literally. Genus-level uncertainty and possible taxonomic nomenclature changes are not silently resolved; *apparent turnover can partially reflect label and observation differences*.

## 3. Predeclared matched ecological detection comparison — 67 site pairs

Actual execution: [**USGS original 2003–08 and 2024 pinned source analysis, CI 38493167832 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38493167832), [analysis code](scripts/analyze_usgs_armi_historic2024_original_detected_assemblages.py), [aggregate reproducible source receipt](receipts/USGS_ARMI_REAL_20Y_MATCHED_FROG_SPECIES_LISTS.json).

No species outcome was used in selecting comparison cells. Selection: source Site ID and median coordinate match as above; **same calendar month** (June/July/August); **same original Microphone method**; source survey start times ≤**60 minutes** apart; choose **one pair per site** with smallest day-of-year difference and source chronological/observer-code tie-breakers, before comparing reported species lists. As this is a field observational dataset, retaining one pair per site is a reproducible equal-weight design decision, not a formal matched-treatment experiment.

| Actual same-site, same-month, same-method, within-60min survey-start pairs | Value |
|---|---:|
| Source eligible site pairs | **67** |
| Historically from source 2003/2004/2005/2006/2007 | **1 / 8 / 12 / 14 / 32** |
| Source common month June / July / August | **18 / 48 / 1** |
| Both selected recorded observer-events reported ≥1 anuran species | **50** |
| Exactly one selected event explicitly reported no anurans | **16** |
| Both original selected events explicitly reported no anurans | **1** |
| Nonempty detected-species-set union pairs for Jaccard | **66** |
| **Equal-site detected-taxon-list Jaccard mean** | **0.416414** |
| Detected-list Jaccard median | **0.500000** |
| Sites with no shared detected species among nonempty union | **23/66** |
| Sites with exact detected list match among nonempty union | **12/66** |

Two explicit no-frog field observations are *not* recoded as a Jaccard=1 species list. A one-sided no-call event and positive source event legitimately produce observed J=0, **not proof of true absence in that era**. These metrics describe original recorded **audible frog assemblages** across 17–21 years, not frog population extinction, colonization or a multi-species occupancy estimator.

**Predeclared source-only diagnostic, not preferred endpoint:** removing the fixed ≤60min clock constraint enlarges the comparison from 67 to **139** site pairs and changes mean detected-list Jaccard to **0.349103** among **130** source nonempty unions (54 with no shared detected taxa). Different selected source events and site composition change the estimate; **do not use this as independent biological confirmation** or cherry-pick whichever shows more turnover.

## 4. Independent observers under the SAME historical night: measurement-noise reference is promising but too sparse for formal normalization

Among the selected eligible 67 sites, there are **10** distinct sites with an independently surveyed **historical same-site/same-night, two-different-observer, same Microphone method, start-gap ≤5min** comparison. Of these, **8** contain an anuran-positive union; their mean detected-list Jaccard is **0.968750**, median **1.0**, with **7 of 8** fully matching reported species lists. The other **2** pairs both explicitly reported no frog call.

The within-night Jaccard **0.969** and across-eras **0.416** are **not** estimates on the same representative site-event frame: the observer-baseline and multi-decade sets differ in date/year, environment, observers and number of usable sites. Only **8 sites** have a positive-union pair in BOTH comparisons; the frozen source rule required ≥10 to quote a within-site difference and site bootstrap. It consequently returned `INSUFFICIENT_SAME_SITE_OBSERVER_CALIBRATION`, without producing a spurious p value/positive 95% interval.

**Biological interpretation:** the source reports much greater similarity between nearly simultaneous original observers than across two decades *descriptively*, but **unmeasured observation, taxonomy and interannual habitat changes could account for some or all of that difference**. Neither an identified magnitude of true community turnover exceeding observer error nor a new causal mechanism has been measured.

## Follow-up v8.1 source-identity and coding sensitivity QA — precommitted after the v8.0 outcome, not a new ecological hypothesis

The primary 67-site Jaccard=0.416414 was already viewed before planning this **source-quality** investigation. The **frozen original outcomes/eligibility/selection remain unchanged**. This source audit, planned **before reading its additional diagnostic results**, must (a) compare complete historical versus 2024 original literal `Species` vocabularies, treating source-only/uncertain-rank taxa as possible **noncomparable label constructs**, not forcing taxonomic synonyms; (b) count how many of the **same 67** frozen site-pair comparisons could be affected by any release-private taxon label, without replacing labels or fitting an alternative Jaccard; and (c) count source `Site×Date×Observer` keys with multiple original times/methods, especially within the 292 consistent-site cohort and potentially eligible historic Microphone June–August observations, distinguishing **separate timed surveys** from actual duplicate lines. Publish aggregate checks only; no new species-by-site values or taxon-specific effects. Use an exact source-file hash gate and run tests before conclusions.

**Hard stop:** the author's original event definition is not fully established merely by the CSV field names. The v8.0 parser conservatively discarded all events belonging to ambiguous `Site×Date×Observer` keys; if multiple valid clock-separated visits exist, that rule may discard legitimate opportunities. The effect on the primary **67** pairs, if any, must be quantified as source eligibility, **not** used to post hoc choose a higher or lower community similarity. Likewise, ITIS recognizes `Acris crepitans blanchardi` as a synonym of `Acris blanchardi`, but no source-row synonym recoding is allowed without verifying that those exact labels occur and reflect identical field taxon concepts. Keep the original 0.416414 intact and downgrade interpretation if source ambiguity is material.

## 5. Connection with prior publication and precise publication ceiling

[Burner et al. (2026), Journal of Herpetology 60:96–104](https://doi.org/10.1670/2719523) already analyzed these programme years using multi-species occupancy with imperfect detection and concluded `Acris blanchardi` occupied more northern sites in 2024. **That range shift, and the concept of imperfect detection, are existing published results.** This new frogcs source pairing is a reproducible exploratory **whole-anuran audible-list similarity audit** with explicit method/month/time/location and original field no-call handling, not an independent experimental confirmation or evidence of re-expansion.

This observational source has no measured corresponding daily wetland-water-depth history, frog movement, reproductive success or independent climate manipulation. **No water-arrival hysteresis, social facilitation, individual frog memory, adaptation or local wetland causal effect is supported.** Between-decade year and observer differences, imperfect hearing, some uncertain genus-level taxa, and variation in phenological weather remain critical.

**Bottom line:** Genuine public data permit **67 controlled-as-far-as-possible source event pairs**, with low-to-moderate detected-species-list similarity (J≈0.416). Same-night historical observer lists are substantially more similar (J≈0.969), but true observer-calibrated long-term ecological turnover remains **unidentified** at eight directly comparable sites. If published as a methodological observation, original source, overlap and prior published analyses must be acknowledged; **do not represent this as a new species-specific decline or rigorous occupancy trend estimate**.

CEWH original audio/wetland depth identity gates remain open, its data enquiry **UNSENT**. Frozen JAE RC6/main untouched. No TinyFish.
