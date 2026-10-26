# Frogcs v2: species occurrence first — source-native survey events

Decision 2026-10-26. This dated user-directed priority **supersedes stage-first harmonization as the active analysis**. Do not delete earlier ontogenetic files: life stage is optional source provenance, not a required grouping dimension for current analyses. All code and evidence stay in frogcs research; RC6 main/science remains completely frozen. This is post-readback exploratory research, not preregistration.

## One comparable analytical observation

**Source namespace × physical-source-site token × exact survey event × recorded species × survey method**. A separate projection aggregates the same rows to source × site × year × month × species × method, with **number of assessed surveys**, number recorded present, number explicitly assessed but not reported, unknown, the numerator and denominator. Collapse multiple life-stage occurrences into one source survey×species record, *without adding synthetic zeros*.

- NPS: the same manually scored sound file is one survey event; ManualCIV 0 is recorded no calling on that sound file, not true taxon absence. Keep original hydroperiod class, and exact month/dates.
- Hungary: 9 target amphibian taxa are separately evaluated at each site×date×method; zeros mean under-method nondetection, not proof of species absence. Site-level static measured emergent and submerged vegetation and water depth, visit weather recorded. No 2024 annual persistence inference or plant sprouting dates.
- INBO: exact cross-archive source locationID, survey event; adult chorus vs larvae/metamorph survey protocols are **different methods**. Merge across life-stage rows **only within the same source event+taxon**. If at least one stage present, treat species detected; if all explicitly absent, treat protocol not detected; don't treat unsampled species as zero.
- NAAMP: positive source taxon call records only and original completed survey stops as *separate effort tables*. Do not create taxon zeros from omitted positive rows. The source 'Species' field contains scientific names but the upstream source-audit script labels them with a 'NAAMP_CODE:' prefix. Strip that prefix **only for simple exact verbatim genus+species binomials** (e.g. 'Lithobates clamitans'), retaining the original source label in a separate column. Complex labels such as 'Pseudacris maculata/triseriata complex' remain source-scoped and non-matching. Do NOT infer Dryophytes↔Hyla or any other synonym without a validated taxonomic reference.
- GBIF: presence-only georeferenced occurrence records; do not attach to original NAAMP stop as predator abundance, and do not interpret lack of GBIF records as a species absence. GBIF 1-degree grid is an **additional geography/method tier** and can later be appended only with its own source ID, original GBIF key, effort semantics and date.

**Original-source duplicate handling:** the Hungary CSV has 381 original method-visit rows but two reused survey identifiers in bottle-trap records, each containing a zero vector and a second partially positive survey row. Five contradictory source event×species assessments are marked **unresolved**, never cherry-picked as detections. Duplicate zero/zero assessments count as a single protocol nondetection. NPS no-call, INBO source explicit statuses and NAAMP positive-only reporting remain separately identifiable.

## Output artifacts (GitHub Actions and inspectable compact receipts)

- Generated event×taxon table: common_occurrence_events.csv.gz. **Original site IDs are hashed with source namespace; INBO adult + larval datasets use same INBO site token**.
- Generated source-site×year×month×taxon×method table: common_occurrence_site_month.csv.gz. Count *assessed* original events, recorded-present events and protocol-nondetected events. Do not treat the same species appearing in 2 development stages on one event as 2 independent occurrences.
- Survey-event richness: source × site × date × method, n taxa assessed and n species detected. Event type remains crucial because frog-only choir methods do not assess odonate larvae, fish or other aquatic competitors.
- Compact observed-profile.json, positive+adverse pairwise co-detection summaries, and source-only environmental Spearman correlations at 29 independent Hungary wetlands or at 66 NPS recorder stations where coverage exists. **Do not pool survey zeros of different methods or model coefficients as identical ecological occupancy estimates.**
- Full original occurrence records (including fine-grained site token linkage) are Actions artifacts only, not large raw source copies added to the research repository.

## First ecological questions, independent of developmental stage

1. Which species share the **same sampled sound file**, source wetland/date, or exact within-method monitoring event? Build only exact-event co-detection tables with both taxa explicitly assessed; report n11/n10/n01/n00, sample n, independent source sites, phi, and a warning about shared habitat, time, effort and species imperfect detection.
2. Does a species' **recorded occurrence across monitored wetlands** associate with source measured precipitation, survey season, water depth, broad hydroperiod class, emergent/submerged % cover or recorded other-taxon co-detection? State the actually observed covariates per source and experimental grain.
3. Are **co-occurrences** distributed differently between NPS ephemeral/semi-permanent/permanent recorder environments? This is broad site classification rather than measured seasonal water dry-out.
4. Stage-specific size matching, predator–prey identification and chronology can be **reintroduced in a later extension** only after occurrence coverage and survey denominators are validated.

**Stop rules:** do not use NAAMP absence unless explicitly established; NPS acoustic zero ≠ organism absent; INBO stage zero ≠ whole animal absent; Hungary visit zero ≠ taxonomic extinction; NPS station ≠ pond; GBIF spatial co-reporting ≠ within-pond encounter; observational species richness ≠ measured competition pressure; no inference about local water persistence from one site depth; no causal predation / refuge from cross-sectional cover.

**Core decision:** first establish observed **species occurrence and co-recording patterns** in the same source event. Stage may explain later patterns; it is not the prerequisite for constructing occurrence data.
