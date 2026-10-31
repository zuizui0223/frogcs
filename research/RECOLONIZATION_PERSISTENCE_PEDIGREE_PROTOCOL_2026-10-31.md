# Rescue versus transient return: post-occupancy and ancestry POM audit (2026-10-31)

## Source and purpose

PR #147 already ran 16 real seven-stage stochastic source-ABM trajectories (20y×8 ring patches×4 seeds×dispersal ON/OFF×F→D reversal ON/OFF), retaining every sampled individual's parent, founder, natal patch and all annual guild occupancy records. [Original successful source artifact #41186773263](https://github.com/zuizui0223/frogcs/actions/runs/41186773263), `frogcs-stochastic-lineage-metapop-20y-20261031`, is frozen and must be used without rerunning the original process. **The source ABM is different from the deterministic main 80-year 4-sign ABC; do not silently equate them.**

Our next ecological diagnostic must distinguish:
1. **recolonization:** (N_{guild,patch,t-1}=0,N_{guild,patch,t}>0);
2. **one-census persistence:** same guild still present at t+1, only observable if t≤19;
3. **two-census persistence:** guild present at both t+1 and t+2 (t≤18);
4. **post-return local birth:** one or more individual offspring *born in that same patch* during the year ((t,t+1]), regardless of subsequent mortality;
5. **parent originally from outside:** at least one such newborn's parent has `parent.natal_patch != child.natal_patch`. This is a **confirmed natal-origin difference**, not genotyped two-parent pedigrees and not necessarily a single immigration event occurring during that same year;
6. **operational reproductive persistence:** two-census persistence AND post-return local birth, with all observations supported. This demonstrates *births plus census persistence*, not survival of those particular offspring to breeding maturity.

Right-censor years 19/20 for two-census persistence and year20 for one-census; never classify no-future-data as failed establishment. Newborns logged by the source are **all born individuals, including those dying before year-end**; the source `n_newborn` must match the full lifetime registry `birth_time` exactly (group annual birth year = ceil(birth_time − 1e−9)). Recheck source annual F and D stage population totals against site/guild patch counts.

**Matched demographic process invariants:** no extra simulation required. For every guild × mobility × F/D reversal × seed, calculate events and denominators; report mean counts over 4 independent seeded replicates, per-event persistence and reproduction; avoid treating dozens of patches or within-seed repeated events as independent stochastic samples. The site-to-site movement recorder excludes individuals dying after moving within the same time step; `known_surviving_immigrant_arrivals` is a lower bound, not an unbiased estimate of all immigration.

### Source resolution and tests

Input from GitHub Actions artifact, not a guessed GitHub repo path: `registry_all_simulated_uids.csv.gz`, `patch_extirpation_recolonization.csv.gz`, `annual_stage_and_demographic_events.csv`, `lineage_generation_and_spatial_reach.csv`, and source `receipt.json`. Verify exactly 16 distinct arms ×21 annual censuses×3 guilds×8 patches, 20 annual population rows per arm, original required source kernel hash and existing source arm identity. Parentages and birth/patch counts must be corroborated from original full registry, including deceased parents.

**Interpretation ceiling:** the pond-stage source ABM lacks empirically calibrated natal dispersal, life-history and detection, and the 8-patch ring is synthetic with no external source. A patch occupancy persistence pattern is a model-native multiscale POM feature, not NAAMP's observed chorus route re-use or current natural vegetation colonization rates. Other main (deterministic) ecological sign targets cannot be assigned to this ABM without explicitly comparing its response factorial with the main source model.
