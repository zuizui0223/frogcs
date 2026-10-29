# 作業稿の主張・根拠・到達点

本稿は2026-10-29の追加検証を含む作業版。固定済み旧稿の差し替えやNEE投稿準備完了を意味しない。

| 本稿の主張／図 | 数値根拠（research/results以下） | 解釈上限 |
|---|---|---|
| 図1：柔軟環境調整でOVは残りOSは減衰 | nee_crossfit_20261029/coefficients.csv：連続V、pooled、両背景、全補助モデル | 条件付き関連。内部空間交差適合。区間は固定した補助モデルに条件付き |
| 図2：発声の頻度／確認時強度 | mechanism_observation_20261029/calling_component_coefficients.csv：uniform、同じ4182地点 | 元の線形調整・二値V。生存・個体数への因果分解ではない |
| 図3：飽和と代替餌処理が異なる作用 | handling_factorial_20261029/dense21_rank_coefficients.csv、dense21_physical_contrasts.csv：0000/1000/0100/1100/1111 | 合成モデル内の介入。uniformの全3区間への一致はない。高Vの危険増幅を全域へ一般化しない |
| 図3：マクロ参照 | scale_comparison_20261029/macro_common_estimators.csv：uniform、binary、rank/rank、space、pooled | 同尺度の比較用参照で、図1の連続V・柔軟調整の結果とは異なる |
| 図4：サイズ逆転の順序依存性 | literature_extension_20261029/paired_size_dynamics.csv：shared_both、risk=false、uniform、2交差順序 | 合成成長・9×9格子。野外での季節内逆転の確認ではない |
| 公開餌実験の記述再解析 | nee_external_prey_check_20261029/summary.csv、matched_alternative_prey_contrasts.csv | 21層ずつ、比較幅不揃い。ヤゴの2餌種実験であり有尾類経路の検証ではない |

図の入力SHA256はfigures/sources.jsonに保存。図はPNGと編集可能なSVGを併置した。O=トンボ類適合度、S=池性有尾類適合度、V=景観冠水植生。モデルO/Sに対応する供給量を野外適合度や局所密度と同一視しない。

## 投稿判断

G1は一部到達、G2・G3は未達。現在の結論は「植生の文脈依存的な関連は比較的残るが、有尾類の第三者作用の野外識別は未解決。モデルは飽和・代替餌処理・発生段階の作用を区別する検証仮説を与える」である。NEE達成と判定しない。

詳細は同時更新のNEE_FOLLOWUP_AND_GATE_UPDATE_2026-10-29.mdとNEE_EXTERNAL_RAW_AUDIT_2026-10-29.mdを参照。投稿前には完全なデータ・SDM方法、書誌、著者情報、公開パッケージ、独立検証を完成させる必要がある。
