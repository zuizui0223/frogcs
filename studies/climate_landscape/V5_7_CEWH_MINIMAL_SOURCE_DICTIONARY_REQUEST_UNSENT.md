# v5.7 — one metadata-only CEWH source inquiry, NOT SENT

**2026-10-10 JST.** Prepared for human author review only, NOT sent. Do not submit to a public forum, fill in a sender identity, or access protected locations from this repository. JAE RC6/main are submission-locked and are not part of this request.

## Official recipient and provenance

**Potential recipient (independently verified on Australian Government dataset catalogue):** `cewomonitoring@dcceew.gov.au`.

- [Official MDMS monitoring-points catalogue](https://data.gov.au/data/dataset/mdms-monitoring-locations), including the **2-page** "Metadata description for MDMS Sample Points" PDF (government CKAN resource `52a2a361-b1a0-466a-a971-8e046bf99e75`).
- [Official Flow-MER Frog Abundance 2014–2022](https://data.gov.au/data/dataset/flow-mer-frog-abundance).
- [Actual v5.5 label↔point result](V5_5_REAL_MDMS_FLOWMER_SAMPLEPOINT_CROSSWALK_AND_WETLAND_UNIT_BOUNDARY.md).
- [Actual v5.6 field equality result](V5_6_REAL_MDMS_ATTRIBUTE_GROUPING_AND_WETLAND_ID_STOP.md).
- [Actual v5.7 government PDF presence check](V5_7_REAL_OFFICIAL_MDMS_PDF_PRESENCE_AND_CROSSWALK_STOP.md).

## Ready-to-review email (UNSENT)

**To:** cewomonitoring@dcceew.gov.au  
**Subject:** Flow-MER frog sample points: MDMS field definitions and wetland-unit crosswalk (metadata only)

Dear CEWH Monitoring Data Team,

I am assessing whether a future secondary ecological analysis of the public Flow-MER Frog Abundance 2014–2022 data can distinguish independently monitored wetland units and use correctly aligned adult frog and tadpole survey records. I am seeking clarification of the original source metadata only, not requesting sensitive fauna locations, site names, coordinates, frog observations, or unpublished water-level records at this stage.

The public frog dataset's `SamplePoint` labels match the `NAME` field of the official 24 December 2022 MDMS point GeoJSON exactly at all 48 distinct public sample points (28 Murrumbidgee, 14 Lachlan and 6 Gwydir). However, a monitoring *point* is not necessarily one independent ecological *wetland*. In the Murrumbidgee subset, 28 point records contain 16 distinct nonempty `DESCRIPTIO` values, including one repeated value on 13 points; this grouping has not been interpreted as wetland membership.

Could the appropriate data manager please clarify the following, ideally through a field dictionary, a versioned mapping specification, or **aggregate non-identifying counts**?

1. What do `NAME`, `SAMO_ID`, `DESCRIPTIO`, `ANAE_TYPE`, `DATATYPENA`, `SystemType` and `SAMPLECOUN` mean in the December 2022 MDMS release? Is any field an authoritative identifier for an independently monitored wetland rather than a sampling point, geographic class or free-text description?
2. Is there a maintained source-defined `NAME/SAMO_ID → physical wetland/ecological monitoring-unit` crosswalk, with identifier continuity across water years 2014–2022? Without sharing names or coordinates, could you state how many distinct wetland units are represented among the 28 Murrumbidgee frog-listed points, and whether multiple points occupy each wetland? If an aggregate for the subset of 24 pre-specified long-interval sample points can be provided after an authorised local join, that would help assess the unit of replication.
3. Does the released frog table's `callingEvidence=N` identify an actually completed negative adult survey? Are dated visits, omitted/unvisited survey opportunities, transect effort, and net-deployment effort available in a programme data dictionary?
4. The historical field report describes some `Limnodynastes` tadpoles pooled at **genus**. How were original field identifications mapped to the publicly released `speciesCode` and `CPUETadpoles` variables, and what is the treatment of genus-identified tadpoles?
5. Are `sampleDateStart`–`sampleDateEnd` source-table spans aggregation intervals, and can original time-stamped adult census and tadpole net events be linked in the source system without disclosing protected locations?

An answer limited to definitions, yes/no data-availability, and non-sensitive counts would be sufficient. If another team manages the original field dictionaries, I would appreciate a referral.

Thank you for maintaining and sharing these important monitoring records.

Sincerely,  
[Author to complete name, affiliation and address only after reviewing/sending]

## Use decision

- **Not sent.** Sending and personal identifying metadata remain the author's decision.
- Do not interpret mere source field equality, spatial proximity or exact coordinate uniqueness as independent ecological wetland membership.
- Do not perform additional species-specific recruitment, causal hydrology or k≥4 analysis unless original physical unit, valid survey opportunities and original stage taxonomic mappings are authenticated.
- A negative answer is a legitimate scientific stop. Report source linkage not identified rather than fabricating a biological null.
