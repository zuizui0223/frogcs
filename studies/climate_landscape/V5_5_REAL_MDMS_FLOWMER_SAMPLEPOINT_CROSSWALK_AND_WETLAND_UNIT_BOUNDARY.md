# v5.5 — REAL official Flow-MER frog SamplePoint to CEWH MDMS exact source crosswalk

**2026-10-10 JST — successful original government data-to-data linkage**, not a biological result, not frog payoff/hydroperiod identification. Independent research PR #135. **Submitted JAE RC6/main unchanged.**

## 1. New original-data result: exact match of every government frog sample-point label to CEWH official monitoring point

Government originals:
1. [CEWH MDMS sample points (Flow-MER monitoring locations)](https://data.gov.au/data/dataset/mdms-monitoring-locations). Actual downloadable official `MDMS_Sample_Points_extracted_24Dec2022.geojson`, resource ID **`35b2b6d7-2557-49c9-bcc0-af98d17cb49a`**. File metadata verified via original [CI 38014637856 SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38014637856): source declared **435,791 bytes**. The GeoJSON was actually fetched; [schema CI 38014708544 SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38014708544) established **681 `Point` features**, every one with nonmissing **`NAME`** and **`SAMO_ID`** attributes. No coordinate or individual label values were output.
2. [CEWH Flow-MER Frog Abundance 2014–2022](https://data.gov.au/data/dataset/flow-mer-frog-abundance), CKAN resource **`70f3b7c9-990b-4770-b306-57c4e7cdac61`**, **673** public frog source rows. The v5.5 join specifically fetched only **`Program` and `SamplePoint`**, neither frogs' Y/N, CPUE, species names nor coordinates.

Original SHA-256 of the government MDMS full GeoJSON source retrieved during real join: **`2fe0672aec63b032594a14d125c644461284ed2099b793e390f6df77d274f9d2`**. The two-field public CKAN projected response hash was **`54a339cb31e7ed23703709a5c90b2ab4bbe02dff3ec459c4a1e2c8e746cf1a6f`**. No raw government point file, coordinates, site IDs or individual response data were committed.

**Executed source-only [GitHub Actions 38015017208 — SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38015017208), [source join and exact-point QC code](scripts/audit_mdms_flowmer_exact_site_labels_v55.py).**

| Frog source `Program` | Distinct `SamplePoint` labels (2014–22 rows) | Exactly one MDMS `NAME` match | Unmatched or duplicate-name match | Exactly unique MDMS Point coordinates within this program |
| --- | ---: | ---: | ---: | ---: |
| Gwydir River System | **6** | **6** | **0** | **6** |
| Lachlan River System | **14** | **14** | **0** | **14** |
| Murrumbidgee River | **28** | **28** | **0** | **28** |
| **Total (unique across programmes)** | **48** | **48** | **0** | **48** |

Comparison was **exact after NFKC Unicode, whitespace collapse, and casefold**. It did **not** use fuzzy text, geographic nearest-neighbor, map overlays, or inferred IDs.

- The MDMS file contained **681 unique normalized `NAME` labels out of 681 populated features**, with no NAME duplicates.
- **All 48 frog source label names matched exactly one original `NAME`**. No frog site matched the separate MDMS **`SAMO_ID`** identifier as a literal label; `SAMO_ID` must not be joined via equality to `SamplePoint`.
- Every matched feature was a **Point** and all **48 have different coordinate pairs**, with **no EXACT same-coordinate duplicates**. The program counts of point-coordinate uniqueness are only private in-memory equalities; **no coordinate values, mapped locations or individual site hashes were saved or displayed**.
- Across the matched points, MDMS `PROGRAM` was populated and had **one distinct value inside each broad frog Program**, consistent with broad programme partitioning; the MDMS `POINT_CATE` was not populated on these 48 features. No source `POINT_CATE` class can therefore be used to label any of these as a distinct wetland or particular sampling technique.

## 2. Critically — matched POINTS are not proven independently replicated WETLANDS

This resolves an important **source identity** question from v5.3: the released frog `SamplePoint` strings are real government CEWH MDMS monitoring **point** labels, not arbitrary unverified names. The previously v5.2-eligible **24 Murrumbidgee sample labels** can therefore be tied *in principle* to the official monitoring point identity system, subject to repeating their strict frame filter. However, 24 source Point labels ≠ 24 known **independent wetland ecosystems**.

The original [Murrumbidgee River System Technical Report 2014–20](https://cdn.csu.edu.au/__data/assets/pdf_file/0008/3853403/Murrumbidgee-2019-20-MER-Technical-Report_final.pdf) describes **12 core wetland monitoring sites** (with expansions), whereas the public 2014–22 frog source has **28 sample-point labels**, or **24 labels** in our predeclared long-interval Murrumbidgee v5.2 subset. Multiple monitoring/sample points could lie within the same wetland; there could also have been changed sampling designs over years. Neither one-to-one wetland membership nor a source-authenticated *site×actual timed survey event* ledger is established by this MDMS GeoJSON.

Thus:
- `NAME` crosswalk **PASS**: external identity of sample points, with the source hash and cardinality fixed.
- **Exact point-coordinate uniqueness PASS**, not distance/independence/ecological-unit verification.
- **Physical wetland unit crosswalk NOT VERIFIED**: no source-authoritative mapping `MDMS NAME/SAMO_ID → original named wetland/ecological site` or same-year wetland boundaries.
- **Original event/effort/stage taxonomy linkage NOT VERIFIED**: short 20-min frog transect, separate overnight net method, recorded negative visits, *Limnodynastes* larval genus-level pooling vs released speciesCode, exact hydrology and true metamorph follow-up remain undocumented at record level.

## 3. What this changes about v5.2 and what must not change

v5.2's **-16.09 percentage-point pooled** but **+19.85 percentage-point within repeated source-label×speciesCode** table-level sign flip is numerically reproducible for the released 579-row long-interval data. [v5.3](V5_3_REAL_SOURCE_STAGE_GRAIN_QA_AND_SIGN_REVERSAL_DOWNGRADE.md) and [v5.4](V5_4_REAL_GENUS_CPUE_TIE_CLASSES_AND_SOURCE_CORRECTION.md) already correctly downgraded any conspecific reproductive-payoff inference because field-method stage taxon assignment and observation units are not authenticated.

**Now improve the source label description:** v5.2's 24 `SamplePoint` resampling clusters are **government MDMS monitoring point-name clusters**, not generic unidentified labels. They still cannot be assumed to be **independent physical wetlands**, and site-cluster bootstrap confidence limits can be optimistic for a study with multiple sample points per wetland. We do **not** refit or expand the v5.2 model after looking at outcomes.

## 4. Scientific go/no-go and remaining exact source request

**Decisive missing layer is much smaller now:** obtain original, non-sensitive **CEWH `SAMO_ID / NAME → wetland/site scientific unit` crosswalk**, with stable original monitoring year and site-level effort/date where known. A table of **anonymous counts of distinct wetlands represented among the 24 eligible Murrumbidgee MDMS names**, and counts of points within each wetland, would settle whether the site-cluster bootstrap had 24 true independent wetland replicates. No protected coordinates or raw frog outcomes needed.

A separate minimal **original field-stage taxon crosswalk** must explain `Limnodynastes` genus-level identified tadpoles and which published speciesCode row, if any, they enter. This cannot be solved by a monitoring point GeoJSON and should not be implied by the v5.5 source match.

**Hard conclusion:** sample-point identity substantially improved by one-to-one official name/geometry mapping; frogcs's acute rain sound/local water/strong-chorus historical site mechanism and genuine species-specific recruitment remain **UNIDENTIFIED from these releases**. Another exploratory sign-reversal regression is low priority until stage mapping and true wetland units are documented. No external inquiry was sent, and submitted RC6/main was not edited.
