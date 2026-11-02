# ②×③×④ as ONE main-kernel mechanism-to-persistence inference (2026-11-01)

**Status: research Draft PR #160. Main and all prior positive findings unchanged.**

## One ecological question

Which food-web structures generate the four macro directions under vegetation and ontogenetic timing, and what do these exact same structures and rates imply for long-run F persistence and return when movement and population scale vary?

**One common unit:** source prior draw ID = original main canonical mechanism M (one of 3,600) + developmental context T (one of 3) + biological parameter vector θ (attack, rho, conversion, vegetation strength, refuge order, size gate). Keep this ID for ②, ③ and ④.

### ② Accept same M,T,θ at 80 years

- Reuse the exact originally seeded 20,000 joint prior IDs from PR #160; do not pre-filter to 20 main finalists.
- Unmodified original main deterministic 120-day season and lagged annual demographic kernel; 80 years, last 20-year mean, half-day integration.
- Four primary signs: OS negative, OV negative, SV positive, OSV positive on the eight V/S/D corners of log(F_B). Raw response and survival floor diagnostics are secondary.
- Predictive finite-N outcomes are NEVER used as acceptance or priors.
- Outcome: full structural axis/combination model-native conditional acceptance and accepted-draw share, with original prior mass retained.

### ③ Same θ crossed with all three stages and vegetation toggles

- Preselect 96 of those accepted 80-year draws by one frozen random seed, 32 per stage context with sample weights to restore true accepted context proportions. No finite outcomes inspected.
- For every exact same model and rate vector, run all three contexts, and ON/OFF of cover_SF or cover_DS separately. 96 × 3 × 2 × 2 = 1,152 true 80-year simulations (8 vertices each).
- The target is not a separate model-selection exercise: output each matched ON-minus-OFF change of mean log(F_B), the four signed contrasts, and four-sign compatibility. Test changes of these differences across stage contexts for the **same source draw**.
- Recheck the original, unmodified model/context against the exact source draw with error no larger than 1e−8.
- When the relevant predator edge is structurally absent the refuge control is inert; retain zero effect and record it as structural inactivity.

### ④ Same accepted θ → finite population consequence

- Use the actual original MAIN stage_vegetation_network seasonal hazards and final_network_summary delayed annual expected recruitment, never substitute the differently extended PR #149/158 seasonal kernel.
- Integer stochastic extension: original cohort densities represented by q=3 or 12 individuals per unit, binomial seasonal completion and adult carryover, Poisson local recruitment and original external immigration, conservative 8-patch annual ring movement of 15% of carryover and local recruits.
- Eight ring patches correspond to the eight V/S/D factorial corners, in a predetermined lexical order, not real wetlands.
- Each of the exact same 96 accepted M,T,θ: 2 q × S→F predation edge ON/OFF × movement ON/OFF × 2 prespecified independent process seeds = 16 counterfactual arms, each 80 years, totaling 1,536 arms (12,288 synthetic patch trajectories).
- Record F occupied patches at year 80, mean occupied years 61–80, local extinction, zero-to-positive return and movement-assisted return indicator. Do not conflate an arrival accompanying return with a uniquely movement-caused return. The original external source stays ON.
- Numerically verify unchanged main deterministic source expectation, integer conservation and exact 16-arm pairing per draw.

### One joined analysis table

The final mechanism-to-dynamics table has **one row per original selected source ID × q** and includes:
1. original mechanism axes and biological rate θ (②)
2. matched stage-dependent plant protection effects at its own stage (③)
3. within-draw movement effect with and without S→F predation, and the difference between those effects (④)

Disaggregate by stage, vegetation and trophic edge. Use accepted-context weights when averaging; bootstrap only source draws, not stochastic arms as independent ponds. Save CSV tables, the prior/seed/algorithm contract and genuine Actions receipts.

## Verification pipeline

1. True source replay / factorial and movement-conservation tests.
2. Eight deterministic 80-year full-prior shards.
3. One source-ID validation and prospective selection of 96 cases.
4. Parallel paired 80y vegetation×stage counterfactuals and four finite-N shards.
5. Final exact source-ID join with a manifest and interval tables.

Workflows and executable scripts are on PR #160. A completed final Actions job is required before reporting any new 80-year acceptance or post-predictive numerical findings.

## Crucial inference limits

This is a model-native categorical ABC/rejection POM under artificial rate priors, **not a calibrated ecological posterior inferred from real predation**. The original signs derive from macro adult-call/suitability patterns but the simulated endpoint is aquatic F_B; the stage-to-chorus observation process is not fitted. In PR #158 a six-vector observed-site comparison did not identify a single predation cause, and stochastic signs occurred even when all predation was absent.

The scientific claim is conditional: an interaction structure can be compatible with those directions and imply particular long-run model consequences under explicitly stated rate, movement and finite-N assumptions. It is not a forecast for actual wetlands or proof of a trophic mechanism in the field.
