"""Compare density-dose slopes, not reversal contrasts, in the existing kernel.

Exploratory synthetic falsification: densities are not SDM suitability, and
cohort completion is not calling. No model parameters are fitted to NAAMP.
"""
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from stage_vegetation_network import simulate


def run(dt=.25):
    rows, cohorts, labels = [], [], []
    variants = {'full': {}, 'no_cue': {'cue': 0.},
                'no_intraguild': {'intraguild': False},
                'independent': {'cue': 0., 'intraguild': False}}
    for roles, order, arrival, vegetation, variant, s, d in itertools.product(
            range(16), ['S', 'D'], [10., 30., 50.], [0., 1.], variants,
            [0., .5, 1., 2.], [.25, .5, 1., 2.]):
        rows.append(dict(community='FSD', roles=roles, refuge_order=order,
                         f_arrival=arrival, vegetation=vegetation,
                         attack_scale=1.5, cue=3.) | variants[variant])
        cohorts.append([1., s, d])
        labels.append((variant, s, d))
    result = simulate(rows, dt=dt, initial_cohorts=np.asarray(cohorts))
    result[['variant', 'S_input', 'D_input']] = pd.DataFrame(labels)
    result['log_F'] = np.log(result.F_completed)
    keys = ['roles', 'refuge_order', 'f_arrival', 'vegetation', 'variant', 'S_input']
    low = result[result.D_input == .25].set_index(keys)
    high = result[result.D_input == 2.].set_index(keys)
    slopes = ((high[['F_completed', 'log_F']] - low[['F_completed', 'log_F']]) / 1.75)
    slopes = slopes.rename(columns={'F_completed': 'D_slope_F', 'log_F': 'D_slope_log_F'}).reset_index()
    keys.remove('S_input')
    a = slopes[slopes.S_input == 0].set_index(keys)
    b = slopes[slopes.S_input == 2].set_index(keys)
    modification = (b[['D_slope_F', 'D_slope_log_F']] - a[['D_slope_F', 'D_slope_log_F']])
    modification = modification.add_prefix('S_change_').reset_index()
    null = modification[modification.variant == 'independent'].S_change_D_slope_log_F.abs().max()
    assert null < 1e-10, null
    return result, slopes, modification, float(null)


if __name__ == '__main__':
    out = Path(__file__).resolve().parents[1] / 'results/path_dose_response_20261026'
    out.mkdir(parents=True, exist_ok=True)
    result, slopes, modification, null = run()
    fine, _, fine_modification, _ = run(.125)
    error = float(np.max(np.abs(result.F_completed - fine.F_completed)))
    assert error < .005, error
    sign_stable = bool(np.array_equal(modification.S_change_D_slope_log_F < -1e-8,
                                      fine_modification.S_change_D_slope_log_F < -1e-8))
    result.to_csv(out / 'dose_grid.csv.gz', index=False, compression={'method': 'gzip', 'mtime': 0})
    slopes.to_csv(out / 'D_slopes.csv', index=False)
    modification.to_csv(out / 'S_modification.csv', index=False)
    stats = {'classification': 'SYNTHETIC_NOT_EMPIRICAL', 'n_scenarios': len(result),
             'D_contrast': [.25, 2.], 'S_contrast': [0., 2.],
             'half_step_max_completion_error': error, 'negative_sign_stable': sign_stable,
             'independent_log_interaction_error': null, 'variants': {}}
    for variant, frame in modification.groupby('variant'):
        stats['variants'][variant] = {col: {
            'min': float(frame[col].min()), 'max': float(frame[col].max()),
            'negative': int((frame[col] < -1e-8).sum()),
            'positive': int((frame[col] > 1e-8).sum()), 'n': len(frame)}
            for col in ['S_change_D_slope_F', 'S_change_D_slope_log_F']}
    (out / 'validation.json').write_text(json.dumps(stats, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(stats, indent=2))
