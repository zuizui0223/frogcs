# v7.0 — Public-only Australian frog observation sources: response-blind feasibility contract

**2026-10-13 JST.** Independent draft PR #135 only. This is a genuinely new **public-data-first** route, after the v6.9 original-acoustic/hydrology source gate. No custodian messages, credentials, restricted audio, private site coordinates, synthetic ecological outcomes, or changes to JAE RC6/main.

## Two separately sourced, NOT merged, original observational data products

1. **CEWH public Frog Abundance 2014–2022**, `data.gov.au` resource `70f3b7c9-990b-4770-b306-57c4e7cdac61`, official open CKAN DataStore (previous actual 673-row v5.0/v5.2 audits). This is a **published species×point×LONG observation-interval table**. Its calling Y/N is for *listed species*; tadpole CPUE is a capture/effort index, not reproductive fitness; no true full species-negative listening ledger or paired hydrology.
2. **Hoefer et al. (2026), version v2.0**, [archived on Zenodo](https://zenodo.org/records/21634473), [public GitHub source repository](https://github.com/cheloniax/repo_PAM_frogs/tree/v.2.0) with README/code and `data/frog_data_season.csv` (Git blob SHA `e5a419574be5e3f9922989f9aa6001fbb7f09d01`), `frog_data.csv` (SHA `b15aa848d50f3914588745a761e60a141e7aa5e6`) and [data dictionary](https://github.com/cheloniax/repo_PAM_frogs/blob/v.2.0/data/ReadMeDataFiles.txt). This is a **different Australian study**, with six sites and four survey plots at each site per the authors' dictionary, methods OBM/PAM.all/PAM.survey and seasonal detections. Its geographies, years and observation denominators are NOT presumed comparable to Murrumbidgee.

Both sources are publicly listed and have author-defined data dictionaries, but one published occurrence/detection row is not necessarily a *completed survey with a species negative*. Never infer biologically absent species from unlisted positive rows or reinterpret their sample units.

## First live read must be response-blind SOURCE FEASIBILITY only

1. Retrieve Hoefer GitHub source **only** via `https://raw.githubusercontent.com/cheloniax/repo_PAM_frogs/v.2.0/data/frog_data_season.csv` over HTTPS, exact host, max **4 MB**, verify bytes' computed Git **blob** SHA-1 equals the pinned source SHA above. Do not read new animal response values in this stage. Parse the CSV headers and profile ONLY number of rows, field names, non-sensitive counts of distinct `site`, `plot`, sampling trip, calendar dates, season, method, positive site×plot×trip support and source methods. Never print species names, individual dates/sites, recording links, precise location or species-specific effects.
2. The `date.time`, `Sampling.trip`, `assessment.method` names are taken verbatim from the published dictionary, subject to observed CSV schema correction. If the data are positive detections only, label `positive_detection_record` and do **not** fabricate all-site zero species or nights.
3. As an independent baseline reference, the existing verified CEWH 673-row source split (Gwydir 36, Lachlan 46, Murrumbidgee 591) is retained from [actual v5.0 QC](V5_0_FLOW_MER_ACTUAL_PUBLIC_FROG_SOURCE_AND_FROZEN_QC.md). No new frog or tadpole outcomes should be re-fitted or folded together with Zenodo data during first stage.

## Conditional analysis path, fixed before source outcome read

If the public Zenodo structure contains **repeated, positively surveyed site×plot×season units**, and at least two seasons and two physical sites with a documented comparable PAM method:
- test **descriptive compositional turnover**: for paired positive-detection assemblages, ask whether community composition changes more across seasons **within a location** versus differences across locations **within a season**, while matching site/plot/period support and recording method. Use presence-based Jaccard similarity at the actual observed site×plot×season frame only, no inferred environmental mechanism and no negative survey inference.
- An alternative, **stronger** test would require a complete site/plot/season opportunity ledger to calculate standardized site×season detection richness or disappearance; if the publication contains positive-only records, **do not** claim effort-corrected occupancy/colonisation or species absence.
- Use one fixed public method (prefer `PAM.survey` for period-matched comparison if repeated coverage is verified, else `PAM.all` with effort restrictions carefully labelled) rather than cherry-picking a method for a favorable directional result.
- Pre-specify pairwise Jaccard contrasts and a permutation/bootstrap procedure **only after first-stage structure**, before opening new biological species identities or association outcomes; nonconclusive results and heterogeneous records must be reported.
- Keep this result completely distinct from Q-A/Q-B **hydrological trajectory / biological history** because this dataset has no authenticated matched local wetland depths or repeated independent flooding events.

**What is NOT an outcome:** the published 2026 paper already demonstrates passive monitoring versus observer sensitivity; merely repeating its detection advantage does not count as a new ecological discovery.

## STOP / fallback

If newer public source is inaccessible or has too little repeated coverage to justify turnover, report the source quality failure and retain only the previous honestly exploratory CEWH sign-reversal description (pooled −16.09 pp versus restricted within species×site positive) without upgrading it to breeding fitness. No new `k≥4`, frog memory, hydrological hysteresis, water-causal or tadpole recruitment conclusions.

The initial script must print aggregate QC and leave the published raw CSV uncommitted. This pre-outcome contract and outcome-independent source checks precede any new method selection.
