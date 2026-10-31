# Post-pilot reversal-strength × mobility × third-guild sensitivity

**Source:** [Actions run #41157727679](https://github.com/zuizui0223/frogcs/actions/runs/41157727679), SUCCESS (8 unit tests, 20-year primary replay and full sensitivity grid). Initial reaction parameters and default trial are recorded separately in `MULTIGENERATION_ABM_PDE_PILOT_RESULT_2026-10-31.md`. This 4×2×2 sensitivity grid was decided **after** observing that the default synthetic reversal `a_fe=0.12` produced long-term dragonfly collapse. It is exploratory, not a pre-registered or field-calibrated forecast.

## What the sensitivity actually shows

All differences below are (`a_fe>0` minus `a_fe=0`) **within the same mobility/third-guild setting**, not across unrelated model baselines. Absolute values are synthetic, aggregated over eight model patches. Two ABM seeds and one deterministic PDE per scenario; estimates are not ecological confidence intervals.

| 20-year outcome | Adult dragonfly change | Adult frog change | Dragonfly occupied patches change |
|---|---:|---:|---:|
| ABM: mobility, D→S on, `a_fe=.01` | −677 | +1824.5 | 0 |
| ABM: mobility, D→S on, `a_fe=.04` | −719 | +2011.5 | −8 |
| ABM: mobility, D→S on, `a_fe=.12` | −719 | +2166 | −8 |
| PDE: mobility, D→S on, `a_fe=.01` | −640.9 | +1586.0 | 0 |
| PDE: mobility, D→S on, `a_fe=.04` | −691.2 | +2018.3 | 0 |
| PDE: mobility, D→S on, `a_fe=.12` | −691.4 | +2063.1 | 0 |

ABM's eight-patch local extinction at .04 and .12 occurs in both seeds under the stage-specific mobility and D→S-on setting; with .01 adults fall strongly but occupied patches persist at year 20. **The comparison does not identify a biological threshold at 0.04**, because rates have arbitrary units, are not calibrated, and just two seeds were run.

## Movement and third-party context

At `a_fe=.01`, ABM mobility with D→S on retained all eight dragonfly patches in both seeds despite a mean −677 adult difference. With movement removed, the mean change in occupied patches was −2 (from the same 8-patch baseline), indicating context-specific local losses. With `a_fe=.04`, movement led to eight lost occupied patches in these two seeds; without movement the mean was seven. This does **not** prove mobility always rescues or always destabilizes: the net difference mixes stochastic repopulation, predator/prey spatial aggregation, and local demographic feedback.

Turning the D-nymph→S-larva link off changed absolute responses but did not erase the negative 20-year D adult contrast under this finite grid. In the PDE, the `.01` rate gave ΔD adults −640.9 with D→S on versus −728.8 with it off under stage-specific mobility. The third guild can therefore counterbalance a two-guild feedback *in this model*, but no field magnitudes or local S/D co-occurrence were used.

## Two essential mechanistic cautions

1. **Stage lumping:** The current experimental `F_adult` includes all postmetamorphic frogs and allows immediate reproduction. The Beranek et al. (2023) example includes postmetamorphic juveniles taking emerging dragonflies. A more realistic next model must separate postmetamorphic juvenile F (may prey, does not reproduce) from reproductively mature F, with age/size maturation and delayed recruitment. The ABM records individual age and parentage but has an exponential stage transition, not individually calibrated age- or size-dependent attack. The PDE is stage-density only.
2. **Emergence exposure:** Model `D_emerging` transitions at a mean exponential stage rate of 16/model-year, which is a **coarse approximately 23-day model stage**, not the observed often nocturnal one-night emergence exposure. Combined with `a_fe` and no external immigration, this can strongly overstate effective encounter opportunity. It must not be inferred from the 2023 predation observation, and the pilot's collapse is not a real-world prediction.

The 1-D ring is a synthetic connected habitat; real ponds would usually need a network, waterbody-specific hydroperiod, stage-specific movement matrices and possible sources/sinks. With all these assumptions, neither matched ABM/PDE trends nor the apparent strength-dependent collapse validate a trophic mechanism in nature.

## Reproducible outputs

- Main source: `research/scripts/multigeneration_reversal.py`, fixed 20 years, four ABM seeds 101–104 and PDE on/off.
- Post-pilot source: `research/scripts/multigeneration_reversal_sensitivity.py`, 16 physical settings (4 rates × 2 mobility × 2 D→S), each PDE and two ABM seeds, years 1/2/5/10/20.
- Audited small table committed: [year 5/20 contrast summary](results/multigeneration_reversal_20261031/post_pilot_year5_year20_summary.csv) (48 rows).
- Full `annual_stage_trajectories.csv`, `reverse_on_minus_off.csv`, `post_pilot_sensitivity_endpoints.csv`, `post_pilot_sensitivity_contrasts.csv` and receipts uploaded to the Actions artifact `frogcs-multigeneration-abm-pde-20261031` (30-day retention).
- CI: 8/8 invariants pass, 210 main trajectory rows, 105 main contrasts, **240 sensitivity endpoint rows and 1,200 contrast rows**, exact zero-rate reference; no modified source data or existing frozen scripts.

**Interpretation:** A spatial ABM/PDE test of the *possibility* of delayed predator–prey reversal feedback has been implemented. Strong synthetic feedback may arise, but the real emergence window, maturation lag and predation rates are unconstrained. It is therefore not yet an empirical explanation for the 4,248-site acoustic macro pattern.
