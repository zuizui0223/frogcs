<!-- GitHub Actions source-run 41190618714 SUCCESS; independent artifact-audit 41190816068 SUCCESS. All numbers are synthetic within-model. -->

# PR #146 source-derived 80y spatial-transport pilot (synthetic)

**Status: true source run complete and post-source ID, conservation, and replay gates passed. Not field-mechanism identification.**

- Source replay abs differences: F_B=0.0, F_fraction=0.0, F_B_sd=0.0.
- 2304 source cube vertices after patch means, 288 factorial 4-sign evaluations (4 parameter draw IDs), 1728 matched movement-vs-off vertex effects.
- **No PR #147 local recolonization estimate**: 80y source is continuous density with retained annual external immigration.

## Movement-associated changes in the model-native four signs

| movement   | context             |   n_cases |   gained |   lost |   any_sign_flip |
|:-----------|:--------------------|----------:|---------:|-------:|----------------:|
| both       | D_first_S_overtakes |        24 |        0 |      0 |               2 |
| both       | S_first_D_overtakes |        24 |        0 |      0 |               2 |
| both       | original            |        24 |        0 |      0 |               0 |
| carryover  | D_first_S_overtakes |        24 |        0 |      0 |               0 |
| carryover  | S_first_D_overtakes |        24 |        0 |      0 |               1 |
| carryover  | original            |        24 |        0 |      0 |               0 |
| recruits   | D_first_S_overtakes |        24 |        0 |      0 |               0 |
| recruits   | S_first_D_overtakes |        24 |        0 |      0 |               1 |
| recruits   | original            |        24 |        0 |      0 |               0 |

## Movement × ontogeny × plant-role summaries

| movement   | context             | plant          |   n_cases |   accepted_log |   accepted_raw |
|:-----------|:--------------------|:---------------|----------:|---------------:|---------------:|
| both       | D_first_S_overtakes | SF0_DF0_DS1_L0 |         8 |              4 |              4 |
| both       | D_first_S_overtakes | SF1_DF0_DS0_L1 |         8 |              0 |              0 |
| both       | D_first_S_overtakes | SF1_DF0_DS1_L0 |         8 |              2 |              2 |
| both       | S_first_D_overtakes | SF0_DF0_DS1_L0 |         8 |              4 |              4 |
| both       | S_first_D_overtakes | SF1_DF0_DS0_L1 |         8 |              0 |              0 |
| both       | S_first_D_overtakes | SF1_DF0_DS1_L0 |         8 |              4 |              2 |
| both       | original            | SF0_DF0_DS1_L0 |         8 |              0 |              0 |
| both       | original            | SF1_DF0_DS0_L1 |         8 |              2 |              4 |
| both       | original            | SF1_DF0_DS1_L0 |         8 |              0 |              0 |
| carryover  | D_first_S_overtakes | SF0_DF0_DS1_L0 |         8 |              4 |              4 |
| carryover  | D_first_S_overtakes | SF1_DF0_DS0_L1 |         8 |              0 |              0 |
| carryover  | D_first_S_overtakes | SF1_DF0_DS1_L0 |         8 |              2 |              2 |
| carryover  | S_first_D_overtakes | SF0_DF0_DS1_L0 |         8 |              4 |              4 |
| carryover  | S_first_D_overtakes | SF1_DF0_DS0_L1 |         8 |              0 |              0 |
| carryover  | S_first_D_overtakes | SF1_DF0_DS1_L0 |         8 |              4 |              2 |
| carryover  | original            | SF0_DF0_DS1_L0 |         8 |              0 |              0 |
| carryover  | original            | SF1_DF0_DS0_L1 |         8 |              2 |              4 |
| carryover  | original            | SF1_DF0_DS1_L0 |         8 |              0 |              0 |
| off        | D_first_S_overtakes | SF0_DF0_DS1_L0 |         8 |              4 |              4 |
| off        | D_first_S_overtakes | SF1_DF0_DS0_L1 |         8 |              0 |              0 |
| off        | D_first_S_overtakes | SF1_DF0_DS1_L0 |         8 |              2 |              2 |
| off        | S_first_D_overtakes | SF0_DF0_DS1_L0 |         8 |              4 |              4 |
| off        | S_first_D_overtakes | SF1_DF0_DS0_L1 |         8 |              0 |              0 |
| off        | S_first_D_overtakes | SF1_DF0_DS1_L0 |         8 |              4 |              2 |
| off        | original            | SF0_DF0_DS1_L0 |         8 |              0 |              0 |
| off        | original            | SF1_DF0_DS0_L1 |         8 |              2 |              4 |
| off        | original            | SF1_DF0_DS1_L0 |         8 |              0 |              0 |
| recruits   | D_first_S_overtakes | SF0_DF0_DS1_L0 |         8 |              4 |              4 |
| recruits   | D_first_S_overtakes | SF1_DF0_DS0_L1 |         8 |              0 |              0 |
| recruits   | D_first_S_overtakes | SF1_DF0_DS1_L0 |         8 |              2 |              2 |
| recruits   | S_first_D_overtakes | SF0_DF0_DS1_L0 |         8 |              4 |              4 |
| recruits   | S_first_D_overtakes | SF1_DF0_DS0_L1 |         8 |              0 |              0 |
| recruits   | S_first_D_overtakes | SF1_DF0_DS1_L0 |         8 |              4 |              2 |
| recruits   | original            | SF0_DF0_DS1_L0 |         8 |              0 |              0 |
| recruits   | original            | SF1_DF0_DS0_L1 |         8 |              2 |              4 |
| recruits   | original            | SF1_DF0_DS1_L0 |         8 |              0 |              0 |

