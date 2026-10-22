# Independent frog acoustic partner test: Midwest ARMI 2024 — 2026-10-22

## Conclusion and current state

**Source successfully verified, original survey keys resolved, independent prediction executed, and original NAAMP positive bullfrog-partner model does *not* meet the frozen independent-survey portability criterion under the observed 2024 USGS ARMI five-minute site-visit scale.**

This is a properly executed **independent observational nonsupport result**, not a proof of zero association, not a failure of NAAMP's *different* 10-stop fixed-margin site-allocation claim, and not any causal result about competition, cooperation or aquatic plants. The independent evidence narrows the range of conditions under which a named frog's acoustic locations can function as a transferable ecological predictor.

## Data provenance and quality

- Public USGS Amphibian Research and Monitoring Initiative (ARMI) 2024 cricket frog survey, **ScienceBase item 68016413d4be0263cab109a8**, [DOI:10.5066/P19ZCGWM](https://doi.org/10.5066/P19ZCGWM), v1.1 revised April 2, 2026.
- Exact original CSV `ARMI_2024_cricket_frog_data_release_2025_v1.1.csv`, **235,391 bytes**, official MD5 `e201e24463d90e23c1f5f903e730e26c`, full-file computed SHA256 `dafd388c7ccb79e08dbadd37a25c604473a8caf4ff5c8318532740acb56a04e4`.
- Original FGDC XML **41,317 bytes**, MD5 `a5a72215d0cd2ad0a027de814edfa701`, SHA256 `a41deac79d0f6be758101b27dc97014896b928723251b4544ddeefd6c4456a15`.
- USGS source says **all anuran species heard during each approximately five-minute survey are recorded**, with `Species=none` explicitly meaning **no anuran heard**. Source is a *positive-list of calls*, **not a complete species×individual census**; absence of a particular species row in a valid surveyed event indicates **no recorded call**, not biological occupancy absence.
- Initial response-blind source and event grouping audit verified **1,934 original rows**, **798 unique visits**, **343 original project×site groups**, **four projects**, **318 sites with two or more visits**, **all metadata keys/date/method/weather valid**. Audited before source calling outcome readback in [workflow 39781861923](https://github.com/zuizui0223/frogcs/actions/runs/39781861923).
- Initial outcome analysis stopped when same species appeared multiple times under the same six-part survey event key. Separate structure-only forensic audit [39782928959](https://github.com/zuizui0223/frogcs/actions/runs/39782928959) found **368 repeated event×species groups**, **367** with different `Compass_direction`; **zero conflicting site, weather or original location metadata**. This supports treating repeated species/bearing records as one **same-survey positive detection**, not independent extra site visits. The exact correction was frozen in `exploration/ARMI_2024_SURVEY_SPECIES_KEY_CORRECTION_V0_2.md` before any species-pair co-calling calculation.
- Analysis passed revised synthetic QA and exact source checks, [successful workflow 39783701641](https://github.com/zuizui0223/frogcs/actions/runs/39783701641), artifact **12428505672**.
- One original 2024 survey is a five-minute observation at a site, by an observer and method. Compare with NAAMP's *ten sequential stops per route-run*; these are scientifically **different estimands**.

No raw USGS field data, original station identities, site coordinates or individual-bearing observations are redistributed in the GitHub result artifacts.

## Exact predeclared primary result

Positive named partner = American bullfrog `Lithobates catesbeianus`; response = green frog `Lithobates clamitans`. Both were selected by the prior NAAMP investigation, *before this independent programme's calling results were read*. ARMI 2024 was explicitly designed to investigate cricket frogs and its stations were not a random sample of all upper Midwest wetland habitats.

- All **798 complete surveyed visits** retained; no selection based on focal species presence.
- Green frog recorded in **306** visits across **172** sites.
- Bullfrog recorded in **214** visits across **133** sites.
- **98** individual five-minute visits recorded **both** named species.
- **220** visits had `Species=none` (no frog heard), and **376** visits heard neither of the two focal frog species.
- Geographic **whole-site** train/test A/B split by fixed SHA256 Project:Site, alternating within project: fold A **398 visits / 172 sites**, fold B **400 visits / 171 sites**. Both folds had adequate focal calls, including 107 bull-positive events per fold, and 154 versus 152 green-positive events.

Two fixed predictive models:
- **M0:** site-disjoint logistic regression of greenfrog recorded call on original project, observer, ear/microphone method, Beaufort wind, recorded sky/cloud categories, day-of-year and local 24-hour arrival-time sin/cos, plus the number of *other* recorded frog taxa.
- **M1:** M0 **plus a bullfrog recorded-call indicator on the same observation**, with otherwise identical ridge-equivalent L2 `C=1`, `lbfgs`, at most 500 iterations. Both models trained exclusively on the complementary project-stratified physical site fold; **no NAAMP model weights imported**.

### Held-out scoring

| Measure | Estimated M1−M0 improvement | 95% site-block bootstrap CI | Support |
|---|---:|---:|---|
| Independent-site Bernoulli **log predictive score** (nats/visit) | **+0.0053205** | **−0.0023349 to +0.0130211** | **Not supported** |
| Independent-site Brier error reduction | **+0.0022126** | **−0.0012462 to +0.0056790** | Not supported |

- Geographic site A and B heldout fold mean log-score increments are **+0.007186** and **+0.003464**, respectively.
- The fitted bullfrog coefficient was positive in both training folds (**+0.71664**, **+0.55049**), but the independently resampled site-level interval **includes 0**. The frozen positive-portability decision requires a strictly positive 95% CI, both fold gains positive, and both fitted partner coefficients positive. **The CI gate failed.**
- This is **not statistical equivalence** or proof of no bullfrog-related association. It is **nonconfirmation of additional heldout prediction** at the 2024 site-survey observation scale with these baseline covariates and available site clusters.

### Ecologically relevant context and source-selection differences

The four original projects were selected with different historical site-selection rules; call occurrence differs considerably among them:

| Original ARMI sampling project | Site surveys | Green frog recorded | Bullfrog recorded | Both |
|---|---:|---:|---:|---:|
| ARMI night surveys | 92 | 70 | 40 | 32 |
| Cricket frog 2006 | 123 | 51 | 17 | 12 |
| Cricket frog 2007 | 203 | **1** | **67** | **0** |
| Cricket frog exploratory | 380 | 184 | 90 | 54 |

These are survey recording counts, not abundance. For example, the 2007-design source project has almost no green frog calls even though many bullfrog calls, illustrating why pooled co-detection cannot safely be interpreted as an organism interaction and why project must be a nuisance variable. Site selection, local conditions, season and differential detection can all explain the heterogeneity. We did **not** search for a subset with a more favorable bullfrog slope.

### Secondary negative partner and first-order site effect limitation

`Dryophytes versicolor` (modern published taxon matching NAAMP `Hyla versicolor`) was heard on **245 visits / 176 sites**. Adding it to M0+bullfrog did **not** improve the heldout site score:
- score increment **−0.0020809 nats/visit**,
- site-bootstrap CI **−0.0079166 to +0.0037326**,
- both fitted training effects were positive (+0.7315 and +0.1326), **opposite** the prior negative partner expectation.
- `Anaxyrus fowleri` was **not present in the published 2024 ARMI species list**; no alternate negative taxon was substituted.

A predeclared within-site logistic site-fixed-effect sensitivity had just **13 sites / 37** usable observations with both species' temporal variation and generated an unstable/quasi-separated fit. Its coefficient/uncertainty was nonfinite or otherwise not identifiable and is **not** cited as valid evidence. The code was amended to fail closed on nonfinite site-fixed uncertainty, JSON emitted with strict finite formatting, and the original primary heldout models/observations were reverified unchanged. This is a measurement/identifiability limit, not a contradictory effect.

## Interpretation: what changed in the ecological claim

| Ecological scale | Supported result |
|---|---|
| USGS NAAMP multi-stop route-run within-community allocation (2001–2015) | Bullfrog `L. catesbeianus` site locations **add route-heldout partner information** for `L. clamitans` at NAAMP's fixed-margin local spatial allocation scale. No causation proved. |
| USGS ARMI 2024 independent five-minute frog-call visit, project/site disjoint | +0.00532 nats/visit mean gain but CI **straddles zero**; **independent portability not confirmed at this distinct observational grain**. |
| Negative frog partner information, conditional on bullfrog | Did not add reliable heldout gain under NAAMP; secondary 2024 `Dryophytes versicolor` likewise not a supported negative increment. |
| Plants / invertebrate or fish predator mediation | Unobserved in the independent ARMI flat file, unverified causal pathway. |

**Most defensible general statement:** the existence of some nonrandom partner-specific frog calling-site patterns within NAAMP does not guarantee that the same named pair contributes portable, marginal predictive information about *recording-level* frog detection in a different field programme. This may reflect distinct statistical grain (spatial allocation conditional on activity vs actual calling/no calling), site selection, climate/weather, habitat, season or genuine ecological context dependence. Those explanations are hypotheses, not distinguished by this study.

The original NAAMP model and observation results remain unchanged; an independent **same-grain spatial-allocation** dataset, or synchronized continuous multi-site frog acoustic monitoring with wetland vegetation/hydrology/predator surveys, is necessary to test broad ecological portability or causation.

## Reproducible sources

- Prereadback source/science contract: `exploration/ARMI_2024_INDEPENDENT_FROG_SOURCE_CONTRACT_V0_1.md`.
- Frozen source-only QA and official checksum: `exploration/ARMI_2024_SOURCE_ONLY_VERIFIED_RECEIPT_V0_1.json`.
- Source forensic repeat-bearing QA: `exploration/ARMI_2024_SURVEY_SPECIES_DUPLICATE_AUDIT_RECEIPT_V0_1.json`.
- Survey grouping amendment before co-detection readback: `exploration/ARMI_2024_SURVEY_SPECIES_KEY_CORRECTION_V0_2.md`.
- Full independent numerical result/validation receipt: `exploration/ARMI_2024_INDEPENDENT_PARTNER_RESULT_V0_1.json`.
- Immutable executed workflows: [source-only 39781861923](https://github.com/zuizui0223/frogcs/actions/runs/39781861923), [duplicate QA 39782928959](https://github.com/zuizui0223/frogcs/actions/runs/39782928959), [final independent model 39783701641](https://github.com/zuizui0223/frogcs/actions/runs/39783701641). Final source data never copied to main or attached to GitHub artifacts.
- All files on independent exploration branch `exploration/armi-independent-bull-green-2026-10-22`; **JAE RC6, supporting material, main and manuscript evidence are unmodified**.
