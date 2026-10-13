# USGS ARMI 2024 — PRE-OUTCOME matched independent observers' frog calling uncertainty test

**Frozen 2026-10-14 JST, AFTER official original-source schema and visit-grain inspection but BEFORE computing any frog response rates, species-list similarities or methods contrasts.** Independent draft PR #135, separate from JAE RC6/main and from Hoefer and CEWH acoustic data. No TinyFish, external email, coordinates, private data or site/taxon names published.

## Authenticated public original source and unit

Source: [U.S. Geological Survey Roth et al. 2025, ver.1.1 April 2026, DOI 10.5066/P19ZCGWM](https://doi.org/10.5066/P19ZCGWM), CC0. Original ScienceBase item `68016413d4be0263cab109a8`, original release CSV exact **235,391** bytes and SHA256 `dafd388c7ccb79e08dbadd37a25c604473a8caf4ff5c8318532740acb56a04e4`, filename `ARMI_2024_cricket_frog_data_release_2025_v1.1.csv`. [Actual pre-outcome original source and FGDC dictionary audit](https://github.com/zuizui0223/frogcs/actions/runs/38422071685), [compact source receipt](receipts/USGS_ARMI_2024_ORIGINAL_OBSERVER_SURVEY_GRAIN_2026_10_14.json). **1,934 original species lines**, **343 original survey locations**, **773 unique site×date keys**, **797 site×date×observer keys**, **2 observer categories**, **51 distinct dates (2024 June–August)**, **24 site×dates where both observers were present**, and **306 sites with ≥2 different survey dates**. A single site×date×observer key reports >1 arrival time; do not silently merge distinct clock observations into one 'exact same survey'.

The original USGS FGDC dictionary says `Arrival_time` is the **local 24h survey start time**; `Method` codes are `Ear` (naked ear) and `Microphone` (Telinga parabolic mic/headphones); `Number_heard` records discernible individuals or a **range**, with **NA when no anurans heard**; `Species` is the scientific taxon heard, plus an explicit no-call sentinel in the released CSV. Source-only audit found **220 no-anuran-sentinel source rows and 220 missing `Number_heard` rows**, supporting but not automatically proving one-to-one complete opportunity encoding; this exclusivity must be checked on source visit keys BEFORE analyses. **24 same-site-date two-observer pairs** are temporally close (start gap 0–5 minutes, median 0), but **23/24 use different Ear vs Microphone methods**; therefore observer identity and device are nearly completely confounded. No independent instrument-only causal effect may be claimed.

## Fixed scientific questions and output before opening species responses

### Primary: how much can near-simultaneous independent observation alter the **detected audible anuran assemblage**?

Treat a source opportunity as `(Site, Date, Observer, Arrival_time, Method)`, NOT each species row; source-specific no-call sentinel yields an **explicit observation with zero heard frog species** if and only if the same source key has no detected species rows. Any empty/ambiguous code, mixed no-call+species key, blank physical ID or duplicate observer-start-method status is **UNKNOWN and excluded** from this observational comparison rather than coded zero.

Select only **exactly two separate observers** at the same source site and same date, each with exactly one original start time and one method. Require a start-time difference **≤5 min** (observed source clock support); only **opposite-method Ear↔Microphone** pairs enter this primary paired-method/observer-package result. The 1 same-method pair, if valid, is a source-control descriptor, not independent replication.

Fixed comparisons, all paired within same original site/date:
- `S_mic - S_ear`: difference in **number of distinct positively heard frog species**, with explicit no-call as 0 and repeated same-species rows collapsed to one. Report each method's all-pairs mean and paired mean difference, median, site-direction counts (+/−/equal), **nonparametric 5,000-draw site-cluster percentile interval, seed 20261014**. If fewer than **5 distinct sites** contribute, return insufficient source support, not a mechanistic claim.
- Binary any anurans heard: cross-tab 2×2 (both positive / both explicitly no call / microphone-only / ear-only), report exact paired method disagreement share and disagreement direction; no McNemar P value or causal instrument claim.
- Species-list Jaccard on paired **nonempty-union** detections only, with mean/median, and a separate both-empty count; don't inflate assemblage agreement by setting both-empty Jaccard=1.

**Observational interpretation only:** if differences are substantial, the *observer–device package* adds detection variability at a fixed site and near-same time. It is not evidence frog populations changed; nor independently identifiable sensitivity advantage of microphone vs ear, because methods and observer are confounded and one observer may influence another or sample different directions.

### Secondary: site-scale variation over repeated survey dates, not independent ecological absence

Among all **fully authenticated** `Site×Date×Observer×Time×Method` opportunities, compute number of source sites with ≥2 distinct valid dates; count **same site, identical observer+method** recorded on ≥2 dates, and if >=5 sites qualify, calculate within-site detected-species-list Jaccard for date pairs separated **1–30 calendar days**. Average within physical source site, not by number of species rows/dates. Report n sites, n paired dates and mean only, plus comparable pairwise observer same-day Jaccard where union nonempty, **explicitly noncausal, not matched temporal experiment**. Do NOT select timing windows or species after seeing results. If no valid repeated method, withhold.

Do not join historical USGS 2003–08 sites without an exact original crosswalk. The [2026 Burner et al. Journal of Herpetology paper](https://doi.org/10.1670/2719523) already reports the species' northward recolonization; this analysis cannot claim that as novel. No local water levels or hydroperiods are provided, so no rising/falling-water Q-A/Q-B inference, memory, recruitment or reproduction.

## QA controls and release

1. Source file and FGDC original metadata must retain original verified SHA. Check exactly **220** no-call sentinel rows, verify these coincide with **220** missing `Number_heard` values; **fail closed** if mismatch. Never interpret NA on a genuine species row as no-call.
2. Verify no-call source opportunities are exclusive of detected species and any multiple-start observers handled separately; note actual number of valid key groups excluded.
3. Enforce exactly original source 1,934 rows, 343 source IDs, 51 original dates, two observer IDs; acknowledge two methods.
4. No individual observer initials, site IDs, original coordinates, species names, dates of individual surveys or raw records leave runner memory. Output *only* anonymized aggregate JSON. The source is public/CC0 but no row-level redistribution is needed.
5. Preserve a first-stage source-only and second-stage biological comparison receipt. Document the **confounded observer+device** limitation at the top, not merely buried in Limitations; never claim replicated independent frog chorus sites or genuine instrument treatment randomization. Use no ad-hoc taxon/date/window search.
6. Predefined null or weak results count as completed. Only write result summaries after the original GitHub workflow runs and the observed output is independently verified; retain JAE RC6 frozen, CEWH enquiry UNSENT, one-off inspection workflow removed after conclusion.

This is a site-specific *observation versus true acoustic community variability* ecological monitoring question with original source **survey opportunities**, unlike the separate Hoefer positive-only 2026 acoustic monitoring file. It remains limited to 2024 US Midwest night surveys and does not prove wider frog species distributions or biological mechanisms.
