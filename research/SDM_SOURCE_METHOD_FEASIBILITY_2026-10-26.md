# 広域GBIFから種別SDMを作りNAAMP地点へ投影するための資料・方法

2026-10-26。最新方針は、NAAMPと同時期・近傍に記録された他群だけを要求せず、広域GBIFの種別presence–backgroundモデルからNAAMP地点の相対的分布適性を予測すること。lifeStageは参加条件にしない。以下は一次資料に基づく実装前確認であり、モデルを実行した結果ではない。

## 無認証の環境資料

| 資料 | 期間・粒度・内容 | 実装用URL／確認 |
|---|---|---|
| WorldClim 2.1 | 1970–2000の平年気候、19 bioclim変数。30秒、2.5分、5分、10分。年別天候ではない | `https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip`。HEAD 200、49,869,449 bytes、認証なし。より細かい版は`10m`を`2.5m`や`30s`に置換する公式リンクあり |
| EarthEnv Consensus Land Cover v1 full | 30秒、12クラス、uint8の0–100 consensus prevalence。複数年代の土地被覆統合で毎年の植生ではない | `https://data.earthenv.org/consensus_landcover/with_DISCover/consensus_full_class_8.tif`。HEAD 200、22,102,767 bytes、認証なし。class12は開水面、8は冠水植生、6は草本 |

