# v6.3 — correct canonical Flow-MER frogs dataset identity before package metadata probe

**2026-10-10 JST. Independent study PR #135. Original JAE RC6/main not modified.** Frozen before corrected official CKAN request. **No frog records, protected locations, or recordings are to be read.**

## V6.2 epistemic correction — URI provenance

The v6.2 attempted CKAN package slug `flow-mer-frog-abundance` was inferred from a portal display title, not independently authenticated. Its HTTP 403 cannot alone establish a source-level denial of access to the **correct** package. Record the original attempt faithfully but do **not** repeat its inaccurate implication as an authoritative dataset gate.

Two **independent research registry** sources identify the actual frog dataset:

1. [Charles Sturt University, *Flow-MER Program Frog Abundance*](https://researchoutput.csu.edu.au/en/datasets/flow-mer-program-frog-abundance/): creator **Skye Wassens**, publisher **Commonwealth Environmental Water Holder**, date made available **30 June 2024**, temporal coverage **1 July 2014 through 30 June 2024**, declared access to `https://data.flow-mer.org.au/dataset/flow-mer-frogs`.
2. [Australian Research Data Commons / Research Data Australia registration](https://researchdata.edu.au/flow-mer-program-frog-abundance/3535992): dataset registration `0e2db3d4-c13d-48f3-bdf2-ca546e4a87fa`, creator/coverage/publisher agreement, public access category **Open**, linked external `flow-mer-frogs` landing URL.

**Source registry access category "Open" is not verification of a currently accessible raw CSV**, nor of actual 2023/24 frog rows, data joins, valid nights, or species-stage metadata. The original 2014–22 government release remains a different frozen data product, and none of its v5.2 analyses should be retrospectively changed.

## The ONLY approved source check now

Execute one bounded, unauthenticated, ordinary official CKAN package metadata request:
`https://data.flow-mer.org.au/api/3/action/package_show?id=flow-mer-frogs`.

Safety: HTTPS, exact official host, bounded response, no browser automation or authentication/circumvention. Print only HTTP status or, if and only if successful, normalized package title/date/license/resource count and resource IDs/formats. Do **not** query any `datastore_search`, original source animal rows, GIS coordinates, direct CSV, raw recordings, or source site IDs in this audit.

If HTTP 403, classify `CORRECT_PACKAGE_API_403_METADATA_NOT_RETRIEVED` — **not** `DATASET_NOT_FOUND`, `DATASET_CLOSED` or proof of an actual dataset-specific access policy. If 404, report exactly `CORRECT_PACKAGE_API_404` — not proof the university research registration is invalid. If successful, classify `PACKAGE_METADATA_VERIFIED_ONLY`.

## Scientific and governance decision

Even if this metadata request succeeds, the new 2014–24 resource would still need actual version/release/record-date/field-schema checks, **not** outcome fitting, before it could serve as an independent time-block test. It is the **same monitoring programme** and may revise earlier rows: not automatically an independent replication of RC6.

The next genuinely discriminating acoustic study depends instead on original **physical wetland ↔ recorder ↔ logger ↔ timestamp ↔ valid listening opportunity** source manifest, hydrology, classifier accuracy and usage rights. The one CEWH metadata enquiry remains **UNSENT**.
