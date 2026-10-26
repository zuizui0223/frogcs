"""Thresholded potential richness and allocation tests for a fixed species pool."""
import argparse
import json
import hashlib
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

from broad_species_sdm import features, thin, fold

ROOT = Path(__file__).resolve().parents[2]
COLS = ['bio1','bio4','bio12','bio15','flooded','water']
POND = {'Notophthalmus viridescens','Ambystoma maculatum','Ambystoma tigrinum','Ambystoma opacum',
        'Ambystoma laterale','Ambystoma mavortium'}


def boot_mean(x):
    x = np.asarray(x, float)
    if not len(x):
        raise ValueError('No complete routes')
    rng = np.random.default_rng(20261026)
    draws = [rng.choice(x, len(x), replace=True).mean() for _ in range(2000)]
    lo,hi = np.quantile(draws,[.025,.975])
    return dict(mean=float(x.mean()), low=float(lo), high=float(hi), routes=len(x))


def paired_test(group, pairs):
    lookup = group.set_index('site')
    q = pairs.copy()
    q['a'] = q.chosen_site.map(lookup.potential_richness)
    q['b'] = q.silent_site.map(lookup.potential_richness)
    q = q.dropna(subset=['a','b'])
    q['difference'] = q.a-q.b
    return dict(pairs=len(q), **boot_mean(q.groupby('route').difference.mean()))


