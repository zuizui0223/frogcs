# NAAMP：よく鳴き声が記録される地点の特徴

2026-10-26。既存データによる探索的相関。予測改善を評価する解析とは別の問い。

対象は2001–2015年、6回以上・3年以上調査された4,248音響地点、432ルート成分。強い鳴き声が記録された訪問割合と、強い鳴き声を記録した年の割合を応答とする。元データ74,317行からtimeout=0の73,211訪問を使用し、7,609地点を集計した。主対象の特徴量結合欠測は0地点。強い鳴き声は、その訪問で報告されたカエル類の最大CallingIndex≥2。種別の集中係数ではなく、少なくとも1種が強く鳴いた地点利用の指標である。

## 主な結果

- トンボ類の平均適合度と強い鳴き声の訪問割合は全域で弱い負の相関。両背景で同方向だが、ルート内では弱まる。広域の配置パターンであり、同じ池でのヤゴ回避とはまだ言えない。
- 池で繁殖する有尾類の潜在種数はtarget-group背景で正の全域相関を示す一方、uniform背景ではほぼ0。頑健な群共通性としては扱わない。
- 冠水植生・開水面との相関は小さい。どちらも高利用・低利用群の中央値・四分位点は0であり、粗い被覆指標で現地の隠れ場や羽化基質を評価し尽くしたとは解釈しない。
- 高利用（強い鳴き声割合≥75%）1,249地点、低利用（≤25%）669地点、中間2,330地点。高騒音フラグの訪問割合の中央値は高利用0.067、低利用0.143。元のMassNoiseIndex≥2（有効時）、または二値Noiseから構成した指標であり音量の実測平均ではない。音響検出と環境の双方が関わりうるため、池の選好そのものとはしない。

## 全指標の結果

各値は相関［ルート単位の1,000回bootstrapによる95%区間］。ルート内は全標本の順位からルート平均順位を差し引いた残差間の相関。両者は異なる空間スケールの記述である。

### 強い鳴き声の訪問割合

| 指標 | 全域 | ルート内 |
|---|---:|---:|
| Mean suitability: Anura (target-group) | -0.082 [-0.146, -0.021] | +0.002 [-0.042, +0.046] |
| Mean suitability: Anura (uniform) | -0.093 [-0.154, -0.032] | -0.013 [-0.051, +0.027] |
| Mean suitability: Caudata (target-group) | +0.029 [-0.036, +0.095] | +0.004 [-0.045, +0.055] |
| Mean suitability: Caudata (uniform) | -0.067 [-0.131, -0.001] | +0.016 [-0.031, +0.061] |
| Mean suitability: Odonata (target-group) | -0.086 [-0.149, -0.018] | -0.019 [-0.059, +0.022] |
| Mean suitability: Odonata (uniform) | -0.095 [-0.154, -0.035] | -0.027 [-0.061, +0.007] |
| Mean suitability: Pond Caudata (target-group) | +0.108 [+0.046, +0.177] | +0.019 [-0.021, +0.057] |
| Mean suitability: Pond Caudata (uniform) | -0.008 [-0.075, +0.059] | +0.021 [-0.026, +0.065] |
| Potential richness: Anura (target-group) | -0.022 [-0.090, +0.037] | -0.016 [-0.059, +0.024] |
| Potential richness: Anura (uniform) | -0.011 [-0.070, +0.050] | +0.008 [-0.036, +0.051] |
| Potential richness: Caudata (target-group) | -0.013 [-0.081, +0.055] | -0.016 [-0.054, +0.019] |
| Potential richness: Caudata (uniform) | -0.086 [-0.149, -0.020] | +0.012 [-0.026, +0.053] |
| Potential richness: Odonata (target-group) | -0.038 [-0.102, +0.021] | -0.043 [-0.087, -0.002] |
| Potential richness: Odonata (uniform) | -0.008 [-0.070, +0.051] | -0.020 [-0.052, +0.013] |
| Potential richness: Pond Caudata (target-group) | +0.151 [+0.088, +0.209] | -0.000 [-0.036, +0.038] |
| Potential richness: Pond Caudata (uniform) | -0.015 [-0.082, +0.055] | +0.016 [-0.023, +0.056] |
| Flooded vegetation cover | +0.012 [-0.020, +0.044] | +0.011 [-0.023, +0.044] |
| Open-water cover | +0.008 [-0.039, +0.053] | -0.003 [-0.040, +0.032] |

