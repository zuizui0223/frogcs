# frogcs: rainfall-gated chorus site allocation × vegetation × hydroperiod × stage-overlap — field-data contract v1

**Authored 2026-10-26.** Supersedes no RC6 scientific files. This combines the user's expanded hypothesis about **whether acoustically preferred wetland sites have fewer competitors or a different stage/phenology match** with actual observed rain, habitat and life-stage information. One intended integrated paper, research only, already post hoc to RC6/NPS/INBO historical results. Crucially, **do not reinterpret NAAMP roadside listening stops as identified ponds**, or GBIF 1-degree taxon occurrence as the true animals in those ponds. No casual claim that predators/competition are absent where undetected.

## Core new testable distinctions

### H_SITE — selection versus environmental quality

The probability that a species is recorded calling at a surveyed **wetland** is affected by **recent precipitation/ambient conditions**, **current water depth and whether it typically persists**, **emergent and submerged vegetation cover and architecture**, plus source-specific detection effort. Persistent habitat quality may cause BOTH frequent calling AND high other-taxon richness, even without any biotic interaction.

- Target 1: **strong/multi-stop within-taxon RC6 conditional concentration C remains frozen** as a *roadside acoustic result*. Never recompute C from unrelated pond observations and call the result an external replication.
- Target 2: **site-selective binary acoustic detections** at independently monitored true wetlands where exact pond/site geometry is source verified; e.g. 2024 Hungary (29 sites, 129 acoustic visits on 26 dates). Repeated same-date observation sets permit site allocation diagnostics, **not RC6 ordinal CI2+/CI3 concentration**.
- Variable `prec` in Hungary is an observed survey weather column with range 0–2.6 in the original 2024 acoustic rows; the sampling interval is not guaranteed to be NAAMP previous-72-hour rainfall. `depth` is site-level one-time depth, NOT hydroperiod days or documented annual drought. `ci` restoration context, NOT water permanence. Site `cover_emerged` and `cover_submers` are measured percent cover, not stem density or annual canopy turnover.
- Separate NPS `Hydroperiod` categories (Ephemeral/Semi-permanent/Permanent) already provide a **broad static source duration** comparison of prior same-taxon site acoustic use (+0.3523, +0.5022, +0.4950 by class). This is distinct from the Hungary rainfall/weather experiment and not a measured local drying time.

### H_COMP — low-competitor versus shared-habitat alternatives (new)

The *low competition at preferred calling locations* prediction requires **quantified directly surveyed other-taxon aquatic-stage pressure present before focal calling**, not merely GBIF nearby sightings or absence of GloBI links. A *negative* relationship between lagged other-frog larval occupancy/density and subsequent focal adult chorus would be consistent with filtering; a *positive* link could indicate common quality, facilitation or social attraction. Neither alone identifies competition or predation.

- Source-blind INBO candidate: `datasetKey/DOI 10.15468/d4bu8j` choir core × `10.15468/swgure` larva core. Use exact original `locationID` and validated locality labels, and strictly **last calendar-year** other Anura larva or Caudata larva **sampling opportunity** before current-year focal `Hyla arborea` choir event. A source's frog survey may systematically target species, so unassessed taxa are never zero. Taxonomic guild ≠ proven competitor or tadpole predator; prespecify `other-anuran-larva` and `caudata-larva` as separate ecological covariates with agnostic sign. Require >=30 complete site-year opportunities, >=15 verified sites, 3 years, and >=10 both explicit present/absent exposed/response values; otherwise stop.
- Do **not** use current-year larval census after the adult chorus to explain why a preceding adult chose that site; this violates temporal order. Same-year larval co-recording can illustrate community **stage structure**, not be a prior exposure.

### H_STAGE — competition at similar phenological stage versus unequal-size predation (new)

These are **competing mechanisms**, not two names for the same observed co-occurrence. Similar-sized, diet-overlapping larval cohorts may compete for resources; large overwintered predatory larvae may consume eggs/tadpoles of smaller taxa. Both can create reduced juvenile success at intermediate time/stage separation, but the expected direction depends on feeding type, sizes, prey escape and water habitat. A true prey juvenile survival denominator or experimental attack measurements are required to tell them apart.

