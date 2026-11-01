# main #1479/#1455 × vegetation role × ontogeny × genuine 80-year demography

Frozen protocol, 2026-11-01. **Model-native test; no wild trophic mechanism identified.**

## Motivating biological claim

Existing main's conditional winner #1479 (and reduced #1455) used (i) shelter of frog larvae from salamander larvae, (ii) odonate predation upon salamanders, and (iii) vegetation-dependent nonlinear odonate feeding on frog larvae. The three rank-interaction directions passed only in one of 24 common parameter blocks. The new 18,432-run PR146 contrast showed that the same plant function's effect on *four model-internal directional signs* (OS−, OV−, SV+, OSV+) flips with coupled developmental contexts. PR153–155 showed conditional effects on 80-year occupancy, but on a separate finite-N design.

**This experiment explicitly connects these two model-native consequences using the same seasonal biological source and same theta, and does not silently claim correspondence between main's old rank/hazard criterion and the newer four-sign ABC criterion.**

## Locked original source identity

- Paper starting ref: Draft PR158, itself stacked on editorial PR156, while original main, PR146 and PR153–158 remain unchanged.
- Original immutable biological module source SHA: `19d45ffb833e2970aff8d88de101736aee289d26` (PR155 ancestry), through GitHub Actions second checkout at `source/`.
- Original `stage_network_extension_20261029.simulate` (120d, dt .25), PR146 annual maturation/recruitment *means*, original PR149–155 finite-N binomial completion/survival, Poisson delayed local recruitment and conservative eight-patch ring movement. No seasonal kernel or annual recurrence edits.
- Original main `research/results/final_mechanism_20261027/catalog.csv` is checked for **all 13 model flags**, with exact expected row fingerprints for 1479/1455. Main #1479 has S→D ON; #1455 differs *only* in S→D OFF. Both have S→F, D→F, D→S ON, SF=1, litter=1, and other main features absent.
- Caveat: this is the **source-kernel representation of their features**, not a numerical replay of main's 40/80-season rank/hazard scoring. New finite-N q and annual patch dynamics are additional synthetic components.

## Primary factorial (all levels, no outcome-based selection)

- Three original biological contexts: original (D day0/S day20, D aquatic 40d); D-first-S-overtakes (D day0/S day20, S growth and D duration jointly changed); S-first-D-overtakes (S day0/D day20, growth/duration jointly changed). The latter two are *not* pure arrival-order manipulations.
- Original four unselected hypothetical 256-LHS process-rate draw IDs **0,4,8,12** with a fixed 2/3yr F maturation delay; same theta throughout every mechanism/plant/stage/q/movement comparison. Four rates are a small illustrative slice, **not** a field prior.
- Six legal vegetation roles: SF1_L1, SF1_L0, SF0_L1, SF0_L0, DS-only, SF+DS (all DF=0; litter=1 implies DF=0). Four plant pathways under other main controls are absent.
- Two main predator-edge structures: #1479 (four active paths), #1455 (S→D removed).
- Original finite-N scales q=3 and 12, **4 independent RNG seed labels 101–104**, movement OFF or both recruited/cohort carryover at .15/year, no external immigration, eight artificial ring patches.
- Three on/off matched plant-path contrasts: litter with frog shelter held ON; frog shelter with litter held ON; salamander shelter from dragonflies with frog shelter/litter OFF. Other mechanisms fixed. No retrospective best-role filtering.
- All same-source V×S×D eight vertices, synthetic vegetation mosaic **V0: 0/.4** and **V1: .6/1** across eight patches. Interpret neither as literal absence/presence of vegetation at NAAMP ponds.

## Output and falsifiable comparisons

For *each* context×theta×plant×main model×q×movement×seed, record from the **same genuine 80year finite-N biological execution**:

1. F aquatic beginning-of-season density averaged over years61–80 at all eight original factorial corners, and exact model-native OS,OV,SV,OSV contrasts, raw and log1p.
2. F year80 occupied patches (0–8), calculated for each original factorial corner and aggregated separately for low/high V, plus true original integer 0→positive local patch return and extinction event counts. External immigration OFF; returns may be due to local delayed recruitment or annual within-ring movement.
3. Matched ON−OFF plant-function effect and #1479 minus #1455 S→D edge effect on both four-sign compatibility and year80 occupancy/returns, within identical theta, stage, q, movement and RNG seed **labels**.
4. Report *every* stage and q/movement setting, including zero and reversed effects. Does the plant function's effect on **long-run occupancy/returns** also change sign across developmental contexts? This is independent of whether its effect on four-sign compatibility flips.
5. Source-audit exact 12 stage×q×2seed-shard receipts; model flag fingerprint; 4year original deterministic replay; 4 original theta IDs; all 8 corners; 4 RNG seed labels; source guild, migration and return conservation; recompute paired effects without selecting favorable arms.

Numerical inventory: 3 stages × 2 main models × 6 legal plant roles × 4 real source-rate vectors × 2 count scales × 2 movement modes × 4 seeds = **2,304 original finite-N 80year scenario-group readouts**, each with 8 V×S×D source vertices, i.e. **18,432 genuine F source vertices**, each containing 8 patches. The four seeds and four hypothetical theta vectors—not the 18,432 model cells—are the variability levels. This is a *subset of main's 3,600 mechanisms*.

## Predeclared inference boundary and decision rule

The strongest positive result of PR146 was the **4-sign compatibility reversal** for SF/litter across stage contexts. Do **not** assert that actual F year80 occupancy/returns reverse until the new source outcome paired contrast is computed and all 12 source shards independently audited. If occupancy shows no reversal, state that the four-sign ontogeny interaction **does not imply** a long-run occupancy sign switch. Model #1455 may remain equal to #1479 if the S→D interaction is inactive at the tested stage/size/rates; equal response is scientifically meaningful.

The original field data are Odonata/Caudata *suitability* and strong adult *calling*, not measured pond S/D density and F aquatic cohorts. No field-calibrated juvenile→adult acoustic observation model, measured q, density or migration. Do not report the model's accepted rates as a posterior, actual field population forecast or empirical predation evidence.

**Primary reporting order:** observed conditional macro association → main 3,600 conditional shortlist → PR146 stage×plant four-sign interaction → current same-theta true80 demographic consequences. Keep source model failure/unknowns visible.
