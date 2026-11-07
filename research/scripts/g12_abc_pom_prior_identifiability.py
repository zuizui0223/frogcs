"""Audit the original model-native R2 ABC–POM screen under fixed alternative rate priors.

No posterior fitted to field observations and no new biological simulation.
Source: original 20,000 **80-year** model proposals, run #41262102436;
SHA manifest: verified R2 source run #41390511365.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd

N=20000
SEED=20261107
RATE_NAMES=("attack","rho","conversion")
RATE_LEVELS=((.5,1.5,3.),(.25,.5,.75),(2.,4.,8.))
U=(1/3,1/3,1/3)
L=(.6,.3,.1)
H=(.1,.3,.6)
PRIORS={
 "uniform_original":(U,U,U),
 "weak_attack":(L,U,U),
 "strong_attack":(H,U,U),
 "high_recruitment":(U,H,U),
 "low_recruitment":(U,L,U),
 "fast_conversion":(U,U,H),
 "slow_conversion":(U,U,L),
 "joint_pattern_favorable":(L,H,H),
 "joint_pattern_unfavorable":(H,L,L)
}
EPS=(0.,1e-6,1e-4,1e-3,1e-2,5e-2,1e-1)
FEATURES=("edge_SD","edge_DS","cover_SF","support_DF","cover_DF",
          "cover_DS","cover_SD","support_DS","survival","timing",
          "reverse","litter","behavior","context_id","gate_code",
          "refuge_order","strength")
SIGNS=("OS","OV","SV","OSV")
STATUS="G12_ORIGINAL_20K_MODEL_NATIVE_ABC_POM_PRIOR_AUDIT_SUCCESS"

def require(v,msg):
    if not bool(v):raise AssertionError(msg)

def accept(a,eps):
    return (a[:,0]<-eps)&(a[:,1]<-eps)&(a[:,2]>eps)&(a[:,3]>eps)

def load(original, receipt_file, frozen_rates, frozen_marginals):
    original=Path(original)
    receipt=json.loads(Path(receipt_file).read_text())
    require(receipt["status"]=="FROGCS_MAIN3600_R2_ALL_20000_SOURCE_RATES_STRUCTURES_VERIFIED"
        and receipt["original_workflow"]==41262102436
        and receipt["original_main_sha"]=="5e2f0a87c639df373fa2700b29403d2ab417a1cc"
        and receipt["source_draws"]==N
        and receipt["accepted_four_sign"]==794
        and receipt["accepted_after_original_survival_floor"]==426,
        "Original R2 source receipt changed")
    paths=sorted(original.glob("shard_*.csv.gz"))
    require(len(paths)==8 and {p.name for p in paths}==
            {f"shard_{i:02}.csv.gz" for i in range(8)},
            "Missing original eight 80-year source archives")
    data=[]
    for path in paths:
        require(hashlib.sha256(path.read_bytes()).hexdigest()==
                receipt["original_shard_sha256"][path.name],
                "Original source SHA mismatch: "+path.name)
        x=pd.read_csv(path)
        require(len(x)==2500, "Original shard not 2500 proposals")
        data.append(x)
    d=pd.concat(data,ignore_index=True).sort_values("draw_id").reset_index(drop=True)
    require(len(d)==N and d.draw_id.eq(np.arange(N)).all()
            and d.model_id.between(0,3599).all()
            and d.model_id.nunique()==3582
            and d.loc[d.accepted,"model_id"].nunique()==647,
            "R2 complete draw IDs / canonical original model IDs changed")
    require(d[list(FEATURES)].notna().all().all(), "Missing categorical model feature")
    for axis,levels in zip(RATE_NAMES,RATE_LEVELS):
        require(set(d[axis].astype(float))==set(levels),"Rate prior changed: "+axis)
    z=d[["log_"+x for x in SIGNS]].to_numpy(float)
    raw=d[["raw_"+x for x in SIGNS]].to_numpy(float)
    require(np.isfinite(z).all() and np.isfinite(raw).all(), "Invalid source interaction contrast")
    baseline=accept(z,1e-6)
    floor=d.floor_ok.to_numpy(bool)
    require(np.array_equal(baseline,d.accepted.to_numpy(bool))
            and baseline.sum()==794 and np.sum(baseline&floor)==426
            and np.array_equal(accept(raw,1e-6),d.raw_accepted.to_numpy(bool)),
            "Original 794 and 426 or raw-model acceptance drift")
    rates=pd.read_csv(frozen_rates)
    calc=d.groupby(list(RATE_NAMES),sort=True).accepted.agg(["sum","size"]).reset_index()
    joint=calc.merge(rates,on=list(RATE_NAMES),validate="one_to_one")
    require(len(joint)==27
            and np.array_equal(joint["sum"].to_numpy(int),joint.n_accepted.to_numpy(int))
            and np.array_equal(joint["size"].to_numpy(int),joint.n_proposals.to_numpy(int)),
            "Original 27 rate-cell table changed")
    marg=pd.read_csv(frozen_marginals)
    require(len(marg)==9,"Original nine rate margins missing")
    for _,r in marg.iterrows():
        g=d.loc[d[r.rate_axis].eq(float(r.rate_level))]
        require(len(g)==int(r.n_proposals) and int(g.accepted.sum())==int(r.n_accepted),
                "Original source rate-margin drift")
    return d,receipt,z,raw

def weights(d,scenario):
    w=np.ones(len(d))
    for axis,levels,prob in zip(RATE_NAMES,RATE_LEVELS,PRIORS[scenario]):
        w*=3*d[axis].map(dict(zip(levels,prob))).to_numpy(float)
    require((w>0).all() and np.isfinite(w).all(),"Invalid alternative synthetic prior")
    return w

def ess(w):
    return float(w.sum()**2/np.dot(w,w)) if np.any(w) else 0.

def diversity(ids,w):
    hist=np.bincount(ids,weights=w,minlength=3600)
    hist=hist/hist.sum()
    positive=hist[hist>0]
    q=np.sort(hist)[::-1]
    return dict(distinct_accepted_models=int((hist>0).sum()),
        shannon_effective_models=float(np.exp(-np.sum(positive*np.log(positive)))),
        simpson_effective_models=float(1/np.square(hist).sum()),
        top10_accepted_mass=float(q[:10].sum()),
        top50_accepted_mass=float(q[:50].sum()))

def calculate(d,z,raw):
    flags=d.accepted.to_numpy(bool)
    floor=d.floor_ok.to_numpy(bool)
    ids=d.model_id.to_numpy(int)
    prior_rows=[]
    feature_rows=[]
    for name in PRIORS:
        w=weights(d,name)
        accepted_weight=w*flags
        row=dict(scenario=name,n_proposals=N,original_accepted=794,
                 weighted_acceptance_probability=float(accepted_weight.sum()/w.sum()),
                 weighted_floor_compatible_probability=float(np.dot(accepted_weight,floor)/w.sum()),
                 proposal_effective_sample_size=ess(w),
                 accepted_effective_sample_size=ess(accepted_weight))
        row.update(diversity(ids[flags],w[flags]))
        prior_rows.append(row)
        for feature in FEATURES:
            vals=d[feature].astype(str).to_numpy()
            for level in sorted(set(vals)):
                matched=vals==level
                base_mass=float(w[matched].sum()/w.sum())
                conditional=float(accepted_weight[matched].sum()/accepted_weight.sum())
                feature_rows.append(dict(scenario=name,feature=feature,level=level,
                    n_prior=int(matched.sum()),n_accepted=int((matched&flags).sum()),
                    weighted_prior_share=base_mass,
                    weighted_accepted_share=conditional,
                    enrichment=conditional/base_mass if base_mass else float("nan")))
    epsrows=[]
    for e in EPS:
        matches=accept(z,e)
        epsrows.append(dict(epsilon=e,n_proposals=N,n_accepted=int(matches.sum()),
            n_accepted_and_floor=int(np.sum(matches&floor)),
            distinct_models=int(d.loc[matches,"model_id"].nunique()),
            n_overlap_with_baseline=int(np.sum(matches&flags)),
            baseline_accepted_lost=int(np.sum(flags&~matches)),
            newly_accepted_relative_baseline=int(np.sum(matches&~flags))))
    rawflag=accept(raw,1e-6)
    rawreport=dict(epsilon=1e-6,raw_accepted=int(rawflag.sum()),
                   log_accepted=794,both=int(np.sum(rawflag&flags)),
                   raw_only=int(np.sum(rawflag&~flags)),
                   log_only=int(np.sum(flags&~rawflag)),
                   raw_and_synthetic_floor=int(np.sum(rawflag&floor)),
                   raw_accepted_distinct_models=int(d.loc[rawflag,"model_id"].nunique()))
    require(prior_rows[0]["distinct_accepted_models"]==647
            and abs(prior_rows[0]["weighted_acceptance_probability"]-794/N)<1e-15
            and epsrows[1]["n_accepted"]==794,
            "Original R2 unchanged-screen gate failed")
    return pd.DataFrame(prior_rows),pd.DataFrame(feature_rows),pd.DataFrame(epsrows),rawreport

def run(args):
    d,r,z,raw=load(args.source,args.receipt,args.rates,args.marginals)
    pri,feat,eps,raw_info=calculate(d,z,raw)
    out=args.out
    out.mkdir(parents=True,exist_ok=True)
    saved={
      "G12_prior_sensitivity.csv":pri,
      "G12_all_feature_level_enrichments.csv":feat,
      "G12_four_sign_epsilon_sensitivity.csv":eps,
    }
    for name,frame in saved.items():frame.to_csv(out/name,index=False)
    (out/"G12_raw_vs_log_contrast.json").write_text(
        json.dumps(raw_info,indent=2)+"\n")
    output=list(out.glob("G12_*.csv"))+[out/"G12_raw_vs_log_contrast.json"]
    rec=dict(status=STATUS,
        source_original_actions_run=41262102436,
        source_R2_verified_actions_run=41390511365,
        original_main_sha=r["original_main_sha"],
        source_shard_sha256=r["original_shard_sha256"],
        n_proposals=N,accepted_4sign=794,accepted_synthetic_floor=426,
        distinct_accepted_canonical_models=647,
        alternative_synthetic_rate_priors=len(pri),model_sign_tolerances=len(eps),
        full_27_rate_original_numerators_denominators_verified=True,
        all_9_original_one_axis_rate_margins_verified=True,
        posterior_calibrated_to_field_observations=False,
        no_new_biological_simulations=True,
        no_field_mechanism_identification=True,
        files_sha256={x.name:hashlib.sha256(x.read_bytes()).hexdigest()
                      for x in output})
    (out/"G12_full_source_receipt.json").write_text(json.dumps(rec,indent=2)+"\n")
    print("G12_SOURCE_20K_RATE_PRIOR_AND_EPS_AUDIT_SUCCESS "+
          json.dumps({k:rec[k] for k in
              ("status","n_proposals","accepted_4sign",
               "distinct_accepted_canonical_models","alternative_synthetic_rate_priors")}),
          flush=True)
    return rec

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True,type=Path)
    ap.add_argument("--receipt",required=True,type=Path)
    ap.add_argument("--rates",required=True,type=Path)
    ap.add_argument("--marginals",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    run(ap.parse_args())
