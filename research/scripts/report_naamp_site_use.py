"""Render all preselected site-use associations from saved estimates."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'research/results/naamp_site_use_associations_20261026'


def label(feature):
    if feature == 'flooded': return 'Flooded vegetation cover'
    if feature == 'water': return 'Open-water cover'
    return (feature.replace('mean_suitability_', 'Mean suitability: ')
            .replace('richness_', 'Potential richness: ')
            .replace('pond_breeding_Caudata', 'Pond Caudata')
            .replace('_target_group', ' (target-group)')
            .replace('_uniform', ' (uniform)'))


def main():
    data = pd.read_csv(DATA / 'primary_correlations.csv')
    meta = json.loads((DATA / 'observed_results.json').read_text())
    assert len(data) == 72 and data.feature.nunique() == 18
    assert data[['correlation', 'low', 'high']].notna().all().all()
    features = data.feature.drop_duplicates().tolist()
    fig, axes = plt.subplots(1, 2, figsize=(13, 9), sharey=True)
    for ax, outcome, title in zip(axes, ['strong_rate', 'strong_year_fraction'],
                                  ['Strong-call fraction of visits', 'Fraction of years with strong calls']):
        for scale, color, marker, offset, name in [
            ('whole_sample_spearman', '#2166ac', 'o', -.12, 'Whole sample'),
            ('within_route_ranks', '#b35806', 's', .12, 'Within route')]:
            subset = data[(data.outcome == outcome) & (data.scale == scale)].set_index('feature').loc[features]
            y = [i + offset for i in range(len(features))]
            ax.hlines(y, subset.low, subset.high, color=color, lw=1.4)
            ax.scatter(subset.correlation, y, c=color, marker=marker, s=25, label=name, zorder=3)
        ax.axvline(0, color='#777777', lw=.8)
        ax.set_xlim(-.24, .24)
        ax.set_title(title, fontsize=12)
        ax.set_xlabel('Rank association (95% route-bootstrap interval)')
        ax.grid(axis='x', alpha=.18)
        ax.spines[['top', 'right']].set_visible(False)
    axes[0].set_yticks(range(len(features)), [label(x) for x in features], fontsize=10)
    axes[0].invert_yaxis()
    axes[1].legend(loc='lower right', frameon=False)
    fig.suptitle('NAAMP calling-site characteristics | 2001–2015', x=.38, fontsize=16)
    fig.text(.38, .94, f"{meta['primary_complete_sites']:,} sites; {meta['primary_routes']} route components; ≥6 visits over ≥3 years", fontsize=11)
    fig.text(.02, .015, 'Exploratory associations; all 18 selected features shown. 1,000 route bootstrap draws; no multiplicity adjustment.\n'
             'Intervals condition on fitted SDMs. Acoustic sites are not delineated ponds; suitability is not occupancy probability.', fontsize=10)
    fig.subplots_adjust(left=.38, right=.98, top=.89, bottom=.12, wspace=.12)
    fig.savefig(DATA / 'site_use_correlations.png', dpi=180)
    plt.close(fig)
    lines = ['# NAAMP：よく鳴き声が記録される地点の特徴', '',
             '2026-10-26。既存データによる探索的相関。予測改善を評価する解析とは別の問い。', '',
             '対象は2001–2015年、6回以上・3年以上調査された4,248音響地点、432ルート成分。'
             '強い鳴き声が記録された訪問割合と、強い鳴き声を記録した年の割合を応答とする。'
             '元データ74,317行からtimeout=0の73,211訪問を使用し、7,609地点を集計した。主対象の特徴量結合欠測は0地点。'
             '強い鳴き声は、その訪問で報告されたカエル類の最大CallingIndex≥2。種別の集中係数ではなく、少なくとも1種が強く鳴いた地点利用の指標である。', '',
             '## 主な結果', '',
             '- トンボ類の平均適合度と強い鳴き声の訪問割合は全域で弱い負の相関。両背景で同方向だが、ルート内では弱まる。広域の配置パターンであり、同じ池でのヤゴ回避とはまだ言えない。',
             '- 池で繁殖する有尾類の潜在種数はtarget-group背景で正の全域相関を示す一方、uniform背景ではほぼ0。頑健な群共通性としては扱わない。',
             '- 冠水植生・開水面との相関は小さい。どちらも高利用・低利用群の中央値・四分位点は0であり、粗い被覆指標で現地の隠れ場や羽化基質を評価し尽くしたとは解釈しない。',
             '- 高利用（強い鳴き声割合≥75%）1,249地点、低利用（≤25%）669地点、中間2,330地点。高騒音フラグの訪問割合の中央値は高利用0.067、低利用0.143。元のMassNoiseIndex≥2（有効時）、または二値Noiseから構成した指標であり音量の実測平均ではない。音響検出と環境の双方が関わりうるため、池の選好そのものとはしない。', '',
             '## 全指標の結果', '',
             '各値は相関［ルート単位の1,000回bootstrapによる95%区間］。ルート内は全標本の順位からルート平均順位を差し引いた残差間の相関。両者は異なる空間スケールの記述である。', '']
    for outcome, title in [('strong_rate', '強い鳴き声の訪問割合'), ('strong_year_fraction', '強い鳴き声を記録した年の割合')]:
        lines += ['### ' + title, '', '| 指標 | 全域 | ルート内 |', '|---|---:|---:|']
        for feature in features:
            rows = data[(data.feature == feature) & (data.outcome == outcome)].set_index('scale')
            cells = [f"{rows.loc[s,'correlation']:+.3f} [{rows.loc[s,'low']:+.3f}, {rows.loc[s,'high']:+.3f}]" for s in ['whole_sample_spearman', 'within_route_ranks']]
            lines.append('| ' + label(feature) + ' | ' + ' | '.join(cells) + ' |')
        lines.append('')
    lines += ['## 感度と解釈', '',
              '訪問・年数条件を変えた対象、年均等重み、日均等重み、3季節均等重み、弱い鳴き声を含めた応答を保存した。'
              'トンボ類uniform適合度の全域相関は、これらで−0.077～−0.136。これは同じ資料内の頑健性であり独立した反復実証ではない。', '',
              '10地点が複数のルート名に属するため、同じ物理地点を共有するルートを一つの成分にまとめて再標本化した。'
              '同地点・日・季節の重複位置にある848行は誤記と決めつけず主解析に残し、日均等感度を別に評価した。', '',
              '潜在種数は相互作用関連28種のSDMに基づく10%訓練出現脱落閾値での集計であり、地域全種の多様性や実現群集ではない。'
              '適合度は種ごとのpercentileを群平均した指標。区間はSDM推定の不確実性を伝播しておらず、多重比較調整をしていない。'
              '種別の全結果も探索表として保存し、上位の相関だけから種を選定しない。', '',
              '## 再現と出典', '',
              '```powershell',
              'python research/scripts/naamp_site_use_associations.py --out research/results/naamp_site_use_associations_20261026 --bootstraps 1000',
              'python -m unittest discover -s research/scripts -p test_naamp_site_use_associations.py',
              'python research/scripts/report_naamp_site_use.py', '```', '',
              '入力音響表：`research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz`。',
              'SHA256: `' + meta['source_survey_sha256'] + '`。',
              '特徴量：`research/results/interaction_species_sdm_20261026/`の環境表、種別適合度、SSDM群別潜在種数。',
              '機械可読の全結果・感度・対象地点・ルート対応：`research/results/naamp_site_use_associations_20261026/`。', '']
    (ROOT / 'research/NAAMP_SITE_USE_ASSOCIATION_REPORT_2026-10-26.md').write_text('\n'.join(lines), encoding='utf-8')
    print('Saved full association report and figure; 72 estimates.')


if __name__ == '__main__':
    main()
