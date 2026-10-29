"""Assemble diagnostic receipts without selecting new successful models."""
import hashlib
import json

import numpy as np
import pandas as pd

from diagnose_model_contexts import OUT, SOURCE


def main():
    paths = [OUT / f'counterfactual_{g}_cells.csv.gz' for g in ['None', '0.5']]
    cells = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    assert len(cells) == 972
    rows = []
    for (mid, bid), g in cells.groupby(['model_id', 'block_id']):
        for vegetation, q in g.groupby('vegetation'):
            q = q.set_index(['S_source', 'D_source'])
            r = dict(model_id=mid, block_id=bid, vegetation=vegetation)
            for col in ['audit_H_DF', 'audit_H_SF', 'F_B']:
                r[col + '_SD'] = (q.loc[(2., 2.), col] - q.loc[(2., .25), col]
                                 - q.loc[(.25, 2.), col] + q.loc[(.25, .25), col])
            r['H_total_SD'] = r['audit_H_DF_SD'] + r['audit_H_SF_SD']
            r['multiplicative_survival_interaction'] = np.exp(-r['H_total_SD'])
            r['F_B_min'] = q.F_B.min(); r['F_B_max'] = q.F_B.max()
            rows.append(r)
    pd.DataFrame(rows).to_csv(OUT / 'counterfactual_pathway_decomposition.csv', index=False)
    baseline = pd.read_csv(OUT / 'counterfactual_scores.csv')
    numerical = pd.read_csv(OUT / 'counterfactual_numerical_scores.csv')
    m = numerical.merge(baseline, on=['model_id', 'block_id'], suffixes=('_check', '_base'))
    checks = []
    for name, g in m.groupby('check'):
        checks.append(dict(check=name, cases=len(g), changed_joint=int((g.joint_pass_check != g.joint_pass_base).sum()),
            changed_conditional=int((g.conditional_pass_check != g.conditional_pass_base).sum()),
            max_abs_hazard_SD_change=float(abs(g.negative_H_SD_check-g.negative_H_SD_base).max())))
    quarter = pd.read_csv(OUT / 'quarter_boundary_scores.csv')
    assert len(quarter) == 1 and not quarter.joint_pass.iloc[0]
    assert quarter.negative_H_SD.iloc[0] > 0
    trace = pd.read_csv(OUT / 'season_trace_1479.csv.gz')
    exposed = trace[(trace.vegetation == 1) & (trace.fw == 1) & (trace.hdf > 0)]
    inputs = [SOURCE / 'validation_design.json', SOURCE / 'validation_scores.csv',
              SOURCE / 'reduced_validation_scores.csv', SOURCE / 'winner_rank_cells.csv.gz']
    report = dict(original_models=[1479, 1455], new_unique_contexts=27, supply_cells_per_context=18,
        base_scenario_evaluations=len(cells), numerical_check_scenario_evaluations=576+18,
        original_model_changed=False, new_candidate_selected=False, field_calibration=False,
        numerical_checks=checks, quarter_step_rejects_reduced_F75_boundary=True,
        baseline_highV_F_during_D_exposure=[float(exposed.f.min()), float(exposed.f.max())],
        baseline_highV_D_hazard_fraction_at_F_above1=float(exposed.loc[exposed.f > 1, 'hdf'].sum()/exposed.hdf.sum()),
        original_inputs=[dict(path=p.relative_to(SOURCE.parents[2]).as_posix(),
            sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in inputs],
        limits=['Local one-factor contrasts do not estimate frequency in nature',
                'Algebraic hazard decomposition is not an independent intervention effect',
                'Rank interaction signs depend on response scale and the synthetic grid',
                'No suitability-density-calling observation bridge has been calibrated'])
    (OUT / 'diagnosis_receipt.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
