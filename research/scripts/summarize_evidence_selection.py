"""Validate outputs and append source-backed selection tables to the report."""
import json
import numpy as np
import pandas as pd
from run_evidence_constrained import OUT


def md(frame):
    def fmt(x):
        if isinstance(x,(float,np.floating)):return f'{x:.6f}'
        return str(x)
    return '| '+' | '.join(frame.columns)+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+''.join(
        '| '+' | '.join(fmt(x) for x in r)+' |\n' for r in frame.itertuples(index=False,name=None))


def full(q):
    return q[(q.metric=='F_B')&(q.D_low==.25)&(q.D_high==2)&(q.S_low==.25)&(q.S_high==2)]


def main():
    primary=pd.read_csv(OUT/'summary.csv')
    stages=pd.read_csv(OUT/'stage_grid_summary.csv',dtype={'size_gate':str})
    means=pd.concat([pd.read_csv(OUT/('stage_'+p+'_mean_summary.csv')) for p in ('refuge_only','litter_response')])
    if (len(primary),len(stages),len(means))!=(25920,34992,8748):raise AssertionError('Incomplete grids')
    selected=pd.read_csv(OUT/'robust_selected_selection.csv')
    su=pd.read_csv(OUT/'robust_selected_validation_summary.csv')
    cs=full(pd.read_csv(OUT/'robust_selected_validation_contrasts.csv'))
    ref=su[(su.intervention=='full')&(su.check=='interventions')]
    maximum=0.
    for r in selected.itertuples():
        a=stages[(stages.profile==r.profile)&(stages.timing==r.timing)].set_index(['vegetation','S_source','D_source'])
        b=ref[ref.profile==r.profile].set_index(['vegetation','S_source','D_source'])
        maximum=max(maximum,float((a[['F_B','F_C','S_B','D_B']]-b[['F_B','F_C','S_B','D_B']]).abs().max().max()))
    if maximum>1e-10:raise AssertionError('Selected rerun drift')
    errors={}
    for g,cols in {'F':['F_killed_by_S','F_killed_by_D','F_dry'],
                   'S':['S_killed_by_D','S_dry'],
                   'D':['D_killed_by_S','D_killed_by_F','D_failure','D_dry']}.items():
        errors[g]=float((su[g+'_B']-su[g+'_C']-su[cols].sum(axis=1)).abs().max())
        if errors[g]>1e-10:raise AssertionError('Cohort accounting')
    checks=cs[(cs.intervention=='full')&cs.check.isin(['half_step','horizon160'])]
    if not checks.all_three.all():raise AssertionError('Numerical joint sign instability')
    score=pd.read_csv(OUT/'robust_stage_scores.csv')
    counts=score[score.passed==5].groupby('profile').size().to_dict()
    report=dict(primary_scenarios=len(primary),stage_scenarios=len(stages),mean_gate_scenarios=len(means),
        demographic_grid_scenarios=34992,total_scenario_evaluations_including_checks=107388,
        max_selected_rerun_error=maximum,cohort_accounting_errors=errors,
        all_selected_numerical_checks_pass=True,all_five_settings_matching_stage_contexts=counts,
        selection='Prioritize S-mediated D suppression plus F refuge; reciprocal predation can amplify but is not universally necessary. No field causal identification or likelihood-based ranking.',
        comparison_caveat='Stage grid uses attack_scale=3 for refuge_only and 1.5 for litter_response; counts are not probabilities or a fair-rate model competition.')
    minimal=pd.read_csv(OUT/'minimal_passing.csv',dtype={'mask':str})
    minimal_checks=full(pd.read_csv(OUT/'minimal_checks.csv',dtype={'mask':str}))
    core=minimal_checks[minimal_checks['mask']=='110110']
    if len(core)!=6 or not core.all_three.all():raise AssertionError('Minimal core robustness failed')
    if not ((minimal['mask']=='110110') & minimal.all_three).any():raise AssertionError('Missing core baseline')
    report.update(selected_explanatory_core='110110: S eats F, D eats F, S eats D, vegetation reduces S eating F',
        selected_core_baseline_and_six_checks_pass=True,
        minimal_subsets=minimal.loc[minimal.inclusion_minimal,'mask'].tolist(),
        counterfactual_scope='Removing a documented edge identifies sufficiency, not its absence in nature.')
    (OUT/'final_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    cs.to_csv(OUT/'selected_fullrange_checks.csv',index=False)
    display=ref[ref.profile=='refuge_only'][['vegetation','S_source','D_source','F_B','S_B','D_B','F_fraction',
        'F_killed_by_S_fraction','F_killed_by_D_fraction','S_killed_by_D_fraction','D_killed_by_S_fraction']]
    display.to_csv(OUT/'selected_mechanism_fluxes.csv',index=False)
    mean_cs=full(pd.read_csv(OUT/'mean_gate_contrasts.csv'))
    meanrows=[]
    for r in selected.itertuples():
        z=mean_cs[(mean_cs.profile==r.profile)&(mean_cs.timing==r.timing.replace('gateNone','gate_mean'))]
        meanrows.append(z[['profile','DV','SV','SD','all_three']])
    meancheck=pd.concat(meanrows,ignore_index=True)
    meancheck.to_csv(OUT/'selected_mean_gate_checks.csv',index=False)
    tables='''\n## 最終選定結果\n\n第一候補は、**発生段階・サイズ条件に依存する捕食者間捕食＋植生によるカエルの非対称な保護**とした。単純な保護系統では、243配置中27配置で基準＋4人口学設定の全てにわたり全供給範囲の三方向一致が残った。機能的反応系統では全5設定一致の配置はなく、代表候補は3/5設定で一致した。ただし攻撃尺度の違いを含むため、件数の差をモデルの確率的な優劣とは扱わない。追加仮定の少なさ、条件内の安定性、経路除去の説明可能性から主候補を選び、機能的反応の代替表現も残す。\n\n最終代表は、まず基準全範囲で一致する配置の中で人口学検証の一致数が最大のものを取り、同点は登場時刻・期間の数値順で選んだ。効果量最大の選択ではないが、探索後選択であり独立な実証ではない。\n\n'''
    tables+=md(selected[['profile','s_arrival','d_arrival','F_duration','S_duration','D_duration','passed','tested']])
    tables+='\nカエル登場は20日。選択した保護系統ではヤゴが20日先行し、有尾類と重なるのは40〜60日。採餌抑制は全て0、逆転捕食なし、植生の採餌・羽化増強も0。\n\n### 経路除去と数値確認\n\n'
    tables+=md(cs[['profile','check','intervention','DV','SV','SD','all_three']])
    tables+='\n### 第一候補のコホート収支\n\n割合は季節開始コホートに対する平均であり、実際の動物の頭数・野外死亡率ではない。\n\n'
    tables+=md(display[(display.vegetation==1)&(display.S_source==2)])
    tables+='\n### 時間平均を保ったサイズ関数対照\n\n'
    tables+=md(meancheck)
    tables+='\n時間平均対照の結果は、サイズ関数の刻々の変化と、経路ごとの平均的な捕食しやすさを区別する材料である。文献で支持されたサイズ依存性の存在を、今回の成長率・期間の実測根拠と同一視しない。\n\n### 完了した検証の範囲\n\n定義した格子・感度・再計算を含め107,388シナリオ評価を保存した。これは独立な107,388実証でも、自然界の全機構の網羅でもない。基準結果の再現・コホート収支・選定代表の数値安定性を検査し、失敗した設定も全て残した。マクロ解析の原因を同定した結論ではなく、既存の結果を説明できる機構の候補を絞った結論である。\n'
    path=OUT.parents[2]/'legacy/mechanism_iterations/research/manuscript/EVIDENCE_CONSTRAINED_RESULTS_2026-10-27.md'
    s=path.read_text(encoding='utf-8')
    marker='\n## 最小経路の組合せ'
    appendix=marker+s.split(marker,1)[1] if marker in s else ''
    s=s.split('\n## 最終選定結果')[0]
    path.write_text(s+tables+appendix,encoding='utf-8')
    print(json.dumps(report,indent=2))
    print(display[(display.vegetation==1)&(display.S_source==2)].to_string(index=False))


if __name__=='__main__':main()
