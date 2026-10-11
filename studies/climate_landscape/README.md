# Independent frog acoustic–hydrology study

**Current handoff — 2026-10-11. Status: BLOCKED — original matched recording and local-water data have not been obtained.**

This is the independent study in draft PR #135, not the frozen JAE RC6 manuscript. Source audits and the v6.5–v6.8 synthetic checks do not establish a new effect in real frogs. No custodian email has been sent. Do not merge this work into `main` or reopen NAAMP analyses.

## Biological target

**First question:** at comparable local water depth, does calling differ between rising and receding water, with season, solar time and recording quality represented?

**Conditional second question:** does calling in a strictly earlier wetting episode improve later-episode forecasts beyond local hydrological history, persistent species–wetland differences and measurement uncertainty?

These are untested observational questions. A positive forecast gain would not identify individual memory, social facilitation, adaptation or reproductive success.

## Start here

| Active document | Purpose |
| --- | --- |
| [Biological GO / LIMITED / STOP decision](V6_9_BIOLOGICAL_GO_LIMITED_STOP_AND_SOURCE_HANDOFF.md) | Required source evidence, restricted alternatives and interpretation boundaries |
| [Single metadata enquiry — UNSENT](V6_0_CEWH_ACOUSTIC_HYDROLOGY_SOURCE_INVENTORY_REQUEST_UNSENT.md) | Three initial availability questions; author review and a separate sending decision are required |
| [Canonical newer frog source and access boundary](V6_3_REAL_CANONICAL_FROGS_SOURCE_AND_403_STOP.md) | Correct source identity; the prior HTTP 403 did not retrieve a newer observation table |

## What remains missing

| Requirement | Current state | Minimum useful original evidence |
| --- | --- | --- |
| W — physical units | Not authenticated for the acoustic panel | Recorder–logger–physical wetland mapping with effective dates, moves and multiple instruments per wetland |
| O — recording opportunities | Not obtained | Scheduled/valid/missing/uncertain intervals, duration, clocks and quality; missing recordings are not silence |
| H — original local water history | Not obtained | Same-wetland dated logger history, datum, precision, calibration, gaps and shared-error information; the nine public display values below are not this record |
| D — detection validity | Not obtained | Source classifier/annotation versions and validation across species, water states and noise conditions |
| T — usable temporal support | Not established | Actual overlapping wetland coverage and repeated rising/receding episodes, with strictly earlier histories |
| R — use of underlying archive | Not established | Custodian, source version, applicable licence or permission and permitted non-sensitive outputs |

Distinct physical wetlands are the proposed sampling units, not a guarantee of statistical independence. Shared catchments, water deliveries and observation dates must still be represented in the design. Existing public metadata permissions do not automatically cover an unreleased audio/depth archive.

## Evidence already retained

The [v6.9 decision](V6_9_BIOLOGICAL_GO_LIMITED_STOP_AND_SOURCE_HANDOFF.md) separates source discoveries, legacy published-table descriptions and artificial counterexamples. The older frog-abundance table is not an authenticated multi-wetland audio/depth panel or a species-specific recruitment dataset.

The [v6.8 numerical receipt](V6_8_LOCAL_NUMERICAL_RECONSTRUCTION_AND_SYNTHETIC_STOP.md) records the completed [CI run 38108980247](https://github.com/zuizui0223/frogcs/actions/runs/38108980247). Its results are entirely synthetic: environmental history and measurement error can leave a predictive acoustic lag even when direct lag influence is zero. This is not empirical evidence of frog memory or a field power calculation.

### Public Nap Nap example: actual display assets verified, original records still missing

The [original presentation](https://media.flow-mer.org.au/napnap/) covers 30 August–7 September 2020 at one wetland. The [creators' article](https://journals.sagepub.com/doi/10.1177/14744740231197813) describes selecting the managed-water-arrival period through visualisation. It is a selected communication case, not an outcome-blind evaluation window.

The bounded public-asset inspection on 2026-10-11 progressed beyond the earlier text-only check. [Actual execution 38126439272](https://github.com/zuizui0223/frogcs/actions/runs/38126439272) and the [compact source receipt](receipts/NAPNAP_PUBLIC_DISPLAY_ASSET_INVENTORY_2026_10_11.json) establish:

| Verified public presentation property | Source-supported result | Limit |
| --- | --- | --- |
| Embedded `daysData` | Nine dated objects, each with `audio`, `date` and one numeric `depth` value | No hourly logger series or within-day observation timestamp; the daily statistic is undocumented |
| Water display | The application uses `Math.floor(da.depth*100)` and the page labels cm | Display rounding is not instrument precision, calibration or measurement accuracy |
| Adjacent daily depth values | Seven increases, one decrease, no equal differences | Not proof of monotonic rise, nor an authenticated recession event or matched-depth rise/fall comparison |
| Daily audio assets | Nine source-constructed `audio/YYYYMMDD-stereo.mp3` URLs returned HTTP 200 and `audio/mpeg` to HEAD requests | No sound bodies downloaded; playback, actual duration, original clip completeness and quality were not tested |
| Playback time mapping | `hourIndex*300+offsetTime`; inverse uses `floor(seek/300)` | Each display hour indexes a 300-second sampled block, not continuous elapsed wall time |

The public interface thus supplies a day-level display mapping, not the original recording-opportunity ledger. Do not treat a daily MP3 as uninterrupted 24-hour monitoring, infer 216 verified valid recordings, convert unrecorded intervals into silence, or copy a daily depth value across hours as though it were independently measured at every recording. The server's 2025 file-modification dates are not the 2020 recording dates.

Only the public HTML/linked JavaScript, embedded daily display metadata and audio response headers were read. No JavaScript was executed, no audio bodies or acoustic-response labels were acquired, no protected locations were requested, and no denied CKAN endpoint was retried. The source script is SHA-256 pinned in the receipt. Inspection code is retained at [the execution commit](https://github.com/zuizui0223/frogcs/blob/3374d13339ea319b1d78123c6e2b84f2346cc4ee/.github/workflows/napnap_public_asset_inventory.yml); the one-off workflow can be removed from the active tree after completion without losing its provenance.

Keep this example **LIMITED to presentation/source feasibility**. The longer underlying archive may contain the necessary repeated episodes, calibrated logger histories and valid recording ledger; this display does not establish them. No frog effect or independent validation has been computed.

## Next permitted work

Review the single enquiry and obtain original non-sensitive availability information through an explicitly approved route. Before any new response analysis, record which requirements are satisfied, fix source-specific quality rules and define temporal evaluation splits. Publicly exposed pilot summaries are not an untouched confirmation set. Without adequate source evidence, retain the LIMITED or STOP classification.

Do not add artificial scenarios, repeatedly probe denied APIs, infer wetland membership from descriptions or proximity, invent zeros, or change the frozen RC6 scientific package. General continuation does not authorize sending email, creating mailbox drafts or accepting new data-use terms.

## History

All original specifications, source receipts, scripts and numerical outputs remain at their existing paths. The [complete pre-consolidation status narrative](https://github.com/zuizui0223/frogcs/blob/e338b09f74dce1b024e887299b9af8e341265e37/studies/climate_landscape/README.md) is preserved at a fixed commit. Historical pending/queued statements describe their recording time, not the current state. This page is the current entrypoint; v6.9 remains the decision authority.
