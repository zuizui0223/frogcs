# NPS GLKN park-specific acoustic monitoring panel audit v0.3 (2026-10-22)

**Source-only correction**, frozen after receiving *only recording/species/park metadata*, before reading any acoustic detection or intensity values. Original ecological hypotheses and NPS source assets unchanged. JAE RC6 untouched.

## Verified original field identity and source receipt

[Actions 39722310835](https://github.com/zuizui0223/frogcs/actions/runs/39722310835) succeeded on the official NPS monitoring CSV:

- original CSV **68,581,307 bytes**, SHA256 **b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2**;
- official NPS XML **131,226 bytes**, SHA256 **a37af87cd333168f52503f823041c4ab578b6968333c7d5f315604222ae4eb8f**;
- **147,913 species×recording rows**, **16,561 distinct recording events**, **66 distinct ParkCode×SiteLocation station IDs** in seven parks (APIS, GRPO, INDU, ISRO, MISS, PIRO, SLBE), 2016–2023;
- zero duplicate `ParkCode×SiteLocation×FileName×StartTime×ScientificName` composite keys;
- **13** distinct scientific-name labels in this CSV. NPS catalogue describes 14 species; the release's observed table has 13 distinct labels (one label is a `Pseudacris maculata/triseriata` complex). No silent correction to "14 distinct measured species".
- Number of species-label rows per recording is **7, 8, 9, 10, or 11**; every recording has fewer than all 13 global taxa. Hence the global 13-taxon complete-panel gate FAILS and cannot be treated as species absence.

The metadata README/XML establishes `ManualCIV` as a *manual call index 0–3* and `SurveyorDetectedStatus` as manually verified YES/NO. NPS also records `Hydroperiod` and `AvgTemperature_C`. These are SOURCE SCHEMA facts; **no response cells were read** in run 39722310835.

## Predeclared alternative explanation to test **before** readback

The 7–11 repeated taxon rows may represent a **park-specific recording target panel**, with species not relevant to a park omitted from every recording there. Before biological outcomes, verify this on metadata alone:

- Enumerate exact per-park species-label sets and count their sizes.
- For every recording event, test whether its recorded taxon-name set equals the full park-specific set; count inconsistent panels and duplicate naming.
- Also test more conservative *site-specific* stable sets if park-specific panels vary.
- Counts and species-identifiers only; do **not** load response fields.
- Count park/station recording events explicitly containing BOTH `Lithobates catesbeianus` and `Lithobates clamitans` species rows.
- Count the same-event availability for fixed negative candidates `Anaxyrus fowleri` and `Dryophytes versicolor` (modern published name for NAAMP's `Hyla versicolor`), but **do not swap in a different negative species if either fails**.
- Count per station×calendar-date number of recordings, especially ≥3, ≥6 and ≥10 recordings, with keys `ParkCode×SiteLocation×StartTime:date`. The prospective unit is a **repeated recording window** rather than NAAMP's fixed spatial stops.
- Count unique hydrological regimes, how frequently a recording's multiple taxon rows disagree on `Hydroperiod` or `AvgTemperature_C`, and whether static within site.
- A recording's missing species row can only be coded as unassessed if it is absent from the site's verified target panel. **If the event contains a complete park- or site-specific explicit target panel, the row for a monitored species can be evaluated using its documented ManualCIV/SurveyorDetectedStatus field after a second frozen analysis contract.**

## Outcome analysis eligibility gates

- Original NPS filename, reference, SHA and year range unchanged.
- ≥1,000 recording events with both bullfrog and greenfrog *explicitly in the confirmed park/site target panel*; ≥20 stations across ≥2 parks.
- ≥100 station-date groups with ≥3 repeated recording events **and both named taxa assessed**, OR ≥300 ordinary recording event opportunities across ≥20 sites for a less-conditioned partner prediction analysis.
- Any risk that species rows only exist for species *actually detected* blocks interpreting missing rows as zero; use only explicitly manual 0–3 or YES/NO values in present rows.
- If park/site panel is irregular, do not infer negative rows from absence, but still report whether an explicit pair panel enables response analysis.
- If target named taxa are absent from most parks, report uneven park coverage; do not assert independent nationwide reproduction of NAAMP.

## Next frozen inferential design if eligible

Primary outcome: `ManualCIV≥1` for green frog **within an explicitly assessed recording**, with `ManualCIV=0` a nondetection, never impute missing/invalid values. Bullfrog `ManualCIV≥1` is the already named partner predictor, and exclude any source rows whose manual status was not validated according to NPS original XML. Negative candidate identities fixed A. fowleri and Dryophytes versicolor.

- Counterfactual comparison is **observational**, not causal. Exact same file/broadcast time is more temporally local than NAAMP listening routes.
- Site, year, season, hour, `AvgTemperature_C`, `Hydroperiod` and generic nonpartner frog calling richness must be controlled as justified by the verified field granularity.
- Hold out entire **ParkCode×SiteLocation** groups (no recordings from a site in both training and test). A park holdout is separate sensitivity if enough park-level coverage.
- Independent signed conditional logscore increment of bullfrog indicator over baseline is the primary decision. Presence prediction is not full-community conditional pseudolikelihood and not directly numerically comparable to NAAMP scores.
- Do not use NAAMP estimated coefficients, site-history inputs, or NWI map to fit the independent model. No new partners after outcome readback.
- Preserve the fact that this is one passive acoustic monitoring dataset, not a newly randomized experimental manipulation. Detection recording does not establish individual behavior, mating or trophic paths.

Pre-outcome source panel audit code `exploration/run_nps_glkn_park_panel_preflight_v0_3.py` and GH Actions result-only artifact. No frozen RC6 files modified.
