# v6.6 — falsify apparent acoustic memory caused by omitted slow hydrology (frozen source-free test)

**2026-10-11 JST. Independent draft PR #135; JAE RC6/main unchanged.** This contract is committed before examining v6.6 synthetic model outputs. This is not a preregistered frog study or real biological inference.

## Critical alternative missing from v6.5

v6.5 correctly separated its four *deliberately simple* artificial regimes. But its hydrological baseline uses **only current depth and immediately preceding depth-change phase**. In real wetlands, frog calling can depend on slow, measured (or unmeasured) *accumulated wetness, hydroperiod and antecedent moisture*; previous calling then **proxies** the same slow water state.

Therefore even if previous acoustic calling **has zero direct generative effect** on future calling, its addition to an under-specified water model may improve held-out predictions. That would be a **predictive gain**, but would not distinguish a biologically additional acoustic state from omitted water.

## Frozen artificial worlds and model contrasts

Simulate 180 entirely invented wetlands, 24 artificial consecutive episodes and 5 fixed seeds (20261011–20261015). Local synthetic depth is autocorrelated across episodes. Its past-only exponential-filtered cumulative water state `slow_water` is a *known artificial cause* of calling. Observation labels follow a Bernoulli distribution with:
- stable wetland propensity;
- present water depth;
- artificial diel proxy;
- nonzero accumulated `slow_water`;
- **zero direct previous-calling coefficient** in world **H0_SLOW_WATER_ONLY**, or nonzero direct previous-calling coefficient in the added positive-control world **H1_SLOW_WATER_PLUS_DIRECT_CARRYOVER**.

Each comparison uses the **same final held-out episode** and estimates site propensity on earlier episodes only. Recorded depth phase is the sign of water change and is never directly sampled as an independent driver.

Four forecasting models:
1. **M1_SHORT_HYDRO**: current depth + phase + diel + wetland fixed propensity.
2. **M2_SHORT_HYDRO_PLUS_ACOUSTIC_LAG**: M1 + last completed episode calling.
3. **M1_FULL_SLOW_WATER**: M1 + strictly past/current-depth-derived `slow_water`; this is hydrological history, NOT calling history.
4. **M2_FULL_SLOW_WATER_PLUS_ACOUSTIC_LAG**: M1_FULL + last completed episode calling.

Score with identical held-out wetland outcomes via negative log loss (larger is better):
- `spurious_gain = score(M2_SHORT) - score(M1_SHORT)`;
- `adjusted_gain = score(M2_FULL) - score(M1_FULL)`;
- `slow_water_gain = score(M1_FULL) - score(M1_SHORT)`.

**Anticipated falsification pattern in H0**: spurious gain may be positive even though direct calling lag = 0; when the actual artificial slow water state is included, adjusted gain must be substantially smaller and not consistently positive. In **H1** a genuine injected direct lag should still improve prediction after slow water is controlled. Do not tune effect sizes/regularization after the first synthetic outcome read to force a preselected desired pattern. Document failure transparently.

To protect against the trivial one-step lag memory of AR water from masquerading as strict historical acoustic state, add a **wrong-wetland placebo** by permuting last-episode labels across wetlands using fixed seeds. It should not systematically beat the correctly measured water-history model.

## Important interpretation

Even if this QA passes, *real* hydroperiod, temperature, water quality and sensory/detection confounding remain challenging: this artificial exponential filter is not proof that a real sensor measures every ecologically relevant state. Observational `M2` gains alone never establish individual memory, philopatry, social attraction, adaptation or breeding success.

The actual proposed observational paper must state **hydrology/history model adequacy is the key discriminator**, not simply that lagged calls add log-score. If comparable depth/phase and true local logger histories are absent, report **HYDROLOGICAL_PATH_INCOMPLETE: ACOUSTIC_HISTORY_MECHANISM_NOT_IDENTIFIABLE**. No sensor-source selection based on frog outcomes is permitted.

No original frog calls, wetland locations, hydrology values, archived audio, API-protected resources or third-party contacts involved.
