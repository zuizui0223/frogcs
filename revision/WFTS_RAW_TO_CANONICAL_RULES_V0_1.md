# WFTS raw-to-canonical adapter freeze rules v0.1

**Status:** frozen design rules for adapting a future WFTS export before ecological outcome inspection.

## Purpose

Define the allowed structural and coding transformations from raw WFTS records to the canonical confirmation inputs. These rules are based on official WFTS documentation and historical methods, not on any observed WFTS ecological effect.

## 1. Route scope

Primary confirmation includes only **traditional WFTS driving routes**.

Exclude:
- 1997–1998 NAAMP/protocol routes and their descendants if flagged as protocol;
- phenology surveys;
- mink-frog surveys;
- ad hoc records;
- any special comparison route not documented as a traditional WFTS route.

Route type must come from DNR/WFTS metadata or an authoritative route lookup.

**Do not infer traditional status from RouteID number alone.**

## 2. Permanent-route boundary

Historical WFTS methods state that routes were considered permanent.

If a route was substantially changed without maintaining comparability, WFTS treated it as a **new route**. Smaller station substitutions were rare and intended to be as similar as possible to the original.

Adapter rule:

- use the programme's documented RouteID/lineage;
- if `first_permanent_year` is available, exclude earlier years from the principal physical-site-history analysis;
- if a former RouteID maps to a later RouteID, preserve both raw IDs and the documented lineage;
- never merge route lineages solely because county/name/coordinates appear similar.

## 3. Station identity

The canonical physical SiteID must be based on the strongest available structural identifier in this order:

1. stable DNR internal station/site ID;
2. documented route + station lineage table;
3. route + site number within a verified period of unchanged station configuration;
4. frozen coordinate/description reconciliation only if no internal identifier exists.

A focal matched pair is principal-analysis eligible only if all ten physical station identities can be verified as the same station set.

If a station is replaced or relocated between focal surveys:
- exclude that pair from the primary confirmation;
- do not attempt response-informed repair.

## 4. Current public coordinates

Public WFTS RouteID pages provide current Site 1–10 latitude/longitude and descriptions.

Use public coordinates only for:
- Daymet extraction;
- structural consistency checks;
- supporting station-identity reconciliation.

Do not use current coordinates to overwrite historical station identity when DNR documents a station change.

## 5. Survey-period normalization

Map raw survey/run labels into exactly:

- `early_spring`;
- `late_spring`;
- `summer`.

Raw labels and exact normalization must be written into the completed mapping manifest before response endpoint calculation.

Do not merge phenology or mink surveys into these periods.

## 6. Date handling

Use the recorded calendar survey date.

If the raw database stores month/day/year separately, assemble the date deterministically.

Timezone for any timestamp normalization:
`America/Chicago`.

The confirmatory Daymet exposure uses calendar date and does not require survey-clock time.

## 7. Complete-run rule

The canonical primary route-run requires:
- one traditional route;
- one survey period;
- one survey year;
- exactly ten verified physical stations;
- no DNR invalid/incomplete-run flag;
- station continuity compatible with the principal analysis.

If duplicate station records occur within a run, fail closed until their semantics are documented.

## 8. Call-index coding

Official WFTS call index:
- 1 = individuals countable/no overlap;
- 2 = overlap but individuals distinguishable;
- 3 = full continuous chorus.

Official instructions state that species not calling are left **blank rather than written as 0**.

Therefore blank may be converted to canonical `0` **only after**:
1. the route-run itself is structurally valid/complete;
2. the species column/taxon coding is documented;
3. the blank is confirmed to mean "not calling", not missing/unknown/not entered.

If the electronic database has an explicit missing/unknown code distinct from non-detection, preserve it as missing and do not coerce it to 0.

## 9. Wide versus long response tables

Both are acceptable.

### Wide field-sheet style

One row/site with one column per taxon:
- reshape to long only after schema mapping is frozen;
- blanks use the rule above.

### Long style

One row per taxon × site observation:
- absence of a row is not automatically 0 unless documentation establishes that the database is a positive-only representation of a valid complete field sheet.

This distinction must be frozen in the mapping manifest.

## 10. Taxon-name harmonization

Freeze a synonym table before endpoint calculation.

Allowed:
- historical scientific-name changes;
- known common-name changes;
- deterministic taxonomic aliases.

Not allowed:
- dropping taxa because they weaken the effect;
- merging taxa because their responses appear similar;
- changing the taxon pool after endpoint readback.

The canonical key should represent the biological taxon consistently through time.

## 11. Rare/extralimital verification flags

Historical WFTS methods flagged dubious, extralimital or otherwise questionable records.

If the database supplies a verification/quality flag:
- define the treatment before endpoint calculation;
- prefer the programme's accepted/validated status where available;
- do not manually review questionable records based on effect direction.

If no flag exists, do not invent one from outcome magnitude.

## 12. Observer and weather fields

Observer ID and recorded weather may be retained for later sensitivity/audit work but do not enter the frozen primary comparator.

Primary weather exposure remains external Daymet.

## 13. RouteID county-code audit

The WFTS RouteID convention largely follows Wisconsin county number codes.

Use `scripts/wfts/audit_wfts_route_master.py` to flag:
- county-prefix consistency;
- special/noncounty identifiers;
- obvious mismatches.

This is QA only. It cannot determine route type or eligibility.

## 14. Freeze receipt

Before response endpoint calculation, commit:

1. raw-file byte receipt;
2. schema-only receipt;
3. completed `WFTS_RAW_TO_CANONICAL_MAPPING_TEMPLATE_V0_1.json`;
4. route-type lookup provenance;
5. station-lineage provenance;
6. taxon synonym mapping;
7. adapter code SHA;
8. Daymet provenance;
9. response-blind structural preflight receipt.

Only then may the canonical response matrix be evaluated by v0.5.

## 15. Fail-closed ambiguities

Stop and resolve structurally before response analysis if any of the following is ambiguous:

- whether a route is traditional;
- whether a blank means zero or missing;
- whether a site identity changed;
- whether a route was renumbered versus replaced;
- whether duplicate rows represent corrections versus repeated observations;
- whether a run has all ten physical stations;
- whether a taxon alias represents the same biological taxon.

No ambiguity may be resolved by looking at the resulting ecological coefficient.

## Authority boundary

These adapter rules do not modify the frozen endpoint or comparator.

Real WFTS analysis remains governed by:
`revision/WFTS_CONFIRMATORY_AUTHORITY_V0_2.md`.
