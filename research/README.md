# 現行研究の入口

## 読む順番

1. [現行の統合原稿：R1–R4・P1・G4–G10](../editorial/MAIN_TEXT_R1_R4_SUBMISSION_CANDIDATE_2026-11-05.md)
1a. [G10：率×発育条件内の比較で分かった73%の解釈](G10_RATE_CONTEXT_STANDARDIZED_G9_VERIFIED_RESULT_2026-11-07.md)
2. [G9：4符号の新規生成782組のカエル量帰結](G9_COMPATIBILITY_DEMOGRAPHY_JOINT_RESULT_2026-11-07.md)
3. [G8：27率条件の全結果と一般化の判定](G8_27RATE_VERIFIED_RESULT_2026-11-07.md)
4. [P1：植生がカエルに有利になる条件と反転の内訳](P1_VEGETATION_BENEFIT_RESULT_2026-11-06.md)
5. [現行Supplement（G8はS10、G9はS11）](../editorial/SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md)
6. [G7の野外予測未達と停止判断](G7_TRAIT_COMPOSITION_RESULT_2026-11-06.md)
7. [一次文献とデータ・コードの由来](../editorial/DATA_CODE_AND_REFERENCE_PROVENANCE_2026-11-06.md)

**主結果は、パターン生成と焦点カエルの人口学的利益の乖離です（合成モデル内）。** P1は元の256食物網構造・全4植生処理を保ち、有尾類の加入時期と水中期間を独立に操作しました。早期加入が植生の不利益をほぼ解消し、早期加入に長い水中期間が加わるとカエル量への効果が正になりました。固定率の植生二機能による4方向成立率増加（3.52%→14.06%）に加え、G8は同じ256構造の**27率条件で全体平均+2.705ポイント［+2.021,+3.410］、平均logカエル量−0.04030［−0.04918,−0.03109］**を示しました。成立率が改善する率条件は限られ、発育条件2ではカエル量への効果が正へ反転します。G8は真の80年モデル82,944本・64分割の監査が完了し、原稿QAも成功。**追加のG9事後診断では、4符号を新たに成立させた782組中571組（73.0%）でカエル量への効果が負**であり、符号生成の成否が個体群利益と同じではないことを直接集計しました。

**G10で率×発育条件を揃えて非生成群と比較すると、減少割合の差は−4.93ポイント［−11.28,+0.83］で、明確な超過減少はありませんでした。** 発育条件0・1と2では関連の方向が逆です。これは事後的な合成モデル内の比較であり、野外因果を同定しません。

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

`results/`と`scripts/`には、現行結果の由来・比較対象・再現依存として必要な過去の計算も残っています。古い結果を現在の主結論に採用するという意味ではありません。研究ルート直下の旧契約・収集計画と旧統合原稿2件は、894ファイルの固定スナップショットや既存QAが参照するため原位置に保持しています。現在の入口は上記のR1–R4・P1・G4–G10統合原稿です。
