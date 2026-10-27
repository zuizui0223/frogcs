# Three-guild stage and vegetation scenario model: design before execution

User-directed extension, 2026-10-26. Empirical snapshot remains `65e5a6f`.
Purpose: improve the one-season `three_guild_delay_toy.py` so all three cohorts can be constrained,
and separate vegetation functions. Do not fit coefficients to the observed calling correlations.

## State and assumptions

Normalized F larva/postmetamorph, S larva/postmetamorph, D nymph/emerging/adult cohorts.
One cohort per group, no reproduction, immigration or repeated annual map. Track deaths by cause.
Size increases with age independently of food; this is a deliberate simplification, not an energy budget.
F, S and D aquatic durations are 45, 70 and 60 model days; D emergence lasts 5 days.
F arrives at day 10/30/50, S at 0/20, D at 10/35. These are arbitrary scenarios, not calibrated phenology.

Directed pathways: S larva -> F larva; D nymph -> F larva; D nymph -> S larva;
S larva -> D nymph (optional size-gated hypothetical reciprocal edge);
F postmetamorph -> emerging D (optional stage-reversal edge).
D suppresses S foraging through an explicit risk term. Published caged-risk experiments support a
possible cue pathway, not the sign of the total free-predator effect. The modeled multi-edge community
combines mechanisms documented in different taxa/regions and additional assumptions, not one verified food web.

Four independent vegetation switches: F refuge, D aquatic encounter support, S refuge from D,
D emergence support. Refuge against D vs S has three orderings (stronger for S, equal, stronger for D).
Emergence support reduces a separate transition-failure hazard; stems also increase F access to emerging D
when reversal is enabled. Both are explicit alternative effects, not measured EarthEnv functions.
Vegetation index 0/1 is synthetic structure, not the observed rank-standardized 3-km land-cover covariate.

## Fixed comparisons

Full factorial: 16 role combinations x 3 refuge orderings x 3 F arrivals x 2 S arrivals x 2 D arrivals
x 2 attack multipliers (0.5/1.5) x 2 cue strengths (0/3) x 2 vegetation levels x 4 communities (F, FS, FD, FSD).
18,432 trajectories at water duration 120 days. This grid is fixed before observing outputs.
Paired removals on identical settings give the D effect with and without S; their difference describes
non-additivity. Compare these quantities between V=0 and V=1. They are survival contrasts, not regression
coefficients for calling. Also repeat the entire grid with the reverse edge removed and reciprocal S->D
edge removed (one at a time). Half-step rerun of the full grid tests numerical stability. A drying sensitivity
uses the full-grid input with water=60. Retain all scenarios, including zero and contrary results.

No expected sign is a pass condition. Tests: closed cohort accounting; no negative states; predator removal;
stage gating; edge-specific ablation; no structural effect when all roles are off; no effect of emergence-only
support on earlier same-season F completion; non-overlap; step-size convergence; finite valid inputs.
Results describe one-season completion, not coexistence, natural reversal frequency or calling behavior.

Scientific review clarification: S refuge affects D->S mortality, not cue perception or activity recovery.
The model permits only suppressive S-D pathways, so departures from the independent-hazard null are
structurally antagonistic. This model does not reconstruct the negative empirical O*S calling coefficient.

Implementation audit amendment before final inference: raw survival difference-of-differences is not
a sufficient interaction diagnostic because independent mortality hazards combine multiplicatively.
Retain that raw contrast for transparency, but use log(FSD)+log(F)-log(FS)-log(FD) for the independent-hazard
null. Add a complete-grid ablation with S-D consumptive edges and D risk suppression removed; this log
contrast must be zero. This amendment corrects the comparison scale and is not selected for a desired sign.

## Deliverables

New model + tests + all-scenario tables + numerical/audit JSON + scientific figure + integrated discussion.
Old empirical and synthetic files remain untouched. Use the original snapshot verifier to check preservation.
