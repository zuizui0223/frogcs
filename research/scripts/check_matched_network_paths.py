"""Exploratory conditional associations in the unchanged 4,040 matched pairs.

Endpoint utilities include all O/S/V interaction terms. Their differences,
not products of differences, enter an intercept-free paired logistic model.
Route-component sandwich intervals account for repeated pairs/sites within
components. These are conditional associations, not mediated causal effects.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import rankdata, t

ROOT = Path(__file__).resolve().parents[2]
TERMS = ['O', 'S', 'V', 'O:S', 'O:V', 'S:V', 'O:S:V']


def endpoint_rank(d, feature):
    a = d['chosen_' + feature].to_numpy(float)
    b = d['silent_' + feature].to_numpy(float)
    r = rankdata(np.r_[a, b]); r = (r-r.mean())/r.std()
    return r[:len(d)], r[len(d):]


def fit(x, groups):
    n, p = x.shape
    assert np.linalg.matrix_rank(x) == p, 'Unidentified paired design'
    # Numerical column scaling does not change the reported coefficient scale.
    scale = np.sqrt(np.mean(x*x, axis=0)); z = x/scale
    opt = minimize(lambda b: np.logaddexp(0., -z@b).mean(), np.zeros(p),
                   jac=lambda b: z.T@(expit(z@b)-1)/n,
                   method='BFGS', options={'gtol': 1e-10, 'maxiter': 2000})
    gradient = float(np.max(np.abs(z.T@(expit(z@opt.x)-1)/n)))
    assert gradient < 1e-7, (opt.message, gradient)
    beta = opt.x/scale; probability = expit(x@beta)
    hessian = x.T@((probability*(1-probability))[:, None]*x)
    score = pd.DataFrame(x*(1-probability)[:, None]).groupby(groups).sum().to_numpy()
    g = len(score); bread = np.linalg.inv(hessian)
    covariance = bread@(score.T@score)@bread * (g/(g-1))*((n-1)/(n-p))
    se = np.sqrt(np.maximum(0., np.diag(covariance)))
    width = t.ppf(.975, g-1)*se
    return beta, beta-width, beta+width, {
        'n': n, 'route_components': g, 'rank': p,
        'condition_scaled_design': float(np.linalg.cond(z)),
        'max_scaled_gradient': gradient, 'optimizer_success': bool(opt.success)}


def main():
    source = ROOT/'research/results/naamp_prior_water_20261026/fixed_pairs_joint_ecological_context.csv.gz'
    d = pd.read_csv(source)
    assert len(d) == 4040
    out = ROOT/'research/results/path_matched_adjustment_20261026'; out.mkdir(exist_ok=True)
    water = endpoint_rank(d, 'mean_water_frequency_3000m')
    history = endpoint_rank(d, 'prior')
    rows, metadata = [], []
    for bg in ['uniform', 'target_group']:
        o = endpoint_rank(d, 'mean_suitability_Odonata_'+bg)
        s = endpoint_rank(d, 'mean_suitability_pond_breeding_Caudata_'+bg)
        v = endpoint_rank(d, 'flooded_3000m_mean')
        utility = [np.column_stack([o[k], s[k], v[k], o[k]*s[k], o[k]*v[k],
                                    s[k]*v[k], o[k]*s[k]*v[k]]) for k in [0, 1]]
        base = utility[0]-utility[1]
        for label, covariates in [('network', []), ('plus_water', [water]),
                                  ('plus_water_history', [water, history])]:
            terms = TERMS + ['prior_water', 'prior_use'][:len(covariates)]
            x = np.column_stack([base]+[a-b for a, b in covariates])
            assert np.isfinite(x).all()
            beta, low, high, info = fit(x, d.route_component)
            flipped, _, _, _ = fit(-x, d.route_component)
            assert np.allclose(beta, -flipped, atol=1e-7)
            info.update(background=bg, specification=label,
                        zero_difference_fraction={name: float(np.mean(x[:, j] == 0))
                                                  for j, name in enumerate(terms)})
            metadata.append(info)
            for j, term in enumerate(terms):
                rows.append(dict(background=bg, specification=label, term=term,
                                 beta=beta[j], low=low[j], high=high[j]))
    result = pd.DataFrame(rows); result.to_csv(out/'coefficients.csv', index=False)
    meta = {'classification': 'EXPLORATORY_MATCHED_CONDITIONAL_ASSOCIATION',
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'scaling': 'Fixed standardized ranks over the 8,080 paired endpoints; repeated sites retain pair frequency',
            'uncertainty': 'Route-component clustered sandwich, t interval; conditional on fitted SDM, matching and scaling; no multiplicity adjustment',
            'weighting': 'Equal pair weight; not equal route weight',
            'same_cohort_all_models': True, 'rematched': False,
            'interpretation': 'Conditional strong-versus-silent association, not the primary site-level strong-visit fraction estimand; prior use can be mediator or shared habitat proxy',
            'fits': metadata}
    (out/'validation.json').write_text(json.dumps(meta, indent=2)+'\n', encoding='utf-8')
    print(result[result.term.isin(['O:S', 'O:V', 'S:V', 'O:S:V', 'prior_use'])].to_string(index=False))
    print('Route components', d.route_component.nunique())


if __name__ == '__main__':
    main()
