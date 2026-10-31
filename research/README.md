# 現行研究の入口

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
