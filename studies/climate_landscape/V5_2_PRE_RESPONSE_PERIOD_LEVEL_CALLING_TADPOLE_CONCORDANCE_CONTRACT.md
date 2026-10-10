# v5.2 — Frozen (before response patterns) period-level calling/tadpole *concordance*, Murrumbidgee

**2026-10-10 JST. Source-metadata-exposed design; response Y/N and tadpole-positive rates NOT consulted at the time of freezing.**
**Not preregistered before source discovery, and not an independent confirmation of RC6.** Study uses the public [Australian government Flow-MER Frog Abundance 2014–2022](https://data.gov.au/data/dataset/flow-mer-frog-abundance), government CKAN resource `70f3b7c9-990b-4770-b306-57c4e7cdac61`. No editorials or outcomes should be selected after seeing the estimates. JAE RC6 is locked on main and must not change.

## Source-grounded observed metadata exposure before freezing

Previously retrieved source-only checks verified:
- 673 total public rows, 591 in **Murrumbidgee**, 36 Gwydir, 46 Lachlan;
- Murrumbidgee **581 rows with a strictly positive period >31 days, 10 zero-length start=end rows** (exclude the 10 from the primary analysis); other two regions not primary;
- Murrumbidgee **152 unique speciesCode×SamplePoint pairs**, **83** observed on ≥2 distinct positive-duration periods and **80** on ≥3 periods; **12 sites with multiple intervals**; **one duplicate same site×species×period key** (do not automatically choose a preferred record);
- all 673 published rows have nonmissing `callingEvidence`, `CPUETadpoles`, `CPUEAdults`; codes are Y/N and numbers are finite/nonnegative. **Frequencies of Y/N and nonzero tadpole CPUE were not reported or used in design choice**.
- public dictionary calls `callingEvidence` *Y/N frogs of speciesName heard calling* and `CPUETadpoles` a mean **catch per unit effort**. It does **not** say a calling detection preceded or caused the tadpole count, nor provide a wet/dry hydroperiod, specific five-minute call strength, or independently verified surveillance zero for all unlisted taxa.

## Frozen inclusion and observational unit — NOT rainfall responses

**Primary frame:** `Program == "Murrumbidgee River"`, `sampleDateEnd(Date/Time) > sampleDateStart` with **duration >31 days**, nonblank `SamplePoint`, `speciesCode`, `SampleDate`, `callingEvidence in {Y,N}`, numeric finite nonnegative `CPUETadpoles`.

**Canonical observation key:** `(Program, SamplePoint, speciesCode, sampleDateStart, sampleDateEnd(Date/Time))`. Reject **ALL** records belonging to keys with >1 record from primary frame, not an arbitrary first/last row; report excluded groups and records. `SampleDate` is a record timestamp and can be used only as a source-identity check, not as true survey time. Sensitivity: including the 10 start=end rows only after verifying their status, **report separately; do not mix with the primary effect**. We currently prefer **exclude them entirely** rather than reinterpret.

**No missing-row zeros:** an absent species in a site-period that has other species rows is **NOT** an observed silence or tadpole zero. Only Y/N and CPUE on **explicit published species rows** contribute to the comparison.

## Frozen outcomes and descriptive contrasts

Let `C=1` for `callingEvidence == Y`, else `C=0` for N. Let `T=1` only when `CPUETadpoles > 0` (measured effort-based positive), else `T=0` for numeric zero. An observed `T=0` is a negative **listed-row tadpole index**, not independently proven tadpole absence or unsuccessful breeding.

1. **Primary**: complete 2×2 counts `n(C=0/1,T=0/1)`, the two conditional source-row proportions `P(T=1 | C=1)` and `P(T=1 | C=0)`, **risk difference** `Δ=P(T=1|C=1)-P(T=1|C=0)`. Do not calculate or interpret if either calling category absent. The two biologically useful *discordant source categories* are `C=1,T=0` (heard calling, no tadpoles caught on row) and `C=0,T=1` (tadpoles caught, no calls recorded on row). They are **not proven failed/hidden breeding**.
2. **Predeclared precision check**: cluster resample by **SamplePoint** with replacement, 1000 replicates with fixed seed **20261010**, retaining all rows of each site, compute empirical percentile 95% interval for `Δ` if both categories survive. Discard bootstrap draws lacking either category and report valid-draw count. This is a **descriptive site-cluster sensitivity interval**, not a population-representative causal CI; number of unique sites is shown.
3. **Independent-variation gate**: group by site×species across **distinct positive-duration intervals** and count pairs represented in both C=Y and C=N states. Only if at least **10 such pairs** and at least **20 interval rows** in those eligible pairs, display an **equal-pair-weight within-species×site mean difference** in tadpole-positive fractions between each pair's Y and N intervals. Otherwise **NOT ESTIMABLE**. No significance test for this exploratory within-pair statistic.

These choices are frozen **before reading Y/N and tadpole-positive frequencies**, not after observing a favorable sign or magnitude. Do not optimize site/species/time subsets or compare alternative thresholds.

## Scientific interpretation constraints

- The study answers only whether *observed calling status and a tadpole CPUE-positive index are concordant within the same published LONG observation interval*, with optional within-site/species temporal comparisons.
- The authors originally designed Flow-MER for annual frog monitoring; source interval metadata show >31-day spans in Murrumbidgee, so **do not** call these instantaneous censuses, rainfall pulses, event-to-offspring survival, or active vs silent habitat switches after a storm.
- A positive concordance could arise from true reproduction, stable site suitability, detection effort, the species' phenology, site/hydrological variation, or the original aggregation itself. A null/negative association similarly says **nothing causal** about rain or evolutionary memory.
- No independent full 5-minute visit ledger, surveyed-but-unlisted species table, local hydroperiod or source-crosswalk to Ocock's 343 surveys has been verified.
- Do not conflate multiple species rows from a shared interval with independent rain events. Clustered uncertainty reflects site reliance but not all shared time/species effects.
- Do not display/release any source site names, species codes/names, latitude/longitude, per-record response values, or any subset with identifiable sensitive locations. Persist **only site-anonymized totals** and CI provenance.

## Required implementation receipt

Publish an aggregate-only GitHub Actions receipt with official resource ID, extraction date, group totals, duplicate/invalid/zero-length exclusion counts, 2×2 table, risk-difference and optional within-pair result, plus noncausal caveats. A failed/zero-contrast result is equally important and **must not** be rescued by searching taxon subsets. If this data source is inadequate, close the Flow-MER avenue for frogcs mechanism and reserve original rain/visit/hydro data access for a future authorized study.