出典：[WorldClim公式](https://www.worldclim.org/data/worldclim21.html)、[EarthEnv公式](https://www.earthenv.org/landcover)。HTTP確認は2026-10-26。WorldClim引用はFick・Hijmans（2017）、EarthEnvはTuanmu・Jetz（2014）。EarthEnv fullには1992–1993 DISCoverも含まれ、reducedはそれを除く。既存解析と版を統一する。EarthEnvはCC BY-NC 4.0。

まず気候の温度・季節性・降水量・降水季節性と土地被覆を少数に固定する。19気候変数を無条件で全部入れない。予測点・背景・出現で同じ座標系、解像度、集約法を使う。10分気候を1 kmに補間しても1 kmの新情報は増えない。細粒度の植生を使うなら別の空間支持であることを示す。EarthEnvの冠水植生は抽水植物被度／茎構造とは異なる。両資料は気候・景観適性に適し、2001年等の調査日の雨・水位の代替ではない。

## 推定対象を固定する

背景点は未調査または在不在不明であって真の不在ではない。presence対backgroundのロジスティック出力は、その標本構成で記録と背景を識別するスコアであり、そのまま絶対的占有確率・存在確率とは呼ばない。観察努力と検出が環境に依存すれば生物の分布と記録過程が混ざる。[Yackulic et al. 2013](https://doi.org/10.1111/2041-210x.12004)

推奨ラベルは「種別の相対的環境適性」。種間で生の0–1値を足して期待種数にしない。種別背景内順位などへ標準化する場合も、固定背景に対する相対順位である。Anura・Caudata・Odonataの適性比較は生態的近さの検討に使えるが、幼生在密度・遭遇・捕食強度ではない。

## 標本バイアスと検証

- 広域化する地理範囲は結果を見る前に固定する。全球の全陸地を自動的に背景にせず、対象種が到達・調査されうる範囲を明示する。分類群と地域を広げても、同義語、座標エラー、飼育・化石、重複、同一画素の集中を点検する。データセット・時期・basisOfRecordと有効画素数も保存する。
- 同じ採集・観察過程を共有するtarget-group背景は、均一背景との差による記録バイアスを減らせる。ただし三群を無条件で混ぜると観察方法が違い得る。まず同群・同資料種別を揃え、均一背景との感度を示す。間引きだけで努力差が解決したとは扱わない。[Phillips et al. 2009の一次比較](https://doi.org/10.1890/07-2153.1)
- 主評価は空間ブロック外予測。近接記録や同一画素をtrain／testに分けない。背景抽出、変数選択、変換、モデル調整は訓練fold内で行う。ブロックの大きさは予測先への移送距離に合わせて固定し、ランダム分割は補助結果とする。[Roberts et al. 2017](https://www.wsl.ch/lud/biodiversity_events/papers/Roberts_et_al-2017-Ecography.pdf)
- AUCが高いことは絶対確率の較正でも因果性でもない。各種の有効記録数・空間ブロック数、保留域の性能、予測のfold間変動、NAAMP地点が訓練環境の範囲外かを報告する。少数地点に集中した種は記録件数が多くても独立情報が少ない。

## NAAMPとの接続

種別SDMはNAAMPの強い鳴き声／無声ラベルを使わずに学習・評価する。投影後、固定matched pairs内で、他群適性、植生、持続性、自種の厳密な過去利用を比較する。可能なら種別予測の不確実性を後段でも伝える。GBIFにNAAMP由来記録が混在する場合はdataset単位で除外し、同じ観察の再利用を避ける。

現在までの広域記録を学習に使う場合、得られるのは後知恵を含む地域的適性地図であって各訪問日前の予測ではない。今回緩めた同時期制約とは整合するが、strict priorである自種利用履歴とは明確に分ける。これにより環境的に近い生物の配置を検討できる。適性の残差や重なりだけで競争・捕食が成立したとは判定しない。

## 15種pilotのCaudata：池の幼生仮説への適否

記録数上位で選ぶことと、池の水生幼生の比較に適した種を選ぶことは異なる。指定された5種を公的種アカウントと発生研究で点検した。広域SDMには全種を残せるが、5種の平均を「池の幼生捕食者適性」と呼ばない。

| 種 | 生活史・水域 | 池の幼生仮説での位置づけ |
|---|---|---|
| *Notophthalmus viridescens* | 幼生は植生のある小水域、成体も池・湖・湿地等を利用。eftは陸生 | 5種中では池への適合が明確。ただし全段階SDMには陸生eftも含まれる。[Kansas州公式](https://kdwpt.ks.gov/Services/Threatened-and-Endangered-Wildlife/All-Threatened-and-Endangered-Species/EASTERN-NEWT) |
| *Pseudotriton ruber* | 主に湧水・滲出水・源流で水生幼生期が1年以上。静水池の幼生記録も例外的にある | 流水／湧水群として分離。池の代表種と一括しない。[North Carolina州アカウント](https://auth1.dpr.ncparks.gov/amphibians/view.php?sciName=Pseudotriton+ruber) |
| *Plethodon cinereus* | 直接発生し、自由生活する水生幼生を持たない | **池の幼生ニッチから除外**。森林・湿潤陸生環境の比較対象には使える。[発生過程の一次研究](https://pmc.ncbi.nlm.nih.gov/articles/PMC9385146/) |
| *Desmognathus ochrophaeus* | 幼生は滲出水や浅く流れの遅い渓流部分を利用。成体には陸生利用もある | 渓流・滲出水群。池の幼生と機能的に同じ群にしない。[Virginia DWR公式](https://dwr.virginia.gov/wildlife/information/allegheny-mountain-dusky-salamander/) |
| *Eurycea cirrigera* | 渓流で産卵、水生幼生期1–3年。周辺森林も利用 | 渓流群。池・一時水域の仮説とは分ける。[Illinois DNR公式](https://dnr.illinois.gov/education/wildaboutpages/wildaboutsalamanders/wassoutherntwolinedsalamander.html) |

次の機構対象候補は、独立した生活史根拠から *Ambystoma maculatum*、*A. opacum*、*A. tigrinum* とする。USGSのDelaware Water Gap調査報告では、前二者は季節的水域に水生幼生を持ち、*A. maculatum*は春に水中産卵、*A. opacum*は晩夏〜秋に乾いた池底等へ産卵し、再冠水で孵化して越冬する。この違いは水域持続性と発育の先行・後行を比較する直接の根拠になる。[USGS 2020報告](https://pubs.usgs.gov/sir/2020/5081/sir20205081.pdf)

*A. tigrinum*も魚のいない池で繁殖し、水生幼生を経る候補。ただし西部の古い資料は現在別種とされる分類群を同名に含みうるため、GBIF accepted taxonと地域を固定する。ここでは東部種を明記したMissouri州の資料を根拠にする。[Missouri Department of Conservation 2026](https://mdc.mo.gov/magazines/missouri-conservationist/2026-02/wild-guide-eastern-tiger-salamander)

この候補選定は今回のSDM性能やNAAMPとの関連の強さで決めない。池種・流水種・直接発生種を対照として残すことで、他群適性の関連が一般的な森林／湿潤環境なのか、池で発育する生活史に特有なのかを次に比較できる。候補の存在は当該NAAMP地点での幼生の実在や捕食を保証しない。
