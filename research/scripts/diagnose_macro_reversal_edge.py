"""Post-selection diagnostic: does the F→emerging-D edge improve macro prediction?

Exploratory AFTER inspecting the nested 24-scenario result, not a new locked
winner selection. Each matched pair shares source demography, refuge, arrival,
growth, and all other predation edges. Only frog reverse predation differs.
"""
from __future__ import annotations
import argparse
import hashlib
import json

import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import (
    OUT, SITE, VISITS, SOURCES, SEED, OUTER, load_cohort, scenario_surfaces,
    candidate_scores_at_sites, predictor_design, assign_folds, fit_predict, neglog
)


def matched_pairs(metadata):
    groups={}
    for key, row in metadata.items():
        label=(row["context"],row["family"],row["risk"])
        groups.setdefault(label,{})[row["edge"]]=key
    pairs=[]
    for label,entries in sorted(groups.items()):
        if set(entries)!={"dynamic","frog_reverse"}:
            raise ValueError("Reversal matched pair missing original")
        pairs.append(dict(context=label[0],family=label[1],risk=label[2],
                          off=entries["dynamic"],on=entries["frog_reverse"]))
    if len(pairs)!=12:
        raise AssertionError("Expected 12 exact reversed-edge pairs")
    return pairs


def compare_all_pairs(d,surfaces,metadata,folds,reps=999):
    pairs=matched_pairs(metadata)
    blocks=[];overall=[]
    for bg in ("uniform","target_group"):
        design=predictor_design(d,bg,candidate_scores_at_sites(d,bg,surfaces))
        for pair in pairs:
            matched=[]
            for fold in range(OUTER):
                test=folds==fold;train=~test
                reference={}
                for label in ("off","on"):
                    x=design[pair[label]]
                    pred=fit_predict(x[train],d.k.to_numpy(float)[train],d.n.to_numpy(float)[train],x[test])
                    reference[label]=pred
                sub=d.loc[test,["spatial_block","k","n"]].copy()
                sub["loss_off"]=neglog(sub.k,sub.n,reference["off"])
                sub["loss_on"]=neglog(sub.k,sub.n,reference["on"])
                matched.append(sub)
            table=pd.concat(matched)
            if len(table)!=len(d):
                raise AssertionError("Missing holdout site in paired reversal analysis")
            g=table.groupby("spatial_block")[["loss_off","loss_on","n"]].sum()
            if len(g)!=d.spatial_block.nunique():
                raise AssertionError("Missing heldout spatial block")
            for block,row in g.iterrows():
                blocks.append(dict(background=bg,**pair,spatial_block=block,
                                   n_visits=int(row.n),loss_off=float(row.loss_off),
                                   loss_on=float(row.loss_on)))
            x=g.to_numpy(float)
            rng=np.random.default_rng(SEED)
            idx=rng.integers(0,len(g),size=(reps,len(g)))
            sampled=x[idx].sum(axis=1)
            gains=(sampled[:,0]-sampled[:,1])/sampled[:,2]
            gain=(g.loss_off.sum()-g.loss_on.sum())/g.n.sum()
            overall.append(dict(background=bg,**pair,n_sites=len(d),n_visits=int(g.n.sum()),
                                n_spatial_blocks=len(g),nll_off=g.loss_off.sum()/g.n.sum(),
                                nll_on=g.loss_on.sum()/g.n.sum(),gain_on_vs_off=float(gain),
                                gain_low_conditional=float(np.quantile(gains,.025)),
                                gain_high_conditional=float(np.quantile(gains,.975))))
            print("PAIRED",bg,pair["context"],pair["family"],pair["risk"],
                  "gain",float(gain),flush=True)
    return pd.DataFrame(overall),pd.DataFrame(blocks)


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    surf,meta=scenario_surfaces([pd.read_csv(path) for path in SOURCES])
    folds=assign_folds(d,OUTER)
    scores,blocks=compare_all_pairs(d,surf,meta,folds)
    scores.to_csv(OUT/"post_selection_reversal_edge_pairs.csv",index=False)
    blocks.to_csv(OUT/"post_selection_reversal_edge_blocks.csv",index=False)
    if len(scores)!=24 or len(blocks)!=24*d.spatial_block.nunique():
        raise AssertionError("Incomplete paired counterfactual")
    receipt=dict(status="POST_SELECTION_EXPLORATORY_NOT_INDEPENDENT_VALIDATION",
                 pairs=12,backgrounds=2,blocks=d.spatial_block.nunique(),seed=SEED,
                 outcome="heldout strong-call binomial log score, positive gain favors reverse-on",
                 matched="Same growth, stage arrival, handling/refuge, vegetation mapping; only original F adult→D emerging edge toggle",
                 seed_derived_block_bootstrap_conditional=True,
                 caveat="Case84 was selected by looking at same cohort nested results; pair checks cannot confirm it independently",
                 sources={str(path.relative_to(OUT.parents[2])):hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in SOURCES},
                 code_sha256=hashlib.sha256(__import__("pathlib").Path(__file__).read_bytes()).hexdigest())
    (OUT/"post_selection_reversal_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("PAIRED REVERSAL SCORES\n"+scores.to_string(index=False))
    return scores


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run",action="store_true")
    args=ap.parse_args()
    if not args.run:ap.error("Explicit --run required")
    run()


if __name__=="__main__":
    main()
