# v5.6 — source-only MDMS candidate parent-unit attribute gate (frozen before real read)

**2026-10-10 JST.** Independent study in draft PR #135. This document fixes the inspection method before accessing any new field-value equality summaries. JAE RC6/main remain untouched. No additional frog response outcomes, site coordinates, protected site labels, or original survey records may be opened or published.

## Identifiability question

The v5.5 join identified 48 distinct public Flow-MER frog `SamplePoint` labels as 48 unique original CEWH MDMS Point features. This **does not** identify how many independent physical wetlands those points belong to. The published Murrumbidgee report describes 12 core wetlands, but there are 28 source frog point labels (24 in the earlier eligible subset).

Before approaching custodians, inspect **only attribute equality-group cardinalities** on these already matched 48 public features. This is a feasibility audit, not a biological hypothesis test or ecological-unit crosswalk.

## Frozen protocol

1. Download only the two previously vetted government sources and project the frog CKAN response to exactly `Program,SamplePoint`. Pin the original MDMS full-file SHA-256 from v5.5 (`2fe0672aec63b032594a14d125c644461284ed2099b793e390f6df77d274f9d2`). Fail closed on unexpected source hash, host, file size, schema or source point cardinality.
2. Reconstruct exact normalized `SamplePoint` ↔ MDMS `NAME` matching; require 6 Gwydir, 14 Lachlan, 28 Murrumbidgee names, each unique in MDMS. Do **not** use fuzzy or coordinate matching.
3. On matched source features only, inspect aggregate non-empty/equality classes for exactly: `DESCRIPTIO`, `ANAE_TYPE`, `DATATYPENA`, `SystemType`, `SAMPLECOUN`, `COMMENTS`, `POINT_CATE`, `PROGRAM`. Per broad programme and field print only `n_nonmissing`, `n_distinct_nonempty`, `n_groups_size_2plus`, `n_points_in_groups_size_2plus`, and `largest_group_size`. Never print any actual attribute value, matching label, site ID, coordinate, reversibly hashed site value, or any row-wise linkage.
4. `PROGRAM` is a programme label, not evidence of wetland membership. The remaining columns have **unverified semantics**. Repeated values may represent generic methodological descriptions rather than wetland identity. Conversely unique descriptions do not prove site independence.
5. A repeated candidate attribute only allows a **metadata-only source question** to the programme owner: does that exact field or another source dictionary encode *independent wetland/ecological-unit membership and site continuity through time*? No inferred number of wetlands, cluster SE, source-specific tadpole recruitment or causal claim may be computed from the attribute equality results.
6. Retain the pre-existing source-stage taxon caveat: original `Limnodynastes` tadpoles were genus-pooled; public species-level CPUE does not authenticate conspecific larvae. This audit neither accesses nor resolves the species-stage mapping.

## Outcomes and decision

- If one or more non-programme attributes repeat on frog-matched points, record only the *candidate field names and aggregate repetition*, and request an **official field dictionary and non-sensitive point→wetland counts**, not the underlying geography.
- If none do, record **NO_PLAUSIBLE_WETLAND_PARENT_KEY_IN_THIS_SOURCE_SCHEMA**; do not infer 28 independently replicated wetlands. Request the original source mapping externally only with author approval.
- In either case the biological go/no-go for a physically independent wetland panel remains **NOT VERIFIED**, and no reanalysis of the v5.2 outcome table is authorized.

Source authority: [official MDMS](https://data.gov.au/data/dataset/mdms-monitoring-locations), [official Flow-MER frog abundance](https://data.gov.au/data/dataset/flow-mer-frog-abundance), [v5.5 crosswalk result](V5_5_REAL_MDMS_FLOWMER_SAMPLEPOINT_CROSSWALK_AND_WETLAND_UNIT_BOUNDARY.md).

No email, registered system, experiment, or protected data was accessed.
