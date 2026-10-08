# v3.6 — Rain sound × water: identifiability, interference and spatial-endpoint design gate

**2026-10-08. Prospective / simulated-only. Separate from JAE RC6.**
**Not an executed field experiment, power analysis or new frog result.** Neither Iowa-native historical wet/dry nor new NAAMP outcomes have been obtained. Preserve the frozen manuscript, SI, and release.

## The key scientific correction to v3.5

Rain sound can elicit calling *without causing inundation* (Muñoz et al., 2020, *Hormones and Behavior* 118:104605, DOI [10.1016/j.yhbeh.2019.104605](https://doi.org/10.1016/j.yhbeh.2019.104605)). Actual inundation can change chorus response in either direction across taxa (Sarker et al., 2022, *Ecological Indicators* 145:109640, DOI [10.1016/j.ecolind.2022.109640](https://doi.org/10.1016/j.ecolind.2022.109640)). **Neither prior study establishes the mechanism of the NAAMP within-taxon spatial-concentration endpoint.**

A 2×2 water × sound table is **not sufficient by itself**. A field study can falsely claim a sensory effect if sound playback changes acoustic **detection** rather than true calling; it can falsely claim a sound×water effect if water and sound are assigned together; it can mistake multiple listening points in one shared chorus for independent experimental ponds; or it can conflate a route-night-wide stimulus with a night effect. The scientific study therefore has to pass four **prospective source-and-design gates** before a biological interaction analysis is authorized.

## Gate 0 — Are true calling and call detectability separable?

At each recording point and stimulus level:

- collect synchronized raw audio and the sound-playback channel, calibrated amplitude/spectrum at animal and microphone locations, clipping/AGC metadata and environmental noise;
- compare **live animal call rate** with playback fragments and background, via blind adjudication or a well-validated animal-only classifier;
- **blind-inject independently recorded known call signals** into representative real background noise at each planned treatment amplitude, and quantify sensitivity/false positives/CI2–3 misclassification with fixed operating thresholds;
- preserve “not assessable” as a distinct state from calling zero or silence; do not convert rain-masked audio to biological noncalling;
- randomize exposure vs control while recording across pre/stimulus/post windows, explicitly monitoring carryover and baseline differences.

**Failure stop:** If rain-noise alters detection or classification and the difference cannot be calibrated/corrected independently, a playback-induced change in measured CI or audible call counts **cannot establish** a change in actual vocal behaviour. Do not fit the frogcs-like spatial endpoint to the uncorrected event calls.

**Negative control:** Predefined matched-rain-like spectral/energy control evaluates generic masking/startle versus characteristic rain sound. A silent/sham speaker control measures equipment disturbances. Because matching all acoustic features of rain can itself reproduce the sensory cue, treat mechanistic “rain specificity” as conditional on the actual stimulus/control contrast, not as a universal property.

## Gate 1 — Can the causal treatment columns be estimated?

The causal *main* comparisons should be based on independently assigned interventions, with the true experimental unit explicitly stated.

For sites `i`, nights `t`, let `S_it` be playback treatment, `W_it` an approved independently randomized water intervention (not just observed rain), and `H_qi` the **pre-treatment** historical strong-chorus-site indicator for species q.

A prospective fixed-effect screening model for actual call rate is:

```
animal_call_it ~ physical_site_FE_i + night_FE_t
               + S_it + W_it + S_it*W_it
               + H_qi*S_it + H_qi*W_it + detection_controls
```

`H_qi` alone is absorbed by physical site fixed effects; no causal claim should be made from its main association. When playback is identical at **all ponds in a night**, `S_it` is absorbed by night fixed effects. **The history×sound contrast may still be estimable** if history differs across ponds and sound changes across nights; this does *not* restore an identifiable stand-alone sound main effect. When water treatment never changes within a site, its main effect is absorbed by site fixed effects. If `S_it=W_it`, their separate effects and interaction cannot be resolved.

**Critical difference:** the above algebraic full-rank check is a *necessary condition*, not a randomization check, power test, interference check or causal assumption validation.

The synthetic, outcome-free rank evaluator is
`scripts/audit_rain_sound_water_design_v36.py`. It checks:
- crossed toy assignments with all five candidate effect columns adding rank;
- night-only sound (sound main effect unidentifiable, history×sound may remain identifiable);
- site-fixed water (water main effect unidentifiable);
- water and sound perfectly confounded (sound and their interaction unidentifiable);
- no variation in H (history treatment modifiers unidentifiable);
- stable site-level H main effect (fully absorbed by site fixed effects).

This is a **mathematical design-QA demonstration**, not an endorsement of the fabricated assignment scheme or an empirical estimate.

## Gate 2 — Do treatment units interfere?

A multisite frog-chorus study is especially vulnerable to cross-site acoustic/social spillover. If a rain-sound speaker at pond A can be heard by frogs at pond B, pond B is **exposed**, not untreated. If one pond's calling induces calls elsewhere, social interaction is potentially part of the process rather than independent measurement error.

Before field randomization:
- map calibrated sound attenuation and background across candidate independent ponds in the species-relevant frequency band; **no universal safe distance is assumed**;
- choose pond/block separation and intervention windows from **measured propagating sound**, measured movement/connectivity and habitat geometry;
- document whether the causal estimand concerns individual ponds, acoustic neighborhoods, or an entire landscape cluster;
- randomize at the **whole acoustic exposure cluster** if interference cannot be prevented; analyze at that level. Do not count within-cluster recorders as independently randomized replicates;
- assess natural calls at untreated sentinel ponds during treatments, and reject nominal unexposed controls when measured spillover is appreciable.

**Stop:** If isolation fails and no credible cluster randomization is possible, a pond-level effect and frogcs-like “independent separated sites” contrast cannot be claimed. A network/spillover effect would require its **own prior design**, not ad hoc exclusion of responding controls.

## Gate 3 — Do the outcomes match the actual frogcs biological question?

Predefine **two separate response levels**:

1. **Marginal calling**: independently verified animal-produced call rate or calibrated strong-chorus state at each true breeding location. Sound-only stimulus effects are meaningful frog behavioral ecology, but they answer a **narrower** question than frogcs.
2. **Conditional spatial arrangement at a fixed calling magnitude**: for each taxon×observation block, define the number `k` of verified active physical sites, then compare **which** sites were active to an out-of-block site-propensity generator conditioning exactly on `k`. Evaluate history overlap and route-wide/dependence structure. Equal k does **not** imply equal placement.

The script's `conditional_exact_k_probs` enumerates `choose(n,k)` subsets from independent site Bernoulli propensities and normalizes the probabilities. For a tiny fabricated example, a selected historical-site subset can have greater expected overlap **solely because its site propensity was already high**; any recurrence analysis must compare against that conditional expectation rather than a naive uniform-random baseline.

Do **not** treat `k≥4` as a discovered new biological threshold; that definition originates in post-hoc NAAMP exploration. In an independently planned study, fix the minimum detectable sites and spatial estimand before outcome readback, using a prospective pilot for feasibility.

## Practical sequence, not an overpromised full factorial

**Phase A (feasibility and sound-first):** choose a naturally occupied and ethically appropriate target species with multiple genuinely independent wetlands; confirm site continuity, historical-chorus strata and measurable spatial separation. Calibrate detection and playback spillover *before* treatment. Use temporally crossed within-site acoustic treatments with washout, sham controls, fixed windows and genuine concurrent within-night controls. If auditory stimulation is not biologically effective, do not infer absence of all rainfall effects.

**Phase B (only if ethically/operationally permitted):** add controlled water-level/inundation manipulation in a managed/approved system. Document actual water levels, chemistry/temperature and sham disturbance. **Independent water assignment** must be crossed with sound assignment at the appropriate pond/block/night unit and not rely on natural rain always co-occurring with noise. Water manipulations can carry over between nights; analyze them as randomized pond/period treatments, not always as instantaneous toggles.

**Phase C (spatial explanation):** only when A/B pass source, detection, interference and crossed-design gates, assess whether a sensory-only, water-only or shared-state×local-filter generator reproduces both **total amount of calling** and **nonuniform conditional site arrangement**, including where previously strong physical sites are activated. Hold out complete physical/acoustic blocks or years, not randomly scattered clips from the same chorus.

### Decision ladder

| Evidence that *could* emerge | Defensible interpretation | What remains unproven |
| --- | --- | --- |
| Playback changes verified animal calls while water remains stable | Proximate sound sensitivity in that population | frogcs site-history selectivity, rainfall hydrology and cross-taxon generality |
| Independent water intervention changes verified calls/placement | Physical water contribution in experimental habitat | mediation of historical NAAMP rain effect |
| Both interventions independently alter calls, with identifiable interaction | Combined sensory/environmental control in the studied system | generic physiological mechanism, demographic success |
| Both explain marginal calls but fail fixed-k spatial arrangement | Activation magnitude explained, **frogcs-like spatial mechanism still missing** | unique common-state/social process |
| Spatiotemporal arrangement and history targeting are also reproduced in held-out independent pond blocks | A transferable *configuration-level generator* becomes credible | individual site fidelity, reproductive success and the original NAAMP mechanism as historically causal |
| Detection, independence, field identity or design-rank gate fails | **Inconclusive / non-identifiable** | no ecological sign claim allowed |

Do not claim an experiment is “pre-registered” unless the full design, target system, intervention amplitude, data quality stop gates, estimand, sample size/power assumptions, model fit criteria and holdout have actually been time-stamped before treatment outcomes are observed. Synthetic QA is **not** preregistration.

## Source and provenance boundaries

- Muñoz et al. (2020), *Hormones and Behavior* 118, 104605. DOI: [10.1016/j.yhbeh.2019.104605](https://doi.org/10.1016/j.yhbeh.2019.104605), field rain/chorus auditory playback and call-rate response in *Batrachyla taeniata*.
- Sarker et al. (2022), *Ecological Indicators* 145, 109640. DOI: [10.1016/j.ecolind.2022.109640](https://doi.org/10.1016/j.ecolind.2022.109640), inundation-associated species- and site-varying chorusing; **observational flow arrival**, not equivalent to randomized pond watering.
- Existing frozen frogcs numerical findings: `paper/manuscript.md`, `paper/supporting_information.md`; independent context: `studies/climate_landscape/V3_4_RAIN_HISTORY_HYDROLOGY_INTERACTION_DECISION_SPEC.md` and `V3_5_RAIN_SOUND_VS_WATER_MECHANISM_DISCRIMINATION.md`.
- Stage: **synthetic design and source audit only**; no wet/dry field values, experimental animals, sensory treatment, new frog outcome observations, causal effect estimates or code tests on real data.
