# frogcs — 成果の統合・投稿判断メモ（2026-10-31）

**編集上の判断メモのみ。野外データ、main原稿、旧RC6、固定snapshotおよびPR #146〜155のソース・数値は変更しない。投稿・事前照会・共著者承認は未実施。**

## 0. 結論と投稿の順番

**今は追加の機構探索を停止する。** 投稿可能性を最優先で考えるなら、現行mainの広域観測結果を中心にした原稿1本を先に整える。PR #146〜155の有限個体モデルは「野外機構を再現した証明」ではなく、**どの条件では機構の符号が変わり得るか／一般化に失敗するかを示したモデル内の補助成果**として整理し、必要なら後続の理論モデル論文の材料にする。

現行mainの[二部構成原稿](../research/manuscript/TWO_PART_MANUSCRIPT_DRAFT_2026-10-26.md)は、北米マクロ観測と3,600候補機構の比較に基づく。モデル部は野外の観測変数・三者項を十分には再現していない。**現行main原稿の機構比較を、後発のPR155までのソースを加えたことだけで査読準備完了と認定しない**。PR146の理論群・PR147の個体ABM・PR148〜155の有限Nは異なる仮定、母数、観測量を持つ。

**原稿A（現在の主目標）：広域カエル発声と三群環境適合度・植生・水域履歴に関する条件付き関連。**
主役はNAAMPの野外**観測的な関連**。未校正の幼生捕食モデルを、観測的結果の原因としてDiscussionで接続しない。モデルを残すなら「互いに異なる説明の成立条件を示す限定的なmodel-native illustration」とし、結果を野外データとの直接適合と言わない。

**原稿B（保留する理論候補）：同じ分散が救済にも長期喪失にもなりうる人口動態の成立条件。**
SF幼生捕食×局所加入×S成長×有限個体性×移動のモデル内関係。#153のq3必要・十分は#155で人口尺度依存（q3 2/2植物、q6 1/2、q9/12 0/2）と判明。元率ID0の単独成長反転も#151で4率中1率の条件限定。したがって汎用的な「有尾類の成長が分散を悪化」「S→Fだけで必ず反転」は主張不可。**生物率・空間・個体数の広い範囲に一般化していないため、理論誌用の独立投稿原稿は現時点では未完成**。

**別途保存済み・優先順位を再決定できる原稿C：RC6 JAE音声空間集中。**
原稿Cは2026-10-26以降のmainの**現行原稿ではない**。科学的結果は保存・初期投稿ファイルQAがSUCCESSで、投稿されたという記録はない。現行の研究方針ではRC6は研究史・参照パッケージである。もし著者が**別原稿として改めて投稿を選ぶ**なら、JAEの元投稿準備ファイルがあり、残るのは著者・責任著者・所属・CRediT・利益相反・Statement on Inclusion等の私的メタデータと共著者/所属承認である。WFTSは指定されたが、取得も検証も行われておらず**現行の提出ゲートではない**。[旧RC6投稿準備](../submission/SUBMISSION_READINESS.md)。NAAMPを共有する原稿A/Cを別誌へ投稿するなら、研究質問・エンドポイント・データ再利用を明示し、重複成果や独立再現扱いを避ける。

## 1. 証拠階層：これが「確かに言える」境界

