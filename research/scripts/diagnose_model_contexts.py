"""Fixed-model one-factor interventions, not a new candidate search."""
import itertools
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from final_mechanism_common import OUT as SOURCE, design, evaluate, score

OUT = SOURCE.parent / 'model_failure_diagnosis_20261029'
CTX = ['f_arrival', 's_arrival', 'd_arrival', 'F_duration', 'S_duration', 'D_duration']
OPT = ['attack', 'rho', 'conversion', 'strength', 'size_gate', 'refuge_order']


def fixed_design():
    blocks = json.loads((SOURCE / 'validation_design.json').read_text())['blocks']
    blocks = [b for b in blocks if b['block_id'] >= 0]
    base = next(b for b in blocks if b['block_id'] == 13)
    rows, aliases, known = [], [], {}

    def add(label, values):
        values = {k: values[k] for k in CTX + OPT}
        key = json.dumps(values, sort_keys=True)
        if key not in known:
            known[key] = len(rows)
            rows.append(dict(block_id=known[key], **values))
        aliases.append(dict(label=label, block_id=known[key]))

    add('baseline_13', base)
    for k in CTX + OPT:
        values = sorted({b[k] for b in blocks}, key=str)
        for v in values:
            if v != base[k]:
                add(f'one_factor:{k}={v}', {**base, k: v})
    for arrival, strength, order in itertools.product([20, 40], [1., .5], ['D', 'S']):
        add(f'cube:s_arrival={arrival};strength={strength};order={order}',
            {**base, 's_arrival': arrival, 'strength': strength, 'refuge_order': order})
    assert len(rows) == 27 and len(aliases) == 31
    return rows, aliases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--numerical-checks', action='store_true')
    parser.add_argument('--quarter-boundary', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    blocks, aliases = fixed_design()
    if args.quarter_boundary:
        return quarter_boundary(blocks, aliases)
    if args.numerical_checks:
        return numerical_checks(blocks, aliases)
    (OUT / 'counterfactual_design.json').write_text(json.dumps(dict(
        models=[1479, 1455], contexts=blocks, aliases=aliases, years=80, window=20,
        dt=.25, purpose='One-factor local diagnosis, not model reselection'), indent=2) + '\n')
    models = pd.read_csv(SOURCE / 'catalog.csv')
    models = models[models.model_id.isin([1479, 1455])]
    frames = []
    for gate in [None, .5]:
        path = OUT / ('counterfactual_' + str(gate) + '_cells.csv.gz')
        pending = []
        for b in blocks:
            if b['size_gate'] != gate:
                continue
            de = design(models, [{k: b[k] for k in CTX}], [b['block_id']])
            for k in OPT:
                if k != 'size_gate':
                    de['batch_' + k] = b[k]
            pending.append(de)
        de = pd.concat(pending, ignore_index=True)
        # Explicitly rerun only if no completed file exists; design is deterministic.
        if path.exists():
            su = pd.read_csv(path)
            np.testing.assert_array_equal(su[['model_id', 'block_id']], de[['model_id', 'block_id']])
        else:
            su = evaluate(de, years=80, window=20, dt=.25, size_gate=gate,
                **{k: de['batch_' + k].to_numpy() for k in OPT if k != 'size_gate'})
            su.to_csv(path, index=False, compression={'method': 'gzip', 'mtime': 0})
        frames.append(su)
        print('Finished', gate, len(su), 'cells', flush=True)
    allcells = pd.concat(frames, ignore_index=True)
    scores = score(allcells)
    scores.to_csv(OUT / 'counterfactual_scores.csv', index=False)
    expanded = scores.merge(pd.DataFrame(aliases), on='block_id', validate='many_to_many')
    expanded.to_csv(OUT / 'counterfactual_labelled_scores.csv', index=False)
    for mid, file in [(1479, 'validation_scores.csv'), (1455, 'reduced_validation_scores.csv')]:
        old = pd.read_csv(SOURCE / file)
        old = old[(old.model_id == mid) & (old.block_id == 13)].iloc[0]
        new = scores[(scores.model_id == mid) & (scores.block_id == 0)].iloc[0]
        columns = [c for c in scores if c not in ['model_id', 'block_id']]
        np.testing.assert_allclose(new[columns].astype(float), old[columns].astype(float), atol=1e-10)
    print('Baseline matches saved block13 for both models.', flush=True)
    print(expanded[['model_id', 'label', 'negative_H_SD', 'rank_DS', 'conditional_pass',
                    'macro_form_pass', 'joint_pass', 'floor_avoiding']].to_string(index=False), flush=True)


def numerical_checks(blocks, aliases):
    # Near-zero contrasts/new successes and the two largest temporal CVs merit
    # timestep/duration checks. These checks never select a new mechanism.
    labels = ['baseline_13', 'one_factor:F_duration=60', 'one_factor:F_duration=75',
              'one_factor:S_duration=40', 'one_factor:strength=0.5',
              'one_factor:D_duration=60', 'one_factor:D_duration=70',
              'one_factor:s_arrival=40']
    ids = {a['block_id'] for a in aliases if a['label'] in labels}
    assert len(ids) == 8
    models = pd.read_csv(SOURCE / 'catalog.csv')
    models = models[models.model_id.isin([1479, 1455])]
    pending = []
    for b in blocks:
        if b['block_id'] not in ids:
            continue
        assert b['size_gate'] is None
        de = design(models, [{k: b[k] for k in CTX}], [b['block_id']])
        for k in OPT:
            if k != 'size_gate':
                de['batch_' + k] = b[k]
        pending.append(de)
    de = pd.concat(pending, ignore_index=True)
    results = []
    for name, years, dt in [('half_step', 80, .125), ('long_run', 160, .25)]:
        path = OUT / f'counterfactual_{name}_cells.csv.gz'
        if path.exists():
            su = pd.read_csv(path)
            np.testing.assert_array_equal(su[['model_id', 'block_id']], de[['model_id', 'block_id']])
        else:
            su = evaluate(de, years=years, window=20, dt=dt, size_gate=None,
                **{k: de['batch_' + k].to_numpy() for k in OPT if k != 'size_gate'})
            su.to_csv(path, index=False, compression={'method': 'gzip', 'mtime': 0})
        sc = score(su); sc['check'] = name
        results.append(sc)
        print('Finished numerical check', name, len(su), flush=True)
    pd.concat(results, ignore_index=True).to_csv(OUT / 'counterfactual_numerical_scores.csv', index=False)


def quarter_boundary(blocks, aliases):
    # The half-step check reversed the reduced model's F_duration=75 sign.
    # Resolve that numerical boundary only; do not search for another success.
    bid = next(a['block_id'] for a in aliases if a['label'] == 'one_factor:F_duration=75')
    b = next(b for b in blocks if b['block_id'] == bid)
    models = pd.read_csv(SOURCE / 'catalog.csv')
    de = design(models[models.model_id == 1455], [{k: b[k] for k in CTX}], [bid])
    path = OUT / 'quarter_boundary_cells.csv.gz'
    su = evaluate(de, years=80, window=20, dt=.0625, **{k: b[k] for k in OPT})
    su.to_csv(path, index=False, compression={'method': 'gzip', 'mtime': 0})
    sc = score(su); sc['check'] = 'quarter_step'
    sc.to_csv(OUT / 'quarter_boundary_scores.csv', index=False)
    print(sc[['model_id', 'block_id', 'negative_H_SD', 'conditional_pass', 'joint_pass']].to_string(index=False))


if __name__ == '__main__':
    main()
