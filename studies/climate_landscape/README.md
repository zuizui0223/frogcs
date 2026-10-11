# Independent frog acoustic–hydrology study

**Current handoff — 2026-10-11. Status: BLOCKED — original matched recording and local-water data have not been obtained.**

This is the independent study in draft PR #135, not the frozen JAE RC6 manuscript. Source audits and the v6.5–v6.8 synthetic checks are complete. They do not establish a new effect in real frogs. No custodian email has been sent. Do not merge this work into `main` or reopen NAAMP analyses.

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
| H — local water history | Not obtained | Same-wetland dated depth/inundation history, datum, precision, calibration, gaps and shared-error information |
| D — detection validity | Not obtained | Source classifier/annotation versions and validation across species, water states and noise conditions |
| T — usable temporal support | Not established | Actual overlapping wetland coverage and repeated rising/receding episodes, with strictly earlier histories |
| R — use of underlying archive | Not established | Custodian, source version, applicable licence or permission and permitted non-sensitive outputs |

Distinct physical wetlands are the proposed sampling units, not a guarantee of statistical independence. Shared catchments, water deliveries and observation dates must still be represented in the design. Existing public metadata permissions do not automatically cover an unreleased audio/depth archive.

## Evidence already retained

The [v6.9 decision](V6_9_BIOLOGICAL_GO_LIMITED_STOP_AND_SOURCE_HANDOFF.md) separates source discoveries, legacy published-table descriptions and artificial counterexamples. The older frog-abundance table is not an authenticated multi-wetland audio/depth panel or a species-specific recruitment dataset.

The [v6.8 numerical receipt](V6_8_LOCAL_NUMERICAL_RECONSTRUCTION_AND_SYNTHETIC_STOP.md) records the completed [CI run 38108980247](https://github.com/zuizui0223/frogcs/actions/runs/38108980247). Its results are entirely synthetic: environmental history and measurement error can leave a predictive acoustic lag even when direct lag influence is zero. This is not empirical evidence of frog memory or a field power calculation.

## Next permitted work

Review the single enquiry and obtain original non-sensitive availability information through an explicitly approved route. Before any new response analysis, record which requirements are satisfied, fix source-specific quality rules and define temporal evaluation splits. Publicly exposed pilot summaries are not an untouched confirmation set. Without adequate source evidence, retain the LIMITED or STOP classification.

Do not add artificial scenarios, repeatedly probe denied APIs, infer wetland membership from descriptions or proximity, invent zeros, or change the frozen RC6 scientific package. General continuation does not authorize sending email, creating mailbox drafts or accepting new data-use terms.

## History

All original specifications, source receipts, scripts and numerical outputs remain at their existing paths. The [complete pre-consolidation status narrative](https://github.com/zuizui0223/frogcs/blob/e338b09f74dce1b024e887299b9af8e341265e37/studies/climate_landscape/README.md) is preserved at a fixed commit. Historical pending/queued statements describe their recording time, not the current state. This page is the current entrypoint; v6.9 remains the decision authority.
