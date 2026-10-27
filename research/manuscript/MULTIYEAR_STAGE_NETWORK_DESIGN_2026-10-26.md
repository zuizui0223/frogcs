# Multiyear stage-network extension: design before results

The user approved extending the existing frog-centered mechanism model with annual density feedback, reversal on/off, caudates present/absent, vegetation roles, and external immigration. This is a synthetic mechanism test, not a fit to NAAMP/INBO or a prediction of calling.

Reuse the existing seasonal hazards without changing their biological signs. Add optional nonnegative initial F/S/D cohort densities to `stage_vegetation_network.simulate`; default densities remain exactly one for present guilds. Validate cohort accounting at arbitrary density and preserve every old saved result.

Let B[g,t] be a normalized breeding-pool index, mapped one-to-one onto the aquatic input cohort in normalized units. The seasonal kernel returns completed cohort density C[g,t]. Update:

`B[g,t+1] = s[g]*B[g,t] + rho*b[g]*j[g]**(m[g]-1)*C[g,t+1-m[g]]/(1+C[g,t+1-m[g]]/K) + (1-rho)*(1-s[g])*I[g]`.

Here s is adult carryover, rho is local recruitment weight, b converts completions to normalized new breeders (bundles reproductive scaling and first-year survival), j is survival during additional maturation-delay years, m is annual delay, K is the recruitment saturation scale, and I=1 for present guilds, 0 otherwise. Immigration is an external reservoir unaffected by local predators. Density dependence is imposed at recruitment, not an empirically inferred competition mechanism. Initial B=I and the pre-observation immature queue is empty. No density floor or artificial rescue at rho=1. No carryover of unfinished aquatic cohorts; chosen main seasonal timings complete before day120.

Primary arbitrary values: s=(0.4,0.5,0), b=(4,4,4), j=(0.8,0.8,0.8), m=(2,2,1), K=1. They are NOT species estimates. The recurrence is bounded by s*B + rho*b*K + immigration, so unbounded numerical growth is impossible. At rho=0 the initial B=1 remains 1 and reversal cannot change later F through density feedback; this is a control, not a claim about dispersal in nature.

Primary grid: community FD/FSD; vegetation roles 0,1,2,4,8,15; vegetation 0/1; refuge ordering S/D; F arrival10/30/50, S0, D35; attack1.5, cue3; rho0/0.5/1; reverse false/true. 864 scenarios. All other seasonal defaults retained. Run80 seasons and report final20-season mean breeding-pool and completion densities, per-input completion fractions, variability, and endpoint changes. Pair reversal on/off within identical contexts; compare paired effects between FD and FSD and vegetation settings. A threshold0.005 in normalized density is only a descriptive near-zero category. Parameter-space counts are not ecological probabilities. Do not claim equilibrium from final-window averages.

Sensitivity on the all-role subset: cue0, altered delays (1,1,1)/(3,3,2), recruitment conversion2/8, juvenile survival0.5/1, adult carryover0, initial densities0.25/2, and horizon160. Run half-step integration for the all-role subset. Store every tested alternative, including no effect and extinction. Do not tune parameters to produce negative reversal effects or match empirical interactions.

Necessary tests: default seasonal replay unchanged; arbitrary-cohort mass balance; invalid/absent guild inputs; no immigration into absent guild; delayed pulse reaches correct year; zero-return control; no same-season F response to reversal; later F response in FD with local return; bounded/nonnegative trajectories. Explain whether a third party attenuates, amplifies or reverses the benefit only from computed matched contrasts. Keep model-internal and empirical claims separate.
