# v6.1 — Public hydrology sources versus ORIGINAL recorder–wetland–depth joins: a falsifiable external-study gate

**2026-10-10 JST, independent frog study PR #135; source-coverage synthesis after source discovery.** This is not a new preregistration, a new animal response result, or a modification of the JAE RC6 paper. `main` remains frozen. The prior v6.0 report documents the government's 2016–2025 Murrumbidgee archived audio and August 2026 four-wetland pilot; this note tightens the **hydrological temporal and ecological-unit joining problem**.

## 1. Actual official public source hierarchy

| Source and original URL | Directly verified meaning/grain | What it does NOT authenticate |
| --- | --- | --- |
| [Government Murrumbidgee 2024–2030 area-scale evaluation plan](https://www.dcceew.gov.au/sites/default/files/documents/flow-mer-murrumbidgee-area-scale-evaluation-research-plan-2024-30.pdf), §5.6 | The programme explicitly describes acoustic monitors **deployed alongside depth loggers** for wetland hydrological regimes and long-term record analysis; this is a *programme design/method statement* | No machine-readable `recorder ID × depth logger ID × independently bounded wetland ID × timestamp` matched series, no proof every archive station has valid paired depth readings |
| [Government 2025–26 implementation plan](https://www.dcceew.gov.au/sites/default/files/documents/flow-mer-murrumbidgee-annual-implementation-plan-2025-26.pdf), §6.3 | Historical 2016–2025 archive, 12 long-term recording stations, mostly archived 5 min/hour, some continuous; recogniser development in four initial wetlands | Not 12 contemporaneously sampled independent ponds, complete audio validity, public availability, a frozen detection classifier, or validated source depth logs |
| [Government annual CEW wetland/floodplain inundation frequency](https://data.gov.au/data/dataset/flow-mer-cew-inundation) | Landsat/Sentinel-based **annual frequency** of selected Commonwealth environmental-water wetland/floodplain inundation | Not exact recording-hour water depth, precise time of water arrival at the frog recorder, or all-water-source wetness; excludes natural flooding and some other water |
| [Government daily flows with CEW component](https://data.gov.au/data/dataset/flow-mer-daily-flows-with-cew-component) | **Daily river-gauge ML/day** plus modeled contribution attributable to Commonwealth environmental water | A river gauge is not the same physical observation unit as local wetland depth/inundation at a recorder; a gauge hydrograph must not be renamed local wetland exposure |
| [Government Flow-MER Vegetation Community Structure](https://data.gov.au/data/dataset/flow-mer-vegetation-community-structure) | Plot/transect vegetation and observed inundation; published dictionary defines `samplePointName` as a **complex of wetlands or streamside area** that may have internal sampling units and trip/date data | Its complex `samplePointName` is NOT automatically the 2014–22 frog `SamplePoint`, MDMS `NAME`, recorder pseudonym or independent wetland. No valid cross-dataset source join established |
| [Government MDMS sample-points GeoJSON + metadata](https://data.gov.au/data/dataset/mdms-monitoring-locations) | An authentic monitoring-*point* lookup; official PDF establishes `NAME` as sample-point name and `DESCRIPTIO` merely an optional description (v5.8) | Original physical independent wetland membership, stationary year-by-year recorder location or one-point-per-wetland sampling |
| [Basin-scale Evaluation and Research Plan](https://www.dcceew.gov.au/sites/default/files/documents/flow-mer-basin-scale-er-plan.pdf), Data Register section | Establishment of a secure source/rights/metadata **Data Register** and potential public searchable metadata index was part of the programme plan | Whether a public index **has been implemented and covers the acoustic file deployment/QA inventory** is not confirmed |

All claims above are **source meaning**, not successful joins or real frog/hydrology tests. This is a source-type distinction to prevent false exposure assignment from public water proxies. A public dataset's stated 2014–2023 coverage must not be conflated with frog audio in 2016–2025.

## 2. The minimal real join — six required keys, not names or GIS proximity

**Ecological unit**: `wetland_id` is an authenticated independent physical wetland (not a recorder, MDMS Point, plot, descriptive field or broad programme). Needed aliases: `recorder_id`, `depth_logger_id`, `source_samplepoint_id` (if any), year-specific effective dates, instrument moves/retirements, multiple sensors per wetland.

**Actual observation denominator**: `recorder_id × start_timestamp_local × stop_timestamp_local × quality/status`, including valid recording intervals **with no species call** and explicit `missing`, broken recorder, poor-quality audio, storm-noise or covered microphone status. Clocks, DST/timezone and 5-min/hour sampling duty cycle must be source documented. Continuously sampled units must not masquerade as equivalent to hourly samples without matching effort.

**Local hydrology**: `depth_logger_id × timestamp × water_depth_or_inundation_status × calibration/quality`, same time basis, known datum/dry threshold and deployment gaps, in the *same wetland* as corresponding recorder, without substituting river discharge or annual raster frequency.

**Classifier & manual validity**: `recording_interval × species × calibrated acoustic score/annotation`, human validation and species-specific FPR/FNR against water/noise regime, model version and effort. Automatically scored absence is not a biological silence until detection performance is defensible.

**Prior history**: `species × authenticated wetland × historical year`, derived ONLY from earlier valid audio opportunities, before forecast year/event. Do not use any later records or already exposed 2026 four-wetland results to choose site history thresholds.

**Data rights & provenance**: archive ownership, source version, permissible derived output, sensitive location policies, approved data use and reproducible source IDs. The programme's Data Register is a promising original metadata route but not verified as accessible.

## 3. Decision matrix before ANY frog response read

| Gate | Required evidence | Without it |
| --- | --- | --- |
| W — Wetland identity | Original recorder→wetland mapping with independent wetland clustering and year-specific moves | No multi-wetland Q2/Q3 or wetland-clustered SE; one-site description only |
| O — Opportunity | Time-indexed good/bad/missing recordings with valid negative listening exposure | No valid silence→calling or absolute detection rate |
| H — Hydrology | Within-wetland water depth/inundation aligned to genuine recording intervals | No ability to reject local-water sufficiency; cannot label river-flow/annual raster substitute “controlled local depth” |
| D — Detection | Species classifier validation and false-negative/error behaviour across wet/dry, seasonal and noise conditions | Do not interpret classifier non-detection as biological acoustic silence; report feasibility only |
| T — Time & repetition | Independent wetlands and multiple distinct future years/events with genuinely overlapping recorder effort | No robust cross-wetland claim; a four-wetland descriptive pilot is not independent replication |
| R — Rights & origin | Explicit access/redistribution approval, source provenance, safe pseudonyms | No source acquisition or public reuse until authorized |

**Assessment as of 2026-10-10:** The sources establish archive **existence** and an *intended/used* audio–hydrology monitoring design. They do not establish completed gates W/O/H/D/T/R for a reusable frog taxon × wetland × timestamp panel. Hence **external replicate remains NOT VERIFIED**.

## 4. Distinguishing biology from repeated statistical bookkeeping

The public 2026 pilot already reports stronger calling in watered wetlands, so the outcome *watered → calling* is not a novel discovery. An independent analysis must separate two predictions using future withheld records:

- **Baseline (H0, hydrology and stable propensity sufficient):** calibrated species acoustics are predicted by local inundation/depth history, recent water change, solar/time of night, season, recording quality, species and **historical stable wetland-specific propensity**. Train only on earlier years/events.
- **Extra-history prediction (H1):** lagged **species-specific chorus-use history** improves out-of-year prediction of the *configuration across genuinely separate wetlands*, over that baseline. If `species × wetland` historical propensity is already represented by the baseline, never add an algebraically redundant historical-site indicator and call that a mechanistic gain. A genuine incremental history variable must encode additional time-varying/episode-specific information (e.g., changes in use following comparable historical water episodes) beyond a static intercept.
- Avoid pseudo-replication: observational units are wetland × hydrological episode or wetland × independent date (with serial/cluster uncertainty), **not individual five-minute clips**. Assign entire events/years to train vs test. Predefine score, partitions, exposure/effort thresholds and ecological unit after non-outcome metadata and **before any new species-call response read**. A classifier's selection/training overlap must also respect this split, otherwise the holdout is leaky.
- Primary performance endpoint, *only if metadata gate passes*: paired **held-out predictive log-score** or Brier-score difference for the same wetland × time outcome under baseline vs extra-history model, aggregated at independent event/wetland units; quantify uncertainty clustered by wetland and event. No positive threshold or biological effect is currently asserted.
- Exploratory secondary: given a realized number of active wetlands `k`, conditional placement versus fixed site propensities can be a prediction check; it is **not a causal water-effect estimand** because `k` is itself post-exposure.

A significant gain would establish conditional **forecast information**, not individual memory, adaptation, hydrological causality, taxon movement or reproductive payoff. A non-gain with sufficient power would support the sufficiency of measured hydrology/stable propensity for that data frame, not all frog species universally.

## 5. Smallest remaining real-world step

The existing [v6.0 unsent official source inventory enquiry](V6_0_CEWH_ACOUSTIC_HYDROLOGY_SOURCE_INVENTORY_REQUEST_UNSENT.md) is amended to ask specifically for the **recorder × logger × wetland-year non-sensitive key**, opportunity/quality manifest and original data catalog/register reference. No protected coordinates, raw audio, unpublished frog responses or correspondence are needed yet.

**NO email sent. NO source data acquired. NO NAAMP or public 579-row frog outcome refit. No change to RC6/main.** The source-only feasibility gate can be finalized before asking for any frog signal values.

## 6. Executed **synthetic-only** ecological-unit source preflight

[GitHub Actions run **38056545252 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38056545252) executed [`scripts/preflight_audio_depth_unit_manifest_v61.py`](scripts/preflight_audio_depth_unit_manifest_v61.py) on deliberately fabricated recorder/depth opportunities. **No real wetland site, acoustic event or water-level value was queried.**

The tests demonstrate the correctness of source-preflight bookkeeping, **not biological inference**:
- **3 recorders mapped to only 2 independently declared wetlands** yield 2 wetland units, not 3 independent replicates;
- a missing audio opportunity stays **MISSING**, not an absence of frogs;
- missing logger timestamps prevent a valid `audio × water` paired unit from being counted;
- concurrent contradictory recorder→wetland assignments, missing timezone information and undefined time-match tolerance **fail closed**;
- all output is aggregate, without recorder, wetland or logger labels. Declared wetland identities still require real original-source authentication.

The preflight requires an explicitly source-defined timestamp tolerance rather than choosing one to produce a favourable matched sample. The code has not passed a real source metadata preflight and does **not** establish there are 2, 12 or any other number of independently sampled wetland units in Murrumbidgee.

