# Real NPS interspecific previous-year chorus test — primary suppression hypothesis not supported

**Data/result frozen:** 2026-10-26; source NPS GLKN 2016–2023 DOI [10.57830/2320505](https://doi.org/10.57830/2320505); 147,913 scored species×recorder observations; SHA256 `b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2`. [Prespecified exploratory model protocol](../../NPS_GREEN_FROG_WOOD_FROG_ACOUSTIC_CROSSLAG_SPEC_2026-10-26.md), [script](../../scripts/nps_stage_crosslag.py), [complete JSON](observed_results.json), [successful empirical workflow](https://github.com/zuizui0223/frogcs/actions/runs/40208016713).

**Study placement:** frogcs stage-legacy exploratory branch only; no change to the locked JAE RC6 submission. This is real **adult acoustic** evidence, not measured frog-larva or predator abundance, so it does **not** identify stage-structured predation.

## 1. Prespecified direction and actual result

The primary proposed sign was **negative**: same-station strong green frog calling in `t−1` would predict less annual strong wood frog chorus (`CI>=2`) in `t` after adjustment for strictly prior focal species calling, other-taxon acoustic prior, observation effort, `park×year`, and stable station identity.

| Previous-year acoustic exposure → current acoustic outcome | Eligible station×year | Parks / sites | Adjusted coefficient | Station-cluster CR1 normal 95% CI | In-sample partial R² of exposure |
|---|---:|---:|---:|---:|---:|
| **Green frog → wood frog (PRIMARY)** | **431** | **7 / 66** | **+0.0143** | **−0.0691 to +0.0977** | **0.000324** |
| Wood frog → green frog (reverse diagnostic) | 431 | 7 / 66 | +0.1181 | +0.0071 to +0.2291 | 0.00936 |
| Green frog → spring peeper (secondary) | 431 | 7 / 66 | +0.0065 | −0.0396 to +0.0526 | 0.000335 |
| Green frog → American toad (secondary) | 431 | 7 / 66 | +0.0714 | −0.0454 to +0.1883 | 0.00510 |
| Green frog → gray treefrog (context comparator) | 431 | 7 / 66 | +0.0054 | −0.0539 to +0.0648 | 0.000065 |
| Bullfrog → wood frog (secondary sparse) | 333 | 5 / 50 | −0.0283 | −0.1837 to +0.1272 | 0.000234 |

Estimates use a two-way `park×year + physical listening-station` fixed-effect linear probability model, with target last-calendar-year strong chorus, source effort, prior generic other-taxon history, and full source coverage guards. Reported confidence intervals are **approximate** CR1 normal intervals clustered by physical station, not randomized-treatment effects. All secondary rows were frozen before coefficients were read. The reverse coefficient is not directly comparable to the primary coefficient as a formal direction-difference test: outcome prevalences, acoustic windows and focal species differ.

## 2. Falsification and evidence interpretation

- **H1A primary suppression is NOT supported.** Point estimate is close to zero, positive rather than the proposed negative, and uncertainty includes both directions. The additional in-sample residual variation associated with previous green-frog CI2 is about **0.032%**. That is not evidence that overwintering green frog larvae suppress wood frog adult acoustic site choice.
- **Reverse is positive**, not the desired `green→wood negative / wood→green neutral` pattern. Park leave-one-out estimates for the reverse remain positive (range +0.0945 to +0.1821), but this is a post-hoc observational association, susceptible to shared site-year conditions and species timing. It is **not** evidence of reciprocal trophic roles.
- **Spring peeper is near zero**; American toad point estimate is positive but its uncertainty spans zero; the gray treefrog context comparator is near zero. This provides no rescue of a common 'long-lived larva suppresses all small spring callers' rule.
- **Bullfrog row is sparse**: only **12 / 333** rows had previous-year strong bullfrog calling, with 11 within-site exposure transitions. It is a weak negative-control/sensitivity surface, not a strong falsification of actual bullfrog predation.
- Missing `t−1` exposure/target species records were **not coded as biological zeros**; same-station year gaps were not substituted for exact `t−1`. The primary sample has 82 prior green-frog within-station strong/weak transitions and 7 parks.

## 3. Boundaries: what this test does NOT answer

No egg counts, Gosner stages, tadpole body sizes, larval overwinter survival, local pond fish/dry-down dates, same-pond site geometry or verified predation events occur in this NPS source. **The year-`t` adult wood-frog chorus cannot be interpreted as a direct result of predation on eggs produced after that chorus.** A true cohort-mediated effect requires species-specific maturation lags and independently identified offspring.

The historic NPS own-species association `+0.4642` was estimated using **ever previously strong** site history, different conditioning and target, whereas the present within-station `t−1` test includes fixed station effects and adjusts own last-year CI. These coefficients cannot be numerically contrasted as if they are the same estimand. Similarly, NAAMP's frozen RC6 +0.2969 route-scale concentration residual has **not** been recalculated or explained by this study.

A non-negative acoustic result does **not** refute the published direct tadpole→egg predation relation between *L. clamitans* and *L. sylvaticus*. It rejects only the proposed simple acoustic proxy-to-next-year adult chorus version in this NPS setting.

## 4. Carroll eight-pond G0 readiness decision

[Source verification receipt](../CARROLL_8POND_G0_SOURCE_ACCESS_RECEIPT_2026-10-26.json): official Dryad DOI [10.25338/B8G92P](https://doi.org/10.25338/B8G92P) exposes workbook metadata/version (workbook SHA256 pinned), but the [source G0 CI](https://github.com/zuizui0223/frogcs/actions/runs/40207244277) got `401 Unauthorized` through file API and `403 Forbidden` through public file_stream. **The original workbook has not been read, its life-stage coverage is not yet checked and no calibration is claimed.**

A separate [Zenodo author R-script archive](https://zenodo.org/records/7596609) lists eight `pond1…pond8` tadpole sheets and references an undefined `Adult_count` plus manually prepared `AdultRelativeFixed.xlsx` and `Adult_needstag_fixed.xlsx`. The Dryad manifest lists only `funneltrapdata.xlsx` and `README.md`. Thus an adult-to-larva reconstruction is also **not currently proven reproducible from the public manifest** even if the workbook download restriction is resolved.

## 5. Scientific decision / next gate

1. **Close H1A as unsupported in NPS**. Do not tune lag windows, species membership, calling thresholds or spatial filters to hunt a negative result.
2. Preserve independent biological H1B (measured overwintering larvae→egg/tadpole survival), H3 (observed pond dry-down reset) as **unidentified and untested**, not as disproved.
3. The next project contribution should be **same-pond paired life-stage exposure and offspring fate**, with verified hydrology and sampling effort. Until that exists, other-species acoustic histories must remain acoustic covariates, **not latent 'predator layers'.**
4. **Protect RC6 unchanged**; a future integrative article can link ecological evidence only if G0–G3 all pass independently.

**Current outcome:** a valuable negative test of a tempting proxy bridge. It prevents conflating predictive acoustic site memory with stage-structured aquatic predation.
