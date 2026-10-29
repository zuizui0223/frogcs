"""Vegetation-context test at actual sites; no stage or density imputation."""
import json
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.linalg import qr

from nee_context_robustness import ROOT, SITE, VISITS, SURVEY, ENV, zrank, load, centered_by_route, block_stats

OUT = ROOT / 'research/results/mechanism_site_20261029'


def fit_setup(x, c, y, groups, mode):
    g = pd.factorize(groups, sort=True)[0]
    if mode == 'within':
        x = centered_by_route(x, g); c = centered_by_route(c, g)
        y = centered_by_route(y, g)[:, 0]
        nuisance = c
    else:
        nuisance = np.column_stack([np.ones(len(y)), c])
    _, r, p = qr(nuisance, mode='economic', pivoting=True)
    rank = int(np.sum(np.abs(np.diag(r)) > max(1., np.linalg.norm(nuisance))*1e-10))
    nuisance = nuisance[:, p[:rank]]
    resid = x - nuisance @ np.linalg.lstsq(nuisance, x, rcond=1e-10)[0]
    sv = np.linalg.svd(resid, compute_uv=False)
    if sv[-1] < max(1., sv[0])*1e-9:
        raise ValueError('UNIDENTIFIABLE_FOCAL_TERMS')
    return np.column_stack([x, nuisance]), y, float(sv[0]/sv[-1])


