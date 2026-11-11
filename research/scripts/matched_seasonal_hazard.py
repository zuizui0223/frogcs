"""Observe the frozen seasonal kernel under matched calendar and feeding interventions."""
from collections import defaultdict
from itertools import product
from pathlib import Path
import inspect
import sys

import numpy as np
import pandas as pd
import stage_vegetation_network as kernel

ROOT = Path(__file__).resolve().parents[1] / "results"
OUT = ROOT / "matched_seasonal_hazard_20261111"
# Three counterfactuals: absent, present but cannot eat frogs, present and feeds.
CELLS = np.array(list(product([1., 2.], [0, 40], [40, 60], [0, 1], [0, 1, 2])))
DT = .5
METRICS = ["frog_density", "caudate_density", "odonate_density", "odonate_hazard_per_day",
           "cumulative_odonate_kills", "cumulative_caudate_kills", "integrated_odonate_hazard"]
lines, start = inspect.getsourcelines(kernel.simulate)
watch, = [start+i for i,line in enumerate(lines) if "death['F_by_S']+=bys" in line]


def season(draws):
    n = len(draws)
    f0, arrival, duration, v, arm = np.tile(CELLS,(n,1)).T
    k = draws.iloc[np.repeat(np.arange(n),len(CELLS))]
    scenarios = pd.DataFrame(dict(vegetation=v, f_arrival=20, d_arrival=20, s_arrival=arrival,
        attack_scale=k.attack.to_numpy(), refuge_order=k.refuge_order.to_numpy(), reverse=k.reverse.to_numpy(),
        cue=np.where(k.behavior.eq("cue_SF"),3.,0.))).to_dict("records")
    paths = {key:k[key].to_numpy()*k.strength.to_numpy() for key in
             ["cover_SF","cover_DF","cover_DS","cover_SD","support_DF","support_DS"]}
    paths.update(edge_SD=k.edge_SD.to_numpy(), edge_DS=k.edge_DS.to_numpy(), edge_SF=(arm==2).astype(float),
                 cue_SD=0., emerge_survival=k.survival.to_numpy()*k.strength.to_numpy(), emerge_exposure=0.)
    initial = np.column_stack([f0,2.*(arm>0),np.full(len(k),2.)])
    stages = np.column_stack([np.full(len(k),45),duration,np.full(len(k),60)])
    hazard = np.zeros(len(k))
    snapshots = []
    # A passive trace reads state before the kernel applies competing mortality.
    def observe(frame,event,arg):
        if event=="line" and frame.f_lineno==watch:
            state=frame.f_locals
            t=state["t"]
            if 20<=t<65:
                if t==int(t):
                    snapshots.append(np.stack([state["f"],state["s"],state["d"],state["hdf"],
                        state["death"]["F_by_D"],state["death"]["F_by_S"],hazard],axis=-1))
                hazard[:] += DT*state["hdf"]
        return observe
    def trace(frame,event,arg):
        return observe if frame.f_code is kernel.simulate.__code__ else None
    old=sys.gettrace()
    try:
        sys.settrace(trace)
        out=kernel.simulate(scenarios,dt=DT,initial_cohorts=initial,stage_durations=stages,
            pathway_controls=paths, diagnostics=True, size_gate=.5 if k.gate_code.iloc[0] else None,
            functional_response="litter" if k.litter.iloc[0] else None,
            behavioral_refuge=k.behavior.iloc[0]=="risk_refuge",emergence_delay=5*v*k.timing.to_numpy())
    finally:
        sys.settrace(old)
    np.testing.assert_allclose(hazard,out.audit_H_DF,atol=1e-12)
    np.testing.assert_allclose(f0,out.F_completed+out.F_killed_by_D+out.F_killed_by_S,atol=1e-11)
    hist=np.stack(snapshots).reshape(45,n,2,2,2,2,3,7)
    ends=out[["F_completed","F_killed_by_D","F_killed_by_S","audit_H_DF"]].to_numpy().reshape(n,2,2,2,2,3,4)
    # Frog attack ablation leaves aquatic predator trajectories identical.
    np.testing.assert_allclose(hist[...,1,1:3],hist[...,2,1:3],atol=1e-12)
    if not k.litter.iloc[0]:
        np.testing.assert_allclose(ends[...,1,3],ends[...,2,3],atol=1e-12)
    return hist,ends


