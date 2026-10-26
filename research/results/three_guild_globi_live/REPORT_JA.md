# 三guildのGloBI照会：段階を入口条件にしない接続候補

2026-10-26。Anura↔Caudata、Anura↔Odonata、Caudata↔Odonataの6方向について、GloBI live APIを全interactionType・生活史段階非必須で照会した。各方向は最大10ページ×1,000行までとし、今回はすべてページ終端まで取得した。原照会URL・時刻・応答SHA256・生JSONは `raw/`、[集計](observed_results.json)、[再実行スクリプト](../../scripts/three_guild_globi_live.py)を保存した。総量は約4.4MB。

| 照会方向 | 返却行 | ページ | 正しいguildかつ二名法形式の種名・関係edge |
|---|---:|---:|---:|
| Anura → Caudata | 1,072 | 2 | 638 |
| Caudata → Anura | 1,072 | 2 | 638 |
| Anura → Odonata | 77 | 1 | 16 |
| Odonata → Anura | 77 | 1 | 16 |
| Caudata → Odonata | 61 | 1 | 5 |
| Odonata → Caudata | 61 | 1 | 5 |

計2,420返却行。うち両taxon_pathに指定guildが完全tokenとして入り、双方が二名法形式である1,994行から、1,318の「名前×名前×返却関係」edgeを得た。これは受容種keyの同定が済んだという意味ではない。種名の異名はまだ統一していない。

両方向照会では、例えばA eats BとB eatenByが同じ関係を表す。これを別の相互作用や相互捕食と数えないように、逆関係を正方向に直し、対称関係を一度だけ数えた [direction_normalized_species_edges.csv](direction_normalized_species_edges.csv) は**659 edge**。元の向き・関係・原典への追跡は [species_edges.csv](species_edges.csv) と生JSONに残した。eatsとpreysOnは別ラベルを維持しており、659は独立した生物学的関係数や観測数ではない。

生活史段階・citationが欠けても取得や候補edgeの入口で除外しなかった。返却行のうち両段階欄が非空なのは164、両方空は1,984、citation空は54。ただし非空の段階文字列もまだ厳密な生活史分類へ解釈していない。段階・原典品質は、種オカレンスとの接続後に評価する補助情報である。

## 検証と制限

- 取得上限、失敗、ページ反復、ページ終端を各方向のreceiptへ明記。今回は上限到達・失敗・ページ反復なし。ページ終端はlive APIの照会終端であり、生物学的な網羅性ではない。
- APIのguild検索だけを信用せず、返却taxon_pathを検証した。Anura→Caudata照会には真菌 `Batrachochytrium dendrobatidis` のhost関係も混ざっていたため、Caudata種との関係として採用していない。
- 240行はsourceまたはtarget guildを完全tokenで確認できず、186行は双方の二名法形式を満たさなかった。すべて[normalized_source_rows.csv](normalized_source_rows.csv)と生JSONに保持した。例えば `Anuri` という別体系の表記は未解決として残しており、この厳格なguild照合にも取りこぼしはあり得る。
- 返却されたrelationはeats/eatenBy、preysOn/preyedUponBy、interactsWith、coOccursWith、ecologicallyRelatedTo、hostOf/hasHost。競争に限定したデータではない。coOccursWithを捕食edgeへ変換しない。
- 原典citation文字列の重複・異なるtaxonomyの表記・同じ情報の逆向き返却がある。行数を独立観測や相互作用頻度としない。
- このlive照会はNAAMP地点・日付へまだ接続していない。取得したGBIFの元種名・受容keyとのcrosswalkを検証し、その後に同じ近傍と時期の**報告の重なり**を評価する。GloBIにedgeがないことは相互作用不在の証拠ではない。
- [GloBI公式](https://www.globalbioticinteractions.org/data.html)は研究用途に版固定データや原データの利用を案内している。今回のAPI結果は探索的な接続監査であり、既存の版固定解析を置換しない。

## GBIF受容種keyへの追加crosswalk

後続の[分類照合スクリプト](../../scripts/three_guild_taxon_crosswalk.py)で、659 edgeのunique109名称（Anura63、Caudata38、Odonata8）をGBIFへ照会した。[taxon_crosswalk.json](taxon_crosswalk.json)、`taxonomy/` に生JSON・URL・時刻・応答hashを保存した。0.4秒の待機、成功応答cache、EXACTかつSPECIES、指定order/class一致のみを許可し、SYNONYMの場合は受容keyのspecies endpointも検証した。

**107/109名称を107受容種keyへ接続した。** `Rana sylvatica` は `Lithobates sylvaticus`（受容名）へ一致。`Amerana draytonii` と `Pelophylax grafi` はHIGHERRANKしか返らず、強制対応せず未解決とした。全110HTTP照会は成功した。通信失敗を同定不能と混ぜていない。

659方向正規化edgeのうち両端を受容keyへ接続できるのは645、残る14は上記未解決名を含む（Amerana4、Pelophylax10）。これは名称の同一性が確認できたという意味であり、NAAMP近傍のGBIF報告や実際の局所相互作用との一致件数ではない。edge CSVの原名は保存し、別crosswalkを用いることで出典へ追跡できる。

GloBI取得の6単体テスト合格：段階・citation欠損の保持、guild部分文字列の拒否、種より上位の名前の除外、向き確認、逆関係と対称関係の重複整理。分類照合の4テストも合格：exact synonym、fuzzy拒否、guild不一致拒否、受容endpointの種階級確認。

### 実際のNAAMP発声種名にも同じ分類照合を適用

後続の `full_naamp_history/naamp_completed_site_surveys.csv.gz` の `source_taxa` をすべて読み、57の異なる元ラベルを得た。二名法48種はすべて同じ厳格条件でGBIF受容種keyへ一致した。残る9の複合種ラベルは明示的に除外し、いずれかの種へ配分していない。この57は今回使う完了調査表のラベル数であり、NAAMP公開資料全体の68ラベルと混同しない。

[naamp_taxon_crosswalk.json](naamp_taxon_crosswalk.json)の `names[].naamp_name`（共通欄 `source_name`）から `accepted_key` が接続キー。`taxonomy_naamp/` に照会と受容名確認を保持し、入力gzipのSHA256も記録した。GloBI原名や受容名にNAAMP表記が含まれる場合だけを拾う方法から、実際のNAAMP側の全二名法名を検証する方法へ補完した。HylaからDryophytes等の別名を未照合扱いのままにしない。これは分類学的な名称接続の補完であり、局所相互作用の発生確認ではない。

```text
python research/scripts/test_three_guild_globi_live.py
python research/scripts/three_guild_globi_live.py --out research/results/three_guild_globi_live
python research/scripts/test_three_guild_taxon_crosswalk.py
python research/scripts/three_guild_taxon_crosswalk.py --edges research/results/three_guild_globi_live/species_edges.csv --out research/results/three_guild_globi_live
```
