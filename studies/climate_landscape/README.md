# Independent frog acoustic–hydrology study

**Current handoff — 2026-10-11. Status: BLOCKED for ecological analysis — original matched recording and local-water metadata have not been obtained.**

This is independent draft PR #135, not the frozen JAE RC6 manuscript. No custodian email has been sent. Do not merge into `main` or reopen NAAMP analyses. Source audits and synthetic counterexamples do not establish a new effect in real frogs.

## New official source-management lead (reviewed 2026-10-12)

The [Murrumbidgee 2024–25 Flow-MER Annual Report (issued 22 January 2026)](https://www.dcceew.gov.au/sites/default/files/documents/murrumbidgee-mer-annual-report-2024-25.pdf), printed pp.22–23, 28, 63 and 98, identifies the original governance path that the public Nap Nap MP3s cannot supply. The Area team's **central Microsoft Access database** is described as authoritative for project **field data since 2014**. Hydrological and ancillary datasets are separately held as versioned, access-controlled project copies. A **Lead Data Manager**, **Data Quality and Systems Analyst** and **Spatial Data Manager** are defined roles; original exceptions may be marked by `qualityCode`/`evaluationCode`. These facts do **not** prove that raw autonomous recordings or their QA ledger are in Access.

The report describes depth loggers deployed across **35 wetland sites** in 2024–25 and derived **daily depth time series**; its earlier monitoring table describes 32 loggers. The nominal counts must not be treated as an authenticated overlap with the **12 historical frog recording stations**, or as 35 fully paired, independent wetlands. The 2024–25 realized frog field procedure was **6 × 2-minute human call surveys**, **2 × 20-minute visual surveys** and 9 wetlands. Larvae not identifiable to one of two `Limnodynastes` frog species were recorded as a **species complex**. These human surveys must not be silently pooled with the 5-minute/hour passive audio archive, nor generalized to all previous years. The report's description of shared NSW Saving our Species–Flow-MER raw audio is in the **bittern/waterbird workstream**, a possible custodian lead rather than a verified join to the frog recognizer archives.

**Next actionable evidence is specific:** ask the official CEWH contact to refer the [single updated UNSENT metadata enquiry](V6_0_CEWH_ACOUSTIC_HYDROLOGY_SOURCE_INVENTORY_REQUEST_UNSENT.md) to the **Lead Data Manager / Spatial Data Manager** and, if separate, the passive-acoustic archive custodian. Request existing identifiers/field dictionary and **non-sensitive year-by-year overlap counts**; do not seek institutional credentials or raw records. The fact that documented systems exist does **not clear** source gates W/O/H/D/T/R. Historical new-MDMS nonavailability was explicitly **as of 30 September 2025**, not a claim about current availability.

## Biological target

At comparable local water depth, does calling differ between rising and receding water, accounting for season, solar time and recording quality? Conditional on adequate source data, does calling in a strictly earlier wetting episode improve later forecasts beyond hydrological history, persistent species–wetland differences and measurement uncertainty?

These remain untested observational questions. Prediction alone does not identify memory, social feedback, adaptation or reproductive success.

## Start here

| Active document | Purpose |
| --- | --- |
| [GO / LIMITED / STOP decision](V6_9_BIOLOGICAL_GO_LIMITED_STOP_AND_SOURCE_HANDOFF.md) | Required source evidence and interpretation boundaries |
| [Single metadata enquiry — UNSENT](V6_0_CEWH_ACOUSTIC_HYDROLOGY_SOURCE_INVENTORY_REQUEST_UNSENT.md) | Three initial availability questions; separate author decision is required before sending |
| [Newer frog-source identity](V6_3_REAL_CANONICAL_FROGS_SOURCE_AND_403_STOP.md) | Canonical identity and earlier unsuccessful metadata access, not a newer observation table |
| [Public Nap Nap source receipt](receipts/NAPNAP_PUBLIC_DISPLAY_ASSET_INVENTORY_2026_10_11.json) | Dated HTML/script, HEAD, prefix and whole-file structural checks; historical scope retained |

## What remains missing for the proposed analysis

| Requirement | Current state | Minimum useful evidence |
| --- | --- | --- |
| W — physical units | Not authenticated for a multi-wetland acoustic panel | Recorder–logger–wetland mapping with effective dates, moves and shared instruments |
| O — recording opportunities | Not obtained | Scheduled/valid/missing/uncertain intervals, duration, original clocks and quality |
| H — original water history | 2024–25 *daily summaries* documented at some wetland loggers, but no source time series or acoustic join obtained | Same-wetland date-effective logger IDs, original timestamps, datum, precision, calibration, gaps and error dependence |
| D — detection validity | Not obtained | Annotation/classifier versions and validation across species, water states and noise |
| T — temporal support | Not established | Actual overlapping wetland coverage and repeated comparable rising/receding episodes |
| R — underlying archive use | Not established | Custodian, source version, applicable licence/permission and permitted outputs |

Distinct wetlands are sampling units, not a guarantee of statistical independence. Catchment, water delivery and date dependence still need to be represented. Public display access does not establish permission to use an unreleased underlying archive.

## Public Nap Nap example: format audit complete, source observation ledger still missing

The [original presentation](https://media.flow-mer.org.au/napnap/) shows one wetland over 30 August–7 September 2020. The [creators' article](https://journals.sagepub.com/doi/10.1177/14744740231197813) describes selection of the managed-water-arrival period through visualisation, not an outcome-blind evaluation window.

The checks below are cumulative, not competing descriptions of a single inspection. Earlier claims of no body download describe the earlier stages only.

| Inspection | Verified result | Remaining limit |
| --- | --- | --- |
| [HTML/script and HEAD check](https://github.com/zuizui0223/frogcs/actions/runs/38126439272) | Nine dated display objects, one depth value per day and nine responding daily audio URLs; seven display increases and one decrease | Daily statistic/time, calibrated water phase and original logger series remain unknown |
| [MP3 prefix check](https://github.com/zuizui0223/frogcs/actions/runs/38147734152) | 8 KiB per asset; MPEG-2 Layer III, 24 kHz, two encoded channels; no explicit frame-count tag in parsed prefixes | Prefix-derived size/bitrate duration was conditional, not a full count |
| [Whole-file frame-chain check](https://github.com/zuizui0223/frogcs/actions/runs/38148733736) | All nine complete public encoded bodies read transiently; each has 300,003 frames at 64 kbit/s and 24 kHz. Every byte belongs to the recognized outer metadata or contiguous frame chain | No audio decoding, payload/CRC verification, encoder-delay adjustment, source recording-quality or original timestamp validation |

Each complete file contains **108 bytes of leading ID3v2 metadata, 57,600,576 MPEG-frame bytes and 128 bytes of trailing ID3v1 metadata**, totaling 57,600,812 bytes. Counting frames gives **300,003 × 576 / 24,000 = 7,200.072 seconds of encoded frame capacity** per daily asset. This is not an authenticated gapless playback duration or valid field-recording time. The previous conditional size estimate, 7,200.088 seconds, included the 128-byte trailing tag as though it were audio.

All nine complete-file hashes differ, ruling out identical whole files, not repeated/padded intervals or identical acoustic content within them. No header-chain break or truncated final frame was detected under the tested parser. An undamaged compressed frame header does not establish an undamaged audio payload, and whole-file structural consistency does not establish completeness of the original observation schedule.

The latest check read **518,407,308 encoded bytes** across nine files in runner memory. No sound was decoded, played, uploaded or redistributed, no species labels were inferred and no private records or coordinates were requested. Only metadata/hashes are retained. The parser passed nine tests, including truncation and corrupt-sync rejection, and matched mutagen 1.47.0 on 84 header configurations. Exact one-off [execution code](https://github.com/zuizui0223/frogcs/blob/6b23387c3416ca1241f798b275ce63332adf66cd/.github/workflows/napnap_whole_mp3_structure.yml) remains at a fixed commit; it is not a new scientific model.

### Timebase and ecological boundary

The display uses `hourIndex*300+offsetTime`. Playback positions 299 and 300 seconds nominally map to 00:04:59 and 01:00:00. These are sampled blocks separated by unobserved time, not a continuously observed one-second transition. Uniform multiplication of playback time by 12 is also wrong. Original recorder timezone, clock calibration and daylight-saving handling remain unauthenticated.

Do not turn each daily two-hour encoded asset into 24 hours of continuous monitoring, assert 216 valid original clips, infer uninterrupted chorus durations across sampled-block boundaries, or replicate one daily display-depth value into independent hourly measurements. Missing, unrecorded, unvalidated and valid-no-call remain distinct; unknown values are not zero.

The bounded public-file format audit is now complete. Further file-format checks cannot establish the missing original recording/depth/quality ledger. Keep this example **LIMITED to presentation/source feasibility**. No empirical frog effect or independent validation has been computed.

## Evidence and next action

The [v6.9 decision](V6_9_BIOLOGICAL_GO_LIMITED_STOP_AND_SOURCE_HANDOFF.md) separates public-source discoveries, legacy table descriptions and synthetic results. The [v6.8 numerical receipt](V6_8_LOCAL_NUMERICAL_RECONSTRUCTION_AND_SYNTHETIC_STOP.md) records artificial counterexamples, not biological memory or field power.

Review the one enquiry and obtain non-sensitive source availability information through an explicitly approved route. Before new response analysis, document which requirements pass, fix source-specific quality rules and define temporal evaluation splits. The longer archive may contain the missing comparisons; this selected public example does not establish them.

Do not add artificial scenarios, repeatedly probe denied APIs, infer wetland membership from descriptions or proximity, invent zeros, or modify RC6. General continuation does not authorize email, mailbox drafts or acceptance of data-use terms.

## History

Existing specifications, receipts, scripts and numerical outputs remain at their paths. The [pre-consolidation narrative](https://github.com/zuizui0223/frogcs/blob/e338b09f74dce1b024e887299b9af8e341265e37/studies/climate_landscape/README.md) preserves earlier progress. Dated pending or no-download statements refer to their recording time. This README is the current entrypoint; v6.9 remains the ecological decision authority.
