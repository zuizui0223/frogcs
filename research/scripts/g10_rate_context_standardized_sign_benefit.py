"""G10: G9 rate/context-standardized sign-creation versus demographic benefit.

Post-hoc, source-background-cluster bootstrap. These are synthetic model
outcomes, not observed pond outcomes or a causal intervention on sign success.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

S, R, C, B, SEED = 256, 27, 3, 10000, 20261107
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/"results/g8_27rate_paired_20261107/audited"
OUT = ROOT/"results/g10_standardized_sign_benefit_20261107"


def ensure(v, message):
    if not bool(v):
        raise AssertionError(message)


def load_inputs(source):
    f = source/"g8_all_source_rate_context_paired.csv.gz"
    r = json.loads((source/"g8_completion_receipt.json").read_text())
    digest = hashlib.sha256(f.read_bytes()).hexdigest()
    ensure(r["status"]=="G8_27RATE_TRUE80_ALL_256_SOURCE_SUCCESS"
           and r["output_sha256"][f.name]==digest, "Original G8 source receipt drift")
    d = pd.read_csv(f).sort_values(["source_id","rate_id","context_id"])
    expected = pd.MultiIndex.from_product([range(S),range(R),range(C)])
    idx = pd.MultiIndex.from_frame(d[["source_id","rate_id","context_id"]])
    ensure(len(d)==S*R*C and idx.equals(expected), "G8 source pairs incomplete")
    ensure(np.isin(d.compatibility,[-1.,0.,1.]).all()
           and np.allclose(d.arm11_compatibility-d.arm00_compatibility,
                           d.compatibility,rtol=0,atol=0), "Invalid sign classes")
    ensure(np.isfinite(d.frog_log_cohort).all(), "Nonfinite frog response")
    ensure(abs(d.compatibility.mean()-.027054398148148147)<1e-12
           and abs(d.frog_log_cohort.mean()+.04029997695177505)<1e-12,
           "G8 published aggregate changed")
    sign = d.compatibility.to_numpy().reshape(S,R*C)
    frog = d.frog_log_cohort.to_numpy().reshape(S,R*C)
    ensure(int((sign==1).sum())==782 and
           int(((sign==1)&(frog<0)).sum())==571, "G9 original 571/782 drift")
    rate = pd.read_csv(source/"g8_27rate_descriptive_counts.csv").set_index("rate_id")
    ensure(len(rate)==R and set(rate.index)==set(range(R)), "G8 rate grid absent")
    attack = rate.reindex(range(R)).attack.to_numpy(float)
    ensure(np.isin(attack,[.5,1.5,3.]).all(), "Unexpected attack grid")
    return sign, frog, attack, digest


def components(sign, frog):
    """Original and bootstrapped source-by-stratum sufficient statistics."""
    weights=np.random.default_rng(SEED).multinomial(S,np.full(S,1/S),size=B)
    loss=frog<0
    output={}
    for name,mask in [("new",sign==1),("other",sign!=1),
                      ("unchanged",sign==0)]:
        a={"n":mask.astype(float),"loss":(mask&loss).astype(float),
           "delta":frog*mask}
        output[name]=({"n":a["n"].sum(axis=0),
                        "loss":a["loss"].sum(axis=0),
                        "delta":a["delta"].sum(axis=0)},
                      {k:weights@v for k,v in a.items()})
    return output


def compare(new, other, eligible):
    n1,l1,d1=[new[0][k] for k in ("n","loss","delta")]
    n0,l0,d0=[other[0][k] for k in ("n","loss","delta")]
    mask=np.asarray(eligible,bool)&(n1>0)&(n0>0)
    total=float(n1[mask].sum())
    ensure(total>0, "No overlap in this requested group")
    p1=l1[mask].sum()/total
    p0=np.sum(n1[mask]*l0[mask]/n0[mask])/total
    f1=d1[mask].sum()/total
    f0=np.sum(n1[mask]*d0[mask]/n0[mask])/total
    bn1,bl1,bd1=[new[1][k][:,mask] for k in ("n","loss","delta")]
    bn0,bl0,bd0=[other[1][k][:,mask] for k in ("n","loss","delta")]
    denom=bn1.sum(axis=1)
    valid=(denom>0)&np.all((bn1==0)|(bn0>0),axis=1)
    ensure(valid.sum()>0, "No supported cluster bootstrap draws")
    with np.errstate(divide="ignore",invalid="ignore"):
        loss0=np.divide(bl0,bn0,out=np.zeros_like(bl0),where=bn0>0)
        effect0=np.divide(bd0,bn0,out=np.zeros_like(bd0),where=bn0>0)
        diff_loss=100*(bl1.sum(axis=1)-np.sum(bn1*loss0,axis=1))/np.maximum(denom,1)
        diff_log=(bd1.sum(axis=1)-np.sum(bn1*effect0,axis=1))/np.maximum(denom,1)
    ci_loss=np.quantile(diff_loss[valid],[.025,.975])
    ci_log=np.quantile(diff_log[valid],[.025,.975])
    return dict(n_supported_strata=int(mask.sum()),
        new_cases_covered=int(total),p_loss_new=float(p1),
        p_loss_comparator_standardized=float(p0),
        adjusted_loss_difference_pp=float(100*(p1-p0)),
        adjusted_loss_low_pp=float(ci_loss[0]),
        adjusted_loss_high_pp=float(ci_loss[1]),
        log_cohort_new=float(f1),log_cohort_comparator_standardized=float(f0),
        adjusted_log_difference=float(f1-f0),
        adjusted_log_low=float(ci_log[0]),adjusted_log_high=float(ci_log[1]),
        bootstrap_valid=int(valid.sum()),bootstrap_total=B)


def run(source=SOURCE,out=OUT):
    source,out=Path(source),Path(out)
    sign,frog,attack,src_sha=load_inputs(source)
    stats=components(sign,frog)
    nnew=stats["new"][0]["n"]
    nother=stats["other"][0]["n"]
    nunchanged=stats["unchanged"][0]["n"]
    groups={"all":np.ones(R*C,bool)}
    groups.update({"context_"+str(c):np.tile(np.arange(C)==c,R)
                   for c in range(C)})
    groups.update({"attack_"+str(a):np.repeat(attack==a,C)
                   for a in (.5,1.5,3.)})
    plans=[(g,"other","any",m) for g,m in groups.items()]
    plans.extend([("all","unchanged","any",groups["all"]),
                  ("all","other","5_each",groups["all"] & (nnew>=5)&(nother>=5))])
    rows=[]
    for group,comp,rule,include in plans:
        s=compare(stats["new"],stats[comp],include)
        n_all=int(nnew[groups[group]].sum())
        s.update(group=group,comparator=comp,support_rule=rule,
                 n_strata_in_scope=int(groups[group].sum()),
                 new_cases_in_scope=n_all,
                 new_fraction_covered=s["new_cases_covered"]/max(n_all,1))
        rows.append(s)
    strata=[]
    for rid in range(R):
        for ctx in range(C):
            h=rid*C+ctx
            ne=int(nnew[h]);nc=int(nother[h]);nu=int(nunchanged[h])
            nl=int(stats["new"][0]["loss"][h])
            ncl=int(stats["other"][0]["loss"][h])
            strata.append(dict(rate_id=rid,context_id=ctx,
                attack=attack[rid],n_backgrounds=S,n_new=ne,n_other=nc,
                n_unchanged=nu,n_loss_new=nl,n_loss_other=ncl,
                comparable=bool(ne and nc),supported_5_each=bool(ne>=5 and nc>=5),
                loss_rate_new=nl/ne if ne else np.nan,
                loss_rate_other=ncl/nc if nc else np.nan))
    est=pd.DataFrame(rows);st=pd.DataFrame(strata)
    p=est.query("group=='all' and comparator=='other' and support_rule=='any'").iloc[0]
    ensure(int(p.n_supported_strata)==50 and int(p.new_cases_covered)==782,
           "Must preserve all 782 new-sign records across 50 identifiable strata")
    ensure(abs(p.p_loss_new-571/782)<1e-12,"G9 loss fraction mismatch")
    ensure(len(st)==R*C and st.n_backgrounds.eq(S).all(),
           "All 81 rate-context strata must be reported")
    out.mkdir(parents=True,exist_ok=True)
    est.to_csv(out/"g10_standardized_comparisons.csv",index=False)
    st.to_csv(out/"g10_all_81_strata.csv",index=False)
    r=dict(status="G10_RATE_CONTEXT_STANDARDIZED_SOURCE_AUDIT_SUCCESS",
       input_g8_sha256=src_sha,n_source_structures=S,n_rates=R,n_contexts=C,
       n_source_rate_context=S*R*C,n_new_sign=782,n_new_sign_loss=571,
       original_all_population_loss_fraction=float((frog<0).mean()),
       primary_supported_strata=int(p.n_supported_strata),
       primary_new_cases_covered=int(p.new_cases_covered),
       primary_adjusted_loss_difference_pp=float(p.adjusted_loss_difference_pp),
       primary_adjusted_loss_ci95_pp=[float(p.adjusted_loss_low_pp),float(p.adjusted_loss_high_pp)],
       primary_valid_bootstrap=int(p.bootstrap_valid),bootstrap_draws=B,
       bootstrap_seed=SEED,posthoc=True,no_biological_reruns=True,
       no_field_causal_identification=True,
       results_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest()
                       for f in sorted(out.glob("g10_*.csv"))})
    (out/"g10_source_receipt.json").write_text(json.dumps(r,indent=2)+"\n")
    print("G10_MODEL_RATE_CONTEXT_ADJUSTED "+json.dumps(
        {k:r[k] for k in ("status","primary_adjusted_loss_difference_pp",
                           "primary_adjusted_loss_ci95_pp","primary_new_cases_covered")}))
    return r


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=SOURCE)
    p.add_argument("--out",type=Path,default=OUT)
    a=p.parse_args()
    run(a.source,a.out)
