# frogcs — **単一の統合論文**による投稿方針（2026-10-31）

**著者方針に従う新しい正式な編集判断：RC6＋main広域マクロ解析＋PR #146〜#155の過程モデルを、別論文としては出さず、一つの原稿へ統合する。** この文書は同日の旧「観測論文A／理論論文B／RC6論文Cに分割する」提案を**明示的に撤回・上書き**する。旧提案の履歴はgit commitで保持。科学的な数値、mainのSHA固定データ、PR #146〜155は変更しない。

**本原稿の現在の英語ドラフト：** [ONE_INTEGRATED_FROGCS_MANUSCRIPT_DRAFT_2026-10-31.md](ONE_INTEGRATED_FROGCS_MANUSCRIPT_DRAFT_2026-10-31.md)。この編集ブランチは現在の実証原稿のレビュー候補で、**学術誌への実投稿は未実施**。

## 1. 中心の一問と、三つの連続した証拠階層

> **カエルの繁殖発声はどのような空間構造を持ち、どのような生物群集・植生の文脈で現れ、その持続や分散を説明する生活史機構はどこまで成立するのか？**

**一つの研究構成：**

1. **現象の定義（短時間の空間パルス）**：RC6のNAAMP雨前後マッチングで、53 taxa・4,236 wetter/drier pairs（うち厳密歴史情報のある2,916 pairs）を解析。補正後でも同一分類群の複数地点に強いコーラスが集中する（観測1.650、帰無1.353、超過0.297、Monte Carlo P=0.000999）。同じ物理地点の過去強発声との対応β=0.151［0.129,0.173］。**個体移動や真の加入ではなく音声活動の空間配置**。
2. **現れる地域・群集の文脈（観測マクロ）**：別の選別・集計単位のNAAMP4,248地点、GBIF/GloBIから28モデル化種の群別適合度、植生・過去水検出・強発声履歴。トンボ環境適合度と強発声頻度の全域負相関−0.095/−0.086、有尾類適合度高低の相関差−0.385［−0.509,−0.240］/−0.179［−0.328,−0.029］、過去強発声履歴差+27.68pp/4,040 pairs、水検出頻度差−1.481pp/3,907 pairs。OSVの正の三者項は背景・空間尺度依存で**一貫した証拠ではない**。**適合度≠ヤゴや有尾類幼生の実測個体数**。
3. **機構の可能性と成立境界（数理仮説のテスト）**：mainの3,600機構構成・20候補×24条件では特定候補の三方向成立が1/24に限定、**野外の正の三者項を再現せず**。PR #146〜155では元120日捕食＋80年加入・有限個体・空間移動の同一ソースを段階的に検証し、S→F幼生捕食が特定の合成率・高加入・q3で移動効果の正→負反転に必要かつ十分。**q6では1/2植物設定のみ、q9/q12では0/2**。仮想生物率ID0だけでの成長主因効果は4率中1率だった。**成立する条件と成立しない条件を並べることが論文のモデル貢献**。

3段階は**一本のResultsの流れ**であるが、推定する対象は互いに異なる。RC6のroute-run行列とmainの地点頻度は同じNAAMPを使用し、独立した野外再現ではない。長期F occupancyを成人カエルのcalling indexに変換する観測モデルは未構築。したがって**モデルが観測された発声や三者項を原因として説明したと書かない**。

## 2. 投稿論文の結論・仮題

第一作業題：**Spatially structured frog calling across rainfall pulses and freshwater community contexts: limits of stage-structured demographic explanations**

第二候補：**Spatial selectivity in frog choruses and the conditional limits of freshwater trophic explanations**

主結論の一文：

> *Frog calling is spatially selective within rainfall-associated pulses and varies with freshwater guild and landscape context, while stage-structured models show that proposed demographic mechanisms are conditional rather than uniquely identified by these acoustic patterns.*

「selective」は比較したnullより集中した**空間的パターン**であり、個体が環境・捕食者を「選んだ」と行動の意思を測定した意味ではない。モデルのlong-term persistenceは野外観測されたrepeated callingの原因とはしていない。

## 3. 一本の論文としての図5本

**Figure 1 — Rainfall-linked acoustic pulse and site matrix.** NAAMP sequential10 stops、CI0→CI2/3、4,236 wetter/drier pairs、2,916 history focal null: observed1.650 / expected1.353。独立する分類群数・routeと物理サイトの情報。

**Figure 2 — Recurrent sites and antecedent water.** RC6 taxon×physical-site historical β0.151とmacro strictly prior +27.68pp/4,040pairs、水検出−1.481pp/3,907pairs。母数が異なるため一つの効果にはまとめない。

**Figure 3 — Third-guild and landscape context.** 4,248 acoustic site locations、28 SDM species、two original backgrounds、Odonata×Caudata high/low contrast、vegetation all two-way and uncertain three-way、全域vs within-route（regional common environment対応）。

**Figure 4 — Mechanistic possibilities and explicit failures.** 元mainの3,600機構、20候補×24設定、1/24 selected success、野外三者＋／シミュレーション三者−の不一致。直接/間接捕食・植生機能を仮説のダイアグラムにするが「実証済み経路」とは表示しない。

