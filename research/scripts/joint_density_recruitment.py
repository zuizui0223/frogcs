"""Exact accounting of the archived log start-density contrast through annual recruitment."""
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from joint_density_history import OUT, ROOT, CORNERS, CONTEXTS, annual, evaluate
from multiyear_stage_network import DEMOGRAPHY


def account(g):
    n=len(g)
    des=g.loc[g.index.repeat(8)].reset_index(drop=True).copy()
    des[["vegetation","S_source","D_source"]]=np.tile(CORNERS,(n,1))
    for col in CONTEXTS[0]:
        des[col]=[CONTEXTS[i][col] for i in des.context_id]
    starts=[]; ends=[]
    kernel=annual.simulate

    def record(params, *, initial_cohorts, **options):
        out=kernel(params,initial_cohorts=initial_cohorts,**options)
        starts.append(initial_cohorts[:,0].reshape(n,2,2,2).copy())
        ends.append(out.F_completed.to_numpy().reshape(n,2,2,2))
        return out

    annual.simulate=record
    try:
        evaluate(des,years=80,window=20,dt=.5,size_gate=.5 if g.gate_code.iloc[0] else None,
                 **{k:des[k].to_numpy() for k in ["attack","rho","conversion","strength","refuge_order"]})
    finally:
        annual.simulate=kernel
    B=np.stack(starts)
    C=np.stack(ends)
    delay=DEMOGRAPHY["delays"][0]
    survival=DEMOGRAPHY["survival"][0]
    juvenile=DEMOGRAPHY["juvenile"][0]
    K=DEMOGRAPHY["capacity"]
    lag=slice(60-delay,80-delay)
    f=B[lag]; r=C[lag]/f
    shape=(1,n,1,1)
    mult=(g.rho*g.conversion*juvenile**(delay-1)).to_numpy().reshape(shape)
    def recruit(begin,retention):
        completed=begin*retention
        return mult*completed/(1+completed/K)
    rll=recruit(f[...,0],r[...,0]); rhh=recruit(f[...,1],r[...,1])
    rlh=recruit(f[...,0],r[...,1]); rhl=recruit(f[...,1],r[...,0])
    # Equal share of the nonlinear interaction (average over substitution orders).
    from_B=.5*((rhl-rll)+(rhh-rlh))
    from_season=.5*((rlh-rll)+(rhh-rhl))
    prev=survival*(B[59:79,...,1]-B[59:79,...,0])
    start=B[60:80].mean(axis=0)
    diff=start[...,1]-start[...,0]
    logdiff=np.log(start[...,1])-np.log(start[...,0])
    scale=np.divide(logdiff,diff,out=1/start[...,0].copy(),where=diff!=0)
    parts=np.stack([prev.mean(axis=0),from_B.mean(axis=0),from_season.mean(axis=0)],axis=-1)*scale[...,None]
    np.testing.assert_allclose(parts.sum(axis=-1),logdiff,atol=2e-12,rtol=0)
    osm=logdiff[:,:,1]-logdiff[:,:,0]
    np.testing.assert_allclose(osm.mean(axis=1),g.log_OS,atol=1e-10,rtol=0)
    values=np.concatenate([logdiff[...,None],parts],axis=-1)
    index=pd.MultiIndex.from_product([g.draw_id,[0,1],[.25,2]],names=["draw_id","vegetation","S_source"])
    return pd.DataFrame(values.reshape(-1,4),index=index,columns=["observed","prior_adults","recruit_from_start","recruit_from_season"])


if __name__=="__main__":
    d=pd.concat([pd.read_csv(f) for f in sorted((ROOT/"g12_abc_pom_prior_20261107/original_20k").glob("*.gz"))],ignore_index=True)
    sel=d[(d.log_OS < -1e-6)&(d.log_OV < -1e-6)]
    assert len(sel)==sel.draw_id.nunique()==1925
    with ProcessPoolExecutor(max_workers=4) as pool:
        contrasts=pd.concat(pool.map(account,[g for _,g in sel.groupby(["behavior","litter","gate_code"])]))
    contrasts.to_csv(OUT/"annual_account_by_draw.csv.gz")
    paired=contrasts.xs(2.,level="S_source")-contrasts.xs(.25,level="S_source")
    print(paired.groupby(level="vegetation").mean().round(6))
    print(contrasts.groupby(level="S_source").mean().round(6))