## Mean F_B and spatial concentration (do NOT call patch occupancy)

| movement   | context             | plant          |   n_vertices |   mean_F_B |   mean_effective_patches |   mean_F_patch_cv |
|:-----------|:--------------------|:---------------|-------------:|-----------:|-------------------------:|------------------:|
| both       | D_first_S_overtakes | SF0_DF0_DS1_L0 |           64 |    0.40269 |                  7.99866 |           0.01028 |
| both       | D_first_S_overtakes | SF1_DF0_DS0_L1 |           64 |    0.48023 |                  7.96630 |           0.05140 |
| both       | D_first_S_overtakes | SF1_DF0_DS1_L0 |           64 |    0.44113 |                  7.99896 |           0.00953 |
| both       | S_first_D_overtakes | SF0_DF0_DS1_L0 |           64 |    0.44758 |                  7.99975 |           0.00460 |
| both       | S_first_D_overtakes | SF1_DF0_DS0_L1 |           64 |    0.50993 |                  7.98376 |           0.03946 |
| both       | S_first_D_overtakes | SF1_DF0_DS1_L0 |           64 |    0.49175 |                  7.99835 |           0.01295 |
| both       | original            | SF0_DF0_DS1_L0 |           64 |    0.98765 |                  7.99843 |           0.01032 |
| both       | original            | SF1_DF0_DS0_L1 |           64 |    1.10949 |                  7.98283 |           0.03007 |
| both       | original            | SF1_DF0_DS1_L0 |           64 |    1.06588 |                  7.99969 |           0.00512 |
| carryover  | D_first_S_overtakes | SF0_DF0_DS1_L0 |           64 |    0.40286 |                  7.99502 |           0.01953 |
| carryover  | D_first_S_overtakes | SF1_DF0_DS0_L1 |           64 |    0.48059 |                  7.90756 |           0.08583 |
| carryover  | D_first_S_overtakes | SF1_DF0_DS1_L0 |           64 |    0.44129 |                  7.99687 |           0.01654 |
| carryover  | S_first_D_overtakes | SF0_DF0_DS1_L0 |           64 |    0.44764 |                  7.99876 |           0.00982 |
| carryover  | S_first_D_overtakes | SF1_DF0_DS0_L1 |           64 |    0.50998 |                  7.95320 |           0.06641 |
| carryover  | S_first_D_overtakes | SF1_DF0_DS1_L0 |           64 |    0.49189 |                  7.99583 |           0.01989 |
| carryover  | original            | SF0_DF0_DS1_L0 |           64 |    0.98792 |                  7.99230 |           0.02250 |
| carryover  | original            | SF1_DF0_DS0_L1 |           64 |    1.10946 |                  7.93385 |           0.05858 |
| carryover  | original            | SF1_DF0_DS1_L0 |           64 |    1.06602 |                  7.99885 |           0.00946 |
| off        | D_first_S_overtakes | SF0_DF0_DS1_L0 |           64 |    0.40310 |                  7.98763 |           0.03068 |
| off        | D_first_S_overtakes | SF1_DF0_DS0_L1 |           64 |    0.48077 |                  7.83272 |           0.11656 |
| off        | D_first_S_overtakes | SF1_DF0_DS1_L0 |           64 |    0.44149 |                  7.99300 |           0.02449 |
| off        | S_first_D_overtakes | SF0_DF0_DS1_L0 |           64 |    0.44778 |                  7.99598 |           0.01757 |
| off        | S_first_D_overtakes | SF1_DF0_DS0_L1 |           64 |    0.50998 |                  7.91542 |           0.09012 |
| off        | S_first_D_overtakes | SF1_DF0_DS1_L0 |           64 |    0.49205 |                  7.99350 |           0.02541 |
| off        | original            | SF0_DF0_DS1_L0 |           64 |    0.98827 |                  7.97077 |           0.04272 |
| off        | original            | SF1_DF0_DS0_L1 |           64 |    1.10917 |                  7.81728 |           0.09757 |
| off        | original            | SF1_DF0_DS1_L0 |           64 |    1.06619 |                  7.99608 |           0.01586 |
| recruits   | D_first_S_overtakes | SF0_DF0_DS1_L0 |           64 |    0.40275 |                  7.99733 |           0.01452 |
| recruits   | D_first_S_overtakes | SF1_DF0_DS0_L1 |           64 |    0.48043 |                  7.94280 |           0.06683 |
| recruits   | D_first_S_overtakes | SF1_DF0_DS1_L0 |           64 |    0.44119 |                  7.99819 |           0.01270 |
| recruits   | S_first_D_overtakes | SF0_DF0_DS1_L0 |           64 |    0.44760 |                  7.99941 |           0.00710 |
| recruits   | S_first_D_overtakes | SF1_DF0_DS0_L1 |           64 |    0.50999 |                  7.97277 |           0.05130 |
| recruits   | S_first_D_overtakes | SF1_DF0_DS1_L0 |           64 |    0.49180 |                  7.99756 |           0.01566 |
| recruits   | original            | SF0_DF0_DS1_L0 |           64 |    0.98779 |                  7.99616 |           0.01593 |
| recruits   | original            | SF1_DF0_DS0_L1 |           64 |    1.10955 |                  7.96435 |           0.04267 |
| recruits   | original            | SF1_DF0_DS1_L0 |           64 |    1.06596 |                  7.99942 |           0.00691 |

The source code and four matched rate draws are predeclared. Differences are properties of a finite synthetic parameter experiment, not empirical effects or robust mechanism probabilities.

Next valid bridge: finite-N stage-demographic transitions on the original seasonal hazard and annual delay equations, with external immigration explicitly varied; do not add arbitrary density thresholds to manufacture local extinction.
