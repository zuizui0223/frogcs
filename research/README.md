# 現行研究の入口

**[補助PR #147：分散・局所絶滅／再占有・真正親子系譜（2026-10-31）](https://github.com/zuizui0223/frogcs/pull/147)**：既存の**7段階確率ABM＋PDE**を変更せず、出生UID/親UID、死亡済みの祖先、始祖の出生パッチ、世代、確認できる生存者の移動、ギルドごとの年末局所絶滅・再占有を記録できるようにした。20年間×8パッチ×4 seed×分散ON/OFF×F成体→羽化期トンボ捕食逆転ON/OFFの全16件が[実行SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/41186529509)。**有尾類の年20占有パッチは分散なし／ありで捕食逆転OFF時2.25／4.00、局所再占有回数0／2.75**（4種の確率的経路の平均）。Fの系譜は孫以降・始祖の故郷と別のパッチへの展開まで追跡。捕食逆転ONでは合成の強いF→D効果によりDは分散あっても年20で全パッチ消失。[完全な結果・推定上限](DISPERSAL_LOCAL_EXTINCTION_PEDIGREE_RESULT_2026-10-31.md)、[ソースベースの台帳](results/stochastic_pedigree_metapop_20261031/metapopulation_seed_level_summary.csv)。**PR #146の別式の真正80年ABCを置換・校正するものではない**。分散率・再定着・親子は現実のNAAMP観測ではなく合成の結果で、音響の過去利用地再発声を直接説明したと主張しない。


## PR #146 最新追加：main重複構造を修正した108クラス植生ABC（2026-10-31）

**[完全な108モデル構造の訂正・3事前分布感度・生態学的解釈](VEGETATION_MAIN_CANONICAL_108_PRIOR_RESULT_2026-10-31.md)**。18,432件の実際の80年間シミュレーションで、植生によるカエルの有尾類からの保護(`cover_SF=0`)がOFFなら`risk_refuge`ON/OFFは同一構造となることを**4,608対、F_B・全4交互作用係数の数値誤差0**で確認。完全144要因実験の結果は保存しつつ、mainと同じ独立構造としては**108クラス**へ正規化。等108構造事前、等12植物機能事前、mainの3,600モデル中の植物役割頻度による事前の3方式を比較。[成功CI #41185620627](https://github.com/zuizui0223/frogcs/actions/runs/41185620627)、[3構造事前×2尺度の比較表](results/macro_vegetation_cross_ontogeny_20261031/canonical_prior_comparison.csv)。

**新しい核心：植生の重要な作用は発生順序で正負反転するが、最高の植生機能は構造事前の定義に依存。** 主尺度logでは108構造等事前の最上位機能は**カエルを有尾類から保護＋有尾類をヤゴから保護、捕食型切替なし**（27.18%）、植物12役割等事前なら**有尾類をヤゴから保護のみ**（32.03%）、main植物役割頻度事前でも後者（24.33%）。発生順序の「元順序」構成比は約28.5〜34.6%で、固定植生の94.5%を一般化できない。これは未校正率範囲と仮定した有限候補に限定。mainの全3,600構造をABCで実際に比較したものではない。


## PR #146 最新：植生の役割を構造軸に戻した真正80年POM/ABC（2026-10-31）

**[植生の12作用機構×256独立率drawの全結果](VEGETATION_MECHANISMS_256_RATE_80Y_ABC_POM_RESULT_2026-10-31.md)**。以前の12構造ABCは、カエルの有尾類からの保護(`cover_SF=1`)と、植生で変わるヤゴの密度依存的捕食型(`litter=1`)を固定していた。今回は`main`の[3,600構造から植生機構の実際の軸を点検](results/macro_intrinsic_factorial_abc_20261031/main_3600_axis_catalog_audit.csv)し、合法な**12植生機構×避難2×256共通パラメータ×捕食逆転ON/OFF2＝12,288回の実80年個体群シミュレーション**で比較した。元のABC採択65/256・48/256を厳密再現済み。

- **log(F_B)の4符号一致率への植生機能の対効果**：捕食型切り替え**+13.04ポイント**（256共通drawの95% Monte Carlo区間+9.23〜+16.65）、カエルを有尾類から保護**+5.57**（+4.43〜+6.71）、有尾類をヤゴから保護**+1.14**（−0.65〜+2.99）、カエルをヤゴから保護**−5.62**（−6.93〜−4.39）。[対比較と区間](results/macro_intrinsic_factorial_abc_20261031/full256_vegetation_paired_main_effects.csv)。
- **植物機構単位の最高条件付きABC構成比**は`SF1_DF0_DS1_L1`（カエルのSからの保護＋SのDからの保護＋litter）**24.27%**、旧固定`SF1_DF0_DS0_L1` **21.94%**。ただし区間が重なり、避難なしの単一クラスでは旧モデルの25.39%が僅かに高い。植物の何が必須か・一意の勝者は未確定。
- **科学的範囲**：本実行は元の発生順序×基準捕食処理×S↔D捕食リンクONの条件下。**mainの全3,600構造をABCで評価したわけではない**。植生の羽化・採餌機会・残りの保護経路、他の発生順序・処理方式との交互作用は未検証。捕食率等は独立の野外データによる事前分布ではない。

**数値ゲート：** [本物の256組の80年計算SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/41183066399)／[256draw全部を使うブートストラップ修正・再検証SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/41183423247)／[生物学的経路ON/OFFの対応差と1999回CI SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/41183607024)。`main`および元の季節・年次カーネルは不変更。

**最新のABC事前分布感度（2026-10-31）：** [生物率の9種類の密度に対する生成可能性とモデル順位の検証](MODEL_NATIVE_ABC_RATE_PRIOR_SENSITIVITY_RESULT_2026-10-31.md)を完了。すでに成功した**6,144回の実際の80年シミュレーション**を、256共有パラメータID×逆転捕食2状態を保持して再重み付けした。mainの補正前4符号を目標とした**元の発生順序×基準捕食処理×避難なし**は、`log(F_B)`の元密度＋8代替密度、raw `F_B`の元密度＋8代替密度の**すべてで最上位**。logで元発生順序の条件付きABC比率92.8〜98.1%、基準捕食処理79.0〜94.6%。[完全実データ入力と重みブートストラップの成功CI](https://github.com/zuizui0223/frogcs/actions/runs/41181199778)。**同一の仮想的な率範囲内の事前密度感度**であり、率範囲を外側へ変えた場合の頑健性、野外で真である確率、成体発声への橋渡しは未検証。


## PR #146 新しい本解析：既存80年モデルの2×2×2四符号POM＋実際のパラメータABC-RF（2026-10-31）

**[今までの肯定的な生態学的結論と実証の限界](FROGCS_SUPPORTED_FINDINGS_AND_MODEL_NATIVE_ABC_2026-10-31.md)**を先に整理した。野外NAAMPの雨後の多地点コーラスの組織化・同じ種の過去利用地点の再発声と、トンボ類／有尾類／植生の広域相関は**実測結果**。植生による捕食者からの保護やヤゴの機能的応答の組合せは**合成モデルで成立した可能性**であり、野外の機構特定ではない。

**[新しい真正ABCと受容パラメータ領域の全結果](MODEL_NATIVE_GENUINE_80Y_ABC_RF_RESULT_2026-10-31.md)**：mainの補正前`OS−・OV−・SV+・OSV+`だけを目標に、モデル固有の2×2×2（V=0/1×S,D供給0.25/2）実験から`log(F_B)`差の差の四方向を取得。**3発生順序×2捕食処理×2避難＝12構造×256共有パラメータ抽出×捕食逆転ON/OFF＝6,144回**、120日季節内＋80年間の決定論的な本モデルを実際に再実行した。元の24×8モデルとF_B誤差7e−16以内で一致。

- 元の発生順序・基準捕食処理・**避難なし：130/512**（256率draw中65で成立）＝**25.39%採択**、12等事前の**条件付きABC共有量51.18%**、率drawの相関を保持したbootstrap区間**44.35–57.89%**。
- 同じ条件の**避難あり：96/512**（48率draw）＝**18.75%採択**、共有量37.80%（31.57–43.59%）。この2群で**226/254＝88.98%**の条件付き共有量。raw`F_B`でも上位2群は同じ（合計250/270＝92.59%）。
- ABC-RFは同じ「避難なし」を選び、2段階OOB誤分類から求める主尺度log(F_B)の**選択クラス条件付き近似正解度53.0%**（raw(F_B)では53.8%）。しかし全12構造の保持率drawでの分類精度は**22.3%**（12等確率チャンス8.3%）。**機構の一意識別は弱い**。
- 受容した独立率drawは、事前中央値より弱めの総捕食倍率とやや高めのカエル生残へ偏る傾向があった。捕食逆転ON/OFFのABC採択可否は全256×12構造で一致したが、一部の四符号自体は違うため「すべて同一のモデル」と呼ばない。
- **追加の真正ABCパラメータ成立条件（検証済み）：** [同じ256率drawでの避難ON/OFF対比較と事前分布四分位](MODEL_NATIVE_ABC_PARAMETER_REGIONS_RESULT_2026-10-31.md)では、元順序・基準処理の4符号一致率が避難なし**65/256**、避難あり**48/256**。差+6.64ポイント（ペア再標本化区間+1.56〜+11.33）。総捕食倍率の最下四分位での一致率は35.9%／40.6%、最上四分位では9.4%／3.1%。[保持率drawのABC-RF軸別検証](results/model_native_abc_rf_20261031/rf_structural_axis_recoverability.csv)では発生順序50.2%（3択）、餌処理方式69.2%（2択）、避難61.9%（2択）、完全12構造22.3%。**構造の粗い成分は絞れるが、細部の唯一解は未確定**。全て仮説的なrate priorsに依存し、野外機構の推定確率ではない。[パラメータCI成功](https://github.com/zuizui0223/frogcs/actions/runs/41179103204)／[RF軸別CI成功](https://github.com/zuizui0223/frogcs/actions/runs/41179497079)。

**本結果の数値は仮想的なパラメータ事前分布・12構造に条件付けたもの**。野外の実際の捕食率・メカニズムの真の事後確率ではない。R²校正した地点ノイズの旧実験は別の観測過程感度として保存するが、今回の2×2×2の成功基準には使用していない。

[main由来4符号とモデル内8条件の固定仕様](MODEL_NATIVE_DIRECTIONAL_ABC_RF_PROTOCOL_2026-10-31.md)／[実数値ABC-12構造](results/model_native_abc_rf_20261031/abc_rejection_model_acceptance.csv)／[rate-drawのペアを守った不確実性](results/model_native_abc_rf_20261031/paired_prior_class_intervals.csv)／[率受容領域](results/model_native_abc_rf_20261031/selected_original_baseline_posterior_parameters_log.csv)。**成功CI：[6,144回モデル＋ABC-RF](https://github.com/zuizui0223/frogcs/actions/runs/41178134567)、[対になった事前率drawの不確実性監査](https://github.com/zuizui0223/frogcs/actions/runs/41178632190)**。ABC-RFと有限12候補群の識別限界を保持し、PR #146はDraft。main、PR #144/#145、原モデルは不変更。


## PR #146 最新の主線：観測R²にノイズを合わせた方向POM（2026-10-31）

[132固定構成・192実際の80年再計算・危険増幅72構成を一度に評価した完全結果](MACRO_R2_MATCHED_DIRECTIONAL_POM_RESULTS_2026-10-31.md)。NAAMP 4,248地点・63,180調査の同じ8項順位回帰R²（uniform 4.70%、target-group 5.18%）だけで各出力の観測ノイズ量を校正し、独立128反復で**OS−・OV−・ΔS−・ΔV−・低Sほぼゼロ**の5条件を評価した。ノイズなしの決定論的全一致0/132・0/192という不一致は、**R²を合わせると複数シナリオで非ゼロ頻度の一致を生成**できるため、観測過程に依存することが判明。ただしノイズ空間構造・変換によって順位が大きく変動し、全8観測条件で厳密5方向一致頻度≥10%の出力群は**132/192/72構成すべて0**。危険増幅型は同じ24構造の中・強増幅 vs 増幅なしの対比較で、**16集計すべて平均類似度が低下**。最良の野外機構・ABC事後確率は未確定。

- [全6系列（独立／空間誤差×132／192／増幅）実計算のSUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/41168178231)
- [6系列統合・R²校正監査のSUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/41168203797)
- [元構造を固定した増幅の対比較・全8条件のSUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/41168371045)
- [保存済みの全系列概要](results/macro_r2_matched_directional_20261031/source_family_summary.csv)／[危険増幅の対照別数値](results/macro_r2_matched_directional_20261031/amplification_paired_summary.csv)／[研究用の固定仕様](MACRO_R2_MATCHED_DIRECTIONAL_POM_PROTOCOL_2026-10-31.md)

この結果は**観測R²を事後に合わせた感度解析**で、モデルの生物学的正しさや成体カエルの発声検出過程を独立校正したものではない。順位を先に取ると振幅情報は回復できないため、log(F_B)へのノイズ追加も同列の感度検査として保持する。POMが主解析、ABM/PDEは必要時のみ補助。PRはDraftのまま、原本・main・PR #144/#145は不変更。


**最新（2026-10-31）：方向だけのPOMで「不一致の最小条件」を定量化。** 4,248地点・63,180回の強発声について、トンボ類×植生（OV）負と、`ΔS = cor(O,発声 | 有尾類適合度高) - cor(O,発声 | 適合度低)` 負を**同時**に実現する構成が、uniformの既存132（完全に同じF_B面をまとめた104群）で0件、実際に80年を再実行した8パラメータ×24構造＝192構成でも0件。target-groupの固定132にはその2条件の1構成があるが、OS負を加えると0件。元の率の再計算ではtarget-groupも2条件で0件。**単に捕食の負方向が出るかではなく、植生条件と有尾類条件の双方の相関変化方向が同時に生じるかが、現行モデルの中心的な失敗。** [実測・最小不一致の全結果](MACRO_SIGNED_CONTEXT_MINIMAL_CONTRADICTION_RESULT_2026-10-31.md)／[30通りの部分条件](results/macro_signed_context_tradeoff_20261031/all_nonempty_direction_subsets.csv)／[検証CI](https://github.com/zuizui0223/frogcs/actions/runs/41167054391)。これは同じNAAMP標本での探索的なパターン指向比較であり、機構の因果推定でもABC事後確率でもない。


**2026-10-31更新：方向だけのマクロPOMで識別すべき問題を絞った。** [132構成の実地点符号＋低S三値・人工観測ノイズ比較](MACRO_DIRECTIONAL_POM_RESULTS_2026-10-31.md)では、低SのO–鳴き声相関が「ほぼゼロ」になる観測bootstrap頻度がuniform93.3%、target-group93.5%。OS/OV等の確かな符号と**低Sほぼゼロを同時に満たす既存132構成は両背景0**。方向署名の最良群はuniform `case_015`代表、target-group `case_005`代表。ただし観測ノイズ事前分布は仮定的で、事後確率や因果性を示さない。

[実際の8パラメータ80年再計算の方向評価](results/macro_directional_process_rate_20261031/)も実行し、構造群の別パラメータ保持回復率は13.5%/20.8%。[有尾類存在がヤゴ→カエル捕食危険を増幅するという追加の仮説的モデル](MACRO_S_FACILITATED_DANGER_POM_RESULTS_2026-10-31.md)では、元のF_B面を1e-15程度で再現する派生モデルで増幅なし・中・強を比較したが、どれも全部の方向を再現せず、量的距離は悪化した。**POMが主解析、ABM/PDEは補助、結果はモデルの再現限界を含めて報告する。** [PR #146](https://github.com/zuizui0223/frogcs/pull/146)はDraft。


## 最新：マクロパターンを直接再現するシナリオ選択（POM、PR #146）

[全132構成の実地点パターン比較と条件付きABC試験](MACRO_POM_132_ABC_RESULTS_2026-10-31.md)を実行した。対象はNAAMP 4,248地点・63,180調査の**実際のO/S/V分布**。マクロのOS・OV・SV・OSV、S低位／高位のトンボ類との関係という**6つの観測パターン**を同じ順位推定量で比較し、さらに選定外の植生別・ルート内の4パターンでも照合した。

- 初回24候補→全132候補へ拡張、完全に同じ応答曲面をまとめると**104群**。
- 最短距離：uniform は`case_005/009`、target-group は`case_036`。ただし両背景とも**6パターン全一致の構成は0**。最短距離の候補も選定外4パターン中2つしか観測区間内に入らなかった。
- 疑似ABCの採択割合は**合成のproxy写像・発声順位ノイズ事前分布に条件付けた参考値**で、捕食率の事前分布に基づく実際のシナリオ事後確率ではない。人工的な群識別率はuniform約46%、target-group約44%。
- [24構成POM仕様](MACRO_POM_ABC_CONDITIONAL_PROTOCOL_2026-10-31.md)・[全132仕様](MACRO_POM_COMPLETE_CATALOG_132_PROTOCOL_2026-10-31.md)／[POMスクリプト](scripts/pattern_oriented_archive132.py)／[完全な132ケース順位](results/macro_pom_catalog132_20261031/compact_full_ranking.csv)／[CI成功](https://github.com/zuizui0223/frogcs/actions/runs/41162205696)。

**研究目的は「最も近いシナリオを比較・選定する」こと**。環境のみの統計モデルとの予測競争は別の問いであり、POMの合否判定として要求しない。もっとも、`NO_ADEQUATE_SCENARIO_IN_ARCHIVED_132`なので、今回の候補に野外機構の証明・全マクロパターンの十分な再現を付与していない。実際の捕食・成長パラメータの事前分布から元のシミュレーションを再実行する段階が次工程で、ABM/PDEは必要な場合に限る。


**最新・実データによる選定失敗の診断（2026-10-31）**：[機構の追加情報量・発声への変換方向・植生有無の予測失敗](MACRO_SCENARIO_INADEQUACY_RESULT_2026-10-31.md)。`case_084`の`log(F_B)`は、既存環境・交互作用で変動の約99.9%が説明される。選定モデルの観測リンクは10fold中8foldで負。target-groupでは植生陽性506地点の予測が環境対照より悪く、逆転捕食ON/OFFは12ペア中8ペアで元のF_B面が完全に同じ。非負のコホート→発声リンクを仮定しても両背景で有力環境モデルに勝てなかった。ABM/PDEではこの観測上の識別問題は解決しない。**NO_EMPIRICALLY_SUPPORTED_WINNERを維持**。


## PR #146の現在の主目的：マクロパターンを説明できるシナリオの選定

**ABM/PDEありきではなく、観測結果をよく予測できる機構を選ぶ。** [24候補のnested spatial CV実測結果](MACRO_FIRST_SCENARIO_SELECTION_RESULT_2026-10-31.md)では、4,248地点・63,180回の強発声を5外側fold×3内側foldで評価した。既存の80年決定論的な季節コホート＋年次遅延加入モデルを主解析に採用し、3発生順序×2捕食処理×2避難×2逆転捕食を比較。**両SDM背景で環境対照に勝つシナリオは確認されなかった**。

- 繰り返し選ばれた探索候補：`case_084`（有尾類先行・後にトンボが成長で追い越す・カエル→羽化期トンボ捕食）。各背景で5fold中3fold。ただしOSは観測と逆符号。
- 同じ条件で逆転捕食だけ外した`case_080`との差は極小で、統計的に区別できず。12組×両背景の24比較でも逆転捕食の独立した予測増分は確認できない。
- 固定仕様：[事前定義した候補と対照](MACRO_FIRST_SCENARIO_SELECTION_PROTOCOL_2026-10-31.md) ／ 再計算：[実装](scripts/select_macro_trophic_scenarios.py)・[6件のテスト](scripts/test_select_macro_trophic_scenarios.py) ／ [実数値の保存](results/macro_scenario_selection_20261031/) ／ [CI成功](https://github.com/zuizui0223/frogcs/actions/runs/41158677472)。

このPR内の空間ABM/PDEは**二次的な合成シナリオ診断**であり、現時点のマクロ説明機構の選定には使わない。


## 独立探索：世代間の捕食関係逆転（PR #146）

[20年の空間ABM＋反応拡散PDE実装](scripts/multigeneration_reversal.py)は、従来の決定論的な年次コホートモデルを**改変せず**、カエルの変態後段階→トンボ羽化期の捕食が翌年以降の個体群・局所的な消失・移動へどう波及し得るかを比較します。親個体IDと世代番号を追跡するABM、同じ捕食危険を用いた7段階の空間PDEを、8パッチ・20年で実行しました。8テストとGitHub Actionsの全シナリオ再計算は成功しています。

- [固定パイロット結果](MULTIGENERATION_ABM_PDE_PILOT_RESULT_2026-10-31.md)
- [追加・探索的な捕食率／分散／第三者作用の結果と限界](MULTIGENERATION_SENSITIVITY_RESULT_2026-10-31.md)
- [後付け感度格子の設計](MULTIGENERATION_POST_PILOT_SENSITIVITY_2026-10-31.md)
- [PR #146](https://github.com/zuizui0223/frogcs/pull/146)

**これは合成モデルの可能性検証であり、NAAMPの発声パターンを説明したものではありません。** 変態後の繁殖前カエルを成体と一括していること、羽化窓が実際の一夜より長いこと、捕食率・池間移動を未校正であることが次版の主要課題です。PR #145の発声観測橋渡しとは別成果物で、今回の陰性結果を上書きしません。


実地点との照合：[相殺条件と4,248地点の植生文脈](manuscript/MECHANISM_SITE_CONFRONTATION_2026-10-29.md)。景観植生で検査できる部分と、未測定の発生段階を分けています。

機構診断：[有尾類作用の相殺・時間的条件・順位化](manuscript/WEAK_THIRD_GUILD_MECHANISM_DIAGNOSIS_2026-10-29.md)。固定モデルの27対照条件と季節内の危険分解を追加しました。

最新の実行結果：[公開データで埋めた接続と残る課題](manuscript/PUBLIC_DATA_GAP_CLOSURE_2026-10-29.md)。44池日の発声―雄数、73池の段階別三群、固定モデルと最新マクロ係数を検査しました。

NEEを目指す最新段階：[追加検証とG1/G2/G3判定](manuscript/NEE_EVIDENCE_PROGRESS_2026-10-29.md)、[全新規結果](results/nee_context_20261029/)。原スナップショットと2026-10-27のシミュレーション結果は保持し、今回の84モデルを別出力に保存しています。

## 読む順番

1. [二部構成の論文原稿](manuscript/TWO_PART_MANUSCRIPT_DRAFT_2026-10-26.md)
2. [最終機構比較と全検証結果](manuscript/FINAL_MECHANISM_COMPARISON_2026-10-27.md)
3. [考察と結論](manuscript/ECOLOGICAL_DISCUSSION_CONCLUSION_2026-10-27.md)
4. [植生機能の一次文献と適用範囲](manuscript/VEGETATION_FUNCTION_EVIDENCE_2026-10-27.md)

## マクロ解析

- [結果総括](FROGCS_MACRO_ANALYSIS_FINAL_REPORT_2026-10-26.md)
- [植生と三群の関連](REMOTE_VEGETATION_NETWORK_REPORT_2026-10-26.md)
- [実係数・区間・全感度解析](results/naamp_remote_vegetation_20261026/)
- [固定データの検証と数値再現](reproducibility/README.md)

## 最終シミュレーション

- [固定設計](../docs/superpowers/plans/2026-10-27-final-mechanism-comparison.md)
- [全結果・選定理由・条件・環境情報](results/final_mechanism_20261027/)
- [機構集合と判定](scripts/final_mechanism_common.py)
- [季節内カーネル](scripts/stage_vegetation_network.py) / [年次集計](scripts/final_network_summary.py)

リポジトリ直下からの実行順：

```console
python research/scripts/verify_macro_snapshot.py
python -m unittest discover -s research/scripts -p "test_final*.py"
python research/scripts/run_final_mechanism_screen.py
python research/scripts/validate_final_mechanisms.py
python research/scripts/audit_final_candidates.py
python research/scripts/check_final_rank_resolution.py
python research/scripts/verify_final_winner.py
python research/scripts/verify_final_reduced.py
python research/scripts/summarize_final_mechanisms.py
```

既存結果を再利用して再開するスクリプトを含みます。独立した全再計算は別のチェックアウトで`research/results/final_mechanism_20261027/`の保存結果を退避して実行し、現行の固定結果と比較してください。Python・パッケージ版は[環境記録](results/final_mechanism_20261027/environment.json)を参照してください。

## 過去の解析と資料

[legacyの索引](../legacy/README.md)から旧機構監査・旧原稿へ進んでください。移動元と移動先は[移動台帳](../legacy/archive_manifest_20261027.json)に保存しました。

`results/`と`scripts/`には、現行結果の由来・比較対象・再現依存として必要な過去の計算も残っています。古い結果を現在の主結論に採用するという意味ではありません。研究ルート直下の旧契約・収集計画と旧統合原稿2件は、894ファイルの固定スナップショットや既存QAが参照するため原位置に保持しています。現在の入口は上記の二部構成原稿です。