| 層 | 確認済み成果 | 主張できること | 主張しないこと |
|---|---|---|---|
| Observational macro — main | NAAMP強発声地点4,248、捕食候補3群のGBIF/GloBI選定30候補・28種SDM（カエル15、池性を含む有尾類7、トンボ類6） | トンボ環境適合度との弱い負の全域相関 uniform −0.095/target-group −0.086。池性有尾類の高低条件では関連差 −0.385 [−0.509,−0.240] / −0.179 [−0.328,−0.029] | ヤゴ実測密度・有尾類の捕食行動・局所の因果的効果 |
| 植生 — main | OS−、OV−は2背景で符号、SV＋とOSV＋は背景依存でCIが0を跨ぐ | 植生が三群の関連を変える「可能性」／環境文脈 | 野外で特定の避難場所や三者高次相互作用を実証 |
| 長期サイト利用・水 — main | 同条件4,040ペアの過去強発声履歴差 +27.68ポイント [25.07,30.17]、3,907ペアの前年周辺水検出頻度差 −1.481ポイント [−2.601,−0.294] | 発声地点の再利用・周辺の衛星水検出頻度との関連 | 池の湛水日数、真の再定着/繁殖成功 |
| 機構比較 — main | 3,600構成→20候補×24共通条件、成立候補1479の三方向一致は1/24条件 | 生残・捕食危険と順位回帰の三方向を限定的に生成できる候補は存在 | 野外の正の3者項（uniform +0.037）の再現：候補は負方向を生成した。共通条件への一般化・真機構同定 |
| 発生と分散 — #146〜149 | 元の季節120日＋80年遅延加入、モデルnative空間輸送・整数個体分散、厳密0→正の再占有と持続を追跡 | 再占有≠長期占有、分散の効果はモデル背景で変わる | 個体標識の親子、野外の成体強発声・繁殖成功を直接生成 |
| 成長・率依存 — #150〜152 | S成長0.014/0.030×D水中40/60の2×2、4仮想生物率。単独成長で正→負はID0だけ（1/4）。rhoとconversionは外部移入OFFでrho×conversionという同じ積 | 有尾類の成長・局所加入・捕食・生残背景はモデル内の反転を条件付ける | 「発生登場順序が原因」の断定、独立したrho/conversionの2機構 |
| 捕食方向 — #153 | SF=S幼生→F幼生。高加入・q3・原率背景でSF削除すると反転消失、SFだけONでも反転維持。DF/DS/SD個別削除では反転維持 | **この固定モデル内**ではSF経路が厳密符号パターンに必要・十分 | 実湿地での必要十分性。F完成→D羽化捕食FEは今回のsubsetでは時間重複ゼロ、PR148第三条件では非ゼロ |
| 個体数尺度 — #154〜155 | q3 / 6 / 9 / 12でSF-only反転が2/2・1/2・0/2・0/2植物設定、全捕食ONも同傾向。12独立seed/条件 | 本モデルの分散救済/喪失は**有限Nの人口規模と占有床・天井に依存**する | 野外の実個体数閾値・汎用的な人口サイズの閾値。q6/9はq12非再現を見た後の追加探索 |

**注意**：全域順位相関・局所固定比較・合成モデルの長期占有は分母と観測過程が異なり、統合した1つの独立な推定量ではない。GBIF出現記録による潜在ニッチの類似度は、NAAMP地点で実現した捕食者密度ではない。自然データの正の三者項を、モデル内の負の三者項に都合よく合わせない。

## 2. 投稿誌の候補・到達条件（2026-10-31、公式スコープに基づく）

| 原稿 | 第一候補 / 到達し得る誌 | 現実的な選択肢 | 投稿判断 |
|---|---|---|---|
| A：広域マクロ・条件付き関連 | **Ecography（挑戦的）**：空間・時間の一般パターンとメカニズムへの一般的含意が必要。全国全域だけでなくwithin-route/地域での交絡分離が鍵 | **Freshwater Biology（優先する現実的第一候補）**。河川・池・湿地の個体群・群集関係、野外・理論双方に適合。ただし現地の捕食を実測していない点を誇張しない。さらに Ecology and Evolution をバックアップに検討 | **本文の主張をmacro観測に絞り、適合度や地点の同一性を守る原稿修正が必要**。現行main二部原稿は未投稿 |
| B：S→F×局所加入×分散の理論モデル | **Oikos（一般原理・予測が成立する場合）** | **Ecological Modelling（モデルを主役とする場合）** | 現時点はhold。4率中1率・q依存・仮想係数の限定が大きく、普遍機構としては未完成 |
| C：RC6 rain-linked multi-site chorus | **Journal of Animal Ecology（元原稿の投稿先）** | その結果に適した別の行動・群集生態学誌 | 現行mainでは保留された別研究。元投稿ファイルQAは成功、WFTS非取得はブロッカーでない。著者メタデータ／承認が必要 |

- Freshwater Biology 公式 scope: https://onlinelibrary.wiley.com/page/journal/13652427/homepage/productinformation.html
- Ecography 公式 for authors: https://nso-journals.org/ecography-for-authors
- Oikos 公式 for authors: https://nso-journals.org/oikos-for-authors
- Ecological Modelling 公式: https://shop.elsevier.com/journals/ecological-modelling/0304-3800
- Journal of Animal Ecology 公式: https://besjournals.onlinelibrary.wiley.com/hub/journal/13652656/author-guidelines

**Nature Ecology & Evolution / Ecology Letters のfirst-shotは、この証拠状態では高リスクで投稿の優先順位に置かない。** mainの[高インパクト誌ゲート](../research/manuscript/HIGH_IMPACT_SUBMISSION_GATES_2026-10-27.md)が要求した、観測された3者項まで再現するmechanism、真の共観測池データ、共有環境・地理との識別・一般原理の独立検証はまだない。これは雑誌による判定でなく、現時点の編集提案。

## 3. 原稿A：推奨する一文の主張と構成

**中心的な問い**：*Does the association between frog acoustic site use and modelled odonate suitability vary with the suitability of a third freshwater guild and landscape vegetation?*

**作業題名案**：**Third-guild context alters the geographic association between frog calling and odonate niche suitability**

