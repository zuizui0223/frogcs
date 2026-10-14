# v5.4 RESULT — original larval genus pooling is real; 7 equal-positive CPUE ties are mostly CROSS-GENUS

**Audit run:** 2026-10-10 JST. **Source:** [Australian Government CEWH Flow-MER Frog Abundance 2014–22](https://data.gov.au/data/dataset/flow-mer-frog-abundance), published CKAN resource `70f3b7c9-990b-4770-b306-57c4e7cdac61`.
**Status:** real post-outcome **SOURCE TAXONOMIC VALIDATION**, **NOT** species-specific breeding success analysis. **No RC6/main change**.

## Provenance and pre-read contract

[Source taxonomy contract](V5_4_TADPOLE_GENUS_POOLING_TAXON_CROSSWALK_GATE.md) was committed **9d604e3** before running the first v5.4 source field/name classification. This follows the previously seen v5.2 sign reversal and is **post-outcome source QA**, not preregistered new frog biology.

[GitHub Actions actual-source **38014198140 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38014198140); [source-only script](scripts/audit_flowmer_genus_cpue_ties_v54.py).

The allowed government projection contains `Program, SamplePoint, SampleDate, sampleDateStart, sampleDateEnd(Date/Time), speciesCode, speciesName, callingEvidence, CPUETadpoles`. No animal coordinates, specimen free-text, observer identities or protected site names are requested. In-memory taxon labels are used only to classify **equality of POSITIVE CPUE across different published species in the same wetland-label×long interval**. Outputs contain aggregate source classifications **only**. No new fitted effect size, rainfall or metamorph hypothesis.

## Actual source result

Same v5.2/v5.3 eligible frame: **673** total public listed-species source rows, **591** from Murrumbidgee, exclude **10** zero-length interval records and **2** records under **one** ambiguous species×source-site×start×end key. Retains **579 source rows across 98 site-label×interval groups** (not verified distinct independent physical wetlands or actual survey bouts).

**All seven positive-CPUE tie groups classify as follows:**

| Species pairs with exactly identical POSITIVE `CPUETadpoles` in the SAME site-label×interval | Distinct groups | Classified positive tied species pairs |
| --- | ---: | ---: |
| Two different published species **within `Limnodynastes`** | **1** | **1** |
| Two different published species within another *same* genus | **1** | **1** |
| Two published species from **different genera** | **5** | **5** |
| **Total** | **7** | **7** |

Other actual source structural checks:
- The published 579 eligible rows include **332 rows labelled `Limnodynastes`**, with **88** having positive `CPUETadpoles`, representing source labels, not verified conspecific larvae. `Limnodynastes` appears in **98/98** site-label×interval groups.
- **Seven source speciesCodes** had exactly one normalized published speciesName each; **zero** codes had multiple name mappings in this version. **Zero genus-only** strings such as `sp.` / `spp.` were present as the CSV's speciesName on accepted rows.
- The original v5.3 total **7 equal-positive intervals / 98 intervals** was fully reproduced, no source schema or coverage change.

## Corrected interpretation

**The original field-method report's taxonomic caveat remains real:** [Wassens et al. Murrumbidgee MER 2014–20 Technical Report](https://cdn.csu.edu.au/__data/assets/pdf_file/0008/3853403/Murrumbidgee-2019-20-MER-Technical-Report_final.pdf), Table 4-23, says *Limnodynastes* tadpoles were identified/pooled **at genus** because they could not be identified to species in field sampling.

But **the numerical coincidence of 7 positive tadpole CPUE ties is NOT mostly a within-`Limnodynastes` phenomenon**: **5/7 occur across different genera**. Ties can arise because CPUE is an effort-standardized discrete count subject to similar net exposure, rounding or coincidence. The present source does **not establish** that any positive value was improperly replicated across species, nor that code-to-name mapping is broken (it was one-to-one).

The **speciesCode↔speciesName consistency** is necessary for using named taxa but does **NOT** independently authenticate a `speciesCode↔larval developmental stage/species` crosswalk. The field method's documented genus pooling could have been handled through earlier preprocessing, later expert identification, source grouping, a different reporting layer or other unknown choices. We cannot choose among those explanations without the original data transformation record.

Therefore prior v5.3 language suggesting “seven positive ties + *Limnodynastes* genus pooling” should be kept strictly as **two distinct audit facts**, **not a single demonstrated source error**. v5.2's −16.1 pp pooled vs +19.8 pp equally weighted repeated-source-pair sign reversal remains numerically correct **for the released table** but cannot claim *species-specific larval fitness or causation*.

## Next non-fishing source decision

Rather than fit additional exploratory taxon subgroups or hydrology regressions, the minimal missing origin material is:
1. **Versioned tadpole identification/dictionary/crosswalk** mapping original fyke-net stage IDs to the published 2014–22 `speciesCode` rows and the *Limnodynastes* genus-level aggregation;
2. **Actual original short field visit times/effort** for adult transects and 2-large+2-small fyke-net sets, with valid missed/zero-survey states and the relation to >31-day publication intervals;
3. **Exact `SamplePoint` → true stable wetland unit** and dated water/hydroperiod to avoid source-label pseudo-replication.

No animal effect regression, exact coordinates, private raw data, source contact or revision to the locked JAE paper was conducted. **If these remain unavailable, STOP species-specific reproductive-payoff interpretation from the 2014–22 public release**. The result is a **verified source-table composition phenomenon**, not a failed biological hypothesis.
