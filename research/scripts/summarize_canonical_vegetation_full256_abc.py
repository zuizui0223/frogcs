"""Full 256 shared rate-draw ABC on 108 main-canonical vegetation×stage classes.

Reuses original baseline full-256, other contexts' original 64 and NEW
192 source rate draws from unchanged, real 80-year deterministic population
dynamics. Never double-count 36 behaviorally identical no-F-shelter risk
classes. Main catalog's other ecological axes remain unrun.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_native_2x2x2_prior import (
    ROOT,DESIGN,SOURCES,matching_prior_draws
)
from canonical_main_vegetation_prior import (
    equal_class_and_role_priors,main_role_multiplicities
)
from run_vegetation_cross_ontogeny_80y import CONTEXTS,FAMILIES
from run_missing192_canonical_vegetation_80y import (
    OUT,N_CANONICAL_CLASSES_PER_SHARD
)

OLD=ROOT/"research/results/macro_vegetation_cross_ontogeny_20261031"
ORIGINAL=ROOT/"research/results/macro_intrinsic_factorial_abc_20261031"
N_DRAWS=256
BOOT=999
SEED=20261110
SCALES=("log","raw")
PLANT_FLAGS=("cover_SF","cover_DF","cover_DS","litter")
PRIOR_TYPES=("canonical108_equal_class","equal_12_plant_roles",
             "main3600_role_multiplicity")
FIELD=("OS","OV","SV","OSV")


def numeric_source_match(reference,actual,source,fields=None):
    keys=["context","family","risk","plant_model","draw","reverse_on"]
    a=reference.sort_values(keys).reset_index(drop=True)
    b=actual.sort_values(keys).reset_index(drop=True)
    if len(a)!=len(b) or not a[keys].equals(b[keys]):
        raise AssertionError("Original 80-year rate/role/edge cohort source mismatch: "+source)
    checks=fields or ["min_F_B","max_F_B"]+[
        f"beta_{scale}_{v}" for scale in SCALES for v in FIELD]
    for name in checks:
        max_error=float(np.abs(a[name].to_numpy(float)-b[name].to_numpy(float)).max())
        if not np.isfinite(max_error) or max_error>1e-8:
            raise AssertionError("Original real process source altered "+name+" max "+str(max_error))
    for scale in SCALES:
        cmp=[f"matches_{scale}"]+[f"sign_{scale}_{v}" for v in FIELD]
        if not a[cmp].equals(b[cmp]):
            raise AssertionError("Four original biological signs changed in "+source)
    return len(a)


def canonical_only(x):
    return x.loc[~(x.cover_SF.eq(0)&x.risk.eq(True))].copy()


def check_rate_parameters(p,expected,parent):
    actual=p.sort_values("draw").reset_index(drop=True)
    source=parent.loc[parent.draw.isin(expected)].sort_values("draw").reset_index(drop=True)
    if len(actual)!=len(expected) or not np.array_equal(actual.draw.to_numpy(int),
                                                        np.sort(np.asarray(expected,int))):
        raise AssertionError("Missing/duplicate original shared rate draw IDs")
    fields=["attack_scale","rho","conversion","f_juvenile_survival",
            "f_adult_survival","s_growth_multiplier","d_growth_multiplier"]
    if not np.array_equal(actual.f_delay.to_numpy(int),source.f_delay.to_numpy(int)):
        raise AssertionError("Original delayed maturation distribution changed")
    if not np.allclose(actual[fields].to_numpy(float),source[fields].to_numpy(float),
                       atol=1e-13,rtol=0):
        raise AssertionError("Original independent 256 process rate priors changed")


def load_all_full256(new=OUT,old=OLD,original=ORIGINAL):
    new,old,original=Path(new),Path(old),Path(original)
    parent=matching_prior_draws(N_DRAWS)
    if len(parent)!=256 or parent.draw.nunique()!=256:
        raise AssertionError("Original 256 biological prior vectors missing")
    reused_original=[]
    provenance={}
    for sf in (0,1):
        for litter in (0,1):
            base=original/f"SF{sf}_L{litter}"
            f=Path(str(base)+"_prior_vegetation_signs.csv.gz")
            p=Path(str(base)+"_rate_draws.csv")
            for path in (f,p):
                if not path.is_file():raise FileNotFoundError(str(path))
                provenance[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
            params=pd.read_csv(p)
            check_rate_parameters(params,range(256),parent)
            allrows=pd.read_csv(f)
            if len(allrows)!=(2 if litter else 4)*2*256*2:
                raise AssertionError("Invalid earlier genuine original-stage plant source")
            reused_original.append(allrows)
    full_original=pd.concat(reused_original,ignore_index=True)
    if len(full_original)!=12*2*256*2:
        raise AssertionError("Previously archived original baseline 256 plant runs incomplete")
    full_original=canonical_only(full_original)
    if len(full_original)!=18*256*2 or full_original.structure_id.nunique()!=18:
        raise AssertionError("Main-canonical original full256 source mismatch")
    frames=[full_original];overlap_checks={}
    for context in CONTEXTS:
        for family in FAMILIES:
            stem=f"{context}__{family}"
            path=old/(stem+"_actual_80year_model_signs.csv.gz")
            if not path.is_file():raise FileNotFoundError(str(path))
            provenance[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
            previous=pd.read_csv(path)
            if len(previous)!=12*2*64*2:
                raise AssertionError("Previous original genuine 64 rate classes truncated")
            previous=canonical_only(previous)
            if len(previous)!=18*64*2:
                raise AssertionError("Cannot preserve original 64 canonical cases")
            params=old/(stem+"_matched_parent256_rate_draws.csv")
            if not params.is_file():raise FileNotFoundError(str(params))
            check_rate_parameters(pd.read_csv(params),range(0,256,4),parent)
            provenance[str(params.relative_to(ROOT))]=hashlib.sha256(params.read_bytes()).hexdigest()
            if context=="original" and family=="baseline":
                overlap_checks[stem]=numeric_source_match(
                    previous,full_original[full_original.draw.mod(4).eq(0)],
                    "original256←old64")
                continue
            f=new/(stem+"_missing192_actual_80year_signs.csv.gz")
            p=new/(stem+"_missing192_original_rate_draws.csv")
            receipt=new/(stem+"_receipt.json")
            for path in (f,p,receipt):
                if not path.is_file():raise FileNotFoundError(str(path))
                provenance[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
            rc=json.loads(receipt.read_text())
            if (rc["n_original_80year_runs"]!=18*192*2 or
                rc["n_independent_missing_rate_draws"]!=192 or
                max(rc["original_archive_and_old_annual_replay"].values())>1e-7):
                raise AssertionError("Original model failed real annual replay "+stem)
            check_rate_parameters(pd.read_csv(p),
                                  [i for i in range(256) if i%4!=0],parent)
            missing=pd.read_csv(f)
            if len(missing)!=18*192*2 or missing.structure_id.nunique()!=18:
                raise AssertionError("Genuine new 192 process source incomplete")
            if len(set(previous.draw)&set(missing.draw)):
                raise AssertionError("Recomputed one of 64 previously valid rate vectors")
            previous_class=set(previous.structure_id)
            if set(missing.structure_id)!=previous_class:
                raise AssertionError("Different ecological hypotheses in new 192 draws")
            frames.extend([previous,missing])
            overlap_checks[stem]=dict(reused64=len(previous),new192=len(missing))
    full=pd.concat(frames,ignore_index=True)
    if (len(full)!=108*256*2 or full.structure_id.nunique()!=108 or
        full.duplicated(["structure_id","draw","reverse_on"]).any() or
        full.groupby("structure_id").draw.nunique().ne(256).any() or
        full.groupby(["structure_id","draw"]).reverse_on.nunique().ne(2).any()):
        raise AssertionError("Original 108 distinct-stage plant models ×256 rates not fully retained")
    if (full.cover_SF.eq(0)&full.risk.eq(True)).any():
        raise AssertionError("Unnecessary main-canonical risk/refuge duplicate reintroduced")
    return full,parent,provenance,overlap_checks


def exact_abc(full,n_boot=BOOT):
    rng=np.random.default_rng(SEED)
    bootids=rng.integers(0,N_DRAWS,size=(n_boot,N_DRAWS))
    rates=[];marginals=[];leading=[];pairedout=[];pairedsummary=[]
    rows=full.drop_duplicates("structure_id").set_index("structure_id")
    if len(rows)!=108:raise AssertionError("Noncanonical structure ID")
    plant_counts=main_role_multiplicities(full)
    for scale in SCALES:
        tag=f"matches_{scale}"
        src=full.copy()
        src[tag]=src[tag].astype(int)
        avg=src.groupby(["draw","structure_id"]).agg(
            accepted=(tag,"mean"),reverse_variants=("reverse_on","nunique"),
            n_repetitions=("reverse_on","size")).reset_index()
        if len(avg)!=108*N_DRAWS or avg.reverse_variants.ne(2).any() or avg.n_repetitions.ne(2).any():
            raise AssertionError("One or more paired real biological models missing")
        matrix=avg.pivot(index="draw",columns="structure_id",values="accepted").sort_index()
        if (len(matrix)!=256 or matrix.isna().any().any() or
            not np.array_equal(matrix.index.to_numpy(int),np.arange(256))):
            raise AssertionError("Incomplete original LHS source rate draw lattice")
        models=rows.loc[matrix.columns]
        prior=equal_class_and_role_priors(models,plant_counts)
        X=matrix.to_numpy(float)
        candidate_rate=X.mean(axis=0)
        bs_rates=X[bootids].mean(axis=1)
        for prior_name in PRIOR_TYPES:
            w=prior[prior_name]
            joint=w*candidate_rate
            if joint.sum()<=0:raise AssertionError("No model can generate target four signs")
            share=joint/joint.sum()
            weights=bs_rates*w[None,:]
            if (weights.sum(axis=1)<=0).any():
                raise AssertionError("Paired bootstrap had no matching prior mass")
            bootshare=weights/weights.sum(axis=1,keepdims=True)
            for j,name in enumerate(matrix.columns):
                obj=models.loc[name]
                rates.append(dict(scale=scale,prior=prior_name,structure_id=name,
                                  context=obj.context,family=obj.family,risk=bool(obj.risk),
                                  plant_model=obj.plant_model,
                                  **{k:int(obj[k]) for k in PLANT_FLAGS},
                                  n_independent_prior_draws=N_DRAWS,
                                  n_reverse_on_off_per_draw=2,
                                  accepted_rate_weight=float(candidate_rate[j]*N_DRAWS),
                                  acceptance=float(candidate_rate[j]),
                                  conditional_abc_share=float(share[j]),
                                  share_ci_low=float(np.quantile(bootshare[:,j],.025)),
                                  share_ci_high=float(np.quantile(bootshare[:,j],.975))))
            for axis in ("context","family","risk","plant_model",*PLANT_FLAGS):
                a=models[axis].to_numpy()
                for v in sorted(pd.unique(a),key=str):
                    ix=np.flatnonzero(a==v)
                    p=bootshare[:,ix].sum(axis=1)
                    marginals.append(dict(scale=scale,prior=prior_name,
                                          axis=axis,value=str(v),n_classes=len(ix),
                                          conditional_abc_share=float(share[ix].sum()),
                                          share_ci_low=float(np.quantile(p,.025)),
                                          share_ci_high=float(np.quantile(p,.975))))
            best=int(np.argmax(share))
            pshare={k:float(share[models.plant_model.eq(k)].sum())
                    for k in sorted(models.plant_model.unique())}
            topplant=max(pshare,key=pshare.get)
            leading.append(dict(scale=scale,prior=prior_name,
                                leading_structural_class=matrix.columns[best],
                                best_class_share=float(share[best]),
                                leading_plant_role=topplant,
                                best_plant_share=pshare[topplant],
                                original_timing_share=float(
                                    share[models.context.eq("original")].sum()),
                                baseline_handling_share=float(
                                    share[models.family.eq("baseline")].sum()),
                                n_original_rate_draws=N_DRAWS,
                                n_main_canonical_structures=108))
        for role in PLANT_FLAGS:
            mask=np.ones(len(src),bool)
            if role=="cover_SF":mask &=src.risk.eq(False).to_numpy()
            if role=="litter":mask &=src.cover_DF.eq(0).to_numpy()
            if role=="cover_DF":mask &=src.litter.eq(0).to_numpy()
            z=src.loc[mask]
            other=[v for v in PLANT_FLAGS if v!=role]
            fixed=["context","family","risk","draw","reverse_on",*other]
            pv=z.pivot(index=fixed,columns=role,
                       values=[tag,*[f"beta_{scale}_{k}" for k in ("OS","OV","SV","OSV")]])
            if pv.isna().any().any():raise AssertionError("Unpaired canonical vegetation pathway "+role)
            delta=(pv.xs(1,axis=1,level=1)-pv.xs(0,axis=1,level=1)).reset_index()
            if not delta.draw.nunique()==256:
                raise AssertionError("Paired main plant role loss of rate vectors")
            for (context,family),g in delta.groupby(["context","family"]):
                values=g.groupby("draw")[tag].mean().sort_index().to_numpy(float)
                if len(values)!=256:
                    raise AssertionError("Missing 256 real biological parameter draws")
                sampled=values[bootids].mean(axis=1)
                pairedsummary.append(dict(scale=scale,context=context,
                                          family=family,plant_axis=role,
                                          n_independent_rate_draws=N_DRAWS,
                                          n_original_pair_configs=len(g),
                                          mean_accepted_sign_gain=float(values.mean()),
                                          gain_ci_low=float(np.quantile(sampled,.025)),
                                          gain_ci_high=float(np.quantile(sampled,.975)),
                                          n_improve=int((g[tag]>0).sum()),
                                          n_worsen=int((g[tag]<0).sum()),
                                          n_tied=int((g[tag]==0).sum()),
                                          **{f"mean_delta_{k}":float(g[f"beta_{scale}_{k}"].mean())
                                             for k in ("OS","OV","SV","OSV")}))
    return dict(full256_108class_abc=pd.DataFrame(rates),
                full256_main_axis_prior_marginals=pd.DataFrame(marginals),
                full256_structural_prior_leaders=pd.DataFrame(leading),
                full256_vegetation_paired_effects=pd.DataFrame(pairedsummary))


def run(new=OUT,old=OLD,original=ORIGINAL,n_boot=BOOT):
    new=Path(new)
    new.mkdir(parents=True,exist_ok=True)
    source,rates,hashes,checks=load_all_full256(new,old,original)
    result=exact_abc(source,n_boot=n_boot)
    for name,frame in result.items():
        frame.to_csv(new/(name+".csv"),index=False)
    receipt=dict(status="TRUE_80Y_COMPLETE_256RATE_108_MAIN_CANONICAL_PLANT_ABC",
                 n_all_source_80year_runs=len(source),
                 n_original_biological_rate_draws=N_DRAWS,
                 n_matched_reverse_edge_modes=2,
                 n_canonical_plant_ontogeny_handling_risk_classes=108,
                 n_newly_executed_model_runs=34560,
                 n_reused_original_baseline_full256_runs=9216,
                 n_reused_previous_64_other_context_runs=11520,
                 n_bootstrap=n_boot,
                 original64_and_original256_source_matches=checks,
                 model_prior_variants=list(PRIOR_TYPES),
                 candidate_main_3600_structures_not_exhaustively_modeled=True,
                 prior_demographic_rates_are_synthetic=True,
                 field_posterior_mechanism_probability_not_calibrated=True,
                 source_hashes=hashes,
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (new/"canonical_full256_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("FULL_256_CANONICAL_PLANT_STAGE_ABC_SOURCE_VALIDATED",json.dumps(checks),flush=True)
    print("FULL_256_CANONICAL_LEADERS\n"+result["full256_structural_prior_leaders"].to_string(index=False),flush=True)
    print("FULL_256_PLANT_MECHANISM_PAIRED\n"+result["full256_vegetation_paired_effects"].to_string(index=False),flush=True)
    print("FULL_256_MAIN_AXIS_MARGINALS\n"+result["full256_main_axis_prior_marginals"].to_string(index=False),flush=True)
    return result,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--new",type=Path,default=OUT)
    p.add_argument("--old",type=Path,default=OLD)
    p.add_argument("--original",type=Path,default=ORIGINAL)
    p.add_argument("--bootstrap",type=int,default=BOOT)
    a=p.parse_args()
    if not a.run:p.error("Explicit --run required")
    run(a.new,a.old,a.original,a.bootstrap)