def heldout_allocation(pred, stacks, pairs, out):
    results, scores_all = [], []
    for kind in ('uniform','target_group'):
        table = pred[pred.background==kind].pivot(index='site', columns='species_key', values='suitability_percentile')
        richness = stacks[(stacks.background==kind)&(stacks.omission==.1)&(stacks.group.isin(['Anura','Caudata','Odonata']))]
        richness = richness.pivot(index='site',columns='group',values='potential_richness')
        pairs_ok = pairs[pairs.chosen_site.isin(table.index)&pairs.silent_site.isin(table.index)].copy()
        xa = table.reindex(pairs_ok.chosen_site).to_numpy()-table.reindex(pairs_ok.silent_site).to_numpy()
        xr = richness.reindex(pairs_ok.chosen_site).to_numpy()-richness.reindex(pairs_ok.silent_site).to_numpy()
        history = pairs_ok.history_difference.to_numpy()[:,None]
        valid = np.isfinite(xa).all(axis=1)&np.isfinite(xr).all(axis=1)&np.isfinite(history[:,0])
        pairs_ok = pairs_ok.loc[valid].reset_index(drop=True)
        xa,xr,history = xa[valid],xr[valid],history[valid]
        routes = pairs_ok.route.to_numpy()
        groups = np.array([int(hashlib.sha256(r.encode()).hexdigest()[:8],16)%5 for r in routes])
        configs = {'richness':xr,'composition':xa,'history':history,
                   'history_richness':np.column_stack([history,xr]),
                   'history_composition':np.column_stack([history,xa])}
        log_scores = {}
        for name,x in configs.items():
            score = np.full(len(x),np.nan)
            for k in range(5):
                tr,te = groups!=k,groups==k
                counts = pd.Series(routes[tr]).value_counts()
                weights = np.array([1/counts[r] for r in routes[tr]])
                xx = np.vstack([x[tr],-x[tr]])
                yy = np.r_[np.ones(tr.sum()),np.zeros(tr.sum())]
                model = make_pipeline(StandardScaler(with_mean=False),
                                      LogisticRegression(C=1,fit_intercept=False,max_iter=2000))
                model.fit(xx,yy, logisticregression__sample_weight=np.r_[weights,weights]/2)
                score[te] = -np.logaddexp(0,-model.decision_function(x[te]))
            if not np.isfinite(score).all():
                raise ValueError('Missing held-out allocation score')
            log_scores[name] = score
            means = pd.DataFrame({'route':routes,'gain':score+np.log(2)}).groupby('route').gain.mean()
            results.append(dict(background=kind,model=name,comparison='chance',pairs=len(score),**boot_mean(means)))
            for route,gain in means.items():
                scores_all.append(dict(background=kind,model=name,route=route,gain_vs_chance=gain))
        for name in ('history_richness','history_composition'):
            means = pd.DataFrame({'route':routes,'gain':log_scores[name]-log_scores['history']}).groupby('route').gain.mean()
            results.append(dict(background=kind,model=name,comparison='history',pairs=len(routes),**boot_mean(means)))
    pd.DataFrame(results).to_csv(out/'allocation_model_comparison.csv',index=False)
    pd.DataFrame(scores_all).to_csv(out/'allocation_route_scores.csv',index=False)
    return results


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--source-commit',default='a24cf204501bcd5ce20f0c5fe6a47396723803a5')
    ap.add_argument('--source-run',type=int,default=40276858237)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    if sklearn.__version__!='1.6.1':
        raise RuntimeError('Use scikit-learn 1.6.1 to replay the source models')
    presence=pd.read_csv(args.results/'training_presence_environment.csv.gz',dtype={'id':str,'species_key':str})
    bg=pd.read_csv(args.results/'background.csv.gz')
    sites=pd.read_csv(args.results/'naamp_site_environment.csv.gz')
    predictions=pd.read_csv(args.results/'naamp_species_suitability.csv.gz',dtype={'species_key':str})
    models=json.loads((args.results/'models.json').read_text())
    pairs=pd.read_csv(ROOT/'research/results/naamp_three_guild_occurrence/full_naamp_history/matched_strong_silent_history.csv')
    sx=sites[COLS].to_numpy()
    ok=np.isfinite(sx).all(axis=1)
    if not ok.all():
        sites=sites.loc[ok].reset_index(drop=True)
        sx=sx[ok]
    stacks, thresholds, validation, replay=[],[],[],[]
    indicators={}
    for m in models:
        if m['status']!='fit':
            continue
        sid,kind=str(m['species_key']),m['background']
        pr=presence[presence.species_key==sid]
        px=pr[COLS].to_numpy()
        if kind=='uniform':
            br=bg
        else:
            candidates=presence[(presence.guild==m['guild'])&(presence.species_key!=sid)]
            kept=thin(candidates.to_dict('records'))
            br=pd.DataFrame(kept)
        bx=br[COLS].to_numpy()
        x=np.vstack([px,bx]); y=np.r_[np.ones(len(px)),np.zeros(len(bx))]
        model=features(x); model.fit(x,y)
        ps=model.decision_function(px)
        ss=model.decision_function(sx)
        uniform_scores=np.sort(model.decision_function(bg[COLS].to_numpy()))
        rank=np.searchsorted(uniform_scores,ss,side='right')/len(uniform_scores)
        original=predictions[(predictions.species_key==sid)&(predictions.background==kind)].set_index('site').suitability_percentile
        delta=np.max(np.abs(rank-original.reindex(sites.site).to_numpy()))
        if delta>.002:
            raise ValueError(f'Source replay differs for {sid} {kind}: {delta}')
        replay.append(dict(species_key=sid,background=kind,max_percentile_difference=float(delta)))
        for omission in (.05,.1,.2):
            cutoff=float(np.quantile(ps,omission))
            thresholds.append(dict(species_key=sid,species=m['species'],guild=m['guild'],background=kind,
                                   omission=omission,decision_cutoff=cutoff))
            indicators[(sid,kind,omission)]=(ss>=cutoff).astype(int)
        # Independent spatial validation of the 10%-omission threshold.
        xy=pd.concat([pr[['lon','lat']],br[['lon','lat']]],ignore_index=True)
        for size in (2,4):
            f=np.array([fold(r.lon,r.lat,size) for r in xy.itertuples()])
            for k in range(5):
                tr,te=f!=k,f==k
                train_presence=tr&(y==1)
                test_presence=te&(y==1)
                if train_presence.sum()<20 or test_presence.sum()<5 or (tr&(y==0)).sum()<20:
                    continue
                fm=features(x); fm.fit(x[tr],y[tr])
                cutoff=np.quantile(fm.decision_function(x[train_presence]),.1)
                retention=float((fm.decision_function(x[test_presence])>=cutoff).mean())
                validation.append(dict(species_key=sid,background=kind,block_degrees=size,fold=k,
                                       heldout_presences=int(test_presence.sum()),retention=retention))
    pd.DataFrame(replay).to_csv(args.out/'source_replay_checks.csv',index=False)
    pd.DataFrame(thresholds).to_csv(args.out/'species_thresholds.csv',index=False)
    pd.DataFrame(validation).to_csv(args.out/'heldout_threshold_retention.csv',index=False)
    metadata={str(m['species_key']):m for m in models if m['status']=='fit'}
    comparison=[]
    for kind in ('uniform','target_group'):
      for omission in (.05,.1,.2):
        for group in ('Anura','Caudata','Odonata','pond_breeding_Caudata'):
            keys=[sid for sid,m in metadata.items() if (m['guild']==group or (group=='pond_breeding_Caudata' and m['species'] in POND))]
            binary=np.column_stack([indicators[(sid,kind,omission)] for sid in keys])
            richness=binary.sum(axis=1)
            frame=pd.DataFrame(dict(site=sites.site,group=group,background=kind,omission=omission,
                                    pool_size=len(keys),potential_richness=richness))
            stacks.append(frame)
            summary=paired_test(frame,pairs)
            lookup={s:i for i,s in enumerate(sites.site)}
            paired=pairs[pairs.chosen_site.isin(lookup)&pairs.silent_site.isin(lookup)].copy()
            ia=[lookup[s] for s in paired.chosen_site]; ib=[lookup[s] for s in paired.silent_site]
            union=np.maximum(binary[ia],binary[ib]).sum(axis=1)
            intersect=np.minimum(binary[ia],binary[ib]).sum(axis=1)
            paired['jaccard_dissimilarity']=np.divide(union-intersect,union,out=np.zeros(len(union),float),where=union>0)
            summary['mean_route_jaccard_dissimilarity']=float(paired.groupby('route').jaccard_dissimilarity.mean().mean())
            comparison.append(dict(group=group,background=kind,omission=omission,pool_size=len(keys),**summary))
    stacks=pd.concat(stacks,ignore_index=True)
    stacks.to_csv(args.out/'naamp_group_potential_richness.csv.gz',index=False)
    pd.DataFrame(comparison).to_csv(args.out/'matched_group_comparison.csv',index=False)
    allocations=heldout_allocation(predictions,stacks,pairs,args.out)
    pool=dict(Counter(m['guild'] for m in metadata.values()))
    pool['pond_breeding_Caudata']=sum(m['species'] in POND for m in metadata.values())
    summary=dict(species_pool=pool,
                 projected_sites=len(sites),primary_omission=.1,
                 richness_definition='Number of modeled species above a species-specific training-presence threshold; not total richness or expected occupied species',
                 source_code_commit=args.source_commit,
                 source_workflow_run=args.source_run,sklearn_version=sklearn.__version__,
                 maximum_source_replay_difference=max(r['max_percentile_difference'] for r in replay),
                 matched_comparisons=comparison,allocation_comparisons=allocations)
    (args.out/'observed_results.json').write_text(json.dumps(summary,indent=2,allow_nan=False),encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('matched_comparisons','allocation_comparisons')},indent=2))


if __name__=='__main__':
    main()
