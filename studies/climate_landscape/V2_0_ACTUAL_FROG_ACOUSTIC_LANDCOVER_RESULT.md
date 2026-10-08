# V2.0 actual frog calling × mapped land-cover crossover at Iowa 360417

Date: 2026-10-08. **Post-hoc descriptive ecological pilot only. NOT a causal land-cover effect, station-level verified habitat response, or new paper result.** Kept separate from locked RC6 and frozen negative v0.9 route-climate heldout test.

## Chronology: what was actually surveyed

USGS original SHA256-pinned Runs and Stops, without reading calls first, established 27 eligible surveys over 6 calendar years: **2010:3; 2011:5; 2012:6; 2013:6; 2014:1; 2015:6**. The most dramatic mapped forest label losses occurred at stop 10 in **2006**, four years before NAAMP monitoring began: **no before-after acoustic comparison is possible for 2006**. For the smaller **2012 mapped class change**, there are 8 visits in 2010–2011 and 13 visits in 2013–2015. The 6 surveys in 2012 were not assigned a direction relative to the change within that calendar year. [Original source-only date gate](https://github.com/zuizui0223/frogcs/actions/runs/37760767999); machine-readable `receipts/IOWA_360417_NAAMP_ACTUAL_SURVEY_YEARS_V20.json`.

## Actual calling × land-cover descriptive readout

The all-taxon, all-ten-site endpoint and treatment of the 2012 uncertainty year were **locked before reading the focal Counts.csv rows** in this new study, but the 2012 contrast itself was chosen after reading prior environmental maps: this is **not prospective confirmation**. [Source-hash-pinned successful run 37761504743](https://github.com/zuizui0223/frogcs/actions/runs/37761504743) used real NAAMP Counts.csv, Runs.csv, Stops.csv and pre-survey-year matched site-level historical NLCD C1V0 fractions. There were **10 observed species** and **592 positive species×stop×run acoustic records** across all 27 runs; no duplicate species-stop-run counts were found. Every acoustic zero arose only from a genuinely surveyed non-skipped stop.

Summary (2010–2011 versus 2013–2015):
- 8 versus 13 survey runs (**6 versus 10 unique dates**, **3 versus 4 distinct observer IDs**); 2012's 6 surveys withheld from pre/post comparisons.
- Strong CI>=2 **species×stop cells per survey**: **11.00 pre** (88/8) and **10.769 post** (140/13). These *do not* demonstrate a large directional change in route-level calling magnitude.
- The site distribution of these strong acoustic cells changed modestly: descriptive total variation of the 10-stop *share vector* = **0.07955** (not a P-value or evidence for cause).
- Stop 10, mapped 250m forest percent **7.727% (2011) → 5.909% (2012)**, strong species-stop cells per survey **0.875 pre → 0.769 post** and shares **7.95% → 7.14%**. The decline is small and **cannot be linked causally** to mapped forest loss.
- Stop 2 had **no mapped forest-class decline at 250m** over 2011–2012, but mean strong species-stop cells **1.250 → 1.846**, share **11.36% → 17.14%**. Stop 6 had no mapped 250m forest decline in that window, yet strong calling was **1.375 → 1.000**, share **12.50% → 9.29%**. Therefore the *observed acoustic rearrangement is not uniquely concentrated at the one 250m mapped forest-loss stop*.
- Strong-stop presence across route/year varies greatly; mean count of stops with any CI>=2 acoustic cell is 5.33 in 2010, 8.60 in 2011, 8.17 in 2012, 6.50 in 2013, 5.00 in the singleton 2014, and 6.83 in 2015. Year and observer / season composition were **not adjusted**, nor was environmental conversion verified on the ground.

**Classification:** Ecological mechanism **not established**. One observation route, environmental-selected 2012 change, only one salient 250m forest change and no geographic replication. This is neither direct movement, site fidelity, abundance nor confirmed reproductive success. The 2021 official map agrees numerically with original 10 archive coordinates but does **not** independently verify 2001–2015 physical field-site continuity. Older C1V0 categories are not the current Collection 1.2; no confidence layer was used.

## A source-selected scaling lane (before reading outcomes for new routes)

The published Iowa DNR route-index ↔ original USGS *metadata only* intersection has 56 common IDs. Applying a fixed and outcome-free `n_years >= 5 AND n_site_ids == 10` rule to **all 56** yields exactly **9 candidate routes**, of which 360417 is the explored discovery route and **8 are potential new independently response-unread routes**:

- `360104`: 14 runs / 5 years
- `360109`: 13 runs / 5 years
- `360110`: 18 runs / 6 years
- `360125`: 14 runs / 6 years
- `360213`: 11 runs / 5 years
- `360219`: 14 runs / 6 years
- `360316`: 11 runs / 6 years
- `360412`: 10 runs / 5 years

This is an *eligibility definition based solely on prior route-source metadata*, not a pre-established treatment or land-cover response group. Before new site-level association analysis, independently audit physical station history, true survey years around any mapped class changes, source category confidence and paired valid pixels in every route. Do not declare these eight independent frog-climate replications without these checks. Do not reuse the negative v0.9 model with tuned lag/penalty/threshold, and do not promote post-hoc stop10/stop2 comparisons to independent validation.

## Next decision

Do not fit a single-route P-value or select favorable frog species. Pursue a fixed, multi-route **source-only** image/temporal eligibility census, then freeze an independently geographically blocked analysis if enough verified locations remain. Alternatively, if independent historical field-station proof or C1.2 confidence layers remain unavailable, retain this as a descriptive environmental/observation-process case study and do not force causal publication claims.
