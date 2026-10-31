"""Stage-1 main-compatible vegetation role ABC/POM with paired 64-rate draws.

Reports conditional generation of four field macro *directions*, not causal
vegetation functions at NAAMP sites or 3600-catalog posterior probabilities.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_native_vegetation_abc import OUT,legal_plant_inventory
from model_native_2x2x2_prior import TARGET,METRICS
from model_native_abc_rf import wilson_ci

N_DRAWS=64
BOOT=999
SEED=20261103
SCALES=("log","raw")


def load_evidence(folder=OUT,n=N_DRAWS):
    sources=[]
    for sf,litter in itertools.product((0,1),repeat=2):
        stem=f"SF{sf}_L{litter}"
        path=folder/(stem+"_prior_vegetation_signs.csv.gz")
        receipt=folder/(stem+"_receipt.json")
        params=folder/(stem+"_rate_draws.csv")
        if any(not p.is_file() for p in (path,receipt,params)):
            raise FileNotFoundError("Missing real source shard "+stem)
        r=json.loads(receipt.read_text())
        p=pd.read_csv(params)
        x=pd.read_csv(path)
        expected_plant_count=2 if litter else 4
        if (r["original_full_80year_archive_replay"]["F_B"]>1e-8 or
            r["original_full_80year_archive_replay"]["F_fraction"]>1e-8 or
            r["n_prior_vectors"]!=n or r["n_plant_scenarios"]!=expected_plant_count):
            raise AssertionError("Frozen original kernel or model catalog not replayed")
        if len(p)!=n or len(x)!=expected_plant_count*2*n*2:
            raise AssertionError("Unbalanced original demographic rate prior")
        if x.groupby(["structure_id","draw"]).reverse_on.nunique().ne(2).any():
            raise AssertionError("No exact reverse edge pairing")
        if x.groupby(["plant_model","risk","reverse_on"]).draw.nunique().ne(n).any():
            raise AssertionError("Missing actual parameter vector in vegetation role")
        for metric in METRICS:
            for scale in SCALES:
                field=f"sign_{scale}_{metric}"
                if not np.isin(x[field],[-1,0,1]).all():
                    raise AssertionError("Malformed four-bit model contrast")
        sources.append(x)
    union=pd.concat(sources,ignore_index=True)
    if len(union)!=12*2*n*2 or union.structure_id.nunique()!=24:
        raise AssertionError("Vegetation ABC archive is incomplete")
    for plant in legal_plant_inventory().plant_model:
        if union[union.plant_model==plant].structure_id.nunique()!=2:
            raise AssertionError("No both risk contexts for "+plant)
    if union.duplicated(["structure_id","draw","reverse_on"]).any():
        raise AssertionError("Duplicate source simulations")
    return union


def class_draw_matrix(x,scale,n=N_DRAWS):
    accepted=f"matches_{scale}"
    by=x.groupby(["structure_id","draw"],sort=True).agg(
        accepted_rate=(accepted,"mean"),n_edges=("reverse_on","nunique"),
        n_rows=("reverse_on","size")).reset_index()
    if len(by)!=24*n or by.n_edges.ne(2).any() or by.n_rows.ne(2).any():
        raise AssertionError("Bad matched 64 real draws and 2 reversible edge states")
    classes=sorted(by.structure_id.unique())
    draws=sorted(by.draw.unique())
    mat=by.pivot(index="draw",columns="structure_id",
                 values="accepted_rate").loc[draws,classes].to_numpy(float)
    if not np.isfinite(mat).all() or np.any(mat<0) or np.any(mat>1):
        raise AssertionError("No valid target acceptance fractions")
    return classes,np.asarray(draws),mat


def bootstrap_abc(x,n_boot=BOOT,n=N_DRAWS):
    rng=np.random.default_rng(SEED)
    ix=rng.integers(0,n,size=(n_boot,n))
    records=[];marginal=[]
    classes=x[["structure_id","plant_model","risk",
               "cover_SF","cover_DF","cover_DS","litter"]].drop_duplicates()
    if len(classes)!=24:raise AssertionError("Risk×plant subcatalog not unique")
    for scale in SCALES:
        names,draws,mat=class_draw_matrix(x,scale,n=n)
        hits=mat.sum(axis=0)
        total=hits.sum()
        if total<=0: raise ValueError("No target-sign-producing original model under prior")
        shares=hits/total
        bootstrap=mat[ix].sum(axis=1)
        if np.any(bootstrap.sum(axis=1)<=0):
            raise ValueError("At least one shared-draw bootstrap had no compatible models")
        bootrates=bootstrap/n
        bootshares=bootstrap/bootstrap.sum(axis=1,keepdims=True)
        for j,model in enumerate(names):
            meta=classes.set_index("structure_id").loc[model]
            records.append(dict(
                scale=scale,structure_id=model,
                plant_model=str(meta.plant_model),risk=bool(meta.risk),
                cover_SF=int(meta.cover_SF),cover_DF=int(meta.cover_DF),
                cover_DS=int(meta.cover_DS),litter=int(meta.litter),
                n_independent_rate_draws=n,
                n_reversal_states_per_draw=2,
                effective_accepted_rate_draws=float(hits[j]),
                acceptance=float(hits[j]/n),
                acceptance_boot_ci_low=float(np.quantile(bootrates[:,j],.025)),
                acceptance_boot_ci_high=float(np.quantile(bootrates[:,j],.975)),
                conditional_abc_share=float(shares[j]),
                share_boot_ci_low=float(np.quantile(bootshares[:,j],.025)),
                share_boot_ci_high=float(np.quantile(bootshares[:,j],.975)),
                enough_effective_accepted_for_stable_parameter_regime=bool(hits[j]>=20),
                posterior_scope="SYNTHETIC_PARAMETER_PRIOR_CONDITIONAL_VEGETATION_PILOT"))
        labels=pd.DataFrame([dict(structure_id=n,plant_model=classes.set_index("structure_id").loc[n].plant_model)
                             for n in names])
        for plant,g in labels.groupby("plant_model"):
            jj=[names.index(n) for n in g.structure_id]
            p=bootshares[:,jj].sum(axis=1)
            marginal.append(dict(scale=scale,plant_model=plant,
                                 n_risk_classes=len(jj),
                                 n_prior_rate_draws=n,
                                 total_accepted_weight=float(hits[jj].sum()),
                                 conditional_abc_plant_share=float(shares[jj].sum()),
                                 bootstrap_ci_low=float(np.quantile(p,.025)),
                                 bootstrap_ci_high=float(np.quantile(p,.975))))
    return pd.DataFrame(records),pd.DataFrame(marginal)


def paired_role_effects(x,scale):
    """ON−OFF paired both rate and reversals, only legal canonical flips."""
    all_records=[]
    roles=("cover_SF","cover_DF","cover_DS","litter")
    for role in roles:
        rest=[k for k in roles if k!=role]
        if role=="litter":
            # This path must hold cover_DF OFF (main-catalog condition).
            restrict=x.cover_DF.eq(0)
        elif role=="cover_DF":
            restrict=x.litter.eq(0)
        else:
            restrict=np.ones(len(x),bool)
        sub=x.loc[restrict].copy()
        sub[f"matches_{scale}"]=sub[f"matches_{scale}"].astype(int)
        keys=["risk","draw","reverse_on",*rest]
        piv=sub.pivot(index=keys,columns=role,
                      values=[f"matches_{scale}",*[f"beta_{scale}_{m}" for m in METRICS]])
        if piv.isna().any().any():
            raise AssertionError("Missing exact matched plant-path ON/OFF unit for "+role)
        on=piv.xs(1,axis=1,level=1)
        off=piv.xs(0,axis=1,level=1)
        difference=on-off
        for key,row in difference.reset_index().iterrows():
            rec=dict(scale=scale,axis=role,risk=bool(row.risk),
                     draw=int(row.draw),reverse_on=int(row.reverse_on),
                     gain_acceptance=float(row[f"matches_{scale}"]),
                     **{f"delta_beta_{m}":float(row[f"beta_{scale}_{m}"]) for m in METRICS})
            for k in rest:rec[k]=int(row[k])
            all_records.append(rec)
    rows=pd.DataFrame(all_records)
    summary=[]
    for (scale,role),group in rows.groupby(["scale","axis"]):
        delta=group.gain_acceptance
        summary.append(dict(scale=scale,plant_axis=role,n_legal_paired_configs=len(group),
                            n_independent_draws=group.draw.nunique(),
                            mean_acceptance_gain=float(delta.mean()),
                            n_improve=int((delta>0).sum()),n_worsen=int((delta<0).sum()),
                            n_tied=int((delta==0).sum()),
                            **{f"mean_contrast_shift_{m}":float(group[f"delta_beta_{m}"].mean())
                               for m in METRICS}))
    return rows,pd.DataFrame(summary)


def run(path=OUT,n=N_DRAWS):
    path=Path(path);path.mkdir(parents=True,exist_ok=True)
    a=load_evidence(path,n=n)
    classes,plants=bootstrap_abc(a,n=n)
    contrasts=[];summary=[]
    for scale in SCALES:
        table,stats=paired_role_effects(a,scale)
        contrasts.append(table);summary.append(stats)
    contrast=pd.concat(contrasts,ignore_index=True)
    summary=pd.concat(summary,ignore_index=True)
    for name,frame in [
        ("vegetation_abc_class_selection",classes),
        ("vegetation_abc_plant_function_shares",plants),
        ("vegetation_paired_rate_edge_effects",contrast),
        ("vegetation_paired_function_summary",summary)]:
        frame.to_csv(path/(name+".csv"),index=False)
    print("VEGETATION_MAIN_LEGAL_PILOT_ABC\n"+classes.to_string(index=False),flush=True)
    print("VEGETATION_ROLE_SHARES\n"+plants.to_string(index=False),flush=True)
    print("VEGETATION_PATH_ON_OFF_PAIRED_EFFECTS\n"+summary.to_string(index=False),flush=True)
    print("VEGETATION_ABC_FIRST_STAGE_ONLY 12 legal plant roles, matched synthetic rate draws",flush=True)
    return classes,plants,summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--draws",type=int,default=N_DRAWS)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run(n=args.draws)
