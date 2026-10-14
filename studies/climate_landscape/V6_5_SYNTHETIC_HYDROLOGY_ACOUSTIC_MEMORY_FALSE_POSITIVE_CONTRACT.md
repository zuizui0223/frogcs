# v6.5 — synthetic false-positive guard for hydrological path versus prior acoustic state

**2026-10-11 JST. Independent draft PR #135; frozen before running v6.5 synthetic scenario readouts.** This is a **code/model-discrimination stress test**, not a new real-world biological analysis, not a prospective registration before past NAAMP or published Flow-MER results. JAE RC6/main remains untouched.

## Reason for this gate

The v6.4 ecological design separates:

- **M0**: present local depth + seasonal/diel proxies + persistent species×wetland propensity;
- **M1**: M0 + strictly antecedent local depth rising/falling phase;
- **M2**: M1 + previous independent episode's same-taxon same-wetland acoustic outcome.

Yet it has not demonstrated that fitting M2 can **avoid falsely claiming chorus memory when acoustic events are actually conditionally independent once hydrology and fixed wetland propensities are represented**. Conversely a model must detect a known injected history dependence before future real biological testing is credible.

## Pre-run, artificial mechanisms (four simulations, no fauna sources)

Generate only pseudorandom, program-created wetland×episode records using source-independent seed **20261011-style fixed numerical seeds**, **180 invented independent wetlands**, **19 artificial chronological wetting episodes**, site-specific fixed propensity, AR(1)-like local water-level trajectories, diel proxy, and artificial Bernoulli calling labels. Depth **phase** is computed from *current minus previous depth* (not a randomly chosen independent treatment). Use five fixed seeds in every regime.

Artificial scenarios, model versions and coefficients are **software QA only**:

1. **S0 Null**: calling depends on present water, diel proxy and stable wetland differences; no rising/falling or acoustic carryover coefficient. Expect neither M1 nor M2 to obtain robust held-out gains.
2. **S1 Hydrological-path only**: additionally inject phase effect, with **no** prior-call coefficient. Expect M1 over M0, but **not** consistently M2 over M1.
3. **S2 Acoustic carryover only**: additionally inject a previous-episode outcome dependence, but no phase effect. Expect M2 over M1; M1 need not gain.
4. **S3 Both**: inject phase and prior-call effects; expect improvements from both M1 and M2, where information is distinguishable.

Build genuine training-history variables using *only completed earlier artificial episodes*; fit a regularized logistic model with identical training/evaluation populations. **Single withheld final episode** per artificial wetland: train on earlier episodes and test only on the last; its calling labels cannot enter any model predictor or its fitted wetland propensity. Site fixed effects are represented explicitly and fitted ONLY on training years, never by held-out outcomes.

### Falsification / negative controls

- **Placebo history**: independently permute prior-episode calling outcomes *across wetlands within each artificial historical episode* before fitting a placebo-M2. The placebo must not consistently show the large extra gain that true lag produces in carryover regimes.
- **Correct temporal boundary**: M2's held-out predictor can use only the immediately preceding **training** episode. An attempt to use a held-out or later outcome as history must raise an error.
- **Full conditional baseline**: wetland-specific intercepts plus current depth and diel proxy in M0, and a **hydrology-derived** phase in M1. Thus an M2 gain cannot be counted as evidence merely because the baseline forgot stable wetland propensity or basic water state.
- **Paired held-out test**: record signed improvements as mean **negative log-loss gains** on the same final-episode wetland outcome rows, not a training AUC, per-clip pseudoreplicated P value or invented ecological effect size.
- Use a pre-run synthetic tolerance for reproducible seeds; this tests software mechanics, NOT power or Type I error rates for real frogs.

## Research-claim firewall

Passing these synthetic tests supports only that the code can distinguish known artificial generative assumptions without automatic spurious M2 improvement under a simple null. It does **not** demonstrate genuine biological hysteresis, frog memory, philopatry, social facilitation, fitness, or real independent wetland sampling. No new source acoustic/hydrology files were acquired. For future real data: obtain approved recorder↔wetland↔logger manifest, detection validation and rights; freeze real source-specific thresholds and genuine held-out units **before** reading species response outcomes. Preserve the ability to report `NO_GAIN`, `NO_COMPARABLE_PHASE_SUPPORT`, and `NOT_IDENTIFIABLE` as substantive possible results.

Neither the 2014–24 canonical portal HTTP 403 nor the unsent CEWH inquiry is altered here.
