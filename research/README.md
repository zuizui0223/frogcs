# 現行研究の入口

## 読む順番

1. [現行の統合原稿：R1–R4・P1・G4–G7](../editorial/MAIN_TEXT_R1_R4_SUBMISSION_CANDIDATE_2026-11-05.md)
2. [P1：植生がカエルに有利になる条件と反転の内訳](P1_VEGETATION_BENEFIT_RESULT_2026-11-06.md)
3. [現行Supplement](../editorial/SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md)
4. [G7の結果・種群の根拠・停止判断](G7_TRAIT_COMPOSITION_RESULT_2026-11-06.md)
5. [一次文献とデータ・コードの由来](../editorial/DATA_CODE_AND_REFERENCE_PROVENANCE_2026-11-06.md)

**主結果は、捕食者の発育条件によって植生の人口学的効果が反転することです（モデル内）。** P1は元の256食物網構造・全4植生処理を保ち、有尾類の加入時期と水中期間を独立に操作しました。早期加入が植生の不利益をほぼ解消し、早期加入に長い水中期間が加わるとカエル量への効果が正になりました。独立した植生機能の比較で得た4符号成立率の増加と合わせ、どの条件で植生がカエルに有利になるかを原稿の中心に置いています。

## 野外との接続

G7は仕様を新しい結果を見る前に固定し、元の5種別SDMを使って完了しました。主係数は両背景で正方向でしたが、区間はゼロを含み、地域外予測も改善しませんでした。[固定仕様](G7_TRAIT_INFORMED_COMPOSITION_PROTOCOL_2026-11-06.md)・[再現コード](scripts/g7_trait_composition_bridge.py)・[出力と独立検証](results/g7_trait_composition_20261106/)。

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

`results/`と`scripts/`には、現行結果の由来・比較対象・再現依存として必要な過去の計算も残っています。古い結果を現在の主結論に採用するという意味ではありません。研究ルート直下の旧契約・収集計画と旧統合原稿2件は、894ファイルの固定スナップショットや既存QAが参照するため原位置に保持しています。現在の入口は上記のR1–R4・P1・G4–G7統合原稿です。
