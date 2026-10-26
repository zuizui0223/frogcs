# PEM季節食物網：繁殖同調の効果と相互侵入可能性を区別する v0.1

Date 2026-10-25. All parameters are **illustrative and synthetic**; the user’s proposed adaptive synchrony/biotic constraint mechanisms are hypotheses, **not** previously estimated from frogcs NAAMP, NPS, GloBI or GBIF. This independent theoretical track leaves JAE RC6 main unchanged.

## The flaw in the first successful toy

The original `research/scripts/simulate_pem_three_guild_stage_balance.py` model produced a **narrow breeding cohort** with greater simulated 3-guild persistence in 108/108 matched cases; but **the model itself gave narrow cohorts both lower imposed cannibalism and an arbitrary predator-satiation survival benefit**. That statistic cannot establish a general synchrony advantage or prove frogs use coordinated breeding to avoid odonate/salamander stages. Original `integrate_years` runs 4 initial conditions but is **not a true rare-invader test**.

## Two controls must be compared before reading output

1. **Phase-only scan**, identical narrow/broad cohort width fixed at σ=0.05 annual cycle for all runs, same wetland water window, same 64 fixed yearly population parameter draws and all other parameters. Vary salamander larval phase `−.12,0,+.12`, odonate nymph phase `−.18,0,+.18`; two refuge settings (.15,.7) and two weak/strong dragonfly→salamander risk cue regimes, 3 historical **hypothetical** PEM1A/C/F annual water windows. Test whether `D⊣S⊣F` indirect effect and `D→F` direct effect produce different signed hazard responses.
2. **Cohort-width contrast**, matched two frog egg-pulse widths σ=.018 versus .095 under same environment, predator phases and parameter vectors. Important: in the primary width contrast, **remove artificial additional within-frog cannibalism and predator satiation factors**. Different water completion and stage overlap can still favor narrow cohort but this does not imply selection. As alternative sensitivity, explicit costly mass-aggregation tradeoff `cost=.0,.3,.8` of narrow pulses can allow broad strategies to outperform in some illustrative regimes, with other parameter values unchanged. Treat the cost magnitude as an invented stress test, not a measured calling or egg investment cost.

## Genuine invasion-when-rare screen (within a synthetic annual map)

Given Beverton–Holt-like annual 3-guild interactions `F=frogs, S=salamanders, D=odonates`, compute for each omitted species i a two-species resident run from nonzero initial populations of the other two for 220 years, then calculate the geometric mean growth multiplier of i if introduced at epsilon density during the final 40 years. A parameter draw passes the stricter screen if **each of its three two-species resident pairs persists and each omitted species has positive mean log growth when rare**. A second all-three-from-common-start persistence diagnostic may be recorded, but is not mutual invasion. This addresses an important limitation of existing toy `integrate_years`.

The test is about **this exact toy map only**. Mutual invasion of all pair-resident systems is informative but neither a theorem of global persistence nor observed community coexistence; alternative two-species attractors, stability changes and unmodelled resources remain possible.

## Readout

- Annual scenarios: 3 PEM × 3 S phases × 3 D phases × 2 submerged shelter × 2 cue regimes × 64 common fixed parameter draws, width fixed σ=.05 for primary phase scan.
- Frog predator pressure derivative wrt D at fixed S versus direct D→F and indirect D⊣S⊣F components. Classify where net frog hazard is increasing vs decreasing with D; changing D can have both signs despite D being a direct tadpole predator.
- Strict invasion screen fraction per fixed named scenario and parameter ensemble. For each PEM, phase shift, and cue level, report full range **without selecting one positive result**.
- Compare with older toy’s biased 108/108 narrow “persistence benefit” result; do not promote it. If all narrow/broad results remain one-sided with matched width, say structural sensitivity cannot yet be identified.
- No randomization or statistics from GloBI or NPS; no interpretation of parameter-draw frequencies as the distribution of real wetlands.
- Output clear source code, self-test of annual map positivity and invader log-growth, machine-readable synthetic contrast and GitHub Actions QA.

## Actual PEM classes are separate from source data

The hydrology scenario widths are chosen by hand and **not calibrated to USFWS PEM1A/C/F flood duration distributions**. NPS sites have Ephemeral, Semi-permanent, Permanent broad classes but no confirmed NWI polygon labels in its public acoustic CSV, and NAAMP coordinates need independent correction. Therefore do not claim any `PEM1F` field-specific frog chorus result from this calculation.
