# NAAMP・GBIF・GloBIの接続監査

後続更新：この入口監査の後、段階非必須の三群GloBI取得、NAAMP適格48種の受容key照合、実際の近傍年月記録への重ね合わせを実行した。最新の到達点は[統合パターン報告](NAAMP_THREE_GUILD_PATTERN_REPORT_2026-10-26.md)を参照。以下の「既存接続なし」は追加作業前の監査を指す。

2026-10-26。結論：**NAAMP録音地点のGBIF近傍取得と、別解析の全球GloBI×GBIF接続は実行できている。ただしNAAMP全体の種・地点・調査日・相互作用を結んだ統合表は完成していない。** 今回、当初の限定検証対象4種についてGBIFの分類学的対応を新たに確認し、GloBIの限定的な種ペア照会も行った。その後のユーザー指示は、カエル同士からカエル・有尾類・トンボの同じ水生発生段階へ重点を移したため、4種照会は補助的な接続監査として残す。

## 水生発生段階のguild間接続を直接点検

版固定GloBI解析の[Actions artifact 40193636562](https://github.com/zuizui0223/frogcs/actions/runs/40193636562)（73KB）から `full_nonself_staged_GloBI_provenance.csv` の1,240行を取得し、[照合結果](results/naamp_pair_connection/staged_global_exact_name_audit.json)に元CSVのSHA256、対象名、原典を保存した。元の68NAAMPラベルとの**完全名一致のみ**では167原典行・18NAAMP種が該当した。

そのうちAnura↔Caudata/Odonataの関係は `Lithobates pipiens → Libellula luctuosa` の juvenile→adult が1行だけで、**両側aquatic_immatureの完全名一致は0行**だった。全1,240行のなかで、このguild組合せ・両側aquatic_immatureは8行、6有向種ペア：`Taricha torosa` または `Anax junius` と、`Anaxyrus boreas`、`Pseudacris regilla`、`Amerana draytonii` の組合せ。6行はCalifornia pondの解釈済みmetaweb区分、2行はcitation欄が空のOTHER_INDEXED_ASSOCIATIONで、独立した8捕食観測ではない。これはNAAMPの元ラベルと直接一致しない。同物異名は追加していないため、全分類学的一致の不存在ではなく、確認できた完全名一致の範囲である。

**局所48地点のGBIF結果からこれらの種×段階edgeに結合した件数は、現在の保存集計では計算不能。** 近傍検索コードは元の `speciesKey`、`occurrenceID`、地点別の種名・年/月を最終artifactに残しておらず、保存されたのは目別集計である。0件という結果ではない。一方、その既定条件では無尾類・トンボ類の明示水生段階記録がともに0、有尾類のみ1行なので、同じ近傍・時期の段階付き三者比較が成立したという主張はできない。

次の接続には、種キー・原名・段階原値・日付・記録出典・不確実性・固定NAAMP地点トークンを保つ小規模再取得表が必要。対象種を独立した水生段階の原典から固定し、同じ地点近傍×年×月に両者の報告があるかを監査する。目の合計件数を相手種の競争強度にせず、段階不明・別名不明・未記録はそれぞれ分ける。照合できても同じ池での接触を示すものではない。

## 接続を区別する

| 層 | 検証済みの内容 | 残る制限 |
|---|---|---|
| NAAMP → GBIF近傍 | 元座標SHA固定、24ルート48地点、2010–2015年・5km、Anura/Caudata/Odonata＋背景192問い合わせ全成功 | 目・分類群レベルの記録可用性監査。NAAMPの各種×調査日への結合ではない |
| NAAMP → NWI | 同じ48地点すべて取得成功 | 録音地点は繁殖池の位置ではない。実測の水位・植生ではない |
| 全球GloBI → GBIF | 版固定GloBIの食物関係と、選択されたGBIFの種×段階×1°格子×年×月の接続成果物あり | NAAMP SiteID/RunIDを使わない。鳴き声競争ではなく、主にeats/preysOn |
| NAAMP全種 → GBIF → GloBI | 既存成果物では全種crosswalkを確認できない。今回4種を限定検証 | 同物異名・複合種コード・相互作用の段階と原典を別途管理する必要 |
| NAAMP地点×日 → GloBI相互作用 | 未確立 | 同じ池・時期で相互作用が起きた証拠はない |

## 既存成果物を実読した根拠

- [GBIF取得修復JSON](results/naamp_gbif_retrieval_repair/observed_results.json)：GBIF192/192、NWI48/48成功。無尾類の精密記録があるのは6/48近傍、有尾類2/48、トンボ類8/48。生活史段階を必須にしない監査でも記録は疎ら。
- [近傍検索コード](scripts/naamp_gbif_wetland_geo_g0.py)：検索taxonKeyはAnura=952、Caudata=953、Odonata=789。NAAMP種別CallingIndexは読み込まず、全NAAMP種のGBIF species key対応表も作っていない。
- [種オカレンスprofile](results/species_occurrence_first/observed_profile.json)：NAAMPの元ラベル68種類。うち11は `NAAMP_CODE:` の複合種ラベル、57は抽出された二名法。未検証の同物異名変換をしないことを明示。GBIF1°記録は地点表に混ぜていない。
- [版固定GloBI全体](results/globi_fixed_full_foodweb/observed_results.json)：元24,453,954行、選択食物関係77,720行、28,958有向種ペア。これはNAAMPに合致したペア数ではない。
- [段階付き全球接続](results/full_globi_2026_stage_gbif_grid/observed_results.json)：881有向種×段階パターンのうち当該初期GBIF走査の両側が揃った18、同1°×年×月が17。後続の[拡張・対照比較](results/expanded_stage_specificity/observed_results.json)では258分類群のGBIF guild確認、77適格GloBIパターン、56対照比較。後者もNAAMP接続数ではない。
- [公式SQLマニフェスト](results/global_globi_gbif/gbif_bulk_cube/manifest.json)：SQL構文はHTTP201で検証済みだが、公式ダウンロードは `NOT_SUBMITTED`。実験的匿名Parquetを用いた全球解析の成功と混同しない。

## 今回の4種の分類学的接続

[小規模照会スクリプト](scripts/naamp_pair_connection.py)と[結果・生JSON](results/naamp_pair_connection/observed_results.json)。2026-10-26のGBIF live match、Animalia/Amphibiaを指定し、EXACTかつSPECIES、ACCEPTEDまたはaccepted key付きSYNONYMのみを許可した。8名称はすべてconfidence100で、各種の別名は同じaccepted keyに一致した。

| NAAMPラベル | GBIF受容種key | 確認した別名 |
|---|---:|---|
| Lithobates clamitans | 2427172 | Rana clamitans（SYNONYM） |
| Lithobates catesbeianus | 2427091 | Rana catesbeiana（SYNONYM） |
| Hyla chrysoscelis | 10863553 | Dryophytes chrysoscelis（受容名。HylaはSYNONYM） |
| Hyla versicolor | 10806364 | Dryophytes versicolor（受容名。HylaはSYNONYM） |

これは4種の同一性の橋渡しであり、特定地点での共存や相互作用の確認ではない。NAAMPの `Hyla chrysoscelis/versicolor complex` を2種のどちらかへ割り当ててはいけない。

## GloBI照会の意味

上記2ペアを両方向・各2名称の全組合せ（16照会、各先頭最大1,000行、種ペアに対するinteractionTypeの限定なし）で問い合わせた。今回すべて正常応答したが、返された行は0だった。ウシガエルのeatsを対象にした別の少量の動作確認では既存記録が返るため、API全体が空という状況ではない。ただし**この16照会の空応答は、自然界に競争・捕食・相互作用が存在しない証拠ではない**。

GloBIの少量動作確認には `Aquarana catesbeiana` という別表記も現れた。追加のGBIF名照会では `Aquarana catesbeiana` と `Aquarana clamitans` はどちらもGENUSへのHIGHERRANK一致にとどまり、種レベルの同一性をこのAPIで確認できなかった。そのため強制結合せず、別の生JSONとして残した。これはGloBI側の分類体系・別名対応が今回の8名称だけで完全とはいえない具体例である。

最初のローカルGloBI問い合わせはHTTP403だったが、既存スクリプトと同じUser-Agent・既知の6フィールドを使った再照会は成功した。原因を断定しない。成功した16照会は現在の結果として保存した。

GloBIは探索用APIと研究用の版固定データを区別し、原データへの帰属を求めている（[公式データ説明](https://www.globalbioticinteractions.org/data.html)、[公式API](https://github.com/globalbioticinteractions/globalbioticinteractions/wiki/API)）。今回の結果はlive探索記録であり、元論文を確認した競争実験の証拠リストではない。主解析のペア選定は独立した繁殖・音声の一次資料に基づけ、GloBIが空だから除外する選択はしない。

## 実際の競争検証で使う接続

NAAMP内の元種名・SiteID・調査時刻と環境条件が主たる比較単位。GBIF受容keyは名称の整合に使える。GloBIは候補相互作用の原典探索に使えるが、近傍GBIF件数を競争強度にしたり、GloBIの食物関係を成体の音声競争へ転用したりしない。接続の成功と因果の識別を別の判定にする。
