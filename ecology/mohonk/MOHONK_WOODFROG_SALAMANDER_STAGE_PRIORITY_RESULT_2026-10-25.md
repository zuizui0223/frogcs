# A recurrent frog-first breeding sequence opens cross-stage encounters with salamander eggs
**Independent ecological observation | 2026-10-25 | NOT evidence of predation**

## Empirical result: original source and sampling unit
Original, publicly accessible *Mohonk Preserve Vernal Pool Amphibian Breeding Ecology Monitoring* (GBIF-US IPT v1.1, 2023 release; <https://doi.org/10.15468/dypfbs>). **Original source archive SHA256** `0309abd9afa4a224287d6853d79ae1f7111a3a7bb19b0d2337f05c280ef12b34`; `occurrence.txt` SHA256 `d52b288608a40c3b721f3561a57ace34728975522892a4fdc1d0b4f6ffb3610e`; 13,862 records (original source extends 1931–2021).

Primary window **2016–2021**, because the later survey records include explicit species × lifeStage zero count cells, whereas earlier survey records are much less consistently complete and are mostly positive reports. Pool identity from generalized coordinates in original data is converted to anonymized deterministic `P01`–`P11`, NOT interpreted as exact pond subhabitats. The original dataset has 11 ponds, 59 pond-years and **240 unique pond × day visits** in 2016–2021; 235 pond-days assessed both the focal wood-frog-tadpole and spotted-salamander-egg cells.

### First positive egg detection by both species, same pool × year
In **44 pond-years** both *Lithobates sylvaticus* wood-frog eggs and *Ambystoma maculatum* spotted-salamander egg masses were recorded at least once:

| Recorded stage order | Pond-years |
|---|---:|
| First wood-frog egg detection preceded first spotted-salamander egg detection | **29** |
| Both egg stages were first detected on same survey date | **14** |
| Spotted-salamander eggs detected before wood-frog eggs | **1** |

Among the **30 pond-years with distinguishable first-positive dates**, 29 (96.7%) were wood-frog first; a *descriptive* pond-cluster bootstrap of this conditional ratio gave **0.889–1.000** (2,000 resamples; seed 2840223). This is NOT a confidence interval for exact laying-time ordering; dates are survey-dependent interval/left-censored detections. The median **recorded first-positive difference** (spotted minus wood frog) was **6 days**, much of which may reflect survey intervals.

**Sampling robustness:** for 34 both-positive pond-years with ≥3 visits, wood-frog first=26, same-date=7, spotted first=1. In 20 pond-years where both species' first-positive egg records occurred strictly *after the first sampling visit* (reduced left-censoring), wood-frog first=14, same-date=5, spotted first=1. These restrictions were considered after exploratory source examination, so they are not independent confirmation.

### Same-day stage coexistence — potential encounter window
Across 235 pond-dates where both relevant stage categories were assessed, **31** had wood-frog tadpoles and spotted-salamander egg masses positively recorded **on the same date and in the same pond**; these occurred in **29 of 59 pond-years** (and 28 of the 44 pond-years with both species' eggs recorded). Also, nine pond-dates had wood-frog tadpoles and Jefferson-salamander eggs co-recorded. The latter is stage co-occurrence only, with no verified egg predation specific to the Jefferson-salamander pairing.

The archive had **zero positive spotted-salamander `lifeStage=tadpole` reports** in these later sampling events. Because monitoring is concentrated in early spring and species/stage detectability varies, this DOES NOT demonstrate absence of spotted-salamander larvae or that the reverse predation route cannot operate.

## Ecological hypothesis supported as an opportunity, NOT as a causal effect
The new empirical statement is:

> Across repeatedly monitored northeastern U.S. vernal pools, detected wood-frog egg masses usually preceded spotted-salamander egg masses when their order could be distinguished, and wood-frog tadpoles and salamander eggs repeatedly co-occurred on actual survey dates. These recurring stage encounters create **opportunities** for a previously documented trophic interaction.

Takahashi & Ruszala (2023; *Ecology and Evolution*, <https://doi.org/10.1002/ece3.10427>) experimentally established wood-frog-tadpole predation on spotted-salamander eggs and found that the consequences of egg-jelly defense can be **non-monotonic**, with intact egg masses benefiting from high predator exposure under specified laboratory conditions. That observed experimental edge is a separate dataset. **No observed attack, prey damage, embryo oxygen, survival, adult dragonfly or odonate nymph is present in the Mohonk GBIF resource.** It would be incorrect to claim that 31 same-day observations were observed predation, reciprocal predation, or hatching effects.

## The genuinely interesting next biological discrimination
A water-filled spring pool contains egg masses, larval predators and larvae at different times. The **direction and sign** of effects may depend on (i) *relative first hatch dates* and larval body size, (ii) *salamander egg development/jelly-layer state*, (iii) *pond oxygen and hydroperiod*, and (iv) *presence of other predator guilds such as odonate larvae and fish*. The experimental study already supports **non-monotonic outcomes** of egg attacks; the Mohonk dataset supports **recurring opportunity**, not the net effect.

This synthesis has more ecological content than method refinement, but the independent Mohonk data currently establish **phenological overlap, not effect on reproductive success**. A novel ecological **interaction-strength** paper would require predator activity and embryo hatching outcomes measured on the same pond/dates. The Oikos study by Carroll, Saenz & Rudolf (2023; <https://doi.org/10.1111/oik.09773>) already reported adult–larval phenological-overlap tracking in amphibian communities; therefore the general concept of cross-stage overlap is **not** claimed as new.

## Reproducibility and fidelity
- Independent source acquisition: [GitHub Actions run 40111669598](https://github.com/zuizui0223/frogcs/actions/runs/40111669598), artifact 12566891370.
- Independent primary analysis: [GitHub Actions run 40112620306](https://github.com/zuizui0223/frogcs/actions/runs/40112620306), artifact 12567002142; 4/4 source-only code validation tests passing.
- Original age-stage counts include many explicit zeros; absent records remain missing, never imputed as zero. Duplicate species×lifeStage×pond×date rows, if present, are collapsed to any positive without summing potentially redundant individual-count columns.
- Full year-specific counts and independently reproducible source processing are preserved under `ecology/data/mohonk/`. GBIF location coordinates are generalized; do not assume individual spatial adjacency within a pond.
- Original JAE RC6 frozen `main` and the earlier frogcs/NAAMP rainfall inference were **not** modified or used in these calculations.
