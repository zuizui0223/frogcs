> 最新更新：[2026-10-29追加検証とゲート判定](NEE_FOLLOWUP_AND_GATE_UPDATE_2026-10-29.md)、[統合作業稿](working_20261029/MANUSCRIPT_JA.md)。以下の方針・履歴を保持し、到達点は最新更新で判断する。

# NEE向けストーリーの更新 — 結果を先に、機構の制約を後に

研究方針はHIGH_IMPACT_SUBMISSION_GATES_2026-10-27.md、今回の実証進捗は[NEE追加検証](NEE_EVIDENCE_PROGRESS_2026-10-29.md)に従う。これは投稿原稿の完成や新しい一般原理の確立を宣言する文書ではない。

## 論文の中心

問いは「三者の捕食をどう説明するか」だけでなく、「繁殖活動と捕食者群の環境適合度の関連が、どの空間スケール・環境条件で残るか」である。鳴き声の集中から始める一つの論文とし、シミュレーションを別論文に切り離さない。

全国的なトンボ類×有尾類、トンボ類×植生の負の関連はuniform背景では環境・調査・地理を調整しても残る。この点を主結果として示す。同時に、背景を変えた結果、ルート内での精度、有尾類×植生・三者項の不安定さを同じ図で示し、強い一例だけを選ばない。

## 暫定的な結果要約（原稿用）

We examined whether associations between frog calling activity and modeled predator-guild suitability persist across observational and environmental contexts. Across 4,248 listening sites, negative odonate-by-caudate and odonate-by-vegetation terms persisted after survey, climate, wetland-context and geographic adjustment under a uniform-background suitability model. Their precision and magnitude depended on background construction and spatial comparison. The caudate-by-vegetation association and the positive three-way term were not stable across the expanded controls and spatial resampling. These results constrain, rather than identify, the trophic interpretation of broad-scale associations. Stage-structured simulations demonstrate conditional mechanisms, but an uncalibrated observation-to-process map and the absence of an independent three-guild test prevent a field-mechanism claim.

この段落はNEE掲載水準の新規性を宣言するabstractではなく、現在書ける結果の上限である。

## 四図の構成と到達状況

| 図 | 内容 | 根拠・到達状況 |
|---|---|---|
| 1 | 4,248地点の全国・ルート内・ルート間の係数を、両背景で並べる。未調整→調査→環境→地理の変化を示す。 | 今回のcoefficients.csvで作図可能。元の関連と調整後を区別する。 |
| 2 | 地理区分の情報量、地域別・地域除外の全係数、56空間ブロックの区間、残差空間診断。 | 今回の新規出力で作図可能。NWの支持不足を表示し、有効な検証として数えない。 |
| 3 | 幼生の過程から成体・発声までの経路と観測対応。旧モデルの成功・失敗を併記。 | 概念図と旧結果のみ利用可能。校正済みの観測空間でのモデル比較はUNACHIEVED。 |
| 4 | 同じ水域・段階で、密度を揃えた対照により植生・有尾類の機構を識別する。 | 独立実証はUNACHIEVED。追加シミュレーションで穴埋めしない。 |

## モデルをどう考察に残すか

モデルは、植生保護や他の捕食者の除去による利益と、密度依存的な危険の増大が差し引かれる例を与える。しかし「広域でその機構が働いた」とは書かない。1/24の一致、正の三者項の不一致、合成密度尺度の未校正を一緒に扱う。今回三者項が不安定となったことを利用して、旧モデルを後付けで実証的に支持されたモデルへ格上げしない。

一般原理候補を強くするには、植生の種類・構造と相対サイズを固定したとき、第三者の効果が変わる密度境界を実測し、別の未使用データで当てる必要がある。II型／III型の式や第三者を足すこと自体は既知であり、新規性ではない。

## 次の実行順

1. 原データを取得できる独立水域資料で、種・段階・同一水域と季節キー・植生構造の有無を確認する。メタデータだけで解析可能と判定しない。
2. 入手できれば観測→過程の校正と未使用データでの検査を分離し、現在のモデル係数を固定したまま予測の不一致を評価する。
3. 入手できなければG2/G3未達を維持し、NEE投稿に進まない。観測関連と機構の制約を中心とする論文として到達点を判断する。

固定済みの二部構成原稿は保存版として維持する。NEE向けの改稿は今回の結果と今後の校正を踏まえて別の作業版で行い、過去の結果を消さない。