def main():
    OUT.mkdir(exist_ok=True, parents=True)
    d = load(); vegetation = d.flooded_3000m_mean.to_numpy()
    v = zrank(vegetation); oref = vegetation > 0
    v0 = float(v[~oref][0]); vp = float(np.median(v[oref]))
    obs = zrank(d[SURVEY].to_numpy()); env = zrank(d[ENV].to_numpy())
    ll = zrank(d[['lat', 'lon']].to_numpy())
    cov = np.column_stack([obs, env, ll, ll[:, 0]**2, ll[:, 0]*ll[:, 1], ll[:, 1]**2])
    y = zrank(d.strong_rate.to_numpy())
    rows, diagnostics, site_values, coefficient_rows = [], [], [], []
    cache = {}
    old = pd.read_csv(ROOT/'research/results/nee_context_20261029/coefficients.csv')
    for bg in ['uniform', 'target_group']:
        o = zrank(d['mean_suitability_Odonata_'+bg]); s = zrank(d['mean_suitability_pond_breeding_Caudata_'+bg])
        for group in ['all', 'zero_detected', 'positive_detected']:
            mask = np.ones(len(d), bool) if group == 'all' else ~oref if group == 'zero_detected' else oref
            ref = 0. if group == 'all' else v0 if group == 'zero_detected' else vp
            vv = v - ref
            names = ['O', 'S', 'O:S'] if group == 'zero_detected' else ['O', 'S', 'V', 'O:S', 'O:V', 'S:V', 'O:S:V']
            x = np.column_stack([o, s, o*s]) if group == 'zero_detected' else np.column_stack([o, s, vv, o*s, o*vv, s*vv, o*s*vv])
            nfocus = x.shape[1]; sub = d[mask]
            for mode in ['pooled', 'within']:
                z, yy, condition = fit_setup(x[mask], cov[mask], y[mask], sub.route, mode)
                beta = np.linalg.lstsq(z, yy, rcond=1e-10)[0][:nfocus]
                cache[(bg, group, mode)] = (z, yy, names, mask, beta)
                if group == 'all':
                    saved = old[(old.background == bg) & (old['mode'] == mode) & (old.adjustment == 'space') & (old.subset == 'all') & (old.outcome == 'strong_rate') & (old.bootstrap_cluster == 'route')]
                    np.testing.assert_allclose(beta, saved.beta.to_numpy(), atol=1e-10)
                    # This is a fitted contextual coefficient, not a local measured effect.
                    for i in range(len(d)):
                        site_values.append(dict(site=d.site.iloc[i], route=d.route.iloc[i], background=bg, mode=mode,
                            flooded_3000m_mean=vegetation[i], fitted_OS_context=beta[3]+beta[6]*v[i],
                            interpretation='ASSOCIATION_MODEL_CONTEXT_NOT_LOCAL_EFFECT'))
                for cluster in ['route', 'spatial_block']:
                    ids = pd.factorize(sub[cluster], sort=True)[0]; k = ids.max()+1
                    weights = np.random.default_rng(20261029).multinomial(k, np.full(k, 1/k), size=999)
                    xx, xy = block_stats(z, yy, ids); matrices = np.einsum('bg,gij->bij', weights, xx); rhs = weights@xy
                    boot = []
                    for a, b in zip(matrices, rhs):
                        coef, _, rank, _ = np.linalg.lstsq(a, b, rcond=1e-12)
                        if rank == z.shape[1]: boot.append(coef[:nfocus])
                    boot = np.asarray(boot)
                    meta = dict(background=bg, group=group, mode=mode, cluster=cluster, sites=len(sub), routes=sub.route.nunique(), clusters=k, valid_bootstraps=len(boot))
                    diagnostics.append({**meta, 'focal_condition': condition, 'eligible': len(boot)>=800})
                    for j, name in enumerate(names):
                        lo, hi = np.quantile(boot[:, j], [.025, .975])
                        coefficient_rows.append({**meta, 'term': name, 'beta': beta[j], 'low': lo, 'high': hi})
                    if group == 'all':
                        contrasts = [('at_zero_detection', 1., v0), ('at_positive_median', 1., vp), ('positive_minus_zero', 0., vp-v0)]
                        for label, a, b in contrasts:
                            estimate = a*beta[3]+b*beta[6]; values = a*boot[:, 3]+b*boot[:, 6]
                            lo, hi = np.quantile(values, [.025, .975])
                            rows.append({**meta, 'contrast': label, 'beta': estimate, 'low': lo, 'high': hi})
                    else:
                        j = names.index('O:S'); lo, hi = np.quantile(boot[:, j], [.025, .975])
                        rows.append({**meta, 'contrast': 'group_OS_at_reference', 'beta': beta[j], 'low': lo, 'high': hi})
    pd.DataFrame(rows).to_csv(OUT/'conditional_OS.csv', index=False)
    pd.DataFrame(coefficient_rows).to_csv(OUT/'all_coefficients.csv', index=False)
    pd.DataFrame(diagnostics).to_csv(OUT/'support.csv', index=False)
    pd.DataFrame(site_values).to_csv(OUT/'site_context_associations.csv.gz', index=False, compression={'method':'gzip','mtime':0})
    # Separate-group estimates share routes. Use the SAME global cluster draws
    # for their difference rather than subtracting independently fitted intervals.
    paired = []
    for bg in ['uniform', 'target_group']:
        for mode in ['pooled', 'within']:
            for cluster in ['route', 'spatial_block']:
                ids = pd.factorize(d[cluster], sort=True)[0]; k = ids.max()+1
                weights = np.random.default_rng(20261029).multinomial(k, np.full(k, 1/k), size=999)
                estimates, point = [], []
                for group in ['zero_detected', 'positive_detected']:
                    z, yy, names, mask, beta = cache[(bg, group, mode)]
                    j = names.index('O:S'); point.append(beta[j])
                    xx, xy = block_stats(z, yy, ids[mask]); w = weights[:, :len(xx)]
                    a = np.einsum('bg,gij->bij', w, xx); b = w@xy
                    values = np.full(999, np.nan)
                    for i in range(999):
                        coef, _, rank, _ = np.linalg.lstsq(a[i], b[i], rcond=1e-12)
                        if rank == z.shape[1]: values[i] = coef[j]
                    estimates.append(values)
                difference = estimates[1]-estimates[0]; valid = np.isfinite(difference)
                lo, hi = np.quantile(difference[valid], [.025, .975])
                paired.append(dict(background=bg, mode=mode, cluster=cluster,
                    positive_minus_zero=point[1]-point[0], low=lo, high=hi,
                    valid_bootstraps=int(valid.sum()), inference_eligible=bool(valid.sum()>=800),
                    meaning='Separate-group refits at group references; sensitivity, not the global linear moderation estimand'))
    pd.DataFrame(paired).to_csv(OUT/'paired_group_refit_differences.csv', index=False)
    # Explicit additional scale sensitivity: same design, standardized original
    # call fraction. Do not replace the prespecified rank-response comparison.
    raw_scale = []
    raw_y = (d.strong_rate.to_numpy()-d.strong_rate.mean())/d.strong_rate.to_numpy().std()
    ids = pd.factorize(d.spatial_block, sort=True)[0]; k = ids.max()+1
    weights = np.random.default_rng(20261029).multinomial(k, np.full(k,1/k),size=999)
    for bg in ['uniform','target_group']:
        for mode in ['pooled','within']:
            z, _, names, _, _ = cache[(bg,'all',mode)]
            yy = raw_y if mode == 'pooled' else centered_by_route(raw_y,pd.factorize(d.route,sort=True)[0])[:,0]
            beta = np.linalg.lstsq(z,yy,rcond=1e-10)[0]
            xx, xy = block_stats(z,yy,ids); a=np.einsum('bg,gij->bij',weights,xx); b=weights@xy
            draws=[]
            for aa,bb in zip(a,b):
                coef,_,rank,_=np.linalg.lstsq(aa,bb,rcond=1e-12)
                if rank==z.shape[1]:draws.append(coef[:7])
            draws=np.asarray(draws)
            for j,name in enumerate(names):
                lo,hi=np.quantile(draws[:,j],[.025,.975])
                raw_scale.append(dict(background=bg,mode=mode,term=name,beta=beta[j],low=lo,high=hi,
                    valid_bootstraps=len(draws),response='standardized_original_call_fraction',
                    status='ADDITIONAL_SCALE_SENSITIVITY_NOT_REPLACEMENT'))
    pd.DataFrame(raw_scale).to_csv(OUT/'raw_response_sensitivity.csv',index=False)
    profile = []
    for label, mask in [('zero_detected', ~oref), ('positive_detected', oref)]:
        q = d[mask]
        for col in ['flooded_3000m_mean', 'bio1', 'bio4', 'lat', 'mean_doy', 'n_visits']:
            profile.append(dict(group=label, variable=col, sites=len(q), routes=q.route.nunique(), median=q[col].median(), q25=q[col].quantile(.25), q75=q[col].quantile(.75)))
        for bg in ['uniform', 'target_group']:
            a = zrank(d['mean_suitability_Odonata_'+bg]); b = zrank(d['mean_suitability_pond_breeding_Caudata_'+bg])
            for oh in [False, True]:
                for sh in [False, True]:
                    zmask = mask & ((a>np.median(a))==oh) & ((b>np.median(b))==sh)
                    profile.append(dict(group=label, variable=f'{bg}_O_high={oh}_S_high={sh}', sites=int(zmask.sum()), routes=d.loc[zmask, 'route'].nunique()))
    pd.DataFrame(profile).to_csv(OUT/'site_support_profile.csv', index=False)
    receipt = dict(sites=4248, zero_detected=int((~oref).sum()), positive_detected=int(oref.sum()),
        observed_positive_median=float(np.median(vegetation[oref])), rank_v0=v0, rank_positive_median=vp,
        seed=20261029, bootstrap=999, original_global_coefficients_replayed=True,
        stage_observed_at_macro_sites=False, model_parameters_fitted_to_sites=False,
        note='Zero remote detection is not absence of pond refuge. A conditional coefficient is not a site-specific causal effect. All comparisons exploratory.')
    receipt['inputs'] = [dict(path=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [SITE, VISITS]]
    (OUT/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    model_conditions()
    print(pd.DataFrame(rows).to_string(index=False))


def model_conditions():
    p = ROOT/'research/results/model_failure_diagnosis_20261029'
    d = pd.read_csv(p/'counterfactual_pathway_decomposition.csv')
    scores = pd.read_csv(p/'counterfactual_scores.csv')
    aliases = pd.DataFrame(json.loads((p/'counterfactual_design.json').read_text())['aliases'])
    d = d.merge(scores[['model_id','block_id','joint_pass','conditional_pass','macro_form_pass']],
                on=['model_id','block_id'], validate='many_to_one')
    baseline = d[d.block_id == 0].set_index(['model_id','vegetation']).H_total_SD
    for i, r in d.iterrows():
        d.loc[i,'net_ratio_to_sameV_baseline'] = r.H_total_SD/baseline.loc[(r.model_id,r.vegetation)]
        d.loc[i,'cancellation_fraction'] = (-r.audit_H_SF_SD/r.audit_H_DF_SD
            if r.audit_H_DF_SD > 0 and r.audit_H_SF_SD < 0 else np.nan)
    d.merge(aliases,on='block_id').to_csv(OUT/'fixed_model_conditions.csv',index=False)


if __name__ == '__main__': main()
