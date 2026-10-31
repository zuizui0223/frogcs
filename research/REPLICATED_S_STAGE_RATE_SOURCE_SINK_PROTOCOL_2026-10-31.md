# S dispersal-stage × rate × trophic-context replication with a complete source–sink identity

## Question and status (2026-10-31)

The successful frogcs seven-stage ABM's **four random seeds** found that salamander-only adult dispersal at diffusion .22 had **more observed survivor movements and more annual recolonizations, yet fewer occupied patches at year 20** than larva-only dispersal at the identical per-capita diffusion .22 (mean year-20 occupied patches **0.25 versus 2.25** with the frog-adult→emerging-dragonfly predation reversal OFF; adult-minus-larva −2.0, negative in 4/4 seeded comparisons). The reverse-predation ON arm changed that direction to +1.0 (positive in 3/4). [Original 32 fully traced 20y runs #41188431040](https://github.com/zuizui0223/frogcs/actions/runs/41188431040); [source-checked 4-seed comparisons #41188575192](https://github.com/zuizui0223/frogcs/actions/runs/41188575192).

**Interpretation must distinguish** (a) stochastic small-n noise; (b) increased gross turnover/redistribution; (c) true net demographic loss. Movement frequency and occupancy do not by themselves identify predation as the cause of an individual's disappearance. It is invalid to claim high-rate adult emigration caused the decline without a patch/guild birth–death–net-migration accounting that closes.

## Precommitted supplementary experiment, not main acoustic POM

Reuse original four seed labels **101–104** from the successful source, adding **exactly eight new independently labeled seeds 105–112** (outcome-blind, not selected based on simulations). Four complete movement treatments `S_larva_005`, `S_adult_005`, `S_larva_022`, `S_adult_022`; frog-adult→emerging-D predation reversal OFF/ON. Run **8 new seeds ×4 treatments×2 predator conditions =64 new genuine stochastic 20-year ABM trajectories**, plus the original 32 = **96 source trajectories /12 seed labels per treatment×predator context**. Original eight-patch periodic vegetation mosaic and seven-stage stochastic `multigeneration_reversal.abm_step` remain exactly unchanged. All other guilds' dispersal rates are set zero. PDE remains secondary density comparison already run; do not mistake density extinction for finite stochastic loss.

**Specific falsifiable prediction**: at per-capita diffusion .22, reversal OFF, S-adult-only should exhibit a lower *end-year occupancy* and greater *patch turnover* than S-larva-only, but its higher number of recolonization events need not yield more persistent births. Under reversal ON, the sign may change. This prediction was chosen after inspecting four-seed results, so **the new eight seed trajectories are a simulation replication conditional on the same specified model**, not an independent ecological/field study.

## Exact annual source–sink bookkeeping

Use the source ABM's immutable registry for every living/deceased simulated uid and the surviving movement ledger. For each guild and patch and census interval `(year-1,year]`, compute:
- `births` from **all** recorded child uids with `birth_time` in the interval, including those who die;
- `deaths` from all registered uids with `death_time` in the interval, assigned to last observed patch immediately before their death step (not exact predation-location or assigned individual death cause);
- `incoming`/`outgoing` movements of surviving uids (source and destination patch), counted once per occurrence.

Check **every single guild×patch×year** against the exact accounting identity
`N_t−N_{t−1} = births−deaths+incoming−outgoing`, including extinct patches. If the original kernel's output does not admit this identity under the specific tracer timing rules, report the residual and **do not invent a causal source/sink decomposition**. Incoming/outgoing records omit moves of individuals dying in the same tick, but since deaths are assigned to their last observed pre-tick location, the source ledger can still close at annual-census scale if there are no other hidden location changes.

For each reversal/mobility/seed/guild compute births, deaths, net survivor migration, patch loss and recolonization; across patches the net flow should be **0** on a closed ring. Report seed-level S *births and deaths*, occupancy, movements, birth–death balances and living-descendant relocation. **An extinction event at annual census is different from permanent basin-scale extinction.**

For every recolonization at census year t, preserve the source previously defined **right-censored** test: persistent in year t+1 and t+2 and local newborns during (t,t+1]. Cite the earlier event definition and never treat near-horizon missing follow-up as failure. The presence of newborns does not prove their survival to breeding age.

## Inference guardrails

1. **No field-calibrated dispersal rates, trophic rates or inheritance mechanisms**: all treatments use the unchanged original synthetic Rates() parameterization; S larval movement among wetland patches is a hypothetical effective process.
2. Within a treatment, 12 random seeds are the numerical replication units; UID records, 20 years and eight patches **are not 12×20×8 independent samples**. Identical numeric seed labels do not guarantee a pathwise coupled counterfactual when different migration stages alter RNG calls.
3. `S` total per patch includes both larval and adult stages; adult and larval stage balances can be computed, but stage transitions must be included before interpreting stage-specific birth/death.
4. The stochastic ABM remains different from PR #146's 80-year deterministic 4-sign ABC model. Do **not** combine simulated recolonization with NAAMP historical chorus-return coefficient +0.151 as if they shared a likelihood or a measured acoustic observation model.
5. Preserve original run receipts, source hashes and original+new seed derivation; any outcome contradicting the four-seed pattern should be retained and reported. A signed seed difference needs an exact pairing declaration, and small-n uncertainty is reported.

## Deliverables and stop rule

One new Draft PR #147 supplement: all 64 new source runs plus complete original-source 32 runs, exact birth/death/movement conservation, full 12-seed matched stage/rate/reversal summary with seed-level paired differences and descriptive uncertainty, original-source reread and SHA256 receipts. Do not adjust biological rates to induce positive outcomes. If any exact source-ledger conservation check fails, **stop and diagnose the tracer's timing rather than declaring movement a causal mechanism**.
