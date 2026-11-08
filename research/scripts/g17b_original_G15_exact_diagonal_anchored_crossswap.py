"""G17b source-exact recovery of original G15 diagonal mixed with G17 offdiagonals.

G17's locked refit-based source replay FAIL remains recorded; this is an explicitly
POST-HOC, source-anchored numerical decomposition using only existing outputs.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

import numpy as np
import pandas as pd

from g17_SDM_environment_source_rank_crossswap import (
    N_TEMPLATES,N_NULLS,N_SITE,N_VISITS,N_STRONG,N_BLOCK,
    NSHARDS,PAIR_CELLS,FIELDS,ACCEPTED,SIGN_ONLY,
    frozen_templates,compute_four_cell,factorial,original_spatial_bootstrap,
)
from g15_abc_selection_specificity_holdout import OUT as G15_ROOT

G15=G15_ROOT/"audited"
RESULTS=Path(__file__).resolve().parents[2]/"research/results/g17b_exact_g15_diagonal_crossswap_20261108"
SEED=20261108
BOOT=9999
STATUS="G17B_EXACT_ORIGINAL_G15_ANCHORED_CROSSSWAP_AUDIT_SUCCESS"


def require(cond,msg):
    if not bool(cond):raise AssertionError(msg)

def sha(f):
    return hashlib.sha256(Path(f).read_bytes()).hexdigest()

def load_orig(shards,original_g15):
    root=Path(shards);original_g15=Path(original_g15)
    frozen,sourceinfo=frozen_templates()
    site_g17=[];site_g15=[];receipts=[]
    expected_sha=sourceinfo["file_sha256"]["G15_frozen_source_templates.csv"]
    for ii in range(NSHARDS):
        p=f"G17_source_crossswap_{ii:02d}"
        old=f"g15_predictive_null_shard_{ii:02d}"
        a=root/(p+"_receipt.json")
        b=original_g15/(old+"_receipt.json")
        require(a.is_file() and b.is_file(),"Missing original G17/G15 source shard receipts")
        ra=json.loads(a.read_text());rb=json.loads(b.read_text())
        require(ra["status"]=="G17_ALL_SOURCE_2X2_ORIGINAL_NAAMP_SHARD_SUCCESS"
                and ra["shard"]==ii and ra["total_shards"]==NSHARDS
                and ra["G15_frozen_source_SHA"]==expected_sha
                and rb["status"]=="G15_ORIGINAL_FIELD_SOURCE_NULL_SHARD_SUCCESS"
                and rb["fixed_source_templates_SHA"]==expected_sha
                and rb["shard"]==ii
                and ra["pair_cells"]==[list(z) for z in PAIR_CELLS],
                "G17/G15 original source model identity differs")
        require(ra["original_199_null_ids"]==rb["null_ids"]
                and ra["source_templates"]==rb["fitted_models"],
                "Original 199 source labels, partitions or controls altered")
        for receipt,dirp in ((ra,root),(rb,original_g15)):
            for name,digest in receipt["files_sha256"].items():
                require(sha(dirp/name)==digest,"Archived original source SHA mismatch "+name)
        x=pd.read_csv(root/(p+"_sites.csv.gz"))
        y=pd.read_csv(original_g15/(old+"_full_site.csv.gz"))
        require(len(x)==ra["site_rows"] and
                len(x)==ra["source_templates"]*4*N_SITE and
                len(y)==rb["site_rows"] and
                len(y)==rb["fitted_models"]*2*N_SITE,
                "Original source-site full sample incomplete")
        require(not x.duplicated(["candidate","env_bg","rank_bg","site"]).any()
                and not y.duplicated(["candidate","background","site"]).any(),
                "Duplicate original source site identity")
        site_g17.append(x)
        site_g15.append(y)
        receipts.append(dict(shard=ii,G17_refit_receipt_sha=sha(a),
                             G15_original_receipt_sha=sha(b),
                             G17_files=ra["files_sha256"],
                             G15_original_files=rb["files_sha256"]))
    a=pd.concat(site_g17,ignore_index=True)
    b=pd.concat(site_g15,ignore_index=True)
    require(len(a)==N_TEMPLATES*4*N_SITE
            and len(b)==N_TEMPLATES*2*N_SITE and
            a.candidate.nunique()==b.candidate.nunique()==N_TEMPLATES,
            "G17 complete 201×4×4248 or original G15 complete 201×2×4248 missing")
    for frame in (a,b):
        prob=frame.predicted.to_numpy(float)
        require(np.isfinite(prob).all() and (prob>0).all() and (prob<1).all(),
                "Nonfinite original observation probability")
        n=frame.n_completed.to_numpy(float)
        k=frame.k_strong.to_numpy(float)
        require(np.all((n>0)&(k>=0)&(k<=n)),"Original adult strong-call response altered")
        err=float(np.max(abs(
            (-(k*np.log(prob)+(n-k)*np.log1p(-prob)))-
             frame.loss.to_numpy(float))))
        require(err<1e-11,f"Source adult acoustic NLL different: {err}")
    return a,b,receipts,sourceinfo


def original_diagonal(a,b):
    d=a[a.env_bg==a.rank_bg].copy()
    o=b.rename(columns={"background":"env_bg"}).copy()
    o["rank_bg"]=o.env_bg
    key=["candidate","env_bg","rank_bg","site"]
    require(len(d)==len(o)==N_TEMPLATES*2*N_SITE,
            "G17 and frozen G15 diagonal identity missing")
    da=d.set_index(key).sort_index()
    ob=o.set_index(key).sort_index()
    require(da.index.is_unique and da.index.equals(ob.index),
            "Original G15 diagonal 201 source ×2 background ×4248 site ID differs")
    for col in ("spatial_block","fold","n_completed","k_strong"):
        require(np.array_equal(da[col],ob[col]),
                "Original G17/G15 field or fold source mismatch "+col)
    probs=abs(da.predicted.to_numpy(float)-ob.predicted.to_numpy(float))
    numerical=[]
    for bg in FIELDS:
        x=d[d.env_bg==bg];y=o[o.env_bg==bg]
        ids=["candidate","site"]
        x=x.set_index(ids).sort_index()
        y=y.set_index(ids).sort_index()
        require(x.index.equals(y.index),"Original background site source mismatch")
        per_model=(x.reset_index().groupby("candidate").loss.sum()-
                   y.reset_index().groupby("candidate").loss.sum())/N_VISITS
        per_block=(x.reset_index().groupby(["candidate","spatial_block"]).loss.sum()-
                   y.reset_index().groupby(["candidate","spatial_block"]).loss.sum())
        numerical.append(dict(background=bg,original_source_templates=N_TEMPLATES,
            original_source_sites=N_SITE,
            max_abs_probability=float(np.max(abs(x.predicted-y.predicted))),
            max_abs_block_loss=float(per_block.abs().max()),
            max_abs_per_template_NLL_per_visit=float(per_model.abs().max()),
            G17_original_refit_frozen_numeric_gate_pass=False,
            G17b_uses_original_G15_probability_verbatim=True))
    fail=pd.DataFrame(numerical)
    # This MUST document the original G17 numerical replay failure.
    require(not fail.G17_original_refit_frozen_numeric_gate_pass.any(),
            "Do not turn original G17 failure into a pass")
    return o,fail


def original_NLL_mixed(a,anchored):
    off=a[a.env_bg!=a.rank_bg].copy()
    both=pd.concat([off,anchored],ignore_index=True)
    require(len(both)==N_TEMPLATES*4*N_SITE
            and not both.duplicated(["candidate","env_bg","rank_bg","site"]).any()
            and both.groupby(["candidate","env_bg","rank_bg"]).site.nunique().eq(N_SITE).all(),
            "G17b exact anchored original 2×2 source and field support missing")
    # Every crossed source cell uses the *same* original 4248 acoustic sites.
    q=(both.groupby(["candidate","env_bg","rank_bg"],sort=True)
       .agg(visits=("n_completed","sum"),strong=("k_strong","sum"),
            sites=("site","size"),blocks=("spatial_block","nunique")))
    require(q.visits.eq(N_VISITS).all() and q.strong.eq(N_STRONG).all()
            and q.sites.eq(N_SITE).all() and q.blocks.eq(N_BLOCK).all(),
            "G17b crossed source adult response/56 geographic blocks changed")
    return both


def source_sensitivity(sites_refit,sites_anchored):
    out={}
    for name,d in [("new_refit",sites_refit),("exact_G15_anchor",sites_anchored)]:
        block=(d.groupby(["candidate","env_bg","rank_bg","spatial_block"],sort=True)
               .agg(total_loss=("loss","sum"),visits=("n_completed","sum"),
                    strong_events=("k_strong","sum"),sites=("site","size")).reset_index())
        score,cell=compute_four_cell(block)
        effects=factorial(cell)
        out[name]=(block,score,cell,effects)
    x=out["new_refit"][3];y=out["exact_G15_anchor"][3]
    rows=[]
    for key in ("D_UU","D_UT","D_TU","D_TT",
                "original_diagonal_difference",
                "environment_main_effect","source_rank_main_effect",
                "crossed_nonlinear_interaction"):
        a=float(x[key]);b=float(y[key])
        rows.append(dict(component=key,original_G17_refit_value=a,
                         exact_G15_anchored_value=b,
                         anchored_minus_refit=b-a,
                         same_sign_or_zero=(np.sign(a)==np.sign(b)),
                         diagnostic_only_after_original_gate_failure=True))
    return out,pd.DataFrame(rows)


def independent_original_G15_NLL_anchor(diagonal_block):
    archived=G15/"G15_all_null_56block_losses.csv"
    receipt=json.loads((G15/"G15_full_source_audit_receipt.json").read_text())
    require(sha(archived)==receipt["file_sha256"][archived.name],
            "Source-original G15 56-block score SHA changed")
    data=pd.read_csv(archived)
    exact=diagonal_block.copy()
    exact=exact.rename(columns={"env_bg":"background"})
    exact=exact[exact.background==exact.rank_bg].drop(columns="rank_bg")
    keys=["candidate","background","spatial_block"]
    a=data.set_index(keys).sort_index()
    b=exact.set_index(keys).sort_index()
    require(len(a)==len(b)==N_TEMPLATES*2*N_BLOCK and a.index.equals(b.index),
            "Original frozen G15 201×2×56 block alignment absent")
    for c1,c2 in [("total_loss","total_loss"),("original_visits","visits"),
                  ("strong_calls","strong_events"),("sites","sites")]:
        err=float(np.max(np.abs(a[c1].to_numpy(float)-b[c2].to_numpy(float))))
        require(err<1e-9,"Original exact G15 source 56-block replay failed "+c1)
    return True


def run(g17_shards,g15_shards,out=RESULTS):
    a,b,sha_rec,source=load_orig(g17_shards,g15_shards)
    diag,num=original_diagonal(a,b)
    anchored=original_NLL_mixed(a,diag)
    result,sensitivity=source_sensitivity(a,anchored)
    ablock,ascore,acell,aeffect=result["exact_G15_anchor"]
    nblock,nscore,ncell,neffect=result["new_refit"]
    independent_original_G15_NLL_anchor(ablock)
    prior=pd.read_csv(G15/"G15_G14_signonly_vs_ABC_null_comparison.csv")
    require(len(prior)==2,"Original G15 signed 2-background rankings absent")
    for bg in FIELDS:
        old=prior[prior.background==bg].iloc[0]
        exact=acell[(acell.env_bg==bg)&(acell.rank_bg==bg)].iloc[0]
        require(abs(exact.ABC_794_nll-old.accepted_ABC_NLL)<1e-12
                and abs(exact.mean199null_nll-old.null_mean_NLL)<1e-12
                and exact.source_nulls_better_or_equal_ABC==old.null_NLL_less_or_equal_ABC
                and exact.conditional_source_p==old.empirical_upper_tail_p,
                "G17b original anchored G15 diagonal source score/199 null rank not EXACT")
    bt=original_spatial_bootstrap(ablock)
    table=[]
    for metric,draw in bt.items():
        lo,hi=np.quantile(draw,(.025,.975))
        table.append(dict(component=metric,estimate=float(aeffect[metric]),
                          original_56block_bootstrap_low=float(lo),
                          original_56block_bootstrap_high=float(hi),
                          original_block_bootstrap_replicates=9999,
                          bootstrap_seed=20261108))
    summary=pd.DataFrame(table)
    key=sensitivity[sensitivity.component.isin((
        "original_diagonal_difference","environment_main_effect",
        "source_rank_main_effect","crossed_nonlinear_interaction"))]
    max_effect_error=float(key.anchored_minus_refit.abs().max())
    offdiag=acell[acell.env_bg!=acell.rank_bg]
    require(len(offdiag)==2 and len(acell)==4,
            "G17b source-cross rank offdiagonal not both represented")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    tables={
      "G17B_all_four_ABC_vs_199source_null.csv":acell,
      "G17B_all_804_source_template_NLL_scores.csv":ascore,
      "G17B_original_45024_geographic_block_losses.csv.gz":ablock,
      "G17B_frozen_56block_bootstrap_9999_effects.csv":summary,
      "G17B_original_failed_G17_numeric_replay_diagnostic.csv":num,
      "G17B_refit_vs_exact_diagonal_factorial_sensitivity.csv":sensitivity,
    }
    for name,frame in tables.items():
        if name.endswith(".gz"):
            frame.to_csv(out/name,index=False,compression={"method":"gzip","mtime":0})
        else:frame.to_csv(out/name,index=False)
    receipt=dict(
       status="G17B_EXACT_G15_ANCHORED_POSTHOC_2X2_SOURCE_AUDIT_SUCCESS",
       original_G17_frozen_numeric_source_gate_pass=False,
       original_G17_attempts_with_failed_source_gates=[
          42431413331,42431674245],
       G17b_is_a_new_posthoc_method_after_gate_failure=True,
       G17_original_successful_source_shards=4,
       G15_original_successful_source_shards=4,
       G17_original_complete_site_refits=len(a),
       G17b_exact_anchored_site_rows=len(anchored),
       original_G15_diagonal_site_rows=len(diag),
       original_ABC_source_templates=N_TEMPLATES,
       original_rate_context_null_templates=N_NULLS,
       original_sites=N_SITE,original_visits=N_VISITS,
       original_geographic_blocks=N_BLOCK,
       source_G15_template_sha256=source["file_sha256"][
          "G15_frozen_source_templates.csv"],
       original_G15_diagonal_reproduced_exactly=True,
       original_G15_source_ranking_uniform=0,
       original_G15_source_ranking_target_group=199,
       original_2x2_anchored_effects=aeffect,
       original_2x2_G17_refit_effects=neffect,
       max_absolute_main_factorial_effect_refit_difference=max_effect_error,
       all_factorial_component_signs_unchanged_by_exact_diagonal_anchor=bool(
           key.same_sign_or_zero.all()),
       G14_G15_both_background_field_mechanism_gates_pass=False,
       no_new_model_fits=True,no_new_biological_models=True,
       not_independent_field_validation=True,no_wild_ABC_mechanism_posterior=True,
       source_original_shard_SHA_receipts=sha_rec,
       files_sha256={name:sha(out/name) for name in tables},
    )
    (out/"G17B_complete_posthoc_source_audit_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("G17B_EXACT_SOURCE_ANCHOR_DECOMPOSITION "+json.dumps({
        "status":receipt["status"],"effects":aeffect,
        "refit_sensitivity":key.to_dict("records"),
        "source_199_null_ranking":acell.to_dict("records"),
        "bootstrap":summary.to_dict("records")}),flush=True)
    return receipt


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--g17-shards",type=Path,required=True)
    ap.add_argument("--g15-shards",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    v=ap.parse_args()
    run(v.g17_shards,v.g15_shards,v.out)
