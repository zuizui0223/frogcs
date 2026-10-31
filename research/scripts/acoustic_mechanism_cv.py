"""Out-of-spatial-block acoustic prediction from frozen trophic response surfaces.

This is a *statistical* observation bridge, not density or calling calibration.
Source labels, species suitability and landscape vegetation are not local counts,
pond refuge or independently observed life-history states.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.linalg import qr
from scipy.special import expit
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz'
VISITS = ROOT / 'research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz'
SURFACES = ROOT / 'research/results/handling_factorial_20261029/dense21_cells.csv.gz'
OUT = ROOT / 'research/results/acoustic_bridge_20261031'
SEED = 20261031
ARMS = ('0000', '1000', '0100', '1100', '1111')
REPLACEMENTS = tuple('replace_' + arm for arm in ARMS)
BACKGROUNDS = ('uniform', 'target_group')
SURVEY = ('n_visits', 'n_years', 'mean_air', 'mean_noise', 'season_2', 'season_3', 'season_4', 'mean_doy')
ENV = ('bio1', 'bio4', 'bio12', 'bio15', 'water_3000m_mean', 'herbaceous_3000m_mean')
TERMS = ('O', 'S', 'V', 'OS', 'OV', 'SV', 'OSV')
N_FOLDS = 5
RIDGE = 10.0  # one pre-fixed penalty, never tuned on held-out calls


def zrank(values):
    a = np.asarray(values, dtype=float)
    r = rankdata(a, axis=0)
    return (r - r.mean(axis=0)) / np.maximum(r.std(axis=0), 1e-12)


def prepare_sites(sites: pd.DataFrame, visits: pd.DataFrame, expected_sites: int | None = None):
    """Reconstruct binomial site outcomes from completed *visits* only."""
    if sites.site.duplicated().any():
        raise ValueError('Duplicate site IDs')
    v = visits[(visits.timeout == 0) & visits.site.isin(sites.site)].copy()
    if v.duplicated(['site', 'run']).any():
        raise ValueError('Duplicate completed survey visits')
    if (v.strong > v['any']).any() or not v.strong.isin([0, 1]).all():
        raise ValueError('Invalid strong-call event')
    counts = v.groupby('site').strong.agg(['sum', 'count']).rename(columns={'sum': 'k', 'count': 'n'})
    d = sites.merge(counts, left_on='site', right_index=True, how='left', validate='one_to_one')
    if d[['k', 'n']].isna().any().any() or (d.n < 1).any():
        raise ValueError('Missing completed site visit')
    if 'n_visits' in d and not np.array_equal(d.n.to_numpy(), d.n_visits.to_numpy()):
        raise ValueError('Visit count differs from original site ledger')
    if 'strong_rate' in d and not np.allclose(d.k / d.n, d.strong_rate, atol=1e-12):
        raise ValueError('Strong-call aggregate differs from frozen site result')
    for run in (2, 3, 4):
        d[f'season_{run}'] = d.site.map(v.assign(yes=v.season == run).groupby('site').yes.mean())
    d['mean_doy'] = d.site.map(v.groupby('site').doy.mean())
    centers = d.groupby('route')[['lat', 'lon']].mean()
    block = (np.floor(centers.lat / 2).astype(int).astype(str) + '_' +
             np.floor(centers.lon / 2).astype(int).astype(str))
    d['spatial_block'] = d.route.map(block)
    d['V'] = (d.flooded_3000m_mean.to_numpy() > 0).astype(int)
    if expected_sites is not None and len(d) != expected_sites:
        raise ValueError(f'Expected {expected_sites} sites, observed {len(d)}')
    required = list(SURVEY + ENV) + ['lat', 'lon', 'V']
    for bg in BACKGROUNDS:
        required += [f'mean_suitability_Odonata_{bg}', f'mean_suitability_pond_breeding_Caudata_{bg}']
    if not np.isfinite(d[required].to_numpy(dtype=float)).all():
        raise ValueError('Nonfinite site predictors')
    return d.reset_index(drop=True)


def assign_spatial_folds(d: pd.DataFrame, folds: int = N_FOLDS):
    """Balance overall and vegetation-positive support using only predictors."""
    blocks = d.groupby('spatial_block').agg(n=('site', 'size'), positive=('V', 'sum'))
    if len(blocks) < folds or (d.V > 0).sum() < folds:
        raise ValueError('Insufficient distinct spatial blocks / positive vegetation')
    blocks = blocks.reset_index()
    blocks['tie'] = np.random.default_rng(SEED).random(len(blocks))
    blocks = blocks.sort_values(['n', 'positive', 'tie'], ascending=[False, False, True])
    fold_n = np.zeros(folds, dtype=float)
    fold_pos = np.zeros(folds, dtype=float)
    mapping = {}
    target_n = max(len(d) / folds, 1)
    target_p = max(float(d.V.sum()) / folds, 1)
    for r in blocks.itertuples(index=False):
        # Marginal cost of adding each whole block to a fold.
        score = ((fold_n + r.n) / target_n)**2 - (fold_n / target_n)**2
        score += ((fold_pos + r.positive) / target_p)**2 - (fold_pos / target_p)**2
        i = int(np.argmin(score))
        mapping[r.spatial_block] = i
        fold_n[i] += r.n
        fold_pos[i] += r.positive
    assigned = d.spatial_block.map(mapping).to_numpy(dtype=int)
    if np.unique(assigned).size != folds or not all((d.V[assigned == i] > 0).any() for i in range(folds)):
        raise ValueError('Fold lacks sites or vegetation-positive observations')
    if d.assign(fold=assigned).groupby('route').fold.nunique().max() != 1:
        raise ValueError('Route leaked across folds')
    return assigned


def extract_frozen_surfaces(cells: pd.DataFrame, levels: int = 21):
    """Fail closed if saved mechanism surface is incomplete or mislabeled."""
    expected = np.linspace(.25, 2., levels)
    surfaces = {}
    for arm in ARMS:
        g = cells[cells.arm.astype(str).str.zfill(4) == arm]
        if len(g) != 2 * levels * levels or g.duplicated(['vegetation', 'S_source', 'D_source']).any():
            raise ValueError(f'Missing/duplicated grid cells for arm {arm}')
        g = g.sort_values(['vegetation', 'S_source', 'D_source']).reset_index(drop=True)
        grid = [(v, s, o) for v in (0., 1.) for s in expected for o in expected]
        if not np.allclose(g[['vegetation', 'S_source', 'D_source']].to_numpy(float), grid, atol=1e-9):
            raise ValueError(f'Unexpected grid axis or order for arm {arm}')
        values = g.F_B.to_numpy(float)
        if not np.isfinite(values).all() or (values <= 0).any():
            raise ValueError(f'Invalid F_B in arm {arm}')
        surfaces[arm] = values.reshape(2, levels, levels)
    return surfaces


def rank_bin(x, levels: int):
    ranks = rankdata(np.asarray(x, dtype=float))
    return np.rint(((ranks - .5) / len(ranks)) * (levels - 1)).astype(int)


def candidate_surface(d: pd.DataFrame, background: str, surfaces: dict):
    if background not in BACKGROUNDS:
        raise ValueError(background)
    n = next(iter(surfaces.values())).shape[-1]
    o = d[f'mean_suitability_Odonata_{background}'].to_numpy()
    s = d[f'mean_suitability_pond_breeding_Caudata_{background}'].to_numpy()
    oi, si = rank_bin(o, n), rank_bin(s, n)
    v = d.V.to_numpy(dtype=int)
    if not np.isin(v, [0, 1]).all():
        raise ValueError('Vegetation must be binary')
    return {arm: np.log(grid[v, si, oi]) for arm, grid in surfaces.items()}


def base_matrix(d: pd.DataFrame, background: str, interactions: bool):
    o = zrank(d[f'mean_suitability_Odonata_{background}'])
    s = zrank(d[f'mean_suitability_pond_breeding_Caudata_{background}'])
    v = d.V.to_numpy(dtype=float)
    lat, lon = zrank(d[['lat', 'lon']].to_numpy()).T
    x = [o, s, v]
    if interactions:
        x.extend((o * s, o * v, s * v, o * s * v))
    x.extend(d[c].to_numpy(dtype=float) for c in SURVEY + ENV)
    x.extend((lat, lon, lat * lat, lat * lon, lon * lon))
    a = np.column_stack(x)
    if not np.isfinite(a).all():
        raise ValueError('Invalid design')
    return a


def train_predict(xtrain, ytrain, ntrain, xtest, ridge: float = RIDGE):
    """Fit acoustic binomial observation link on training sites only."""
    mu, sd = xtrain.mean(axis=0), xtrain.std(axis=0)
    good = sd > 1e-12
    z = (xtrain[:, good] - mu[good]) / sd[good]
    t = (xtest[:, good] - mu[good]) / sd[good]
    z = np.column_stack([np.ones(len(z)), z])
    t = np.column_stack([np.ones(len(t)), t])
    if np.any(ntrain <= 0) or np.any(ytrain < 0) or np.any(ytrain > ntrain):
        raise ValueError('Invalid binomial counts')
    p0 = np.clip(ytrain.sum() / ntrain.sum(), 1e-6, 1-1e-6)
    initial = np.zeros(z.shape[1]);initial[0] = np.log(p0/(1-p0))
    def objective(beta):
        lin = z @ beta
        loss = np.logaddexp(0, lin) @ ntrain - lin @ ytrain + ridge * (beta[1:] @ beta[1:]) / 2
        grad = z.T @ (ntrain * expit(lin) - ytrain)
        grad[1:] += ridge * beta[1:]
        return float(loss), grad
    result = minimize(objective, initial, jac=True, method='L-BFGS-B', options={'maxiter': 500, 'ftol': 1e-11})
    if not result.success and np.linalg.norm(result.jac, ord=np.inf) > .1:
        raise RuntimeError(f'Binomial optimizer: {result.message}')
    probability = expit(t @ result.x)
    return np.clip(probability, 1e-10, 1 - 1e-10)


def log_score(k, n, probability):
    p = np.clip(np.asarray(probability, dtype=float), 1e-10, 1-1e-10)
    return -(np.asarray(k)*np.log(p) + (np.asarray(n)-np.asarray(k))*np.log1p(-p))


def out_of_block_predictions(d: pd.DataFrame, surfaces: dict, folds: np.ndarray):
    out = []
    for bg in BACKGROUNDS:
        predictions = candidate_surface(d, bg, surfaces)
        baseline = base_matrix(d, bg, interactions=True)
        additive = base_matrix(d, bg, interactions=False)
        options = {'env_interactions': baseline, 'env_additive': additive}
        options.update({arm: np.column_stack([baseline, feature]) for arm, feature in predictions.items()})
        # Exploratory extension AFTER first primary results: structural response
        # surfaces replace, rather than augment, four free empirical interactions.
        options.update({'replace_'+arm: np.column_stack([additive, feature]) for arm, feature in predictions.items()})
        for fold in range(int(np.max(folds)) + 1):
            test = folds == fold
            train = ~test
            if not train.any() or not test.any():
                raise ValueError('Empty train/test fold')
            for arm, design in options.items():
                p = train_predict(design[train], d.k.to_numpy()[train], d.n.to_numpy()[train], design[test])
                for j, pos in enumerate(np.flatnonzero(test)):
                    out.append(dict(site=d.site.iloc[pos], route=d.route.iloc[pos], spatial_block=d.spatial_block.iloc[pos],
                                    fold=fold, background=bg, candidate=arm, k=int(d.k.iloc[pos]), n=int(d.n.iloc[pos]),
                                    V=int(d.V.iloc[pos]), predicted=float(p[j])))
    result = pd.DataFrame(out)
    if result.duplicated(['site', 'background', 'candidate']).any():
        raise ValueError('Duplicate held-out predictions')
    return result


def paired_block_interval(data: pd.DataFrame, reps: int = 999):
    """Paired block intervals; conditional on frozen spatial CV predictions."""
    rows=[];fold=[]
    for (bg, arm), group in data.groupby(['background', 'candidate']):
        n=group.n.to_numpy(dtype=float);k=group.k.to_numpy(dtype=float);p=group.predicted.to_numpy()
        score=log_score(k,n,p)
        rows.append(dict(background=bg,candidate=arm,n_sites=len(group),n_surveys=int(n.sum()),
                         positive_vegetation_sites=int(group.V.sum()),n_spatial_blocks=group.spatial_block.nunique(),
                         nll_per_survey=float(score.sum()/n.sum()),
                         brier_per_survey=float(np.sum(k*(1-p)**2+(n-k)*p**2)/n.sum())))
        for block_id,g in group.assign(loss=score).groupby(['fold']):
            fold.append(dict(background=bg,candidate=arm,fold=int(block_id[0]),n_surveys=int(g.n.sum()),
                             positive_vegetation_sites=int(g.V.sum()),nll_per_survey=float(g.loss.sum()/g.n.sum())))
    summary=pd.DataFrame(rows);fold_scores=pd.DataFrame(fold)
    for bg in BACKGROUNDS:
        for base,label in [('env_interactions','interaction'),('env_additive','additive')]:
            b=data[(data.background==bg)&(data.candidate==base)][['site','spatial_block','n','k','predicted']].rename(columns={'predicted':'p_null'})
            for arm in ARMS + REPLACEMENTS:
                g=data[(data.background==bg)&(data.candidate==arm)][['site','spatial_block','n','k','predicted']]
                pair=g.merge(b,on=['site','spatial_block','n','k'],validate='one_to_one')
                if len(pair)!=len(g) or len(pair)!=len(b):
                    raise ValueError('Unpaired held-out comparison')
                lossdiff=log_score(pair.k,pair.n,pair.p_null)-log_score(pair.k,pair.n,pair.predicted)
                block=pair.assign(delta=lossdiff).groupby('spatial_block')[['delta','n']].sum()
                vec=block[['delta','n']].to_numpy(dtype=float)
                rng=np.random.default_rng(SEED)
                draw=rng.integers(0,len(vec),size=(reps,len(vec)))
                bootstrap=vec[draw].sum(axis=1)
                improvement=bootstrap[:,0]/bootstrap[:,1]
                mask=(summary.background==bg)&(summary.candidate==arm)
                prefix='gain_vs_'+label+'_null'
                summary.loc[mask,prefix] = float(lossdiff.sum()/pair.n.sum())
                summary.loc[mask,prefix+'_low_conditional'] = float(np.quantile(improvement,.025))
                summary.loc[mask,prefix+'_high_conditional'] = float(np.quantile(improvement,.975))
    return summary,fold_scores


def pattern_diagnostic(d: pd.DataFrame, predictions: pd.DataFrame):
    """Same acoustic response-space interaction estimand, *not* a selection score."""
    results=[]
    lookup=d.set_index('site')
    for bg in BACKGROUNDS:
        o=zrank(d[f'mean_suitability_Odonata_{bg}'])
        s=zrank(d[f'mean_suitability_pond_breeding_Caudata_{bg}'])
        v=zrank(d.V)
        x=np.column_stack([o,s,v,o*s,o*v,s*v,o*s*v])
        lat,lon=zrank(d[['lat','lon']].to_numpy()).T
        cov=np.column_stack([zrank(d[list(SURVEY + ENV)].to_numpy()),lat,lon,lat*lat,lat*lon,lon*lon])
        nuisance=np.column_stack([np.ones(len(d)),cov])
        _,rr,order=qr(nuisance,mode='economic',pivoting=True)
        nn=int(np.sum(np.abs(np.diag(rr)) > 1e-9 * max(1., np.linalg.norm(nuisance))))
        nuisance=nuisance[:,order[:nn]]
        focal=x-nuisance@np.linalg.lstsq(nuisance,x,rcond=1e-10)[0]
        if np.linalg.matrix_rank(focal, tol=1e-8) < 7:
            raise ValueError('Unidentified focal interaction terms')
        z=np.column_stack([x,nuisance])
        for candidate in ('observed', 'env_interactions', 'env_additive') + ARMS + REPLACEMENTS:
            if candidate=='observed':
                y=d.k.to_numpy()/d.n.to_numpy()
            else:
                preds=predictions[(predictions.background==bg)&(predictions.candidate==candidate)].set_index('site')
                if len(preds)!=len(d) or not preds.index.is_unique:
                    raise ValueError('Missing predicted sites')
                y=lookup.index.map(preds.predicted).to_numpy(dtype=float)
            b=np.linalg.lstsq(z,zrank(y),rcond=1e-10)[0]
            results.append(dict(background=bg,candidate=candidate,**{term:float(b[i]) for i,term in enumerate(TERMS)}))
    return pd.DataFrame(results)


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    d=prepare_sites(pd.read_csv(SITE),pd.read_csv(VISITS),expected_sites=4248)
    surfaces=extract_frozen_surfaces(pd.read_csv(SURFACES,dtype={'arm':str}))
    folds=assign_spatial_folds(d)
    preds=out_of_block_predictions(d,surfaces,folds)
    score,foldscore=paired_block_interval(preds)
    diag=pattern_diagnostic(d,preds)
    preds.to_csv(OUT/'heldout_site_predictions.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    score.to_csv(OUT/'candidate_scores.csv',index=False)
    foldscore.to_csv(OUT/'fold_scores.csv',index=False)
    diag.to_csv(OUT/'observed_predicted_interactions.csv',index=False)
    blocks=d.assign(fold=folds).groupby(['spatial_block','fold']).agg(n_sites=('site','size'),positive_V=('V','sum'),n_visits=('n','sum')).reset_index()
    blocks.to_csv(OUT/'fold_support.csv',index=False)
    receipt=dict(status='CONDITIONAL_PREDICTIVE_BRIDGE_NOT_BIOLOGICALLY_CALIBRATED',
                 seed=SEED,folds=N_FOLDS,ridge=RIDGE,arms=list(ARMS),backgrounds=list(BACKGROUNDS),
                 site_count=len(d),visit_count=int(d.n.sum()),surface_levels=21,
                 score='out-of-block binomial nll per completed survey, fixed two-degree route-mean spatial blocks',
                 mapping='predictor-only suitability ranks -> D/S model source ranks; positive 3km flooded vegetation -> V=1',
                 fitted_link='binomial logit of environmental controls and log seasonal F_B; training blocks only',
                 caveats=['F_B not mature calling males','suitability not predator density','landscape vegetation not pond refuge',
                          'survey timing controls do not estimate detection','block bootstrap conditional on fitted folds',
                          'positive score does not establish trophic causality'],
                 sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (SITE,VISITS,SURFACES)},
                 runtime={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__})
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(score[['background','candidate','nll_per_survey','gain_vs_interaction_null','gain_vs_additive_null']].to_string(index=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true',help='Require explicit full-data run; no accidental source download')
    args=parser.parse_args()
    if not args.run:
        parser.error('Use --run to execute on the fixed original-source data')
    run()
