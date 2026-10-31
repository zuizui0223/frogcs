# frogcs：ID0↔ID12の単一生物率交換、全16条件・80年・4seedの源監査

2026-10-31 / Draft PR #152。これは生物学的パラメータ軸の**モデル内探索診断**であり、次の新規8seed独立再現の前段結果である。

## 現状とデータ根拠

[元のsourceに対する全8率×双方向の単体テストSUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/41196720534)、
[16条件すべての真正80年計算SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/41196851204)、
[元のPR151のID0・ID12の観測結果を再利用した全16条件の独立監査SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/41197208457)。

source kernelは元の120日季節内捕食関数と80年遅延成熟・加入式。元の4seed（101–104）×2植物役割×2成長率×2D水中期間×F→羽化D逆転捕食ON/OFF×2×2×2元植生・供給頂点×8合成環状パッチ、q=3、外部流入OFF、年次移動OFF／加入と残存の両成分15%移動。真の元生物率ベクトルは元の256個の仮説的LHS設定中ID0/12を利用し、異なる8軸を1つずつ双方向で交換した。

55,296件のギルド×処理×seed結果、27,648件の移動あり−なし対応結果、608,219件の追加整数局所ゼロ→正イベントを監査。ただし独立な乱数反復は各条件**4seedだけ**であり、イベントやパッチ数が独立野外標本の大きさではない。

## 8率軸と双方向の最初の結論

反転成立の定義：移動あり−なしの**年80末F占有パッチ差**について、低S成長×D期間40/60日がともに正、速いS成長×D期間40/60日がともに負。表の値は**この条件が成立した植物機能の数／2**。

| 単独交換する元LHS軸 | ID0（元は2/2反転）にID12の軸値を交換 | ID12（元は0/2反転）にID0の軸値を交換 |
|---|---:|---:|
| 元の無交換対照 | 2/2 | 0/2 |
| attack_scale（全捕食の共通倍率） | **0/2** | 0/2 |
| conversion（加入の変換係数） | 1/2 | **2/2** |
| rho（回帰率） | 2/2（ただし成長主効果は大幅に弱まる） | **2/2** |
| f_adult_survival（F成体生残） | **0/2** | 0/2（後者は最終占有ゼロの床効果） |
| s_growth_multiplier | 2/2 | 0/2 |
| d_growth_multiplier | 2/2 | 0/2 |
| f_juvenile_survival | 2/2 | 0/2 |
| f_delay | 2/2 | 0/2 |

**1つの率軸だけでどんな背景でも反転を操作できるわけではない。** とくに、ID0で攻撃倍率や成体生残をID12の値にすると反転は消えたが、それらをID12にID0の値で導入しても反転は生成しなかった。一方、ID12ではconversionまたはrhoをID0から導入すると2植物で反転が出た。結果は「元の7軸を固定したときの単一介入効果」であり、必要十分を普遍的に示すものではない。

## 構造的注意：rhoとconversionは独立機構でない

外部流入OFFの元年次加入の式は

local = rho × conversion × juvenile^(delay−1) × due/(1+due/K)

であり、rhoとconversionは**積としてしか現れない**。外部流入OFFのこのモデルでは、積が一定なら双方を別々に定めることができない（構造的非識別）。したがってrhoとconversionの類似効果は、2つの独立機構の裏付けではなく、同一の局所加入の強度の操作と整合する。外部流入ONではimmigrant=(1−rho)×(1−survival)×sourceという別項にrhoが入るため、別の識別経路が生じ得る。

元seasonal kernel・有限Nの個体整数会計に対し、同じrho×conversionならOFFで同じパスの生成、ONなら異なる外部移入が生じるというテストも別途実装し実行している（[テスト](scripts/test_rho_conversion_product_identifiability.py)、[CI](https://github.com/zuizui0223/frogcs/actions/runs/41197668836)）。

## 本結果の上限と次の検証

- 4seedは初回探索であり、たとえば成体生残の交換による「反転消失」は終点占有がゼロに潰れるだけの可能性もある。真の機構の必要性を意味しない。
- 元モデルのLHS値は外部データによる実測・校正ではない。浮動小数演算の固定点での結果であり、実湿地のS成長・D水中期間・捕食・分散の因果の直接証拠ではない。
- 双方向の作用が違うこと自体は、複数率の**相互依存**を支持する手掛かりとなるが、数値的な一因子比較だけでは相互作用の形まで一意に特定できない。
- この4seed結果を見た後、攻撃倍率・conversion・rho・F成体生残の4軸×双方向の全8条件について**追加seed105–112を独立実行**することを事前に固定済み。残り4軸の初回結果はすべて保存している。12seedの確認前には率軸別の機構結論を上げない。

## 永続化した検査可能な結果

- [全8率×双方向の元率の反転判定CSV](results/growth_rescue_rate_axis_swaps_20261031/verified_first4_all16_rate_axis_signs.csv)
- [全16条件×2植生機能×4段階セルの占有効果CSV](results/growth_rescue_rate_axis_swaps_20261031/verified_first4_all16_frog_cells.csv)
- [元率ID0/12の真の16条件の全実行artifact](https://github.com/zuizui0223/frogcs/actions/runs/41197208457)
- [事前固定プロトコルと追加8seed追補](PRIOR_RATE_AXIS_SINGLE_SWAP_PROTOCOL_2026-10-31.md)