def run():
    OUT.mkdir(exist_ok=True)
    data=pd.concat([pd.read_csv(p) for p in sorted((ROOT/"g12_abc_pom_prior_20261107/original_20k").glob("shard_*.csv.gz"))])
    data["case"]=(data.log_OS < -1e-6)&(data.log_OV < -1e-6)
    assert data.draw_id.nunique()==len(data)==20000 and data.case.sum()==1925
    series=defaultdict(float)
    totals=defaultdict(float)
    counts=defaultdict(int)
    for (behavior,litter,gate),group in data.groupby(["behavior","litter","gate_code"]):
        for i in range(0,len(group),200):
            batch=group.iloc[i:i+200]
            hist,ends=season(batch)
            for case,ids in batch.reset_index(drop=True).groupby("case").indices.items():
                key=(case,litter)
                counts[key]+=len(ids)
                series[key]+=hist[:,ids].sum(axis=1)
                z=ends[ids]
                direct=z[...,2,3]-z[...,1,3]
                net=z[...,2,3]-z[...,0,3]
                prey=z[...,2,0]-z[...,1,0]
                measures=np.stack([prey,direct,net,z[...,2,1]-z[...,1,1],z[...,2,2],
                    (direct>1e-10),(direct < -1e-10),(net>1e-10),(net < -1e-10),
                    (prey < -1e-10)&(direct>1e-10)],axis=-1)
                totals[key]+=measures.sum(axis=0)
    daily=[];summary=[]
    for (case,litter),count in counts.items():
        key=(case,litter)
        daily.append(pd.DataFrame((series[key]/count).reshape(-1,7),columns=METRICS,
            index=pd.MultiIndex.from_product([range(20,65),[1,2],[0,40],[40,60],[0,1],["absent","feeding_off","feeding_on"]],
            names=["day","initial_frog","arrival","duration","vegetation","caudate_arm"])).reset_index().assign(original_joint=case,litter=litter,draws=count))
        summary.append(pd.DataFrame((totals[key]/count).reshape(-1,10),
            columns=["delta_completed_frogs","delta_H_feeding","delta_H_net","delta_odonate_kills_feeding","caudate_kills_on",
                     "fraction_H_feeding_up","fraction_H_feeding_down","fraction_H_net_up","fraction_H_net_down","fraction_fewer_frogs_higher_H"],
            index=pd.MultiIndex.from_product([[1,2],[0,40],[40,60],[0,1]],names=["initial_frog","arrival","duration","vegetation"])).reset_index().assign(original_joint=case,litter=litter,draws=count))
    pd.concat(daily).to_csv(OUT/"daily.csv.gz",index=False)
    season_summary = pd.concat(summary)
    season_summary.to_csv(OUT/"season.csv",index=False)
    write_calendar_contrasts(season_summary)


def write_calendar_contrasts(season_summary):
    contrasts = []
    for key,group in season_summary.groupby(["original_joint","litter","initial_frog","vegetation"]):
        for metric in ["delta_H_feeding","delta_H_net","delta_odonate_kills_feeding"]:
            value = group.set_index(["arrival","duration"])[metric]
            late40 = value[40,40] - value[0,40]
            late60 = value[40,60] - value[0,60]
            long_early = value[0,60] - value[0,40]
            long_late = value[40,60] - value[40,40]
            contrasts.append([*key,metric,late40,late60,long_early,long_late,late60-late40])
    pd.DataFrame(contrasts,columns=["original_joint","litter","initial_frog","vegetation","metric",
        "late_minus_early_short","late_minus_early_long","long_minus_short_early","long_minus_short_late",
        "arrival_duration_interaction"]).to_csv(OUT/"calendar_contrasts.csv",index=False)


if __name__=="__main__":
    run()