因果性をさらに抑える代案：**Frog calling–odonate suitability associations vary with caudate and vegetation contexts across North America**

**主張する一文**：*The geographic association between frog acoustic activity and odonate niche suitability varies with caudate suitability and landscape context, while past site use is a strong correlate of present calling.*

**本文の図（4本を標準案）**
1. NAAMP4,248地点、対象種28、野外発声指標、同じ相互作用の現地測定でないことを示す分布・方法図。
2. トンボ適合度×強発声の関連を池性有尾類の適合度低高で層別（uniform/target-group両背景・地域全体vsルート内を同じ図に）。これが主図。
3. 植生を含む3群の二者項と三者項、背景・1km/3km・within-routeによる不確実性（正の三者項は一部だけ）。
4. 強発声の過去履歴+27.68ポイントと前年水検出頻度−1.481ポイントを、異なる分母・条件付きの衛星観測指標と明示して示す。

**mainモデルは図5と本文の「因果説明の証拠」として追加しない。** 使うならDiscussionの conceptual scenarios またはSIの sensitivity/failed-model audit として、3方向1/24・三者項の不一致を必ず記載。PR146-155の膨大な合成実験を、マクロ論文の独立実証として統合しない。

**原稿A用の仮要旨（英語、未推敲・原稿依拠、約165語）**：

> Breeding calls provide spatially extensive records of amphibian activity, yet their associations with potential aquatic community context remain poorly resolved. We analysed repeated acoustic surveys at 4,248 North American locations and modelled environmental suitability for frogs, odonates and caudates using occurrence-based distribution models. Frog strong-calling frequency was weakly negatively correlated with odonate suitability at the regional scale. Importantly, this association differed between locations with low and high suitability for pond-breeding caudates, with negative high-minus-low correlation contrasts under both background specifications. Landscape vegetation modified several two-guild associations, although the three-way term was sensitive to model background and spatial scale. Calling locations also showed strong association with prior calling history, while antecedent satellite water-detection frequency provided a distinct, weaker environmental correlate. These findings identify conditional geographic associations across freshwater guilds and repeated use of acoustic survey locations. Because environmental suitability is not a measure of realised predator density, the results provide observational constraints for future tests of trophic mechanisms rather than evidence of predation-driven site use.

最後のセンテンスが投稿の防御に重要。observational dataから「predation suppresses breeding」とは書かない。

## 4. 原稿B：理論的な発見はあるが、今は独立投稿にしない

**作業題名案**：**The limits of dispersal rescue under stage-dependent predation and finite population size**。

観測ではなく、80年のoriginal-source合成個体群モデルの反証可能な問い：*When does dispersal increase recolonization events without maintaining occupied patches?*

図案は、(a) 捕食/成熟/移動の厳密な状態流、(b) local recruitment strength×S growthで移動ON−OFFの年80占有符号、(c) S→F-only・no_SF・全直接捕食OFF、(d) q3/6/9/12での反転成立域・床/天井、(e) rateID0/4/8/12の不成立とrho×conversion構造的非識別を同格に示すこと。成功条件だけに色を付けて過剰一般化しない。

投稿を始める条件：人工的な率・人口サイズを「真の閾値」と呼ばない理論の中心問いを一つに絞ること、元のモデル内部の必要十分性が他の背景では崩れる事実も結論に含めること、rate/case選定が結果後の探索であること、理論と野外観測の対応が欠けていることを全文で明示すること。単独モデル論文は現在の第一優先でない。

## 5. 投稿のために残る最小タスク（解析追加より優先）

1. **原稿Aの権威を固定**：mainの二部構成稿を、野外4,248地点の条件付き関連を主題とする英語原稿へ改稿。旧RC6は研究史・別原稿、#146〜155は「野外データを説明できた」の証拠にしない。mainの元894ファイルsnapshotには触れない。
2. **数値と分母を1回だけ監査**：4,248地点・28モデル種・uniform/target-group・有尾類低高・植生/三者項・4,040/3,907ペアの固定snapshotを照合。非再現と地理・共有環境の影響を同時に記載する。
3. **図4本・短い要旨・査読防御**：平均効果と背景差、within-routeの弱さ、地理的共通環境、音響と幼生モデルの不一致を本文やSIへ明示。仮タイトル/abstractを本編の正しい結論へ落とす。
4. **雑誌決定と著者チェック**：現状態の第一候補Freshwater Biology、挑戦先Ecography、バックアップEcology and Evolutionを共著者と確認。必要なData availability、作者・所属・CRediT・利益相反・資金・許諾／倫理・著者全員承認を揃える。**本人の承認前に学術誌へ送信しない**。

現段階では**論文投稿、共著者承認、外部審査、出版社からの受理**は実行していない。mainの実科学原稿本文、既存CI・収集契約およびモデルPRは一切変更していない。
