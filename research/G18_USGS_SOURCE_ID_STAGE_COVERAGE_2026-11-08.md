# G18：USGS独立原本の同一サンプル対応監査（応答値を開く前に確認）

**日付：2026-11-08（JST）。** Glorioso & Waddle（2025）、USGS DOI [10.5066/P9T71JCO](https://doi.org/10.5066/P9T71JCO)、CC0。G18の初回原本取得・SHA256・全7 CSVヘッダー監査は [GitHub Actions #42440852240](https://github.com/zuizui0223/frogcs/actions/runs/42440852240) で **SUCCESS**。この段階では発声や幼生の種ごとの検出数・個体数をまだ読んでいない。

## 元ファイルの結合鍵と支持

| 元ファイル | 元CSVレコード数（ヘッダー除外） | `Sample ID`の異なる値 | 元Sample_DataにないSample ID |
|---|---:|---:|---:|
| `Sample_Data.csv`（Site, Date, Sample ID） | **2,221** | 2,221 | 適用外 |
| `Vocalizations.csv`（各種の`_In` / `_Out`） | **2,222** | 2,222 | 1 |
| `Tadpoles_Larvae.csv`（種ごとの記録） | **1,055** | 1,055 | 1 |
| `Observations.csv`（目視観察） | **17,364** | 2,088 | 1 |

両ファイルのSample ID集合の共通部分は1,054 ID。そのすべてが元`Sample_Data.csv`の地点・日付に結合でき、**64地点・2012–2016年・230地点×年**を構成する。元`Sample_Data.csv`全体は70地点・2008–2016年の478地点×年。前期2008–2011年には、後期と同じ同一Sample ID発声×幼生の一致データがない。

**結合はSample IDの完全一致で行う。** 異なる`Sample ID`は座標・日付の近さから補完せず、3ファイルにまたがる孤立IDは監査してのみ除外する。元の地理的な野外発声NAAMPサンプルはこのUSGSソースへ合流・上書きしない。

## 同一種として照合できる元列名（応答値は未読）

発声元列は14種について`Species_In`と`Species_Out`のペア。幼生元列は19分類項目。前後空白を除く**完全一致の13種**：

`Acris blanchardi`, `Anaxyrus fowleri`, `Gastrophryne carolinensis`, `Hyla chrysoscelis`, `Hyla cinerea`, `Hyla squirella`, `Incilius nebulifer`, `Lithobates catesbeianus`, `Lithobates clamitans`, `Lithobates grylio`, `Lithobates sphenocephalus`, `Pseudacris crucifer`, `Pseudacris fouquettei`。

未同定`Hyla species`、`Lithobates species`、`Pseudacris species`、`Unknown species`や、複合`Anaxyrus fowleri/Incilius nebulifer`を都合よく13種へ振り分けない。幼生にのみある`Ambystoma opacum`は発声するカエルと同じ種ではないので、**カエル成体発声と有尾類幼生の同種生残**と誤認しない。

## まだ判定できないこと

1. 幼生表の0／空欄が**標準的な調査機会における非検出**か、未調査かの区別。幼生表の外の1,167件を「幼生0」にしてはいけない。
2. `Vocalizations.csv`の`_In`／`_Out`の調査範囲、記録値の意味、および非検出と欠損の符号。
3. 同一種で両ステージが報告される件数、各種の陽性・陰性支持、地点ごとの観測偏り。
4. 同じ年に**厳密に先行する発声調査と後の幼生調査**が存在するか（同一Sample IDは同時期の対応であり、将来予測ではない）。

この元データの鍵の適合は、実際の捕食者密度、幼生生残確率、4方向野外相関の再現や野外食物網機構の同定を支持するものではない。USGSの公式FGDC XMLコードブックを取得し、次の応答値読取り前の [G18プロトコル](G18_USGS_ATCHAFALAYA_STAGE_OBSERVATION_PREFLIGHT_PROTOCOL_2026-11-08.md) に従って非検出の扱いを確定する。
