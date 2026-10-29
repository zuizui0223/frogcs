# NEE external raw-data audit — 2026-10-29

## Decision

This audit retrieves original public files and checks their observation/design structure; **no model was fitted**. Hossie et al. provide immediately usable dragonfly–two-tadpole raw experiments. They do **not** identify salamander frog handling (FF) versus salamander dragonfly handling (FD). Urban et al. provide salamander–Daphnia metadata, but the workbook download failed. Carroll et al. are the strongest newly located calling–larval candidate, with potentially relevant predator bycatch; raw download and absent adult-input dependencies currently prevent calibration. None closes the full G2/G3 gates.

All retrieved source bytes and SHA256 receipts are in `research/results/nee_external_followup_20261029/`; `source_receipts.json` records exact URLs, byte counts and hashes. `csv_schema_audit.json` records actual CSV dimensions, fields, ranges and missingness. Download errors were not saved as purported data.

## 1. Hossie et al. 2021: actual raw data retrieved

Sources: [original article](https://doi.org/10.1038/s41598-021-86080-x), [versioned dataset](https://doi.org/10.6084/m9.figshare.14346557.v1), [original metadata API](https://api.figshare.com/v2/articles/14346557), [original article XML mirror](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7991668/fullTextXML). The dataset includes its own `Metadata - Hossie et al 2021 Sci Reports.pdf`. Files are CC BY 4.0.

Predators are late-instar Aeshnidae; prey are Gosner-25 Lithobates pipiens and Anaxyrus americanus. Do not relabel the predator as species-resolved Anax. There is no salamander, vegetation treatment, calling, or temporal stage crossover. Total prey counts 6/12/24/60, predator counts 1/3/6, and seven prey ratios formed 168 trials over four days (two replicates per treatment). Daily allocation was stratified-random. Physical contact among dragonflies occurred; killed predators were replaced in three trials. Counts measure killing, not necessarily consumption.

| File | Actual rows × columns | Main fields and observation unit |
|---|---:|---|
| multiprey_L_1h.csv | 144 × 10 | Trial, Time, LeopStart, ToadStart, numPredators, N_P_Leop, LeopRemaining, ToadsRemaining, L_killed, prop_L_killed; one trial endpoint, excludes toad-only |
| multiprey_T_1h.csv | 144 × 10 | Trial, Time, LeopStart, ToadStart, numPredators, N_P_Toad, LeopRemaining, ToadsRemaining, T_killed, L_killed; excludes leopard-only |
| multiprey_PreyPreference.csv | 120 × 13 | initial/remaining counts, predator count, total and prey ratios, per-capita kills, diet proportions; mixed-prey 3-hour endpoints |
| Multi-prey_SurplusKilling.csv | 166 × 11 | initial counts and predator count; L_waste/T_waste are carcass counts, with less than half consumed, after 3 hours; two missing trials omitted by authors |
| toad_palatability.csv | 36 × 17 | two prey presented sequentially; prey identities, Treatment LL/LT/TL/TT, strike/capture/consumption timings, strikes, initial/consumed masses and fractions |

CSV numerical ranges/column names are recorded exhaustively in the schema JSON. Masses in the sequential experiment are grams according to the paper. Timing units in its CSV are not explicitly stated in the included metadata; do not silently assign units to tStrike/tCapture/tConsume before checking the original table labels. These sequential trials used different predators and larger prey than the functional-response trials, so they cannot be joined as individual-level observations.

### Design safeguards and conditional contrasts

- `Time` is **2 in every 1h CSV row**, but both the author metadata and original methods explicitly identify these endpoints as **one hour**. The numeric code is undocumented; it is not evidence of two elapsed hours.
- `Trial` ranges 1–14 and repeats. It is not a globally unique tank identifier, experimental day, or independent replicate label.
- The key `(Trial, Time, LeopStart, ToadStart, numPredators)` is unique within each 1h file. Exactly **120 keys match between L and T**, representing the same mixed-prey experiments; stacking files as independent trials would pseudoreplicate. The union is 168 keys.
- Missing ToadsRemaining in L (24 rows) occurs exactly when ToadStart=0. Missing LeopRemaining and L_killed in T (24 rows) occurs exactly when LeopStart=0. These are structural absences; retain provenance if deriving zero alternate-prey kills.
- Each side has 48 distinct `(focal initial count, predator count)` combinations. **21** have 2–3 alternative-prey levels. Thus fixed-focal/fixed-predator conditional contrasts are possible within support, but this is not a full independent factorial of both prey counts. For example, matched focal counts include 2, 4, 6, 8, 10, 12, 20 at predator counts 1/3/6. Day/tank identities are unavailable. The source describes single-prey and mixed-prey levels within the same functional-response experiment, not separate years/protocols; only the sequential palatability experiment is separate. Unequal alternative-prey increments mean a mean of stratum-specific min/max differences is not a balanced treatment effect.
- Density-dependent prey depletion must be retained. These endpoints identify candidate functional response shapes and mixed-prey effects under specified models; they do not directly measure how much of shared feeding time each prey consumes during those same trials.

**Relevance:** this is an edge-level check of dragonfly predation and alternative tadpole effects, not a direct check of salamander FF/FD. Previously used literature must be disclosed; a withheld raw condition can constrain a model but is not an untouched external discovery. These data cannot decide vegetation functions or the three macro interactions.

## 2. Urban et al. 2020: public metadata, raw retrieval failed

Sources: [paper](https://doi.org/10.1098/rspb.2020.1665), [Dryad](https://doi.org/10.5061/dryad.j0zpc86cd). The saved metadata names `Urban_PrSB_functional_response_data.xlsx`, 21,393 bytes, repository SHA256 `f106c7f7cb91f4cf877ebb70bfac2240f22b013c5edad11165cf06f5b5db11b6`. API download `/api/v2/files/839314/download` returned HTTP 401; public `/downloads/file_stream/839314` returned HTTP 403. **No workbook was obtained and no rows were counted.**

Metadata describes Ambystoma maculatum larvae feeding on **Daphnia**, not tadpoles or dragonflies. Variables: `rep`, `pred.risk`, `cue`, `vase`, `family`, `food.given`, `food.eaten`, `wt`; prey are numbers initially offered/eaten in 24 hours and wet mass is mg. This can constrain general salamander functional-response variation, including cues and population origin. It cannot identify separate frog and dragonfly handling terms, and numerical Daphnia parameters must not be transferred as frog/dragonfly values.

## 3. Carroll et al. 2023: promising stage bridge, incomplete accessible package

Sources: [Oikos paper](https://doi.org/10.1111/oik.09773), [Dryad dataset](https://doi.org/10.25338/B8G92P), [author code on Zenodo](https://doi.org/10.5281/zenodo.7596609). Metadata and original R code were downloaded; code was read as evidence, not executed.

The study pairs adult calling and larval observations at eight Texas ponds across 2001–2006. Daily calls summarize six one-minute recordings, capped at 30; weekly larvae come from two funnel traps per pond. This is an activity/capture-index bridge, not absolute density or survival. The reported taxon sets differ between collection and analysis, so do not impose a single species count before raw inspection. Site-year seasonal timing and overwintering matter.

Dryad lists only `funneltrapdata.xlsx` (196,918 bytes) and README (2,963 bytes). Both public file streams returned HTTP 403; exact raw columns, dimensions, sample rows and actual predator detection counts remain **unverified**. File list and metadata are saved. No evidence that lack of access means absence of data.

The downloaded `funneltrapdata_finalanalysis.R` provides these inspectable pointers:

- Lines 52–62 read pond1 through pond8 Excel sheets.
- Lines 82–129 expect DATE and tadpole species columns including R.sph, R.cla, R.cat, P.cru, H.ver, R.pal, H.cin, G.car, B.woo, B.val, P.tri; they derive Year, Pond, Sp, doy, Count. These are **code-expected fields**, not verified workbook headers.
- Lines 112–114 exclude `Naiad`, `Newt`, `newt.larvae`, `A.talpoid`, `mole.sala.larvae`, `A.texanum` and other aquatic taxa from the frog analysis. This makes the source promising for predator/stage bycatch. Do not assume Naiad means Odonata specifically, or that these columns contain nonzero observations, until README/raw data establish it.
- Adult_count is used at line 404 without a preceding creation/import in the deposited script. Later lines 504 and 540 require manually prepared AdultRelativeFixed.xlsx and Adult_needstag_fixed.xlsx, absent from published file inventories. The listed raw workbook could conceivably have additional sheets; contents have not been inspected. It is therefore premature to assert the acoustic data are completely absent, but their reproducible import is missing.

### Pre-specified next test if paired data become available

Use species × pond × biologically defined breeding season as the unit. Predict subsequent weekly larval occurrence/capture index and timing from preceding calls, keeping zero-call and zero-larva seasons rather than conditioning only on both being detected. Avoid training/test splits across days from the same breeding event; withhold ponds or whole years. Compare lagged call information against species-specific seasonal and pond baselines. Report capture-index and timing calibration separately from density calibration. Adult calls and larvae may represent different cohorts, and trap catchability/overwintering prevent a naive survival ratio. Predator bycatch, if validated, can add stage co-occurrence, but not individual encounter or consumption rates. Vegetation and measurement effort remain separate requirements.

This candidate cannot currently be used to fit a defensible calling–larval bridge, and cannot close G2 until the raw acoustic inputs and linkage are verified. It cannot independently validate the entire macro mechanism (G3).

## 4. Davenport & Chalcraft 2013

The [original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3790551/) lists supporting literature, supplementary methods and planned-contrast ANOVA tables. No trial-level machine-readable raw dataset was identified in this bounded audit. Its documented newt–tadpole and caged Anax pathway is biologically relevant, but summary ANOVAs must not be represented as independent individual experimental observations.

## Remaining discriminating evidence

Direct FF-versus-FD testing requires a salamander predator with frog and dragonfly prey independently varied, stage/size measured, both prey removals retained, and ideally attack/handling observations. Single-prey saturation alone cannot identify alternative-prey time allocation. Vegetation protection of frogs versus salamanders requires separate recipient-specific contrasts. No retrieved file meets that joint requirement. Next analysis should use Hossie only for its actual dragonfly edge; pursuing a complete Carroll raw package could make a more substantial G2 advance.