**Figure 5 — Demographic contingency / limits.** 元120day+80year、F/S/D幼生捕食、S→F-only/no-SF/all-predation-off、rho×conversionの積、q3→6→9→12の strict sign-reversal 2/2→1/2→0/2→0/2。再占有≠人口維持、0/8と8/8床・天井、12 independent RNG labelsを明示。FE reverse predationは該当2発生条件で時間重複ゼロ（PR148第3発生条件では非ゼロ）、過度に主張しない。

詳細の率・seed・失敗ケース・各モデルのCI・野外の地理/感度結果は統合Supplementary Informationへ。**全部の解析を本文に列挙する必要はないが、全部の結果を一論文の再現資料として保持する**。

## 4. 一つの投稿先を選ぶ

**第一候補：Freshwater Biology, Research Article。** 同誌の[公式Aims & Scope](https://onlinelibrary.wiley.com/page/journal/13652427/homepage/productinformation.html)は淡水における動物行動・個体群・群集相互作用・生物地理学、観測・理論・概念的アプローチを対象にしており、**一本の多尺度観測×過程モデル論文**として最も自然な整合を持つ。査読での最大の弱点は、モデルと観測の直接的対応がないこと。本文では「mechanistic constraints」を前面に出し、当該観測データのcause demonstrationと誤解させない。

**挑戦的な代替：Journal of Animal Ecology, Research Article。** [公式Aims](https://besjournals.onlinelibrary.wiley.com/hub/journal/13652656/aims-and-scope/read-full-aims-and-scope)は行動・個体群・群集を横断した一般的原理の試験を要求。既存RC6がJAE向けQA済みであることは論文構成の参考だが、**原稿を統合した時点で旧RC6向けの「投稿ファイルQA成功」を新原稿のQA成功と取り違えない**。JAEへ投稿するなら新しい統合原稿の原理・因果解釈に厳しい査読を想定する。

**より挑戦的：Ecology Letters (Letter)** [公式ガイド](https://onlinelibrary.wiley.com/page/journal/14610248/homepage/forauthors.html)は簡潔・革新的な仮説検証を重視し、純記述を奨励しない。現状の観測→機構橋渡し不足を抱えたまま第一投稿誌にするとデスクリジェクトリスクが高いため、主張の一般性を追加観測で検証した場合に限る。

**すべて同じ一本の原稿の投稿順序候補**であり、複数の原稿や同時投稿を提案しない。

## 5. 新しい統合ドラフトの構成・方法防御

[英語原稿案](ONE_INTEGRATED_FROGCS_MANUSCRIPT_DRAFT_2026-10-31.md)の章立て：

Introduction：rain pulse→site selectivity→third-guild context→why trophic model constraints matter、という一本のギャップと問い。

Methods：RC6のroute-run null、mainのsite-level 4,248とGBIF/GloBI/vegetation/satellite water、3,600機構モデル、120day/80year finiteN/12seed移動、**推定量が違うことの監査**。

Results：1. rain/recurrent spatial allocation；2. third-guild+vegetation geographic associations；3. water/history；4. limited model explanation incl empirical 3-way mismatch；5. direct predator S→F and recruitment/count-scale dependent movement.

Discussion：観測の空間構造は確か、コミュニティ関連は観測的、過程モデルには成立域・否定域、物理池・実幼生密度・成熟までの野外多年度追跡がまだない。一つの原因を一意に同定できないことをそのまま記す。

査読防御する分母：
- 4,236雨前後ペア/53 taxa/585 routes/21 statesと2,916厳密歴史subset；
- 4,248 acoustic sites/432 route components（別filter）と28モデル化種；
- 4,040 prior history pairsと3,907 water-detected eligible pairs；
- 3,600機構と20×24 sensitivity；
- PR146–155のモデルnative seed 12、仮想qの4値、外部移入OFF。
**同一NAAMPの二つの解析が「二つの独立した実証データセット」だと誤認されないよう、Figure 1と3のMethodsに重複/異なる単位を注記する**。

## 6. 次の実務：新しい解析でなく提出原稿化

1. 英語統合ドラフトをベースに本文・Methods・図5本と統合Supplementを揃える。古いRC6の投稿向けtitle pageや図をそのまま提出しない。
2. main/RC6/PR146–155の全数字・定義・引用・重複データを統一したclaim ledgerで確認し、短い要旨と図から逆引きできるようにする。
3. 特に「野外正の三者項 vs 元モデル負の三者項」「率ID0の単独成長反転は他3率で失敗」「q9/12の反転消失」「SF-onlyの植物機能一部無効」を本文かSIで明示。
4. 対象誌のスタイルに最終整形し、著者・所属・CRediT・利益相反・許諾/倫理・Data Availability・データ/コードの最終版を責任著者と全共著者が承認した後にのみ、本人の明示的な投稿指示で提出する。

元mainの固定894ファイルSHAの科学的入力、\`paper/\`の旧RC6投稿用原本、\`submission/\`、PR #146–155 の生物モデル・数値は**一切編集しない**。本編集ブランチのドラフトを既存main原稿へ反映するかはPRでレビューする。

**完了状態：** 単一投稿方針へ訂正済み、統合論文の英語working draft完成、全主張・図構成・対象誌候補を統合。**未完了：** Figure本体、SI照合、版下、著者承認、出版社への実投稿。