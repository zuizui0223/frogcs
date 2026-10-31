"""Correct the main-catalog vegetation/refuge structural-prior multiplicity.

Original 144-class crossed factorial source experiments are real 80y model
runs. Main's model catalog, however, canonicalizes risk refuge ON to NONE
whenever frog-from-S plant shelter is OFF. Verify exact numerical equality,
collapse those redundant labels to 108 classes, and independently audit three
explicitly hypothetical structural priors using 64 matched biological draws.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_native_2x2x2_prior import ROOT
from summarize_vegetation_cross_ontogeny_abc import (
    OUT,SEED,N_DRAWS,BOOT,SCALES,PLANT_FLAGS,
    load_archived_cross_sources
)

PRIORS=("canonical108_equal_class","equal_12_plant_roles",
        "main3600_role_multiplicity")
N_CANONICAL=108
MAIN_CATALOG=ROOT/"research/results/final_mechanism_20261027/catalog.csv"


def confirm_main_equivalence(original):
    source=original[original.cover_SF.eq(0)]
    ref=source[source.risk.eq(False)]
    fake=source[source.risk.eq(True)]
    key=["context","family","plant_model","draw","reverse_on"]
    ref=ref.sort_values(key).reset_index(drop=True)
    fake=fake.sort_values(key).reset_index(drop=True)
    if len(ref)!=6*6*64*2 or len(fake)!=len(ref) or not ref[key].equals(fake[key]):
        raise AssertionError("Main-canonical no-frog-shelter risk ON/OFF pairing invalid")
    numeric=["min_F_B","max_F_B"]
    numeric += [f"beta_{scale}_{term}"
                for scale in SCALES for term in ("OS","OV","SV","OSV")]
    a=ref[numeric].to_numpy(float);b=fake[numeric].to_numpy(float)
    max_error=float(np.abs(a-b).max())
    if not np.isfinite(max_error) or max_error>1e-10:
        raise AssertionError("Risk-induced F refuge is *not* a no-op when F shelter is OFF")
    for scale in SCALES:
        fields=[f"matches_{scale}"]+[f"sign_{scale}_{t}"
               for t in ("OS","OV","SV","OSV")]
        if not ref[fields].equals(fake[fields]):
            raise AssertionError("Categorical ecological mechanism states differ")
    cleaned=original[~((original.cover_SF.eq(0))&(original.risk.eq(True)))].copy()
    if (len(cleaned)!=N_CANONICAL*N_DRAWS*2
        or cleaned.structure_id.nunique()!=N_CANONICAL):
        raise AssertionError("Main-canonical 108 structural roles not obtained")
    return cleaned,dict(n_exactly_equal_risk_pairs=len(ref),
                        max_difference_F_B_and_pattern_metrics=max_error,
                        raw_factorial_cases=len(original),
                        canonical_distinct_model_cases=len(cleaned),
                        discarded_noop_cases=len(original)-len(cleaned))


def main_role_multiplicities(canonical):
    main=pd.read_csv(MAIN_CATALOG)
    if len(main)!=3600 or main.model_id.nunique()!=3600:
        raise AssertionError("Main source has changed")
    flags=main[["cover_SF","cover_DF","cover_DS","litter"]].copy()
    flags["plant_model"]=[
        f"SF{p.cover_SF}_DF{p.cover_DF}_DS{p.cover_DS}_L{p.litter}"
        for p in flags.itertuples(index=False)]
    observed=flags.plant_model.value_counts().sort_index()
    expected=set(canonical.plant_model.unique())
    if set(observed.index)!=expected or len(observed)!=12:
        raise AssertionError("Not the 12 canonical main plant roles")
    if observed.sum()!=3600 or (observed<=0).any():
        raise AssertionError("Unbalanced or duplicate main role counting")
    return observed


def equal_class_and_role_priors(meta,count):
    """Full-support explicit structural priors; no response-based tuning."""
    n=len(meta)
    if n!=N_CANONICAL:raise AssertionError("Canonical class inventory altered")
    role_class_counts=meta.plant_model.value_counts()
    pi={}
    pi["canonical108_equal_class"]=np.repeat(1/n,n)
    pi["equal_12_plant_roles"]=np.asarray([
        1/(12*role_class_counts[x]) for x in meta.plant_model],float)
    pi["main3600_role_multiplicity"]=np.asarray([
        count[x]/(3600*role_class_counts[x]) for x in meta.plant_model],float)
    for name,w in pi.items():
        if len(w)!=n or not np.isfinite(w).all() or (w<=0).any() or abs(w.sum()-1)>1e-12:
            raise ValueError("Invalid positive structural prior "+name)
    return pi


def reweight_main_canonical(original,n_boot=BOOT):
    source,eq=confirm_main_equivalence(original)
    main_count=main_role_multiplicities(source)
    labels=source.drop_duplicates("structure_id").set_index("structure_id")
    if len(labels)!=N_CANONICAL:raise AssertionError("Duplicate response-class index")
    rng=np.random.default_rng(SEED+910)
    ix=rng.integers(0,N_DRAWS,size=(n_boot,N_DRAWS))
    models=[];marginals=[];best=[]
    for scale in SCALES:
        field=f"matches_{scale}"
        x=source.copy()
        x[field]=x[field].astype(int)
        paired=x.groupby(["draw","structure_id"]).agg(
            accepted_fraction=(field,"mean"),n_reverse=("reverse_on","nunique"),
            n_original_runs=("reverse_on","size")).reset_index()
        if len(paired)!=N_CANONICAL*N_DRAWS or paired.n_reverse.ne(2).any() or paired.n_original_runs.ne(2).any():
            raise AssertionError("Source lost independent paired reverse edge")
        matrix=paired.pivot(index="draw",columns="structure_id",values="accepted_fraction")
        if len(matrix)!=N_DRAWS or matrix.isna().any().any():
            raise AssertionError("Source lost one of the 64 identical rate IDs")
        mat=matrix.to_numpy(float)
        meta=labels.loc[matrix.columns]
        weights=equal_class_and_role_priors(meta,main_count)
        rate=mat.mean(axis=0)
        b_rate=mat[ix].mean(axis=1)
        for prior_name in PRIORS:
            prior=weights[prior_name]
            joint=rate*prior
            mass=joint.sum()
            if mass<=0:
                raise ValueError("No model matches four main direction targets")
            share=joint/mass
            w=prior[None,:]*b_rate
            if (w.sum(axis=1)<=0).any():
                raise ValueError("Zero accepted-mass source in paired bootstrap")
            bshare=w/w.sum(axis=1,keepdims=True)
            for j,k in enumerate(matrix.columns):
                val=meta.iloc[j]
                models.append(dict(scale=scale,structural_prior=prior_name,
                                   structure_id=k,context=val.context,
                                   family=val.family,risk=bool(val.risk),
                                   plant_model=val.plant_model,
                                   n_independent_prior_draws=N_DRAWS,
                                   exact_sign_acceptance_rate=float(rate[j]),
                                   model_prior_mass=float(prior[j]),
                                   conditional_model_share=float(share[j]),
                                   share_ci_low=float(np.quantile(bshare[:,j],.025)),
                                   share_ci_high=float(np.quantile(bshare[:,j],.975))))
            for dim in ("context","family","risk","plant_model",*PLANT_FLAGS):
                v=meta[dim].to_numpy()
                for label in sorted(pd.unique(v),key=str):
                    chosen=np.flatnonzero(v==label)
                    uncertainty=bshare[:,chosen].sum(axis=1)
                    marginals.append(dict(scale=scale,structural_prior=prior_name,
                                          dimension=dim,label=str(label),
                                          n_canonical_classes=len(chosen),
                                          conditional_share=float(share[chosen].sum()),
                                          share_ci_low=float(np.quantile(uncertainty,.025)),
                                          share_ci_high=float(np.quantile(uncertainty,.975))))
            top=int(np.argmax(share))
            totals={k:float(share[np.flatnonzero(meta.context.eq(k))].sum())
                    for k in sorted(meta.context.unique())}
            topPlant=sorted([(float(share[meta.plant_model.eq(p)].sum()),p)
                        for p in meta.plant_model.unique()],reverse=True)[0]
            best.append(dict(scale=scale,structural_prior=prior_name,
                             leading_model=matrix.columns[top],
                             leading_model_conditional_share=float(share[top]),
                             leading_plant_model=topPlant[1],
                             leading_plant_share=float(topPlant[0]),
                             original_timing_share=totals["original"],
                             D_first_S_overtakes_share=totals["D_first_S_overtakes"],
                             S_first_D_overtakes_share=totals["S_first_D_overtakes"],
                             total_prior_classes=N_CANONICAL,
                             bootstrap_n=n_boot))
    return dict(canonical_model_prior_class_shares=pd.DataFrame(models),
                canonical_model_prior_marginals=pd.DataFrame(marginals),
                canonical_prior_comparison=pd.DataFrame(best),
                main_catalog_role_multiplicities=pd.DataFrame(
                    {"plant_model":main_count.index,"n_of_3600_main":main_count.values})),eq


def run(folder=OUT,n_boot=BOOT):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    original,rates,source_sha=load_archived_cross_sources(folder)
    results,eq=reweight_main_canonical(original,n_boot=n_boot)
    for name,frame in results.items():
        frame.to_csv(folder/(name+".csv"),index=False)
    receipt=dict(status="MAIN_CANONICAL_108_CLASS_VEGETATION_ABC_STRUCTURAL_PRIOR_SENSITIVITY",
                 source_runs_80year=18432,source_raw_classes=144,
                 canonical_distinct_classes=108,
                 n_shared_original_rate_draws=N_DRAWS,
                 three_structural_priors=list(PRIORS),
                 results_derived_from_real_80year_sources=True,
                 no_new_demographic_runs=True,
                 exact_main_canonical_risk_equivalence=eq,
                 main_catalog_roles_not_entire_3600_source_model_run=True,
                 caveats=["Main model catalog weighting is a conditional prior architecture, not an independent biological prior",
                          "Original rates 64/256 synthetic common prior subdraws",
                          "Four observed macro directions do not supply a field stage-occupancy likelihood",
                          "All candidate model posterior shares are conditional on finite tested source classes"],
                 source_hashes=source_sha,
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (folder/"canonical_main_prior_receipt.json").write_text(
        json.dumps(receipt,indent=2)+"\n")
    print("MAIN_CANONICAL_108_PRIORS\n"+results["canonical_prior_comparison"].to_string(index=False),flush=True)
    print("MAIN_CANONICAL_108_PLANT_ROLE_MARGINALS\n"+
          results["canonical_model_prior_marginals"].query(
              "dimension in ['plant_model', 'context', 'family']").to_string(index=False),flush=True)
    print("MAIN_CANONICAL_108_SOURCE_REPLAY\n"+json.dumps(eq),flush=True)
    return results,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--dir",type=Path,default=OUT)
    p.add_argument("--bootstrap",type=int,default=BOOT)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run(args.dir,args.bootstrap)
