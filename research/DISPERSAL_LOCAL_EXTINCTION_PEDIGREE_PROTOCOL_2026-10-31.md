# Event-logged frogcs stochastic stage-space experiment: migration, extirpation and pedigree

## Position in the research programme
This is an **optional spatial/individual supplement to draft PR #146**, not a replacement for its source-verified deterministic **120-day season + 80-year annual cohort** model and model-native `OS−, OV−, SV+, OSV+` ABC. The existing stochastic `research/scripts/multigeneration_reversal.py` has a seven-stage, eight-patch ABM with individual `uid, parent, generation`, diffusion jumps, prey/predator hazards, stage change and reproduction, and a reaction-diffusion PDE with the same local hazards; its **Rates and demographic timing differ** from the 80-year stage–annual kernel. Do not claim exact interchangeability.

## Explicit task
Use the **unchanged original `abm_step`** to create a durable individual event/ancestor ledger across years. Each newborn gets immutable ID, parent ID, founder ID, natal patch, generation, year and guild. Keep deceased ancestors in the ledger rather than dropping them when they die. Record a movement from source patch to destination patch for *survivors known at the end of a time step* (not for individuals who emigrated and died within the same tick). Thus movement counts are a **lower bound on all attempted moves**. Keep per-guild total annual births, adult/juvenile abundance, survival/disappearance, predator-caused deaths aggregated as returned by original kernel. Never assign a specific predation cause to a dead UID, because the unchanged original `abm_step` does not expose it.

Define **local extinction** as transition occupied → no living individual of that guild in a patch between consecutive annual census boundaries, and **recolonization** as absent → occupied. These are **annual census transitions**, not proof of successful reproduction or stable establishment; the model has periodic boundaries and no external immigration. Record incoming observed survivor movements for the same calendar year to classify mobility-consistent recolonization, not a fitted arrival-rate estimate.

True **parent-offspring traceability**: every live or dead child in the registry must reference its own parent's immutable UID and have generation exactly parent.generation+1, even after the parent's disappearance. Founder IDs and origin-patch ancestry allow multi-generation and cross-patch lineage turnover and reach. This is a *single sampled parent's identity*, NOT a genetically resolved maternal+paternal pedigree or an inference from real acoustic observations.

### Contrasts
Prespecified synthetic 20-year pilot on original uneven eight-patch vegetation mosaic with four matched random seeds (101–104), `mobility∈{off,original}` × frog adult→emerging dragonfly reversed predation `reverse∈{off,on}`. All other seven-stage trophic hazard, birth, maturation, density and environment formulas are unchanged. Run original stochastic ABM and original PDE as comparison on the same treatments, but **PDE does not yield parentage nor true finite-N extinctions**. The stochastic paths pair seed labels but not event-by-event random numbers under divergent mobility/reversal, so contrast intervals are **simulation variability**, not field uncertainty.

Keep annual and patch-level occupancy/transition histories, all ancestor rows (including extinct/died), movement events and aggregated cause-specific predation deaths. Report for each replicate, taxon and treatment:
- year-20 occupancy, cumulative local extinction events, annual-census recolonizations, observed survivor movement counts, and numbers of donor-founded lineages spanning >1 patch;
- fraction of living descendants currently in a patch other than founder origin; max generation and count of generation≥2 (grandchildren or later);
- frog adult and dragonfly abundance on years 1,2,5,10,20 and predator-edge reversal contrasts; illustrate which effects persist through generations.

**Scientific decision:** Does dispersal permit rescue and recolonization after stochastic loss, and does the frog→emerging-dragonfly reversal alter the persistence of predator occupancy under this *synthetic* landscape? Does a lineage's historical natal patch continue to predict where its descendants appear? This is a **testable model output**, not a field-identified spatial frogcs mechanism. Do **not** claim this spatial model explains NAAMP historical site returns or 4 macro signs until an independent data contract and model-native 2×2×2 POM bridge are validated.

### Must-pass tests
1. With same seed, `tracked_abm` must reproduce the original `simulate_abm` **exactly** for every stage count and predator death ledger; recording cannot consume extra random numbers or change hazards.
2. Every birth UID has a known parent with same guild, correct generation and founder chain (parents remain after death); registry unique and tracks all original birth assignments.
3. Population count identity for each tick: `N_{after}=N_{before}+births-deaths`; all recorded surviving moves are adjacent periodic-ring moves; movement disabled gives exactly zero movement.
4. Local extinction/recolonization definitions tested on contrived patch occupancy sequences, including empty→occupied; no phantom colonization on first census.
5. Reproducibility with fixed seed; fail closed on missing sources, invalid diffusion time-step, excessive population or impossible genealogy.
6. Preserve original ABM/PDE tests; no modifications to frozen original season kernels, `main`, PR #144, #145 or #146. Separate stacked Draft PR.

All priors are arbitrary 2026 synthetic rates; the 20-year pilot is not empirical evidence for rates or predator extirpation. Parent/offspring records are simulated, not observed family relationships.