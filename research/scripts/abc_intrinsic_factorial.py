"""Intrinsic 2x2x2 F/S/D source-vegetation factorial POM for frogcs.

Only four directions are targets: OS−, OV−, SV+, OSV+.
No site SDM rank transport, rank correlation, acoustic noise or ABC
is used to compute these intrinsic model contrasts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import ROOT
from run_macro_process_prior_predictive import DESIGN, SOURCES, scenario_set

OUT=ROOT/"research/results/macro_intrinsic_factorial_abc_20261031"
TARGET=np.asarray([-1,-1,1,1],dtype=int)
METRICS=("OS","OV","SV","OSV")
LEVELS=(.25,2.)
BASELINE_SOURCES=tuple(SOURCES)
ROOT_CASES=24
STRUCTURAL_CLASSES=12
N_CORNERS=8
EPS=1e-10


def eight_corners():
    return np.asarray([(v,s,d) for v in (0.,1.) for s in LEVELS for d in LEVELS],
                      dtype=float)


def subset_corners(frame):
    needed=frame[frame.S_source.isin(LEVELS)&frame.D_source.isin(LEVELS)].copy()
    if not needed.vegetation.isin((0.,1.)).all():
        raise ValueError("Unexpected V levels")
    needed=needed.sort_values(["case","vegetation","S_source","D_source"])
    if needed.duplicated(["case","vegetation","S_source","D_source"]).any():
        raise ValueError("Duplicate 2x2x2 ecological cell")
    return needed


def one_factorial(y):
    """Return four ecological difference-in-difference effects for n x 8 Y.

    Corners sort by (V0,S0,D0), (V0,S0,D1), (V0,S1,D0),
    ..., (V1,S1,D1). Orientations are D high minus low,
    S high minus low, V present minus absent.
    """
    x=np.asarray(y,dtype=float)
    if x.ndim!=2 or x.shape[1]!=8 or not np.isfinite(x).all():
        raise ValueError("Expected finite (n,8) endogenous factorial response")
    x=x.reshape(len(x),2,2,2)
    d_effect=x[:,:,:,1]-x[:,:,:,0]            # [n,V,S]
    os=(d_effect[:,:,1]-d_effect[:,:,0]).mean(axis=1)
    ov=(d_effect[:,1,:]-d_effect[:,0,:]).mean(axis=1)
    s_effect=x[:,:,1,:]-x[:,:,0,:]            # [n,V,D]
    sv=(s_effect[:,1,:]-s_effect[:,0,:]).mean(axis=1)
    osv=(d_effect[:,1,1]-d_effect[:,1,0]-
         d_effect[:,0,1]+d_effect[:,0,0])
    return np.column_stack([os,ov,sv,osv])


def sign_code(contrasts,eps=EPS):
    a=np.asarray(contrasts,dtype=float)
    if a.ndim!=2 or a.shape[1]!=4 or not np.isfinite(a).all():
        raise ValueError("Contrasts require finite n x 4")
    out=np.where(a>eps,1,np.where(a < -eps,-1,0)).astype(int)
    return out


def summarize_factorial(frame):
    """Compute log(F_B) primary and raw(F_B) sensitivity for all cases."""
    if not {"case","vegetation","S_source","D_source","F_B"}.issubset(frame):
        raise ValueError("Missing endogenous model columns")
    eight=eight_corners()
    rows=[]
    for name,g in frame.groupby("case"):
        sub=g.sort_values(["vegetation","S_source","D_source"])
        xyz=sub[["vegetation","S_source","D_source"]].to_numpy(float)
        if len(sub)!=8 or not np.allclose(xyz,eight,atol=1e-10,rtol=0):
            raise ValueError("Missing eight corners in "+str(name))
        f=sub.F_B.to_numpy(float)
        if not np.isfinite(f).all() or np.any(f<=0):
            raise ValueError("Endogenous F_B must be finite and positive")
        for mode,y in (("log_F_B",np.log(f)),("raw_F_B",f)):
            z=one_factorial(y[None,:])[0]
            sig=sign_code(z[None,:])[0]
            rows.append(dict(case=int(name),scale=mode,
                             **{f"effect_{k}":float(z[i]) for i,k in enumerate(METRICS)},
                             **{f"sign_{k}":int(sig[i]) for i,k in enumerate(METRICS)},
                             matching_target=bool(np.array_equal(sig,TARGET)),
                             n_matching_signs=int(np.sum(sig==TARGET))))
    return pd.DataFrame(rows)


def class_name(context,family,risk):
    return "|".join([str(context),str(family),"refuge_on" if bool(risk) else "refuge_off"])


def catalogue_structure():
    spec=pd.read_csv(DESIGN)
    original_grid,selected=scenario_set(spec)
    if len(selected)!=ROOT_CASES:
        raise AssertionError("Existing scientific 24-case source missing")
    design=selected.copy()
    design["structural_class"]=[
        class_name(row.context,row.family,row.risk) for row in design.itertuples()]
    if design.structural_class.nunique()!=STRUCTURAL_CLASSES:
        raise AssertionError("Not exactly 12 ontogenetic structural classes")
    if design.groupby("structural_class").edge.nunique().ne(2).any():
        raise AssertionError("Reversal switches not paired inside each structure")
    return design,original_grid


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    classes,grid=catalogue_structure()
    frozen=pd.concat([pd.read_csv(p) for p in BASELINE_SOURCES],ignore_index=True)
    frozen=frozen[frozen.case.isin(classes.case)]
    reduced=subset_corners(frozen)
    if len(reduced)!=ROOT_CASES*N_CORNERS:
        raise ValueError("Frozen 80y source fails eight-corner completeness")
    out=summarize_factorial(reduced)
    joined=out.merge(classes[["case","context","family","risk","edge","structural_class"]],
                     on="case",validate="many_to_one")
    if len(joined)!=ROOT_CASES*2:
        raise AssertionError("Missing factorial response-scale rows")
    joined.to_csv(OUT/"archived_intrinsic_24_factors.csv",index=False)
    # POM is structural; do not count exact-equal ON/OFF as independent wins.
    summary=[]
    for (scale,structure),g in joined.groupby(["scale","structural_class"]):
        if len(g)!=2:raise AssertionError("Unbalanced edge pair")
        x=g.set_index("edge")
        a=x.loc["dynamic"];b=x.loc["frog_reverse"]
        raw=np.array([a[f"effect_{k}"] for k in METRICS],float)
        swapped=np.array([b[f"effect_{k}"] for k in METRICS],float)
        summary.append(dict(scale=scale,structural_class=structure,
                            contexts=a.context,feeding=a.family,risk=bool(a.risk),
                            dynamic_case=int(a.case),reversal_case=int(b.case),
                            dynamic_match=bool(a.matching_target),
                            reversal_match=bool(b.matching_target),
                            n_match_scenarios=int(g.matching_target.sum()),
                            identical_effects=bool(np.allclose(raw,swapped,atol=1e-10,rtol=0)),
                            identical_all_four_signs=bool(np.array_equal(
                                sign_code(raw[None,:]),sign_code(swapped[None,:]))),
                            n_signs_match_dynamic=int(a.n_matching_signs),
                            n_signs_match_reversal=int(b.n_matching_signs)))
    pd.DataFrame(summary).to_csv(OUT/"archived_intrinsic_12_classes.csv",index=False)
    receipt=dict(status="INTRINSIC_2X2X2_POM_FIXED_80YEAR_F_B",
                 goals="OS− OV− SV+ OSV+ versus endogenous synthetic source-factorial F_B",
                 use_original_80year_source=True,source_case_count=ROOT_CASES,
                 structural_classes=STRUCTURAL_CLASSES,source_cells=len(reduced),
                 primary_scale="log_F_B",secondary_scale="raw_F_B",
                 no_site_mapping=True,no_ranking=True,no_noise_model=True,
                 no_causal_biological_prior=True,
                 sources_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in [DESIGN,*BASELINE_SOURCES]},
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"archived_factorial_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("INTRINSIC_POM_ARCHIVED_CASES\n"+
          joined[["scale","case","structural_class","edge","matching_target",
                  "n_matching_signs",*[f"effect_{x}" for x in METRICS]]].to_string(index=False),
          flush=True)
    print("INTRINSIC_POM_ARCHIVED_CLASS_SUMMARY\n"+
          pd.DataFrame(summary).to_string(index=False),flush=True)
    return joined,pd.DataFrame(summary)


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--run",action="store_true")
    arg=a.parse_args()
    if not arg.run:a.error("Explicit --run required")
    run()
