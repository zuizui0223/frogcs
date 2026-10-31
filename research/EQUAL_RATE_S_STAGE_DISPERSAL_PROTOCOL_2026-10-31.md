# Equal-per-capita salamander stage dispersal: disentangle stage from diffusion magnitude

The successful five-mode spatial POM found *many* S patch returns with adult-only/S-only mobility and *few* under aquatic-only movement. **That alone does not identify stage** because the original ABM assigned S larva diffusion 0.05 per model-year and S adult diffusion 0.22 (4.4× higher). This targeted pilot fixes one scalar **per-individual source diffusion coefficient** across S larva vs S adult and holds all other guild movements at zero.

Exactly four predeclared new mobility settings, each 20 years × 4 stochastic seeds (101–104) × reverse adult-F→emerging-D predation OFF/ON:
- `S_larva_005`: only SL diffusion=0.05, SA=0.
- `S_adult_005`: only SA diffusion=0.05, SL=0.
- `S_larva_022`: only SL diffusion=0.22, SA=0.
- `S_adult_022`: only SA diffusion=0.22, SL=0.

All F and D stage diffusion entries zero, all original natural mortality, maturation/size, reproductive hazard and trophic coefficients **unchanged**. Full model uses eight synthetic periodically connected patches, 7 actual stage labels, 20 years, dt=0.05; record all historical parent IDs and all original newly-born individual census records through the original tracer. This adds **32 genuine 20-year stochastic trajectories** and 8 original PDE companion density trajectories.

### Primary comparisons

For each of two reversal settings and each of the two fixed per-capita movement coefficients, compare **S adult-only − S larva-only** for annual-census patch recolonization count, year20 occupied-patch count, two-year followed occupancy + local births, and multiple-patch live founder lineages, preserving four matched seed *labels* and reporting per-seed variation, not site-independent pseudo-n. Next compare **0.22 − 0.05** within each S movement stage. The original source's all/none mobility and S-only mixed rates are additional contextual rows but **not included in the equal-rate stage contrasts**.

Annual temporary return is not establishment: right-censor t=19/20 for 2-year persistence and distinguish newborns after return from their survival to maturity. All newborns (dead or alive by year-end) require exact original UID→parent registry reconciliation. Source unchanged stochastic `abm_step` must be verified against original fixed-seed 2-year trajectory for each mobility setup (tests), with no new random draws. Synthetic rates remain uncalibrated to observed pond connectivity.

**Important caveat**: even when S larval and adult per-capita diffusion coefficients are identical, the two stages have different population sizes, time spent in stage, natural mortality and their available spatial/seasonal behavior. The *realized number of migrants need not be the same*, nor is movement of aquatic larvae between isolated ponds biologically assumed. `S_adult` is a compound stage in this simulator, not independently measured reproductive adults. This establishes a model-native contrast conditional on the original biological stage ecology, not a field causal effect, not NAAMP acoustic recolonization and not the 80-year main ABC.
