# v4.0 — Gwydir source: weather blocks, time aliasing and what river water can identify

**2026-10-08. External published-source and algebraic design audit, not a new frog response analysis.** Separate from locked JAE RC6. No raw Sarker chorusing records, new NAAMP endpoints, historical Iowa wet/dry measurements or field interventions were accessed.

## 1. Final source-grounded finding from original Sarker et al. 2022

Original publication: Sarker et al. (2022), *Ecological Indicators* 145:109640, [DOI 10.1016/j.ecolind.2022.109640](https://doi.org/10.1016/j.ecolind.2022.109640), Section 2.2.3, Section 2.3.2 and Table 2. The project monitored **six** acoustic sites for up to four nights immediately **before and after** the arrival of environmental river flows, with Gingham Waterhole missing one post-flow night (seven nights total).

The **published environmental Table 2** was transcribed, without call response values, into `reference_routes/GWYDIR_SARKER_2022_SIX_SITE_EXPOSURE_TABLE2_V39.csv`. The independent [v4.0 metadata/design verification](https://github.com/zuizui0223/frogcs/actions/runs/37797249847) is **SUCCESS**, with the receipt produced by `scripts/audit_gwydir_temporal_block_alias_v40.py`. It detects:

- **6 recording sites, but only 4 unique calendar × summarized-weather blocks.**
- **Carol Creek, Combadello and Tyreel** share the **same before/after calendar window**, Table 2 rain summary **0 → 4.6 mm**, and minimum-temperature summary **18.8 → 14.4 °C**. They are distinct habitats, not three independent weather interventions.
- **Allambie Bridge and Gundare** each have Table 2 rainfall **0 → 0 mm**, but **at different dates**. Their zeros do not establish a single paired control, a fully rain-free four-night period, or an absence of rainfall acoustic cues at the microphone.
- **Gingham Waterhole** has a later February/March observation window, temperature and prior rainfall context distinct from the other sites, plus **one missed post-flow night**.

### Subtle rainfall-source ambiguity; do not overcorrect

Table 2 calls the rain entries **“Total rainfall within 24 h (in mm)”** with **before-flow** and **after-flow** columns, while the same paper's acoustic Methods say that the regression used **rainfall in the previous 24 hours summed across all nights within each pre/post category** (and mean minimum temperature averaged across nights). The precise correspondence between the six Table 2 cells and the summed nightly regression input is not completely reconstructible from this published summary alone.

Accordingly the v3.9 table columns `rain_before_24h_mm` and `rain_after_24h_mm` must be read as **reported Table 2 labels**, **not verified cumulative rainfall for all pre/post acoustic nights**, **not exact measurements at each microphone**, and **not actual rain-sound/no-rain-sound treatment records**. Original meteorological data came from nearest weather stations, rather than colocated acoustic rain/sound sensors. Neither universal “completely dry for four nights” nor “only one specific day's rain is represented” should be claimed without the nightly source/dictionary.

The paper's reported river flow data includes managed environmental water and natural catchment runoff. Upstream flow arrival can make water available without immediate local recorded precipitation in some comparison windows, but it also changes water sound, inundation, phenology/availability and other factors.

## 2. Algebraic inferential problem: all 6 have the same exposure sequence

For each six-site Table 2 summary, `F_it = 0` denotes the **before-flow** observation period and `F_it = 1` denotes the **after-flow** observation period. Let `P_it` be an indicator for after rather than before. The published design has **F_it = P_it exactly for every site**.

A simple two-period design with site fixed effects contains an intercept, five site indicators and P, with rank **7**. Adding an identical flow-arrival indicator raises the **column count to 8 but leaves rank at 7**. The [v4.0 outcome-blind rank check](https://github.com/zuizui0223/frogcs/actions/runs/37797249847) verifies that identity from the published Table 2 structure.

**Interpretation:** with a fully general common pre/post-period effect in this two-period summary, there is no extra column that isolates a flow effect. This does **not** invalidate the original authors' observational mixed-effects comparison: the published mixed model uses a different adjustment structure and richer nightly information. It means **the design contains no simultaneously monitored no-flow counterfactual whose trajectory can identify the impact of flow independently of time**.

This restriction is even sharper when the 3 Carol Creek/Combadello/Tyreel habitats are mistakenly treated as three independent rain/temp contrasts. Their geographic sites are distinct, but their summarized weather/time drivers are shared. Six site labels do not provide six distinct hydrometeorological exposure realizations.

## 3. What the authors' actual chorus analysis does and does not find

Original paper, Section 3.2, not a new analysis:

- **River flow × frog species** interaction in chorus duration was **supported** (χ²=18.8, P=0.016), so there is no universal direction of the flow-associated calling change.
- Overall flow main effect was **not statistically supported** in their all-species chorus-duration model (χ²=2.6, P=0.107).
- Their rain term was **not statistically supported** in the same model (χ²=0.005, P=0.945). **Non-significance is not evidence of no rain effect**, nor a direct test of sensory rainfall noise.
- Follow-up species models associated arrival of flow with **increased** `Limnodynastes tasmaniensis` chorus duration and **decreased** `L. fletcheri` duration. These are site/time observational associations, not randomized causal contrasts.
- Original paper reports the nights were averaged/combined to avoid too-complex models in the small dataset; nightly soundscapes were collected, but the published Table 2 does not expose the full time-resolved taxon × site response array.

**Scientific synthesis:** the ecological pattern of a species-dependent response to river-flow/inundation is already published. frogcs must not claim to have independently discovered it by transcribing the author's exposure table.

## 4. The exact missing contrast needed for a stronger future test

For a prospective or independently obtained fixed-wetland system, the minimum discriminating target is **multiple water-arrival events with contemporaneous reference wetlands lacking arrival**, while independently monitoring:

- actual local precipitation **and rain acoustic level**, including verified no-rain windows;
- measured local water height, inundation rate/area and **running-water sound** (which can also elicit behavioural responses);
- matching temperature/time-of-year and animal availability/occupancy to the extent measured;
- synchronized original frog calling rather than modelled zeros from skipped/masked recordings;
- independent taxon × physical-site historical activity before any evaluation period;
- true wetland/acoustic cluster identity and propagating sound between controls.

For different independent flow events, include genuine conditions **rain without local inundation**, **inundation without local rain**, **both**, **neither**, with enough time/site replication that at least some water exposure contrasts exist **within shared observation dates**, not just before versus after. Exact-k history placement is a *conditional predictive* endpoint, never a controlled causal effect after conditioning on k influenced by exposure.

**Stop rule:** If only a single before/after flow event exists per site and no concurrent no-flow reference group exists, label flow as an **association with arrival/time**, not a unique causal hydrological mechanism; no rain-sound pathway can be ruled out without acoustic rain measurement.

## 5. Evidence provenance

- Original full text and Table 2: [ScienceDirect open article](https://www.sciencedirect.com/science/article/pii/S1470160X2201113X).
- Independent six-site Table 2 transcription and v3.9 exposure audit: `reference_routes/GWYDIR_SARKER_2022_SIX_SITE_EXPOSURE_TABLE2_V39.csv`, `scripts/audit_gwydir_flow_rain_table2_v39.py`.
- v4.0 **environment-only** block/rank script: `scripts/audit_gwydir_temporal_block_alias_v40.py`, [validated GitHub Actions run 37797249847](https://github.com/zuizui0223/frogcs/actions/runs/37797249847).
- No original raw nightly Sarker data acquired, and archived study files are not established as open response data by this exercise.
- **JAE RC6 scientific source `main` remains untouched**. No new frog calling coefficient has been fitted and no external original-source data custodian contacted.
