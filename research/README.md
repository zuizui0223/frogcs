# 現行研究の入口

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
