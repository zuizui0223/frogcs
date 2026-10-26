# NAAMP地域の候補種プールを独立資料で監査する

2026-10-26。対象座標外接範囲は緯度25.746–49.345、経度−99.001–−67.465（親解析指定）。18種pilotも、最初の近傍由来205種も、地域の全候補種を確認したリストではない。GBIF広域検索へ拡張し、独立チェックリストとの名前・範囲差分を残す。以下の全国／北米数はこの外接範囲の種数ではない。

## 実際に取得・抽出した資料

[checklist_candidates.csv](results/regional_species_pool_20261026/checklist_candidates.csv)に759項目を保存した。列は`source, scientific_name, range_text, scope`。原資料とSHA256は同ディレクトリの[manifest](results/regional_species_pool_20261026/checklist_extraction_manifest.json)。これは候補照合の土台であり、全項目がNAAMP地域に分布すると認定した表ではない。

| 出典 | 地理・分類時点 | 抽出状況と用途 |
|---|---|---|
| [DSA Paulson・Dunkle 2024チェックリスト](https://www.odonatacentral.org/public/media/uploads/files/NA_Odonata_Checklist_2024.pdf) | Canada＋continental US、2023年までの記録、2024版 | 原PDF94ページ取得。471個の`Range:`と471重複なし項目を照合して抽出。学名と原文分布を保存。未記載の`Orthemis sp.`も1項目として保持するため、471すべてがaccepted binomialではない |
| [USGS ARMI National Amphibian Atlas](https://armi.usgs.gov/atlas/) | 全米county分布、ページは最終主要更新2021と記載 | サイトの公開JSONからAnura106、Caudata182、合計288項目取得。**全国種一覧のみ取得、分布抽出は未完了**なのでCSVのrange_textは空欄。最新分類の全米完全目録とは断定しない |

DSAの学名はPDF抽出が`T elebasis`等と分離した先頭Tを修正した。range_textはPDF抽出の改行・`T exas`等の字間を保持しているため、厳密な州名検索前に正規化が必要。項目数一致は内容監査の一部であり、PDFの分布記述を座標ポリゴンへ変換したわけではない。少なくとも全471項目に非空の分布欄があることを確認した。

ARMIの実取得URLは `https://armi.usgs.gov/scripts/select2.php?ddl=species`。公開HTMLとJSから、州選択には`&statecode=`、county選択には`&countyfp=`を加える仕組みを確認した。rawJSONにはITIS IDと元表示文字列が残っている。各種境界の公開参照先は `https://armi.usgs.gov/uploads/data/geojson/{itis}.json`。境界全件は今回未取得。Excel出力の参照先は `/phpspreadsheet/export.php?statecode=...`（JSから確認、Excel本体未取得）。APIの無認証取得は成功した。web読取ツールでは403があったが通常HTTPでは成功しており、恒常的可用性までは保証しない。

## 分類・導入種・範囲の追加照合元

- **SSAR第9版2025**：[学会案内](https://ssarherps.org/publications/north-american-checklist/)、[原PDF](https://ssarherps.org/wp-content/uploads/2025/03/9th-Edition-Scientific-and-Standard-English-Names-of-Amphibians-and-Reptiles.pdf)。US／Canadaの学名整合に使用できる。導入種章は原産域・導入先・定着情報を拡充。2025-03-31公開でオンライン更新も予定されているため、版・取得日・名称変更根拠を記録する。今回のARMI 2021基準と差がありうる。未抽出。
- **USGS GAP CONUS_2001**：[説明](https://www.usgs.gov/programs/gap-analysis-project/science/species-data-overview)、[ダウンロード](https://www.usgs.gov/programs/gap-analysis-project/science/species-data-download)。両生類を含む脊椎動物の範囲と予測生息域。範囲はHUC12に属性を付けた粗いベクトル、予測地図は2001土地被覆基準。地域交差の補助になるが新分類や新規分布を網羅する最新目録ではない。Odonataを含まない。機械読取可能な範囲データは配布されるが今回未取得。予測生息域を独立した現地確認とは扱わない。
- **DSAの更新HTML**：[University of Puget Sound掲載リスト](https://www.pugetsound.edu/puget-sound-museum-natural-history/biodiversity-resources/insects/dragonflies/world-odonata-list/north-american-odonata)。2025-02-18更新。HTMLから名前抽出可能で2024版との差分確認に使える。詳細分布は2024 PDFで補完。今回未抽出。
- **Odonata Central**：[公式サイト](https://www.odonatacentral.org/)。Western Hemisphereの観察と地域リスト。iNaturalistも含むためGBIFと独立した全記録ではない。トップページは表計算download可と述べる一方、[FAQ](https://www.odonatacentral.org/FAQ/)は未提供とするため、bulk APIを利用可能と断定しない。課金・登録・問い合わせはしていない。

DSA2024は導入された`Crocothemis servilia`を明記する。ARMI rawJSONにも一部の表示名に`*`があるが、その記号だけから機械的に導入状態を決めず、SSAR等の根拠と照合する。直接発生／池幼生／流水幼生は分類目録の機能ではないため、種別の生活史列として別に付ける。直接発生種も地域分布SDMの候補からは除かず、池幼生機構の集計から分ける。

## 完全性監査の判定単位

1. 広域GBIF種リストと独立目録の和集合を出発点にする。原表名→accepted名→GBIF keyの対応を保存し、synonymや分類分割を落とさない。
2. 各項目に「範囲交差／外側／不明」「GBIF記録あり／なし」「学名対応成功／要確認」「SDM推定可能／不足」の別々の判定を付ける。GBIFなし・標本不足は地域不在とは違う。
3. ARMI county境界やGAP範囲をNAAMP外接域と交差し、境界近くは粗い地図誤差を考えて候補として残す。北部Canada側はUS資料だけでは完結せずDSAや別のCanadian資料が必要。Odonata原文の曖昧な範囲は未判定のまま残す。
4. 既存18種、205種、新GBIF地域プール、独立目録に由来する追加候補の各段階を別集計する。「全部精査」は未対応名・範囲不明・独立目録未照合を隠した状態では使わない。

本作業で完成したのは、原資料付き候補表と取得可能性の確認。GBIFとの最終差分、全種の対象域交差、分類更新、生活史の全件注釈は親解析と後続監査に残る。

## 追記：指定東部州のARMI unionを取得

[armi_eastern_state_union_candidates.csv](results/regional_species_pool_20261026/armi_eastern_state_union_candidates.csv)に**203項目（Anura72、Caudata131）**を保存した。AL AR CT DE FL GA IA IL IN KS KY LA MA MD ME MI MN MO MS NC ND NE NH NJ NY OH OK PA RI SC SD TN TX VA VT WI WVの37州を対象に、州ごとのAPI応答を全件保存しITIS IDでunionした。取得失敗0件。指定されたDCは実HTMLの州選択肢に存在せず、推測呼出しせず未取得とした。

州コードは保存した`armi_atlas.html`の`ddlStates`から確認した2文字値。各応答は`select2.php?ddl=species&statecode=AL`等。例としてAL73項目、ME18、NC90で、全米リストがそのまま返る挙動ではないことも確認した。州名対応、全37応答、件数・hashは[州union manifest](results/regional_species_pool_20261026/armi_state_union_manifest.json)に記録。

このリストは保守的な箱（−101..−65、24..50）にかかる指定州**全域**を含み、箱内への種別交差は未確認。西Texas等の箱外の分布種を含み得る。またCanada側は含めていない。`range_text`は原資料の文章ではなく、APIで確認できた対象州を列記した派生記述と明記した。原表示名は`source_display_name`、州別記録は`states`に保存し、旧分類・亜種・導入表示の照合に利用できる。
