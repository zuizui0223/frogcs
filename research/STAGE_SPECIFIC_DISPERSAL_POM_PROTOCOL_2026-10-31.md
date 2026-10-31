# Stage-specific dispersal ablation on the original 7-stage frogcs spatial ABM

**Purpose:** The original 20-year source experiment showed that turning on all existing stage-specific mobility can restore salamander patch occupancy after annual local extinction. But the stages/guilds enabling that result were not separated. Test mechanistic *possibility* in the original model rather than treating the observed source NAAMP acoustic multi-site recurrence as a quantified consequence.

## Prespecified five mobility regimes

No original `multigeneration_reversal.abm_step` or `Rates` change. Keep the source's original per-stage diffusion tuple `(FT,FA,SL,SA,DN,DE,DA)=(.05,.50,.05,.22,.04,.02,.65)`. Run as a stage-wise ablation:
- `off`: all zero (source #41186773263, reused unchanged).
- `original`: original 7-stage diffusion vector (source #41186773263, reused unchanged).
- `adult_only`: FA, SA, DA keep source movement, all other stages zero (including D emergence).
- `aquatic_only`: FT, SL, DN keep source movement; FA, SA, DE, DA zero. **Between-patch aquatic exchange is a purely model-specific effective connectivity hypothesis, not established open-water movement between geographically separate ponds**.
- `S_only`: SL and SA keep source movement, F/D movement zero; tests whether S immigration itself is sufficient to create S patch reoccupation and reproductive persistence.

Cross each *new* mobility regime with adult F→emerging D predation reversal OFF/ON and independent seeds 101–104, 20 years, 8 synthetic periodic ring patches and `dt=.05` years. **3×2×4=24 NEW stochastic 20-year source trajectories**. No inflated new-run claim for 16 already verified original/off runs. Run original same-reaction PDE for all new mobility × reversal combinations as a mean-density companion, never use PDE to estimate finite-individual local extinction.

## Fixed outcome hierarchy

A. Count year-20 occupied patches for F/S/D, all local 1→0 census transitions, all 0→1 recolonization transitions, observed survivor movement per guild, living descendants with founder from another patch and maximum alive generation.
B. Link newborn UID to its permanent parent's natal patch **even after death**. Confirm exact newborn counts against original annual patch census. Distinguish one-census and two-census survival following recolonization, with t+1/t+2 right-censoring, and whether a local newborn occurred after return. Distinguish local births of parents whose **own natal patch differs** from the recolonized patch. These are parent-origin-reproduction indicators; none confirms survival of offspring to maturity.
C. Compare the same seed labels across mobility regimes as **paired model-parameter designs but not identical stochastic histories**, because migration changes RNG paths. Report 4-seed average and full seed-ledger, not conventional independent n=32 on repeated patches.

**Scientific ceiling:** Model is an arbitrary seven-stage stochastic ABM **different from** the 120-day + 80-year genuine main frogcs four-sign ABC. It is not calibrated to predator field density, vegetation refuge, adult acoustic detection or actual pond connectivity. `F_adult` lumps post-metamorph and reproductive frogs. The original emerging dragonfly compartment duration and extreme reversal predation may be unrealistic. No conclusion that ontogenetic movement controls real NAAMP recolonization or a true trophic mechanism should be made.

## Falsifiable stage-specific predictions

- Salamander colonizations may be possible under `S_only` independently of F/D movement; if not, community-level connectivity and predators matter even in the synthetic model.
- Adults-only may be more effective for rescue than effective aquatic-only connectivity, or the reverse. **Do not guess the winner or tune rates to observed output.**
- Local presence following a dispersal event may be transient; only annual persistence plus subsequent births is the stricter operational outcome.
- Despite strong modeled F→D reversal, dragonfly movement may create *transient* returns without rescue by year20, as prior source indicated.

Preserve original stochastic generation/prey hazard, stage transitions, parents and all source randomness. Two distinct stages of result: source-backed new 24 runs, then a five-regime aggregation with **unaltered original 16-run source artifact**; all source SHA256 and full ancestor/move tables attached to CI. No promotion into main's field-supported ABC/POM without an explicit model mapping.
