# NAAMP同地点への水域持続性資料の結合可能性

**実装済み更新（同日）**：このノートで確認した年次GLAD経路を、72タイル年・6,293地点年・固定4,040ペアで実行した。前年のみを用い、1/3 kmの周辺水面頻度と面積割合を分離。詳細は `PRIOR_WATER_NETWORK_REPORT_2026-10-26.md`。以下は実装前の経路調査記録であり、最新の実行状況ではない。

2026-10-26。強い鳴き声対無声の固定比較に、相対的環境ニッチ・植生・過去利用と同時に加える水域指標の調査。コード変更なし。資料説明と公開HTTP／rasterioによる小範囲読取を確認した。11,947地点、4,040組・389ルートという対象規模は親解析の指定であり、本ノートで再集計した値ではない。

## 推奨

**無認証で直ちに利用可能なのはUMD GLADの年次water percent。前年値または前年までの固定期間平均を主指標にできる。旧版の個別月次も実読取できるため、前月・過去繁殖季の季節性を別感度解析にできる。** JRCの2021 seasonalityを2001–2015の同時期hydroperiodとして使う必要はない。NWIは分類と植生の別軸として有用だが画像年を必ず結合する。

名称は「周辺の衛星開水面持続性／検出頻度」とする。調査点は聴取位置であり繁殖池中央とは限らない。画素の開水面、池の実際の連続湛水日数、植生下の水位、幼生が変態まで利用できる期間は異なる。発育段階・捕食記録がなくても環境比較は成立する。

## 1. GLAD：実装に最も近い経路

