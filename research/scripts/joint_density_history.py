"""Matched replays of the final 20 seasons of the archived joint-sign draws."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd

from abc_pom_main3600 import CONTEXTS, CORNERS, corner_contrasts
from final_mechanism_common import evaluate
import final_network_summary as annual

ROOT = Path(__file__).resolve().parents[1] / "results"
OUT = ROOT / "joint_density_history_20261111"
ARMS = ["natural", "common_frog", "matched_predators", "both_matched"]
METRICS = ["F_start","S_start","D_start","F_end","H_D","H_S","kills_D","kills_S","log_survival"]


def replay(g):
    n=len(g)
    des=g.loc[g.index.repeat(8)].reset_index(drop=True).copy()
    des[["vegetation","S_source","D_source"]]=np.tile(CORNERS,(n,1))
    for col in CONTEXTS[0]:
        des[col]=[CONTEXTS[i][col] for i in des.context_id]
    kernel=annual.simulate
    sums=np.zeros((4,n*8,len(METRICS)))
    year=0

    def observe(params, *, initial_cohorts, **options):
        nonlocal year
        natural=kernel(params, initial_cohorts=initial_cohorts, **options)
        year+=1
        if year<=60:
            return natural
        original=initial_cohorts.reshape(n,2,2,2,3)
        # Within draw, year and vegetation, preserve each predator's own
        # low/high supply contrast but remove abundance differences due to
        # the other predator's supply. Use symmetric geometric means.
        log=np.log(original)
        f=np.exp(log[...,0].mean(axis=(2,3),keepdims=True))
        s=np.exp(log[...,1].mean(axis=3,keepdims=True))
        d=np.exp(log[...,2].mean(axis=2,keepdims=True))
        for j,arm in enumerate(ARMS):
            B=original.copy()
            if arm in ("common_frog","both_matched"): B[...,0]=f
            if arm in ("matched_predators","both_matched"): B[...,1],B[...,2]=s,d
            B=B.reshape(-1,3)
            out=natural if j==0 else kernel(params,initial_cohorts=B,**options)
            log_survival=np.log(out.F_completed/B[:,0])
            np.testing.assert_allclose(log_survival,-out.audit_H_DF-out.audit_H_SF,atol=1e-9)
            sums[j]+=np.column_stack([B,out.F_completed,out.audit_H_DF,out.audit_H_SF,
                                    out.F_killed_by_D,out.F_killed_by_S,log_survival])
        return natural

    annual.simulate=observe
    try:
        baseline=evaluate(des,years=80,window=20,dt=.5,
                size_gate=.5 if g.gate_code.iloc[0] else None,
                **{k:des[k].to_numpy() for k in ["attack","rho","conversion","strength","refuge_order"]})
    finally:
        annual.simulate=kernel
    assert year==80
    predicted=corner_contrasts(np.log(baseline.F_B.to_numpy().reshape(n,2,2,2)))
    np.testing.assert_allclose(predicted,g[["log_OS","log_OV","log_SV","log_OSV"]],atol=1e-10,rtol=0)
    output=[]
    for j,arm in enumerate(ARMS):
        rows=des[["draw_id","vegetation","S_source","D_source"]].copy()
        rows["arm"]=arm
        rows[METRICS]=sums[j]/20
        output.append(rows)
    return pd.concat(output)


def summarize(rows):
    rows=rows.copy()
    for name in ["F_start","F_end"]:
        rows["log_"+name]=np.log(rows[name])
    rows["log_retention"]=rows.log_F_end-rows.log_F_start
    measures=METRICS+["log_F_start","log_F_end","log_retention"]
    idx=["arm","draw_id","vegetation","S_source"]
    lo,hi=[rows[rows.D_source.eq(level)].set_index(idx)[measures] for level in [.25,2.]]
    delta=hi-lo
    delta.groupby(level=["arm","vegetation","S_source"]).mean().to_csv(OUT/"high_minus_low_odonate.csv")
    byveg=delta.xs(2.,level="S_source")-delta.xs(.25,level="S_source")
    within=byveg.groupby(level=["arm","draw_id"]).mean()
    byveg.groupby(level=["arm","vegetation"]).mean().to_csv(OUT/"interaction_by_vegetation.csv")
    within.to_csv(OUT/"interaction_by_draw.csv.gz")
    report=within.groupby(level="arm").mean()
    report["fraction_OS_end_negative"]=within.log_F_end.lt(-1e-6).groupby(level="arm").mean()
    report["fraction_H_D_amplified"]=within.H_D.gt(1e-6).groupby(level="arm").mean()
    report.to_csv(OUT/"interaction_summary.csv")
    print(report.round(5).to_string(),flush=True)


if __name__=="__main__":
    OUT.mkdir(exist_ok=True)
    d=pd.concat([pd.read_csv(f) for f in sorted((ROOT/"g12_abc_pom_prior_20261107/original_20k").glob("*.gz"))],ignore_index=True)
    selected=d[(d.log_OS < -1e-6)&(d.log_OV < -1e-6)]
    assert len(d)==20000 and len(selected)==selected.draw_id.nunique()==1925
    groups=[g for _,g in selected.groupby(["behavior","litter","gate_code"])]
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows=pd.concat(pool.map(replay,groups),ignore_index=True)
    assert len(rows)==1925*8*4
    rows.to_csv(OUT/"season_means.csv.gz",index=False)
    summarize(rows)
