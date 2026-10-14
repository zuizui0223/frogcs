# v5.1 — Actual Flow-MER frog record grain rules out acute rainfall/larval causal timing

**Audit date: 2026-10-10 JST. Independent source-only research; JAE RC6 remains locked on main.**
The real government Flow-MER 2014–2022 source has been queried using **only a nine-field projection**, with no coordinates, site-name output, species identity/name output or model fitting. `callingEvidence`, `CPUEAdults` and `CPUETadpoles` were tested only for code/value *validity*, not Y/N frequencies, abundance distributions or inter-variable associations.

## Verified live outcome-blind source readout

Official [Flow-MER frog abundance catalogue and metadata](https://data.gov.au/data/dataset/flow-mer-frog-abundance), Australian Commonwealth Environmental Water Holder. Published data dictionary distinguishes:
- `SampleDate`: unique date-time stamp identifying a data record;
- `sampleDateStart`: start of period over which the measure is observed, inclusive;
- `sampleDateEnd`: end of observation period, exclusive (actual server field name **`sampleDateEnd(Date/Time)`**);
- `callingEvidence`: Y/N evidence a **listed** frog species was heard calling;
- `CPUEAdults`, `CPUETadpoles`: mean catch-per-unit-effort, not a five-minute CI or successful metamorph count.

**Reproducible, actual 673-row source QC:** [GitHub Actions run 38011776073 — SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38011776073); code [`scripts/audit_flowmer_interval_and_event_grain_v51.py`](scripts/audit_flowmer_interval_and_event_grain_v51.py). This is a **real downloaded-data source-quality result**, not a regression or frog ecological result.

### Direct interval-duration and region results

| Government Program label | Rows with start→end ≤1 hour | Rows with start→end >31 days | Rows with **zero-length** start=end | All |
| --- | ---: | ---: | ---: | ---: |
| **Gwydir River System** | **36** | 0 | 0 | **36** |
| **Murrumbidgee River** | 0 | **581** | **10** | **591** |
| **Lachlan River System** | 0 | **46** | 0 | **46** |
| **Total** | **36** | **627** | **10** | **673** |

These are calculated from the actual public start/end timestamp fields. A zero-length range may be a source convention/quality issue rather than a nonexistent biological survey. The data dictionary says the end is **exclusive**, so such rows must be resolved with the custodian/source protocol before treating them as positive-duration listening events.

- All **673/673** real records had `callingEvidence`, `CPUEAdults` and `CPUETadpoles` values present in the earlier v5.0 source check. In v5.1, no unknown `callingEvidence` codes beyond allowed Y/N and no nonnumeric/negative/nonfinite CPUE values were detected. **This is not a complete absence/non-detection denominator.**
- Gwydir 2015–16: **12 unique site×start×end source groups**, four distinct interval boundaries; no ≥4-listed-site common-interval groups.
- Murrumbidgee 2014–22: **103 unique site×start×end groups**, 28 distinct interval boundaries, seven interval groups that contain rows from ≥4 site names. The **majority of these source rows aggregate a period >31 days**; one `site × speciesCode × start × end` combination is represented by more than one record. This need not be an error — `SampleDate` or an original visit/sample ID may distinguish them — but interval fields alone are **not** always a unique biological observation key.
- Lachlan 2015: **14 site×interval groups**, one shared interval and one source calendar date, all 46 rows with period >31 days.

Importantly, the study source's `SampleDate` record date and `sampleDateStart` dates were also checked separately. Same calendar date or common interval boundary is not proof of **simultaneously completed listening surveys**. The public resource contains **no precipitation, rain-sound level, local wetland depth, hydroperiod duration, verified complete five-minute survey denominator or source-matched metamorph follow-up** in its 16 actual fields.

## Ecological consequences: three honest decisions

### A. No acute cue → chorus mechanistic test from this resource

The overwhelming majority of Flow-MER rows are associated with intervals longer than one month. They do **not** form 627 independent short rain events or 627 temporally resolved paired chorus/tadpole observations. Without source-authenticated within-interval visit times and separately timestamped hydrology, a short rainfall/rain-sound pulse cannot be aligned with individual calling decisions or downstream larval outcomes.

The 36 short Gwydir source records cover only **six named sites, four source date groups, and 12 site×interval groups**, rather than the 15-site 2015–2020 original Ocock monitoring frame. They cannot support an independent reproduction of frogcs's route-scale `k≥4` spatial history mechanism.

### B. Possible narrower descriptive question, but requires *new* source-definition confirmation

The Murrumbidgee data may reflect longer-term species-level calling and tadpole indices across vegetation/habitat site groups. A modest association between *listed-species presence of calling evidence* and *tadpole CPUE* **at the original aggregated grain** might eventually be assessed, but it would **not** test rain sound, a known lag from call to tadpole, causal reproduction, or NAAMP-like chorus strength. Before such a study, verify whether the CPUE/YN values summarize **the same observation interval and effort** and whether Y/N=N is a proper sampled negative for **that listed species only**. A source-defined season/year grouping, effort and original sample IDs are necessary to avoid pseudo-replication.

### C. Recommended source acquisition priority

Unlike uninformative synthetic rearrangements, actual missing source fields are now clear:
1. one source-verified **site × genuine survey event × target species** opportunity table, with non-detection and survey effort retained;
2. exactly timed (not >31-day aggregated) audio / soundscape or original 5-minute CI, physical site, date/night and observer/detection status;
3. original local water depth/inundation/hydroperiod and actual precipitation/rain sound;
4. biologically lagged tadpole/metamorph records with stage-specific sampling effort and stable physical site links.

If these cannot be obtained, declare `ACUTE_RAIN_HISTORY_MECHANISM_NOT_IDENTIFIABLE_FROM_FLOWMER_PUBLIC_2014_22`. This is a **data-grain limitation**, not a negative finding about frogs or rainfall.

## Complete source QA/provenance boundary

- Source read: actual government CKAN public data resource `70f3b7c9-990b-4770-b306-57c4e7cdac61`.
- Raw projected columns used internally: `Program, SamplePoint, SampleDate, sampleDateStart, sampleDateEnd(Date/Time), speciesCode, callingEvidence, CPUEAdults, CPUETadpoles`.
- CI status: **SUCCESS**, with no-effect model; zero species-level value reports, zero raw geocoded outputs, zero individual row publication.
- The **10 zero-length rows** and **one duplicate interval-level site×species key** should be queried against field-protocol documentation before any outcome-stage treatment.
- The government source's long interval may be a valid *summary* of source measures and is not proof the original monitoring lacked fine-grained internal observations.
- JAE RC6 `main`: **unchanged**. No external data request, credentials, private wildlife coordinates, or response-stage regression conducted.

## Practical stop

**After this QC the next valuable step is not another interaction/p-value on the 673 published rows.** It is a choice of either (i) an authorized source-specific event-level survey/water/method request for a genuine rain-triggered mechanistic study, or (ii) a separate predeclared coarser-timescale association where the observation unit and interval semantics are explicitly grounded in original field protocols. This source cannot be relabeled a temporally independent spatial-chorus replication without those records.
