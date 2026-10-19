#!/usr/bin/env python3
"""Frozen exploratory NAAMP conditional-placement forecast, not a memory test.

Contract: research/RECENT_VS_OLDER_SITE_HISTORY_CONTRACT_2026-10-19.md.
All response rows remain outside Git; only aggregate receipts are written.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp

ROOT = Path(__file__).resolve().parents[2]
RIDGE = 1e-6
TRAIN_END = 2008
SEED = 20261019


@lru_cache(None)
def masks(k: int) -> np.ndarray:
    if not 0 <= k <= 10:
        raise ValueError('k must be 0..10')
    rows = list(combinations(range(10), k))
    out = np.zeros((len(rows), 10), dtype=float)
    for i, selected in enumerate(rows):
        out[i, list(selected)] = 1
    return out


def features(history: dict[int, np.ndarray], year: int):
    past = [np.asarray(v, float) for t, v in sorted(history.items()) if t <= year-3]
    if len(past) < 3 or year-1 not in history or year-2 not in history:
        raise ValueError('need three background visits and both exact annual lags')
    for v in past+[history[year-1], history[year-2]]:
        if np.asarray(v).shape != (10,) or not np.isin(v, [0, 1]).all():
            raise ValueError('each history vector must have ten binary entries')
    q = (np.sum(past, axis=0)+0.5)/(len(past)+1)
    return np.log(q/(1-q)), np.asarray(history[year-1], float), np.asarray(history[year-2], float), len(past)


def design(frames: list[dict], extra: str | None):
    blocks = {}
    groups = defaultdict(list)
    for i, f in enumerate(frames):
        y = np.asarray(f['y'], float)
        if y.shape != (10,) or not np.isin(y, [0, 1]).all():
            raise ValueError('current response must be ten binary recorded states')
        k = int(y.sum())
        if not 1 <= k <= 9:
            raise ValueError('placement likelihood requires k=1..9')
        groups[k].append(i)
    for k, ix in groups.items():
        x = np.stack([np.column_stack([frames[i]['z']] + ([frames[i][extra]] if extra else [])) for i in ix])
        y = np.stack([frames[i]['y'] for i in ix])
        if not np.isfinite(x).all():
            raise ValueError('non-finite predictor')
        candidate = np.einsum('cj,ejp->ecp', masks(k), x, optimize=True)
        observed = np.einsum('ej,ejp->ep', y, x, optimize=True)
        blocks[k] = (np.array(ix), candidate, observed)
    return {'n': len(frames), 'blocks': blocks}


def scores(beta: np.ndarray, d: dict) -> np.ndarray:
    out = np.empty(d['n'])
    for ix, candidate, observed in d['blocks'].values():
        eta = candidate @ beta
        out[ix] = observed @ beta-logsumexp(eta, axis=1)
    return out


def objective(beta: np.ndarray, d: dict):
    loss = 0.
    grad = np.zeros(len(beta))
    for ix, candidate, observed in d['blocks'].values():
        eta = candidate @ beta
        norm = logsumexp(eta, axis=1)
        p = np.exp(eta-norm[:, None])
        loss += np.sum(norm-observed @ beta)
        grad += (np.einsum('ec,ecp->ep', p, candidate)-observed).sum(axis=0)
    return float(loss/d['n']+RIDGE*(beta @ beta)), grad/d['n']+2*RIDGE*beta


def fit(frames: list[dict], extra: str | None):
    d = design(frames, extra)
    initial = np.array([1., 0.] if extra else [1.])
    result = minimize(objective, initial, args=(d,), jac=True, method='L-BFGS-B',
                      bounds=[(-6., 6.)]*len(initial),
                      options={'maxiter': 300, 'ftol': 1e-12, 'gtol': 1e-7})
    if not result.success or np.max(np.abs(result.x)) >= 5.999:
        raise RuntimeError(f'optimizer did not pass fixed gate: {result.message}; beta={result.x}')
    return {'coefficients': result.x.tolist(), 'train_mean_log_score': float(np.mean(scores(result.x, d))),
            'converged': bool(result.success), 'iterations': int(result.nit), 'extra': extra}


def load_archived():
    path = ROOT/'exploration/run_naamp_local_chorus_memory_targeting.py'
    raw = path.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if blob != 'f85e9ce5b1fdfa599d512163d6423dcd3f911a99':
        raise ValueError('archived calling/SiteID loader drift')
    spec = importlib.util.spec_from_file_location('archived_memory', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, blob


def assemble():
    old, code_blob = load_archived()
    raw = old.load_retry()  # Original full-file SHA256 checks before parsing.
    runs, _ = old.base.build_runs(raw)
    eligible = set(runs.RunID.astype(str))
    sampled, _ = old.spatial.stop_matrix(raw, eligible)
    sites = old.site_map(raw, eligible)
    ci = old.ci_map(raw, eligible, sampled)
    observers = defaultdict(set)
    for r in raw['Runs.csv']:
        rid = str(r.get('RunID') or '').strip()
        who = str(r.get('ObserverTrackingID') or '').strip()
        if who:
            observers[rid].add(who)
    audit = Counter()
    frames = []
    for key, group in runs.groupby(['State', 'RouteNumber', 'RunNumber'], sort=True):
        duplicate = group.SurveyYear.duplicated(keep=False)
        audit['ambiguous_stratum_year_surveys_excluded'] += int(duplicate.sum())
        group = group.loc[~duplicate].sort_values('SurveyYear')
        visits = {}
        for row in group.itertuples(index=False):
            rid = str(row.RunID)
            st = sampled.get(rid, set())
            if len(st) != 10 or any((rid, x) not in sites for x in st):
                audit['bad_physical_identity_surveys'] += 1
                continue
            sid_to_stop = {sites[(rid, x)]: x for x in st}
            if len(sid_to_stop) != 10:
                audit['bad_physical_identity_surveys'] += 1
                continue
            visits[int(row.SurveyYear)] = {'rid': rid, 'site_order': tuple(sorted(sid_to_stop)),
                                          'sid_to_stop': sid_to_stop, 'row': row}
        for year, current in visits.items():
            if year-1 not in visits or year-2 not in visits:
                continue
            identity = current['site_order']
            if any(visits[y]['site_order'] != identity for y in (year-1, year-2)):
                audit['lag_site_set_changes'] += 1
                continue
            earlier = {y: v for y, v in visits.items() if y <= year-3 and v['site_order'] == identity}
            if len(earlier) < 3:
                continue
            audit['source_eligible_target_surveys'] += 1
            taxa = set()
            for v in earlier.values():
                for sid in identity:
                    taxa.update(ci.get((v['rid'], v['sid_to_stop'][sid]), {}))
            def vector(v, species):
                return np.array([ci.get((v['rid'], v['sid_to_stop'][sid]), {}).get(species, 0) >= 2
                                 for sid in identity], dtype=float)
            ids = [visits[y]['rid'] for y in (year, year-1, year-2)]
            obs = [observers[rid] for rid in ids]
            same = all(len(v) == 1 for v in obs) and obs[0] == obs[1] == obs[2]
            for taxon in sorted(taxa):
                outcome = vector(current, taxon)
                if not 1 <= outcome.sum() <= 9:
                    audit['uninformative_taxon_frames_k0_or_k10'] += 1
                    continue
                history = {y: vector(v, taxon) for y, v in earlier.items()}
                history[year-1] = vector(visits[year-1], taxon)
                history[year-2] = vector(visits[year-2], taxon)
                z, recent, older, n = features(history, year)
                frames.append({'z': z, 'recent': recent, 'older': older, 'y': outcome,
                               'year': year, 'state': str(key[0]), 'route': str(key[0])+':'+str(key[1]),
                               'taxon': taxon, 'same_observer': bool(same), 'background_visits': n})
    return frames, {'original_eligible_surveys': len(runs), 'source_sha256': old.base.PINS,
                    'archived_loader_git_blob': code_blob, 'selection_counts': dict(audit)}


def coverage(frames):
    return {'frames': len(frames), 'routes': len({f['route'] for f in frames}),
            'states': len({f['state'] for f in frames}), 'taxa': len({f['taxon'] for f in frames}),
            'target_years': dict(sorted(Counter(f['year'] for f in frames).items()))}


def summarize(frames, predicted, bootstrap=True):
    if not frames:
        return {'coverage': coverage(frames), 'status': 'NO_ELIGIBLE_FRAMES'}
    df = pd.DataFrame({'route': [f['route'] for f in frames], **predicted})
    route = df.groupby('route')[['M0', 'MR', 'MO']].mean()
    differences = np.column_stack([route.MR-route.MO, route.MR-route.M0, route.MO-route.M0])
    ci = None
    if bootstrap and len(route) >= 2:
        rng = np.random.default_rng(SEED)
        boot = differences[rng.integers(0, len(route), size=(2000, len(route)))].mean(axis=1)
        ci = np.quantile(boot, [.025, .975], axis=0)
    out = {'coverage': coverage(frames), 'route_equal_log_scores': route.mean().to_dict(), 'comparisons': {}}
    for j, name in enumerate(['MR_minus_MO_PRIMARY', 'MR_minus_M0', 'MO_minus_M0']):
        out['comparisons'][name] = {'route_equal_mean_nats': float(differences[:, j].mean()),
                                   'route_fraction_positive': float((differences[:, j] > 0).mean()),
                                   'ci95_route_bootstrap': ci[:, j].tolist() if ci is not None else None}
    return out


def run(output: Path):
    frames, source = assemble()
    train = [f for f in frames if f['year'] <= TRAIN_END]
    test = [f for f in frames if f['year'] > TRAIN_END]
    out = {'analysis': 'recent_vs_older_acoustic_site_history_forecast_2026_10_19',
           'status': 'POST_HOC_SAME_NAAMP_PROGRAMME', 'source': source,
           'training_coverage': coverage(train), 'test_coverage': coverage(test),
           'no_new_environment_data': True, 'not_individual_memory_test': True,
           'not_JAE_concentration_estimand': True, 'conditional_on_current_observed_k': True,
           'not_unconditional_forecast': True, 'no_frozen_main_changes': True}
    if any(len(part) < 200 or coverage(part)['routes'] < 50 for part in (train, test)):
        out['status'] = 'INSUFFICIENT_FIXED_SAMPLE_NO_THRESHOLD_RELAXATION'
    else:
        models = {}
        predictions = {}
        for name, extra in [('M0', None), ('MR', 'recent'), ('MO', 'older')]:
            models[name] = fit(train, extra)
            predictions[name] = scores(np.asarray(models[name]['coefficients']), design(test, extra))
        out['models_trained_through_2008'] = models
        out['test_2009_2015'] = summarize(test, predictions)
        out['by_test_year'] = {}
        for year in sorted({f['year'] for f in test}):
            ix = np.array([f['year'] == year for f in test])
            out['by_test_year'][str(year)] = summarize([f for f, keep in zip(test, ix) if keep],
                                                     {k: v[ix] for k, v in predictions.items()}, False)
        ix = np.array([f['same_observer'] for f in test])
        out['same_observer_three_visits_no_refit'] = summarize([f for f, keep in zip(test, ix) if keep],
                                                             {k: v[ix] for k, v in predictions.items()})
        out['interpretation'] = 'Recency prediction only; hydrology, demographics, detection, and learning remain inseparable.'
        out['uncertainty_boundary'] = 'Route bootstrap conditions on the trained coefficients; training uncertainty and spatial dependence across routes not included.'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print('RESULT_JSON_BEGIN', flush=True)
    print(json.dumps(out, indent=2, sort_keys=True), flush=True)
    print('RESULT_JSON_END', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT/'research/output/RECENT_VS_OLDER_SITE_HISTORY_2026-10-19.json')
    args = p.parse_args()
    run(args.output)
