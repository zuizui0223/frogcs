# Independent frog network validation — NPS / Dryad source status, 2026-10-22

## Topline

**Independent external frog calling prediction is NOT YET TESTED.** Original NAAMP geography-held-out model remains an **internal dataset result**, not an independently demonstrated biological frog-frog interaction.

The user-directed external verification advanced source acquisition and *response-blind* dataset coverage but did **not reach the expert recording detection outcomes**. The stopping condition is source-server transport, not an ecological null or failure of the predeclared prediction.

## NAAMP finding to be challenged externally

On USGS NAAMP 2001–2015, after static NWI 250-m mapped wetland/PEM cover, strictly previous-year physical site calling history and generic local taxon richness, the **site identity of bullfrog `Lithobates catesbeianus`** improved `L. clamitans` held-out conditional placement predictions on unseen geographic routes. Original v0.3 gains (nats/route-run):
- comparison with `Anaxyrus fowleri` present: **+0.09648**, route-bootstrap 95% interval **+0.05671 to +0.13842**;
- comparison with `Hyla versicolor` present: **+0.11118**, interval **+0.06548 to +0.15708**.
Adding either named negative partner *after bullfrog* did **not** improve the independently heldout location score consistently. No direct attraction, competition, third-body interaction or macrophyte-mediated trophic effect was identified.

## First external source — Dryad GL Coastal Wetland Monitoring Programme

Source: Tozer et al., 2025, `doi:10.5061/dryad.hmgqnk9v8`, published survey data (2011–2023). The original CSV `CWMP_MaxOcc.csv` (4,004,194 bytes; SHA256 `9b6e1b11d371a6bfac2b49e0aee369a57ed4fdeaeb7378c81ea79dc92c9b2587`) and README metadata were identified before outcome readback. Both official API file routes and dataset ZIP returned **HTTP 401**; original public UI download returned **HTTP 403**. No source bytes verified and no frog responses read.

Immutable failure receipt: `exploration/GLCWMP_INDEPENDENT_SOURCE_ACCESS_RECEIPT_V0_2.json`, [Actions 39721164365](https://github.com/zuizui0223/frogcs/actions/runs/39721164365). No biological conclusion.

## Second external source — NPS Great Lakes Inventory & Monitoring frog acoustics

Official NPS DataStore reference **2320505**, 2016–2023.
- Original survey CSV file 763377: **68,581,307 bytes**, SHA256 **`b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2`**.
- Original NPS XML metadata 763466: **131,226 bytes**, SHA256 **`a37af87cd333168f52503f823041c4ab578b6968333c7d5f315604222ae4eb8f`**.
- Source-only quality checks **passed** in [39722310835](https://github.com/zuizui0223/frogcs/actions/runs/39722310835) and [39722811424](https://github.com/zuizui0223/frogcs/actions/runs/39722811424). Underlying observation schema:
  - **147,913** taxon-by-recording metadata rows; **16,561** recording events; **66** physical park×site locations across **7** park units.
  - **13** distinct species/group scientific-label units. Every recording includes 7–11 explicit species rows; never impute omitted taxon rows to "no call."
  - Bullfrog and green frog both have explicitly assessed species rows in **12,499** recordings across **50** locations and **5** parks. The negative partners `Anaxyrus fowleri` and `Dryophytes versicolor` also have 4,121 and 12,376 explicit triple-row opportunities respectively.
  - The files contain `ManualCIV` (expert 0–3 call index), expert `SurveyorDetectedStatus`, `AvgTemperature_C`, `Hydroperiod` (Ephemeral, Semi-permanent, Permanent), date/time/park/station metadata.
  - The 12,499 matched pair-row recordings contained **no site-date grouping with three or more recordings**; NAAMP's 10-stop fixed-margin null is **not directly reproducible** with these recording units.

The independent scientific analysis was **predefined before inspecting any NPS frog detection outcomes**: `exploration/NPS_GLKN_BULLFROG_GREENFROG_HELDOUT_VALIDATION_CONTRACT_V0_4.md`. Expert-label QA (≥90% valid ManualCIV, ≤1% status discordance), site/park sample gates, deterministic whole-site geographic train/test partition, logistic M0 vs M1 with fixed water-regime/temperature/season controls, and 2,000 site-block bootstrap had all been frozen, with no NAAMP coefficients reused.

### Why analysis stopped after earlier source-only success

Original two NPS source-quality workflows retrieved and SHA-verified the correct 68,581,307-byte published CSV. Subsequent NPS response-bearing model run [39772267174](https://github.com/zuizui0223/frogcs/actions/runs/39772267174) and single-bounded source retry [39772678418](https://github.com/zuizui0223/frogcs/actions/runs/39772678418) instead received **14,538 bytes** when requesting the same official file.

To distinguish transient full-transfer truncation from legitimate byte-range availability, [response-blind HTTP diagnostic 39773281318](https://github.com/zuizui0223/frogcs/actions/runs/39773281318) checked official HTTP HEAD, capped GET and first/last 1 KB Range:
- normal GET and HEAD returned **HTTP 200**, `Content-Type: text/html; charset=utf-8`, **14,538-byte HTML**;
- both requests with `Range: bytes=...` likewise returned **HTTP 200 HTML** (no `Content-Range`, no 206);
- the file's exact-source SHA is therefore **unverified in the response-analysis runs**, and **no valid frog calling outcome row was read**.

Official source failed its transport gate, so **do not proceed** to expert-status validation, source co-calling counts, training or biological conclusions. No attempts to bypass website protection or use unverified mirrors should be made.

Frozen diagnostic `exploration/NPS_GLKN_INDEPENDENT_RESPONSE_ACCESS_GATE_V0_5.json`. The earlier verified source-only *metadata coverage* remains credible, but it **cannot** substitute for the missing expert-labelled observations.

## Current inference hierarchy

| Test / level | Evidence state |
|---|---|
| NAAMP: species-specific calling association with mapped emergent wetland habitat | Exploratory taxon-level association in five units |
| NAAMP: spatial pairwise residual beyond NWI and prior-year physical site use | Internally supported for selected same-route-run CI1–3 taxon configurations |
| NAAMP: bullfrog identity adds prediction of greenfrog within-route allocation in heldout routes | Internally supported in fixed-margin conditional pseudolikelihood |
| NAAMP: negative partner information adds beyond bullfrog | **Not supported** in the corrected v0.3 incremental test |
| NPS/Dryad independent model of the bullfrog–greenfrog relationship | **Not assessed: external source access blocked** |
| Aquatic macrophyte species → fish/odonate or frog trophic mediation | **Not observed; no causal conclusion** |

## Next actual scientific discriminator

External confirmation requires a lawfully accessible independent recording file with explicit species-specific *survey opportunity and negative call codes*, station/time metadata, and independently sampled parks/sites. A fixed plant/calling microhabitat manipulation with simultaneous acoustic recording and fish/odonate survey would test mechanisms but cannot be inferred from these archived acoustic detections alone.

If the identical NPS file later becomes officially accessible, the precommitted v0.4 source hash/outcome QA and model can be run unchanged. No threshold relaxation, unverified mirror or inferred missing-species absences.

## Repository boundary

All source-only receipts, preregistered analysis contracts, model code and access gate live on independent exploration branch `exploration/nps-glkn-independent-frog-network-2026-10-22`. **No modifications to JAE RC6 manuscript, Supporting Information, GitHub main, journal submission or published positive-claim provenance.**
