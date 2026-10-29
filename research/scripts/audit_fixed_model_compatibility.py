"""Descriptive coordinates only; unlike observables preclude a model fit test."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / 'research/results/final_mechanism_20261027'
MACRO = ROOT / 'research/results/nee_context_20261029'
OUT = ROOT / 'research/results/model_compatibility_20261029'
TERMS = {'DS': 'Odonata:Caudata', 'DV': 'Odonata:vegetation',
         'SV': 'Caudata:vegetation', 'DSV': 'Odonata:Caudata:vegetation'}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = [FROZEN / p for p in ['validation_scores.csv',
               'reduced_validation_scores.csv', 'winner_rank_resolution.csv', 'macro_targets.csv']]
    sources += [MACRO / 'coefficients.csv']
    candidates = []
    for source, mid in [(sources[0], 1479), (sources[1], 1455)]:
        d = pd.read_csv(source)
        d = d[(d.model_id == mid) & (d.block_id >= 0)]
        assert len(d) == 24 and d.block_id.nunique() == 24
        for r in d.to_dict('records'):
            candidates.append(dict(candidate=f'{mid}_block{r["block_id"]}_grid3',
                model_id=mid, block_id=r['block_id'], levels=3, family='fixed_contexts',
                original_joint_pass=r['joint_pass'], floor_avoiding=r['floor_avoiding'],
                **{k: r['rank_' + k] for k in TERMS}))
    for r in pd.read_csv(sources[2]).to_dict('records'):
        candidates.append(dict(candidate=f'1479_block13_grid{r["levels"]}',
            model_id=1479, block_id=13, levels=int(r['levels']), family='grid_sensitivity',
            original_joint_pass=None, floor_avoiding=None, **{k: r[k] for k in TERMS}))
    candidates.append(dict(candidate='zero_interaction_benchmark', model_id=-1,
        block_id=-1, levels=0, family='uninformative_interval_benchmark',
        original_joint_pass=None, floor_avoiding=None, **{k: 0. for k in TERMS}))
    c = pd.DataFrame(candidates)
    # Duplicate 3-level coordinates are deliberately labelled by diagnostic role.
    a = c[(c.family == 'fixed_contexts') & (c.model_id == 1479) & (c.block_id == 13)]
    b = c[(c.family == 'grid_sensitivity') & (c.levels == 3)]
    np.testing.assert_allclose(a[list(TERMS)], b[list(TERMS)], atol=1e-12)
    c.to_csv(OUT / 'fixed_candidates.csv', index=False)
    observed = pd.read_csv(sources[4])
    observed = observed[(observed.outcome == 'strong_rate') & (observed.subset == 'all')
        & observed['mode'].isin(['pooled', 'within'])
        & observed.adjustment.isin(['none', 'space']) & observed.term.isin(TERMS.values())].copy()
    observed['source_version'] = '20261029_fixed_rank'
    old = pd.read_csv(sources[3]); old = old[old.term.isin(TERMS.values())].copy()
    # Keep the original bootstrap definition separate from the fixed-rank replay.
    old['source_version'] = '20261026_frozen_original'
    old['adjustment'] = 'none'; old['mode'] = 'pooled'; old['bootstrap_cluster'] = 'route'
    observed = pd.concat([observed, old], ignore_index=True)
    keys = ['source_version', 'background', 'mode', 'adjustment', 'bootstrap_cluster']
    rows = []
    for key, g in observed.groupby(keys):
        g = g.set_index('term'); assert len(g) == 4
        for candidate in candidates:
            for short, term in TERMS.items():
                r = g.loc[term]; estimate = candidate[short]
                rows.append({**dict(zip(keys, key)), **{k: candidate[k] for k in
                    ['candidate', 'model_id', 'block_id', 'levels', 'family']},
                    'term': term, 'model_coordinate': estimate, 'macro_beta': r.beta,
                    'macro_low': r.low, 'macro_high': r.high,
                    'coordinate_inside_marginal_interval': r.low <= estimate <= r.high,
                    'macro_interval_contains_zero': r.low <= 0 <= r.high,
                    'same_point_sign': np.sign(estimate) == np.sign(r.beta),
                    'interpretation': 'DESCRIPTIVE_UNCALIBRATED_NOT_A_JOINT_TEST'})
    long = pd.DataFrame(rows)
    long.to_csv(OUT / 'coordinate_comparison.csv', index=False)
    summary = long.groupby(keys + ['candidate', 'model_id', 'block_id', 'levels', 'family']).agg(
        marginal_intervals_containing_coordinate=('coordinate_inside_marginal_interval', 'sum'),
        macro_intervals_containing_zero=('macro_interval_contains_zero', 'sum'),
        matching_point_signs=('same_point_sign', 'sum')).reset_index()
    summary['all_four_coordinate_intervals'] = summary.marginal_intervals_containing_coordinate == 4
    summary.to_csv(OUT / 'coordinate_summary.csv', index=False)
    counts = summary[summary.family == 'fixed_contexts'].groupby(keys + ['model_id']).agg(
        contexts=('block_id', 'size'), all_four_coordinate_intervals=('all_four_coordinate_intervals', 'sum')).reset_index()
    assert counts.contexts.eq(24).all()
    counts.to_csv(OUT / 'fixed_context_counts.csv', index=False)
    receipt = dict(inputs=[dict(path=p.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources],
        model_retuned=False, candidate_reselected=False,
        calibrated_observation_model=False, statistical_equivalence_test=False,
        note='Four marginal interval inclusions do not constitute a joint test. Different observables and predictor distributions prevent calibration or fit claims.')
    (OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    show = long[(long.source_version == '20261029_fixed_rank') & (long.background == 'uniform')
        & (long['mode'] == 'pooled') & (long.adjustment == 'space')
        & (long.bootstrap_cluster == 'route') & (long.family == 'grid_sensitivity')]
    print(show[['levels', 'term', 'model_coordinate', 'macro_beta', 'macro_low', 'macro_high',
                'coordinate_inside_marginal_interval']].to_string(index=False))


if __name__ == '__main__':
    main()
