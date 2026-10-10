# v5.8 — Original official MDMS PDF DEFINES the candidate source fields (2026-10-10)

**Source-based result, not a frog biological model.** The investigation is isolated on independent draft PR #135. Locked JAE RC6/main and its reported outcomes are unchanged.

## Reproducibility and exact source

- [Pre-extraction source contract](V5_8_MDMS_SOURCE_PDF_CONTEXT_INSPECTION_CONTRACT.md) was committed *before* reading the additional contextual text.
- [Successful real GitHub Actions run **38040526904**](https://github.com/zuizui0223/frogcs/actions/runs/38040526904); targeted [PDF metadata-only audit script](scripts/audit_mdms_public_pdf_field_context_v58.py), pinned to original document SHA-256 `b802f313e58981e6919baa08a300303adeca86ea451a630c06c6b8ba63509b7a`.
- Original official public document: Australian Government [MDMS sample points (Flow-MER monitoring locations)](https://data.gov.au/data/dataset/mdms-monitoring-locations), two-page resource **Metadata description for MDMS Sample Points**; resource ID `52a2a361-b1a0-466a-a971-8e046bf99e75`, original data lineage **exported MDMS 24/12/2022**.
- The run read **only the public metadata PDF**. No MDMS GeoJSON point-attribute values, individual sample labels, raw coordinates, frog observations, tadpole outcomes, registered or private datasets, or source custodian emails were accessed.

## Field definitions resolved directly from the original PDF

The government's document includes a field / data type / description table on PDF page 1. The short literal-definition wording is as follows:

| MDMS published field | Original field definition | Implication for ecological-unit identity |
| --- | --- | --- |
| `NAME` | Location-specific sample-point name, unique within program | Identifies a **sample point**, not an independently sampled wetland |
| `DESCRIPTIO` | **Optional description** | **Not an authenticated wetland-parent key**; its value equality is not a wetland crosswalk |
| `PROGRAM` | Name of the contributing Selected Area | Broad programme membership, not independent wetland identity |
| `DATATYPENA` | Types of data collected at this location and stored in MDMS | Type/content descriptor, not a wetland-parent identifier |
| `SAMPLECOUN` | Number of data records for this location stored in MDMS | Record-count attribute, not wetland sample size, ecological-unit membership, or spatial replication |
| `LATITUDE`/`LONGITUDE` | Geographic decimal degrees | Spatial reference only, not proof of unit independence |

The v5.7 field-token hits have thus advanced from mere **presence** to **actual original-publication field definitions** for `DESCRIPTIO`, `DATATYPENA` and `SAMPLECOUN` in particular. `SAMO_ID`, `ANAE_TYPE` and `SystemType` were not defined in the extracted PDF field table. Their complete original MDMS internal semantics have **not** been independently authenticated.

## Strong negative identification result

The v5.6 official field-equality result remains arithmetically correct: among **28** frog-matched Murrumbidgee official MDMS **point features**, **16** unique `DESCRIPTIO` strings occur, one shared by **13** point records. But the original Australian Government PDF identifies `DESCRIPTIO` as merely an **optional description**.

Therefore:

1. **Do not infer "16 wetlands" from 16 distinct descriptions.**
2. **Do not infer "one wetland containing 13 monitoring points" from the 13 identical descriptions.**
3. **Do not assume the 24 v5.2 source-point bootstrap clusters are 24 physically independent wetlands.**
4. Distinct coordinate points establish different point features, not spatially independent ecological basins. `SAMPLECOUN` counts source **database records**, not frogs, sample independence, or reproductive success.
5. No field defined in this *published PDF table* provides an authenticated `NAME/SAMO_ID → physical wetland/ecological unit` crosswalk. This does **not** prove such a mapping is absent from CEWH internal records.

This is a substantive **source-identification boundary**, not a negative frog biological effect. It precludes the appealing but incorrect field-cardinality shortcut.

## Implication for the existing published frog tables

The 579-row v5.2 pooled versus within-source-point-label sign reversal remains a correctly reported **table-level association**, not an identified contrast in conspecific breeding payoff. The historical field method notes regarding genus-pooled `Limnodynastes` tadpoles still demand an original field-stage taxonomy crosswalk and effort/visit opportunity metadata.

Neither a generic field description nor a monitoring-point coordinate can repair the missing relation of:
- 28 Murrumbidgee public monitoring points to actual independent historical wetlands;
- adult call observations to valid source survey efforts and explicit no-call opportunities;
- original larvae identified to genus versus released species-specific CPUE records;
- dated water state versus subsequent reproductive-stage outcomes.

## Final next decision: request only the missing **source-defined** keys

The existing unsent enquiry is replaced by an **even narrower clarification** in [v5.8 CEWH wetland-unit and larval-source dictionary question (UNSENT)](V5_8_CEWH_FOCUSED_WETLAND_AND_LARVAL_PROVENANCE_REQUEST_UNSENT.md). The original PDF already answers what `DESCRIPTIO`, `DATATYPENA` and `SAMPLECOUN` mean, so no further web-PDF schema inspection or additional statistical endpoint mining is justified.

No enquiry was sent. No protected locations or biological event records were accessed. No change to JAE RC6/main.
