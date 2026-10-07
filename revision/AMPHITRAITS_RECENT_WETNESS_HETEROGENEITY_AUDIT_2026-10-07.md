# AmphiTraits audit of recent-wetness prediction heterogeneity — 2026-10-07

## Status

Exploratory interpretation audit performed after the DSWEmod reproductive-activity prediction result.

No hand-built life-history categories were created.

External trait source:
Gould et al. (2026), AmphiTraits, USGS data release DOI 10.5066/P135WFOE.

## Mapping rule

Only exact single-species NAAMP labels were mapped.

Legacy NAAMP `Hyla` labels were matched mechanically to the same specific epithet under current `Dryophytes`.

NAAMP complex labels were not assigned or averaged across component species.

## Trait variation among 44 exact single-species taxa

- BreedingSystem: Aquatic = 44 / 44.
- BreedingHydrotherm: Flexible = 44 / 44.
- BreedingHydroperiod:
  - Flexible = 38
  - Permanent = 6.

The six Permanent taxa are:
- Lithobates catesbeianus
- Lithobates clamitans
- Lithobates grylio
- Lithobates palustris
- Lithobates septentrionalis
- Lithobates virgatipes

## Relation to recent-3-month held-out gain

Across all 44 exact taxa:
- Permanent n=6: mean recent gain = -0.00154; median = -0.00053.
- Flexible n=38: mean recent gain = +0.00561; median = 0.

However many taxa have zero gain because prediction fits failed the pre-specified estimability gate.

Restricting to exact taxa estimable in both route folds:
- Permanent n=3: mean = -0.000965; median = -0.001062.
- Flexible n=20: mean = +0.003025; median = -0.000949.
- Flexible signs: 9 positive, 11 negative.

## Conclusion

The predefined AmphiTraits breeding traits do not provide a convincing explanation for the heterogeneous recent-wetness predictive gain in this NAAMP subset.

Reasons:
1. BreedingSystem and BreedingHydrotherm have no variation.
2. BreedingHydroperiod is highly imbalanced.
3. Only three Permanent taxa are estimable in both route folds.
4. Even among Flexible taxa, recent-wetness gain is heterogeneous and the median is slightly negative.

Therefore do not promote a temporary-water/flexible-breeder trait explanation from these data.

No hand classification or alternate trait grouping should be introduced after this readback.