一次資料：[UMD研究室のデータ説明](https://glad.umd.edu/dataset/global-surface-water-dynamics/)、[更新版公式download](https://storage.googleapis.com/earthenginepartners-hansen/waterC2/download.html)、[Pickens et al. 2020原著](https://doi.org/10.1016/j.rse.2020.111792)。研究室は個別月次を含む配布と255欠測を明記。更新版はLandsat Collection 2を使う暫定v2.0で1999–2025、10度タイル、約30 m。water percentはwater／landとして分類された観測を分母にする。実湛水日数とは呼ばない。

| 系列 | 確認した実URL | 時間上の使い方 |
|---|---|---|
| 更新版年次 | `https://storage.googleapis.com/earthenginepartners-hansen/waterC2/40N_080W/2001_percent.tif` | 年yの訪問にはy−1年またはそれ以前。年y全体は訪問後を含むため同年記述的感度解析に限る |
| 旧版個別月次 | `https://storage.googleapis.com/earthenginepartners-hansen/water/individualMonthMaps/40N_080W/2001_01_percent.tif` | 調査月より前の完了月、または前年の同季節。調査月全体には訪問後が含まれる |
| 更新版長期月平均 | downloadページの`01_Jan_mean_99_25`等 | 1999–2025を混ぜるのでstrict prior主解析に使わない |

2001年の旧版12月分の実在を公開bucket一覧で確認した。月次の全対象年・タイルの欠落は取得manifestで別に点検する。月次旧版と年次Collection 2を一つの連続系列として混ぜず、版別の比較とする。

**読取確認（2026-10-26）**：年次例はHTTP HEAD成功、30,113,354 bytes、ETag `93f072ca41ed8e496652d98cfda70451`、Last-Modified 2024-11-13、Accept-Ranges bytes。rasterio遠隔小窓読取成功。年次・月次ともEPSG:4326、40000×40000、0.00025度、uint8、LZW。左上は経度−80・緯度40。行単位strip `(1,40000)`で**COGではない**。年次nodataタグ255、月次nodataタグなし（読取例は255）なので月次も明示的に255を欠測にする。0を欠測扱いしない。0–100以外の値を品質検査で集計し、未知コードを自動的に水へ変換しない。

公開一覧APIの確認例：
`https://storage.googleapis.com/storage/v1/b/earthenginepartners-hansen/o?prefix=water%2FindividualMonthMaps%2F40N_080W%2F2001&maxResults=20`

URLはタイル左上の緯度・経度から組み立てる（北緯上端10度刻み、経度西端10度刻み）。ルートをタイル×年でまとめて読み、必要窓だけを抽出してキャッシュする。strip型なので多数点のランダム遠隔読取は同じ行を繰り返す；対象が広ければ該当タイル年を一度保存して利用する。全世界取得は不要。元ファイルのURL、取得日、ETag／hash、版、画素窓、欠測率を保存する。

## 2. JRC：歴史系列はあるが経路を区別

[公式配布](https://global-surface-water.appspot.com/download)は、2026-10-15更新でv1.5を案内している。長期集計は1984–2024だが新しい直接配布Monthly Historyは2022–2024で、NAAMP期間へ転用できない。旧v1.4のMonthlyHistoryは1984年3月–2021年12月、30 m、`water=0`欠測、1非水、2水、`year`／`month`属性。[Google公式カタログ](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory)

GEE asset `JRC/GSW1_4/MonthlyHistory`は履歴抽出に適するがGEE登録・認証が必要。公開ダウンロード用APIだと誤記しない。公式は2016–2021 seasonality修正と月別recurrenceの既知問題も告知しているため、版と期間の固定が必要。[新しい配布スクリプト説明](https://global-surface-water.appspot.com/gsw/Download_Instructions.html)

無認証の代替候補として次のImageServerのJSON metadata応答は確認できた：
`https://di-jrcglobaldata.img.arcgis.com/arcgis/rest/services/GSW_Yearly_History_TimeEnabled/ImageServer`

説明上1984–2021年次分類、`AcquisitionDate`、Image／Metadata／Catalog機能、最大画像5000×5000。**実画素の年指定抽出と提供主体・版対応は未確認**なので、現時点でGLAD実読取と同等の実装確度にしない。旧公式FTP入口は開けたが歴史月次の具体ファイル経路は今回確定できなかった。

## 3. NWI：植生と水文分類を同時に持つ静的背景

[FWS公式REST案内](https://www.fws.gov/program/national-wetlands-inventory/web-mapping-services)にある次のサービスは無認証JSON metadata取得成功。

- 湿地ポリゴン：`https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0`
- 画像年：`https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Data_Source/MapServer/3`

前者は`OBJECTID, ATTRIBUTE, WETLAND_TYPE, QAQC_CODE, ACRES`。後者は`IMAGE_YR, IMAGE_DATE, PROJECT_NAME, SOURCE_TYPE, FGDC_METADATA`等。それぞれ最大500／2000件でpagination対応。`/query`で固定近傍ポリゴンと交差する対象を取得し、geometry付きで等積投影の交差面積を計算する。サービス側のWeb Mercator `Shape_Area`をそのまま比較面積にしない。件数上限・重複・境界跨ぎを検査する。

`ATTRIBUTE`のCowardin分類からPEM等の植生型と水位regimeを別に抽出する。[FWS分類図](https://www.fws.gov/sites/default/files/documents/wetlands-and-deepwater-map-code-diagram.pdf)ではA=temporarily flooded、C=seasonally flooded、F=semipermanently flooded、G=intermittently exposed、H=permanently flooded。全末尾文字をregimeとみなさず、人工改変等のspecial modifierも含む正式コードを解読する。植物被度・茎密度や実際の乾燥日を直接測る資料ではない。

[FWS FAQ](https://www.fws.gov/page/national-wetlands-inventory-frequently-asked-questions)によると地図の時間的根拠は解釈に使った画像であり、現在の配布年ではない。`IMAGE_YR < visit_year`の部分はpriorに整合する背景として感度解析可能だが、古い地図が当時も不変だった保証はない。訪問後／年不明の地図は将来情報を含む背景比較へ分離する。履歴完全版の全国年次パネルとは呼ばない。

## 固定比較への組込み案

1. 既存のmatched pairを変えず、両側の元座標から同一半径の近傍を作る。聴取点一点の0水判定より、近傍の開水面割合・持続性を使う。半径は結果を見る前に固定し、別半径は感度解析と明示。
2. 主指標は前年年次GLADの近傍平均water percent。これは水域面積と持続性を混合するため、可能なら水検出画素割合と水のある画素での平均頻度を別に出す。後者の画素選択も前年以前だけで固定し、将来のmaximum extentを使わない。
3. 同じ年に比較するペアでもstrict priorの自種利用履歴は別変数にする。植生・持続性・他群への環境近さを一緒に扱うが、他群の近さを捕食圧と呼ばない。
4. 欠測を0水にせず、両側有効なペア数・ルート数を報告。追加指標ありの共通標本上で基準モデルも再評価し、対象減少による改善と区別する。
5. 月次・NWIを追加できなくても年次環境比較を止めない。確認できるのは繁殖活動の環境配置であり、捕食や繁殖成功を要求しない。因果説明には未測定の池構造・検出・履歴選択を残す。

**結論**：GLADは2001–2015の調査期間に対応する無認証・実読取済みの選択肢。NWIは植生と持続性分類を補うが画像年に依存する。これらを使うことで、2021年や2025年までの全期間背景を過去の水文条件として扱うことを避けられる。
