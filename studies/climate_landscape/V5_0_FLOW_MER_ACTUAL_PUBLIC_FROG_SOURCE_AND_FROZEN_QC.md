# v5.0 — An ACTUAL publicly queryable government frog source (Flow-MER)

**2026-10-10 JST. Independent study data-source audit, not an extension or change to JAE RC6 main.**
The direct source of this discovery is the **Australian Government Flow-MER Frog Abundance 2014–2022**, a published open-data resource, rather than inferred data from the NSW 2024 Ocock papers. The latter's real 343-visit source opportunity denominator remains **unverified**.

## 1. Real live public dataset metadata is now verified, not merely a landing page

Official [data.gov.au landing and downloadable CSV](https://data.gov.au/data/dataset/flow-mer-frog-abundance). Official [dataset metadata and dictionary](https://data.gov.au/data/dataset/304f9db6-4506-40de-9ff0-cb32b0705ecf/resource/a28bca46-b29c-4def-9545-4c0815997fc9/download/metadata_flow-mer_frog_abundance.pdf). Program/custodian: Australian Government Commonwealth Environmental Water Holder (CEWH); stated data range 1 July 2014 to 30 June 2022; Gwydir and Murrumbidgee wetland frog surveys, plus a 2015 Lachlan contribution.

A public, unauthenticated **zero-record CKAN DataStore schema query** on resource ID
`70f3b7c9-990b-4770-b306-57c4e7cdac61` actually succeeded in [GitHub Actions 38011111995](https://github.com/zuizui0223/frogcs/actions/runs/38011111995):

- **673** records according to the official response's `result.total` — a *record count*, emphatically **not 673 completed unique wetland/visit opportunities**.
- **16 actual server columns**: `_id, Program, SamplePoint, Description, Latitude, Longitude, SampleDate, sampleDateStart, sampleDateEnd(Date/Time), speciesCode, speciesName, CPUEAdults, callingEvidence, CPUETadpoles, vegCommunity, Comments`.
- Some values in the **PDF dictionary** differ from the **actual CSV/API spelling**, especially `SamplePoint` vs `samplePoint`, `SampleDate` vs `sampleDate`, and `sampleDateEnd(Date/Time)` vs `sampleDateEnd`. **Use the actual observed API names when querying.**
- Public dictionary defines `callingEvidence` as **Y/N whether frogs of that particular listed species were heard calling**, `CPUEAdults` and `CPUETadpoles` as mean **catch per unit effort**, `sampleDateStart` inclusive and `sampleDateEnd` exclusive. These are **different** endpoints and scales than the original 0–3 NAAMP CallingIndex or Ocock's species-level 1/6/11/20 bins.
- The same public dataset's `Latitude` and `Longitude` may give precise site locations; **do not export any raw site coordinates or location-linked animal records into public GitHub audit receipts**.

This is a **material positive data-access result** compared with Nebraska Mendeley API HTTP 401 and NSW's login-restricted original Systematic Fauna Survey. No login, custodian contact or unverified ZIP download is needed to access this specific public field catalog.

## 2. The boundary of its ecological use remains critical

- **Calling Y/N is not strong chorus CI2/3**, not number of simultaneous ponds in the same species-night state, and not acoustic sound level.
- **Tadpole CPUE is not metamorph survival, egg viability or verified recruitment**. Adult CPUE is likewise a distinct sampled population indicator from calling males.
- **A Y/N on a species row does not establish a survey-opportunity ledger for all species not appearing as rows.** A published table can include opportunistic and positive-only event rows even if some listed species have `callingEvidence=N`.
- A site-date value **within `Gwydir` is not confirmed equivalent to the Ocock 15-wetland frame**, and the source might overlap governmental monitoring. Neither independence nor the complete 343-visit row crosswalk is established.
- No contemporaneous **site-specific water depth, pond hydroperiod, local rain-sound, egg/metamorph follow-up** fields appear in these 16 names.
- The **2014–22 CSV version** should not be silently conflated with the [university-linked Flow-MER release described as 2014–24](https://researchoutput.csu.edu.au/en/datasets/flow-mer-program-frog-abundance/); this audit addresses the pinned government 2014–22 resource ID.

## 3. Source-only real-rows QC plan, frozen before inspecting ecological outcomes

The next bounded source-quality exercise may fetch all **673 public records** only from the official resource via CKAN, with **no outcome estimation or raw record publication**, to report exactly:

1. number of source records by `Program` and broad calendar year;
2. number of **distinct nonblank sites** in each program (no names or coordinates output), source *site-date keys* with records (not complete surveyed opportunities);
3. within-program **site-date counts** and distribution of recorded distinct site-date support; a summary of nights having 2/3/4+ source-recorded sites, explicitly **not** verified 5-min completed audio visits or within-taxon strong chorus;
4. nonmissingness and original variable types/ranges **as schema** for `callingEvidence, CPUEAdults, CPUETadpoles`; do **not** print Y/N rates, CPUE values, species frequencies or individual records at this source stage;
5. whether the records appear to provide event IDs/methods/effort fields (the 16-column schema suggests **none**) and whether any source-preserved zero-call visit denominator can be established (**not from this API alone**).

The QC script must discard record values after in-memory aggregation, write **only non-sensitive aggregated counters**, and avoid any model fit or post-hoc search for favourable species/calling results. No automatic join to protected coordinates. No ecological hypothesis is regarded as supported by a source-quality pass.

**Source admissibility conditions**: original field-name semantics and provenance established, no date parsing failures silently discarded, uncertainty about omitted completely silent sites kept visible. Treat records with `callingEvidence=N` as *a listed species not heard calling*, **not** evidence that a completely unlisted species or the entire wetland was listened to.

## 4. New research decision

If actual public QC shows multiple same-region repeated dated wetland records and both calling evidence/tadpole data routinely populated, there is a viable **narrowly descriptive, independently sourced calling-activity–tadpole opportunity study**. It would require a separately frozen analysis protocol with site-year blocking and missing-opportunity limits; no claim of successful metamorphosis and no direct equivalence to frogcs's original 10-stop spatial configuration.

If source coverage is too sparse, too temporally aggregated, or lacks explicit survey opportunities, log that negative *data adequacy* result and **stop**, rather than extending the synthetic pipeline or treating population associations as causal. The Ocock 2015–20 original 343 survey ledger still needs authorized source-level confirmation for the actual spatial-chorus/reproductive payoff test.

## Source & source-protection provenance

Live field-only test: [run 38011111995](https://github.com/zuizui0223/frogcs/actions/runs/38011111995) (success). Machine code: `scripts/audit_flowmer_public_schema_zero_rows_v50.py`. The CKAN returned **zero rows** for this test; no live species responses/locations were loaded or computed. No JAE RC6 main changes, external contacts, private logins or field experiments.
