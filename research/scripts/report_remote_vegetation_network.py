"""Report the complete vegetation-association specification, without selection."""
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/results/naamp_remote_vegetation_20261026'


def main():
    d=pd.read_csv(OUT/'network_rank_coefficients.csv')
    sites=pd.read_csv(OUT/'primary_site_landscape_context.csv.gz')
    rho=spearmanr(sites.flooded_3000m_mean,sites.flooded_3000m_sd).statistic
    keys=d[['background','group','vegetation_metric']].drop_duplicates()
    labels=[('All Caudata' if x.group=='Caudata' else 'Pond Caudata')+' | '+x.background+' | '+x.vegetation_metric for x in keys.itertuples()]
    fig,axes=plt.subplots(1,3,figsize=(15,6),sharey=True)
    for ax,term,title in zip(axes,['Odonata:vegetation','Caudata:vegetation','Odonata:Caudata:vegetation'],
                            ['Odonata × vegetation','Caudata × vegetation','Odonata × Caudata × vegetation']):
        for within,color,marker,offset,label in [(False,'#2166ac','o',-.12,'Whole area'),(True,'#b35806','s',.12,'Within route')]:
            sub=d[(d.term==term)&(d.within_route==within)].set_index(['background','group','vegetation_metric']).loc[list(keys.itertuples(index=False,name=None))]
            y=[i+offset for i in range(len(keys))]
            ax.hlines(y,sub.low,sub.high,color=color,lw=1.3)
            ax.scatter(sub.beta,y,color=color,marker=marker,s=25,label=label)
        ax.axvline(0,lw=.8,color='#777777');ax.set_title(title,fontsize=11)
        ax.set_xlabel('Standardized rank interaction coefficient')
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='x',alpha=.15)
    axes[0].set_yticks(range(len(keys)),labels,fontsize=10);axes[0].invert_yaxis()
    handles,legend_labels=axes[-1].get_legend_handles_labels()
    fig.legend(handles,legend_labels,loc='lower center',bbox_to_anchor=(.64,.115),ncol=2,fontsize=10,frameon=False)
    fig.suptitle('Landscape vegetation and three-guild association patterns',fontsize=15)
    fig.subplots_adjust(left=.29,right=.98,top=.86,bottom=.25,wspace=.28)
    fig.text(.03,.045,'3-km context around 4,248 acoustic sites; 1,000 route-bootstrap draws; 95% intervals. All lower-order terms included.\n'
             'Mean and spatial SD describe almost identical variation (rho=0.99984); they are not independent structural effects.\n'
             'Exploratory associations conditional on SDMs; no multiple-testing adjustment. Remote landcover is not observed plant use.',fontsize=10)
    fig.savefig(OUT/'vegetation_network_coefficients.png',dpi=160)
    plt.close(fig)
    lines=['# リモセン植生を三者の関係へ接続した結果','',
           '2026-10-26。取得済みEarthEnv full v1の同じ元ファイルを再利用し、音響座標の一点から周辺の環境へ集計範囲を広げた。主解析は半径3 km、感度解析は1 km。結果を見て半径を選び直していない。','',
           '## 何が新しく使えたか','',
           '4,248地点のうち、冠水植生が記録されるのは一点の46地点から、周辺1 kmで126地点、3 kmで506地点・110ルートになった。草本植生は3 kmで3,570地点、開水面は1,540地点。欠測は0地点。これは周辺環境の情報であり、506の繁殖池で植生を現認したという意味ではない。','',
           '元の3ラスターは保存済みSHA256と完全一致し、既存の冠水植生・開水面の一点サンプルも全11,947地点で一致した。0を欠測にせず、255を欠測として、円内の画素中心を緯度に応じた面積重みで平均した。','',
           '## 植生の役割を調べる比較','',
           '鳴き声頻度を応答に、トンボ類適合度、有尾類適合度、周辺植生と、全ての二者項・三者項を含む順位回帰を実行した。植生を単独の正の相関で評価しない。2背景×全有尾類／池繁殖群×植生平均／空間SD×全域／ルート内の全16設定を保存した。','',
           '池で繁殖する有尾類・植生平均の結果は以下。全変数を順位化・標準化しているため、係数は占有確率や鳴き声割合の変化量ではない。','',
           '| 背景 | スケール | 項 | 係数［95%区間］ |','|---|---|---|---:|']
    names={'Odonata:vegetation':'トンボ×植生','Caudata:vegetation':'有尾類×植生','Odonata:Caudata:vegetation':'トンボ×有尾類×植生'}
    for row in d[(d.group=='pond_breeding_Caudata')&(d.vegetation_metric=='mean')&d.term.isin(names)].itertuples():
        lines.append(f"| {row.background} | {'ルート内' if row.within_route else '全域'} | {names[row.term]} | {row.beta:+.3f}［{row.low:+.3f}, {row.high:+.3f}］ |")
    lines+=['',
            '**周辺植生との組合せが、トンボ類と有尾類で違う方向を示す**ことが、今回洗い出した相関である。全域のトンボ×植生項は両背景で負、池繁殖有尾類×植生項は両背景で正の点推定だった。後者の同群背景区間は0を含む。','',
            '三者項は全域の均一背景・池繁殖群で+0.037［+0.008,+0.068］。これは有尾類の適合度によって変わるトンボ類との関係が、さらに植生条件で変わるという記述である。負のトンボ×植生項も同時にあるため、この正の三者項だけから「植生がカエルを救う」とは読まない。','',
            'モデル上、トンボ適合度Oに対する応答の傾きは βO + βOS S + βOV V + βOSV S V。したがって植生Vによる傾きの変化は βOV + βOSV S であり、一つの係数だけで機能を決められない。','',
            '同じルート内では三者項の区間はいずれも0を含む。1 km感度の池繁殖群三者項は均一背景+0.008、同群背景+0.019で、3 kmより小さい。これらはパターンの空間スケールを示す材料であり、全域の相関を無効とする条件ではない。','',
            '## 構造について何が分かり、何が残るか','',
            f'冠水植生の平均と空間SDの順位相関は **{rho:.6f}**。0が多く、平均とSDがほぼ同じ配置を表していた。この二つを別々の植生構造の証拠、または独立した反復結果とは数えない。','',
            'リモセンを使う価値は確認できたが、現在測れたのは「周辺の冠水植生という環境文脈」。隠れ場、卵付着、羽化基質という役割を個別に測定したわけではない。約1 kmの土地被覆のばらつきを、茎密度、水草の高さ、池内の複雑さと呼ばない。','',
            '植生の役割仮説は、トンボ側・有尾類側への作用が異なる、という今回の相関を起点に整理する。段階別の利用と水域持続性を加え、直接・間接経路のどこが変わるかを後続研究で調べる。','',
            '## 再現・出典','',
            '- `python research/scripts/naamp_remote_vegetation_context.py`：hash検証、11,947地点の1/3 km抽出、4,248地点への結合。',
            '- `python research/scripts/naamp_remote_vegetation_network.py`：1,000回のルートbootstrap、全下位項、両背景・両有尾類群、1 km感度。',
            '- `python research/scripts/report_remote_vegetation_network.py`：報告と全設定の図。',
            '- `python -m unittest discover -s research/scripts -p test_remote_vegetation_context.py`：円外除外、欠測と0の区別、定数場の分散の3テスト成功。回帰のルート処理は既存の明示的固定効果一致テストで検証。',
            '- 全データ・係数・感度・入力hash：`research/results/naamp_remote_vegetation_20261026/`。',
            '- EarthEnv full v1、Tuanmu & Jetz 2014、CC BY-NC 4.0。公式仕様：https://www.earthenv.org/landcover 。歴史資料の静的合成であり、調査前年の植生状態とは保証しない。',
            '- 探索的な条件付き相関。多重比較補正なし、SDMの推定不確実性の伝播なし。SDMも環境から作った指標であり、この交互作用項を実測した生物間相互作用に置き換えない。','']
    (ROOT/'research/REMOTE_VEGETATION_NETWORK_REPORT_2026-10-26.md').write_text('\n'.join(lines),encoding='utf-8')
    print('Report and complete vegetation-interaction figure saved.')


if __name__=='__main__':main()