### 強い鳴き声を記録した年の割合

| 指標 | 全域 | ルート内 |
|---|---:|---:|
| Mean suitability: Anura (target-group) | -0.080 [-0.138, -0.021] | -0.007 [-0.043, +0.028] |
| Mean suitability: Anura (uniform) | -0.087 [-0.143, -0.030] | -0.007 [-0.046, +0.025] |
| Mean suitability: Caudata (target-group) | +0.006 [-0.059, +0.067] | -0.003 [-0.047, +0.042] |
| Mean suitability: Caudata (uniform) | -0.060 [-0.128, +0.005] | +0.012 [-0.027, +0.051] |
| Mean suitability: Odonata (target-group) | -0.054 [-0.114, +0.006] | -0.014 [-0.051, +0.021] |
| Mean suitability: Odonata (uniform) | -0.082 [-0.141, -0.028] | -0.017 [-0.052, +0.016] |
| Mean suitability: Pond Caudata (target-group) | +0.081 [+0.016, +0.142] | +0.006 [-0.028, +0.040] |
| Mean suitability: Pond Caudata (uniform) | -0.015 [-0.083, +0.050] | +0.016 [-0.024, +0.055] |
| Potential richness: Anura (target-group) | -0.040 [-0.104, +0.018] | -0.009 [-0.052, +0.034] |
| Potential richness: Anura (uniform) | -0.013 [-0.068, +0.046] | +0.011 [-0.028, +0.046] |
| Potential richness: Caudata (target-group) | -0.055 [-0.116, +0.007] | -0.006 [-0.037, +0.023] |
| Potential richness: Caudata (uniform) | -0.111 [-0.170, -0.051] | +0.010 [-0.027, +0.049] |
| Potential richness: Odonata (target-group) | +0.005 [-0.058, +0.066] | -0.041 [-0.086, +0.000] |
| Potential richness: Odonata (uniform) | -0.021 [-0.078, +0.036] | -0.008 [-0.043, +0.026] |
| Potential richness: Pond Caudata (target-group) | +0.109 [+0.047, +0.168] | -0.001 [-0.032, +0.030] |
| Potential richness: Pond Caudata (uniform) | -0.050 [-0.110, +0.010] | +0.013 [-0.022, +0.046] |
| Flooded vegetation cover | +0.040 [-0.002, +0.078] | +0.020 [-0.014, +0.056] |
| Open-water cover | +0.011 [-0.036, +0.052] | +0.011 [-0.024, +0.040] |

## 感度と解釈

訪問・年数条件を変えた対象、年均等重み、日均等重み、3季節均等重み、弱い鳴き声を含めた応答を保存した。トンボ類uniform適合度の全域相関は、これらで−0.077～−0.136。これは同じ資料内の頑健性であり独立した反復実証ではない。

10地点が複数のルート名に属するため、同じ物理地点を共有するルートを一つの成分にまとめて再標本化した。同地点・日・季節の重複位置にある848行は誤記と決めつけず主解析に残し、日均等感度を別に評価した。

潜在種数は相互作用関連28種のSDMに基づく10%訓練出現脱落閾値での集計であり、地域全種の多様性や実現群集ではない。適合度は種ごとのpercentileを群平均した指標。区間はSDM推定の不確実性を伝播しておらず、多重比較調整をしていない。種別の全結果も探索表として保存し、上位の相関だけから種を選定しない。

## 再現と出典

```powershell
python research/scripts/naamp_site_use_associations.py --out research/results/naamp_site_use_associations_20261026 --bootstraps 1000
python -m unittest discover -s research/scripts -p test_naamp_site_use_associations.py
python research/scripts/report_naamp_site_use.py
```

入力音響表：`research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz`。
SHA256: `74d28435ce6e1a842e003eaa6754c6db373e026728cfbf457784814c47cd997c`。
特徴量：`research/results/interaction_species_sdm_20261026/`の環境表、種別適合度、SSDM群別潜在種数。
機械可読の全結果・感度・対象地点・ルート対応：`research/results/naamp_site_use_associations_20261026/`。
