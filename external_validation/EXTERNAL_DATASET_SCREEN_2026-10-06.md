# External dataset screen — 2026-10-06

## Purpose

Freeze the external-dataset selection logic before inspecting any candidate dataset for the
predefined spatial-selectivity outcome. This prevents choosing among public datasets because one
happens to give a favourable result.

The inherited prediction is:

> Broad activation need not erase spatial selectivity; broad species-night activity may retain a
> taxon-specific spatial signature learned from earlier observations.

This is a new external-validation line and does not reopen the closed RC6 NAAMP analysis.

## Selection criteria

A useful external dataset should provide, in descending priority:

1. repeated observations at the same multiple physical sites;
2. taxon-specific activity measured on the same dates/nights across sites;
3. enough temporal replication to estimate historical species × site structure strictly before validation;
4. an activity/intensity measure that remains informative when a taxon is active at all monitored sites;
5. weather or pulse context measured independently of the frog response;
6. public raw data with an auditable provenance trail.

## Candidate ranking frozen before outcome inspection

### 1. Brodie, Schwarzkopf & Allen-Ankins — SELECTED PRIMARY

Public record: DOI 10.25903/bpkv-gf77.

Published metadata describe:
- 17 frog species;
- three fixed breeding sites near Hervey Range, Queensland;
- nightly chorus activity measured as minutes chorusing;
- 2012-10-04 through 2014-04-27;
- nightly environmental data including rainfall.

Why selected:
- the continuous chorus-duration response remains informative even when a taxon is active at all
  three sites;
- the two-season temporal span permits a strict historical/validation split;
- fixed sites permit a direct test of whether maximal spatial breadth homogenizes chorus allocation;
- weather is available in the same record.

Primary analysis authority:
`external_validation/BRODIE_CHORUS_PROSPECTIVE_CONTRACT_V0_1.md`.

### 2. Hoefer et al. 2026 PAM frog dataset — NOT PRIMARY

Public data/code: Zenodo DOI 10.5281/zenodo.21634473 and GitHub `cheloniax/repo_PAM_frogs`.

Structural strengths:
- six survey sites;
- four fixed plots per site;
- date-stamped taxon detections;
- long-duration passive acoustic monitoring.

Reason not selected as primary:
- the public frog table is fundamentally a detection/event dataset rather than nightly chorus
  intensity at each plot;
- with four plots, a binary k=4 event contains no within-night allocation information;
- WetA/WetB versus DryA/DryB is an intentionally strong habitat contrast that would require a
  different ecological estimand;
- complete recorder-operation/zero-detection nights must be reconstructed carefully before absences
  can be defined.

It is therefore not a cleaner test of the frozen prediction than Brodie and must not be promoted
after seeing a Brodie result.

### 3. Wisconsin Frog and Toad Survey — STRUCTURALLY STRONG, NOT PURSUED

WFTS most closely matches the repeated multi-stop route structure of NAAMP and a prospective analysis
was fully specified in the parent project. However, the current project explicitly decided not to
request or analyse WFTS response data. That decision remains authoritative. WFTS is not reopened by
this external-validation branch.

### 4. Sarker et al. 2022 inundation dataset — NOT SELECTED

This study is biologically close because it samples a hydrological pulse across multiple frog sites,
but the response data are not available through a comparably direct open raw-data route for the
required repeated historical-template analysis, and the focal before/after window is much shorter.

### 5. Other public acoustic datasets — NOT SELECTED

Datasets with one recorder per locality, no repeated physical-site network, or no strict prior period
cannot test the frozen historical spatial-selectivity prediction without changing the estimand.

## Anti-selection rule

The Brodie dataset is the sole first external test.

Do not run the frozen endpoint on multiple public datasets and then report only the most favourable
one. If Brodie cannot be obtained in usable raw form, record **access failure / structural
ineligibility** before considering a replacement dataset. A replacement requires a new,
response-blind selection record before its frog outcome rows are inspected.

## Current access status

The public metadata record is open and identifies the relevant frog-chorus and weather files. During
this audit, the repository/file-delivery endpoint was not yet successfully materialized in the
analysis environment. No Brodie frog response row has been used to compute the frozen external
endpoint.

