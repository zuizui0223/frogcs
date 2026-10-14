# v5.6 — Real government MDMS attribute-equality gate: wetland identity remains unverified

**2026-10-10 JST — actual government source analysis; no frog outcomes accessed.** This is a *source schema and point hierarchy* audit on independent draft PR #135. Locked JAE RC6/main unchanged.

## Execution and pre-read provenance

- Pre-read authority: [v5.6 attribute contract](V5_6_MDMS_CANDIDATE_PARENT_UNIT_ATTRIBUTE_CONTRACT.md), committed **before** the live script returned field-grouping counts.
- Actual GitHub Actions: [run 38015649475 — SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38015649475).
- Code: `scripts/audit_mdms_candidate_parent_attributes_v56.py` with a synthetic privacy and duplicate-ID fail-closed test. An initial test-only failure incorrectly treated the name of an aggregate boolean `coordinates_or_individual_site_names_reported` as if it disclosed coordinates. The test was corrected without inspecting/retuning field-group results.
- Input: original **681-feature** government CEWH MDMS 24-Dec-2022 GeoJSON, pinned SHA256 `2fe0672aec63b032594a14d125c644461284ed2099b793e390f6df77d274f9d2`, and an official Flow-MER frog CKAN projection of **only `Program,SamplePoint`**, 673 rows. Exactly **48 public point labels** from the v5.5 canonical crosswalk, 6/14/28 across Gwydir/Lachlan/Murrumbidgee.
- No individual point, property value, coordinates, frog call, tadpole observation or row-wise inferred point grouping were printed or saved. Only programme-wide field equality cardinalities were emitted.

## Most important real data result

The `DESCRIPTIO` property is nonempty on all **48** frog-matched official MDMS points, but **its meaning is not documented as an independent wetland identifier**.

| Programme | Official matched points | Distinct nonempty `DESCRIPTIO` values | Repeated-value groups | Points in repeated-value groups | Largest repeated group |
| --- | ---: | ---: | ---: | ---: | ---: |
| Gwydir | 6 | 6 | 0 | 0 | 1 |
| Lachlan | 14 | 14 | 0 | 0 | 1 |
| Murrumbidgee | 28 | 16 | 1 | 13 | 13 |

In Murrumbidgee, **13/28 public point records share a single `DESCRIPTIO` value**. That is real source-field equality, **not** proof that those 13 points all belong to the *same wetland*. The repeated value might be a common placeholder, an area label, a system-level narrative, or any other descriptive category. Equally, the remaining 15 different descriptions do not prove 15 independent wetland units.

Additional metadata-field repetition (counts only; **not a wetland mapping**):

| Field | Murrumbidgee nonempty fields | Distinct values | Points in repeated-value groups | Largest group |
| --- | ---: | ---: | ---: | ---: |
| `ANAE_TYPE` | 28 | 8 | 26 | 10 |
| `DATATYPENA` | 28 | 6 | 25 | 13 |
| `SystemType` | 28 | 3 | 28 | 13 |
| `SAMPLECOUN` | 28 | 27 | 2 | 2 |
| `POINT_CATE` | 0 | 0 | 0 | 0 |
| `COMMENTS` | 0 | 0 | 0 | 0 |

The `PROGRAM` field is the broad government monitoring programme; it has one value per programme and cannot serve as an independent wetland key. None of these candidate attributes has authenticated physical-wetland semantics, stable site-history semantics, or survey-event semantics.

## Ecological consequence and decision

The v5.5 **48 official site point names** remain successfully crosswalked, but **48 independent wetlands are NOT confirmed**. The v5.2 Murrumbidgee **24 bootstrap source-point clusters** still cannot be described as 24 independent wetlands. The v5.2 −16.09 pp pooled versus +19.85 pp within repeated taxon×point-label descriptive sign flip remains a *published-table-level* pattern, **not** demonstrated species-specific frog reproductive payoff.

The known pooled-*Limnodynastes* tadpole-stage taxonomy issue is also **unresolved**. Neither descriptive-column grouping nor exact point coordinates can repair missing field-stage source mapping, missing actual survey-opportunity negatives, or observation effort. No new model was fitted.

**Next actual information required (only via an approved, non-sensitive official metadata request):** an authenticated source dictionary defining `DESCRIPTIO`, `ANAE_TYPE`, `SystemType` and the original CEWH `NAME/SAMO_ID` to independent named wetland/site unit; version and site continuity across water years; anonymous counts of distinct wetland units represented by the 24 v5.2-eligible source points. Separately, the source `CPUETadpoles`→field larval identification/effort/negative-survey dictionary must be obtained before any conspecific recruitment analysis.

**Hard stop:** no inferred wetland count, no reclustering/CI re-estimation using field-value equality groups, no frog response expansion and no change to JAE RC6. No records request or custodian email has been sent.