- Stage **difference must be observed within the same year and source pond**: known stage, first/last observation timestamps and preferably body size/Gosner stage of both guilds. GBIF `larva` for both taxa and a within-month cell do not measure comparable ages/body sizes or physical encounter.
- A species record `adult` versus `larva` is **not** a quantitative distance in ontogenetic space. Only source-validated `Gosner stages`, snout–vent/body sizes or predetermined numeric maturity-stage chronology can support a numerical developmental-stage proximity test.
- The registered full GloBI source identifies candidate directed stage links but predominantly poorly replicated source DOIs; GBIF reports stage presence, not *interactions*. Use a feeding-guild verified matched **nonpredatory** aquatic taxon as a negative control at identical detection coverage. *Caudata* guild is not automatically a predator of *Hyla* eggs; *Chironomidae* includes some predatory larvae and is not automatically a negative control.

### H_RAIN×WATER×VEG×BIOTIC — one evidence hierarchy, not a flat full regression

- **E0**: survey-date/weather `prec`, temperature and humidity + season/detection effort.
- **E1**: E0 + **measured** actual water depth or *actual* source water persistence category.
- **E2**: E1 + independently measured emergent/submerged vegetation, optionally `rain × emergent` / `rain × depth` interactions (when identifiable across surveyed independent wetlands).
- **E3**: E2 + **strictly preceding** observed aquatic-stage competitors/predators and validated nonpredator controls, if those exposures refer to exactly the same waterbody.
- **E4**: E3 + stage-size/phenology overlap × verified water history (wet/dry reset); **no current source permits an unbiased full E4**.

Every tier uses **identical eligible site/date/taxon observations and held-out entire physical sites/year blocks**. If E3 requires unmeasured covariates, return `NOT_ESTIMABLE`, **not** numeric zero. Never merge Hungary weather/cover to INBO source sites or NPS Hydroperiod, because they are not the same wetlands.

## Two actual next analyses frozen before new outcomes

1. **Hungary independent rain×vegetation site prediction:** use archived original CC BY files `research/external/zenodo_15044115` already source-pinned. Response = `frog_any` at each of **129 acoustic surveys**, not a chorus intensity or true colonization. Baseline = already frozen `W1_plus_depth_context` model (day-of-year linear/quadratic, `temp`, `humid`, `prec`, `depth`, `ci`); M1 adds `prec×cover_emerged` AND raw `cover_emerged`, M2 adds `prec×depth` AND `cover_emerged` on identical source rows. **Fixed 5-fold GroupKFold by wetland site**; scikit-learn logistic C=1, train-only normalization and one-hot context, 2000 site-cluster resamples of fixed held-out errors. M2 test is modest/noisily identified due to only one year. Evaluate no other interaction if M1/M2 fails; negative results stay.
2. **INBO strictly lagged same-wetland cross-species stage coverage:** source-SHA checked original two event archives, **source-blind to actual presence/counts**; count current *Hyla arborea* explicit choir opportunities with *previous-year* (not future) **other-anuran-larva** and **Caudata-larva** scheduled surveys at the same exact `locationID`. Report independent locations, site-years, years and survey protocol metadata. Only after G0 passes, lock detection/effort rules and consider G1 other-larvae-status vs choir. Prior acoustic species source-selection remains post hoc, not a new pristine confirmatory hypothesis. **GBIF ordinary occurrence coordinates are not source wetland site keys.**

## No false equivalence or paper gate

- NPS observed class-slope difference establishes historical acoustic-site signal is weaker in broad Ephemeral than Permanent, **not evidence that predator density causes this**.
- Hungary site survey weather is no paired dry/wet random treatment; a precipitation interaction cannot prove rain activates breeding.
- GBIF global juvenile/tadpole photo counts cannot be called cohort survival, and matched nontrophic controls cannot remove all shared effort or habitat effects.
- Historic RC6 physical coordinates have known outliers. Exact physical wetland/geometry crosswalk from authoritative route-stop station information is required before assigning external GBIF environmental/predator layers to a selected RC6 stop.
- A true test of the hypothesis **"chorus concentrates at low-competitor ponds after rain in vegetation with particular hydroperiod"** needs all exposures in the **same pond network and same rain event**. Present public sources allow separate *conditional predictions*, NOT the completed unified causal regression. If no qualified same-site shared data exist, report which physical/environmental layer blocks identification.

**Claim ceiling:** spatial acoustic site selection + environment covariates, source-recorded prior aquatic stages, and independent phenological potential. **Not** competition or predation as observed causal mechanisms, not reported synchronized oviposition, and not individual frog movement/recruitment.
