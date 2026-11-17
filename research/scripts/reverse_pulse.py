"""Single-season reverse-predation pulse on matched P1 backgrounds."""
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit, prange, set_num_threads, get_num_threads
from frog_arrival_p1 import CALENDARS, FROZEN, ROOT, run_vertex
from final_mechanism_common import catalog
from abc_pom_main3600 import CORNERS

OUT = ROOT / "research/results/reverse_pulse_20261111"
METRICS = ["emerged", "next_yago", "next_H_DF"]

@njit(parallel=True)
def evaluate(parameters, stages, corners, offsets):
    result = np.empty((len(parameters), len(corners), 2, 3))
    replay = np.empty((len(parameters), len(corners), 3))
    for i in prange(len(parameters)):
        row = parameters[i].copy()
        fa, sa, da = offsets
        for j in range(len(corners)):
            v, s, d = corners[j]
            args = (v, s, d, 20+fa, stages[i,0]+sa, stages[i,1], 20+da, 180)
            if fa == sa == da == 0:
                replay[i,j] = run_vertex(parameters[i], *args, -1)[:3]
            row[10] = 1  # permit the link; its single-season activation is set by pulse
            for pulse in range(2):
                result[i,j,pulse] = run_vertex(row, *args, pulse)[3:]
    return result, replay

def main():
    OUT.mkdir(exist_ok=True)
    set_num_threads(min(12,get_num_threads()))
    saved = pd.read_csv(FROZEN/"P1_original4096_isolated_timing_duration_80year.csv.gz",dtype={"arm":str})
    src = saved[saved.arm=="11"].sort_values("draw_id").merge(catalog(),on="model_id",validate="many_to_one")
    src["cue"] = np.where(src.behavior=="cue_SF",3.,0.)
    src["order"] = src.refuge_order.map({"D":.25,"equal":.75,"S":1.25})
    cols = "cover_SF cover_DF cover_DS cover_SD survival timing support_DF support_DS edge_SD edge_DS reverse litter cue order gate_code attack rho conversion strength".split()
    pars = src[cols].to_numpy(float)
    assert len(src)==1024 and src.source_id.nunique()==256 and np.isfinite(pars).all()
    stages = src[["s_arrival","S_duration"]].to_numpy(int)
    corners = np.array(CORNERS)
    key = src.iloc[np.repeat(np.arange(len(src)),8)][["source_id","stage_design","timing","rho"]].reset_index(drop=True)
    key[["vegetation","s_supply","d_supply"]] = np.tile(corners,(len(src),1))
    ref = pd.read_csv(FROZEN/"P1_original32768_vegetation_predator_corners.csv.gz").sort_values(["draw_id","vertex"])
    target = ref[ref.draw_id.isin(src.draw_id)][["F_B","audit_H_SF","audit_H_DF"]].to_numpy().reshape(len(src),8,3)
    frames=[]
    for offsets in CALENDARS:
        vals,replay = evaluate(pars,stages,corners,offsets)
        if offsets==(0,0,0):
            np.testing.assert_allclose(replay,target,atol=1e-10,rtol=1e-10)
            baseline=vals.copy()
        if offsets==(78,78,78):
            np.testing.assert_allclose(vals,baseline,atol=1e-12,rtol=0)
        table=key.copy()
        table[["frog_delay","s_delay","d_delay"]]=offsets
        f_end=20+offsets[0]+45
        d_end=20+offsets[2]+60+5*table.vegetation*table.timing
        table["reverse_overlap_days"]=np.clip(d_end+5-f_end,0,5)
        table["larval_overlap_days"]=np.maximum(0,np.minimum(f_end,d_end)-max(20+offsets[0],20+offsets[2]))
        for j,name in enumerate(METRICS):
            pair=vals[:,:,:,j].reshape(-1,2)
            table[name+"_off"],table[name+"_on"]=pair.T
            table[name+"_difference"]=pair[:,1]-pair[:,0]
            assert np.isfinite(pair).all() and (pair>=0).all()
            assert np.allclose(table.loc[table.reverse_overlap_days==0,name+"_difference"],0,atol=1e-12)
        assert (table.next_yago_difference<=1e-12).all()
        assert np.allclose(table.loc[table.larval_overlap_days==0,"next_H_DF_off"],0)
        frames.append(table)
    data=pd.concat(frames,ignore_index=True)
    groups=["frog_delay","s_delay","d_delay","vegetation"]
    cols=[name+suffix for name in METRICS for suffix in ("_off","_on","_difference")]
    for name in METRICS:
        data[name+"_lower"]=data[name+"_difference"] < -1e-10
        cols.append(name+"_lower")
    data.to_csv(OUT/"pairs.csv.gz",index=False,compression={"method":"gzip","mtime":0})
    data.groupby(groups)[cols].mean().to_csv(OUT/"calendar_summary.csv")
    data.groupby(groups+["stage_design","reverse_overlap_days","larval_overlap_days"])[cols].mean().to_csv(OUT/"overlap_summary.csv")

if __name__=="__main__":
    main()
