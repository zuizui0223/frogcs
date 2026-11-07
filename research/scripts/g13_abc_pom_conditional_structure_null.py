"""G13 source-audited 81-rate-by-context conditional-null ABC/POM structure test.

Permute acceptance labels only WITHIN exact hypothetical rate × original developmental
context strata; preserves original 20,000 proposal exposures and all 81 accepted counts.
This cannot identify a wild Bayesian posterior or natural trophic mechanism.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE=Path(__file__).resolve().parents[1]/"results/g12_abc_pom_prior_20261107"
OUT=Path(__file__).resolve().parents[1]/"results/g13_abc_structure_null_20261107"
N=20000
B=4999
SEED=20261107
G13_STATUS="G13_81_RATE_CONTEXT_CONDITIONAL_NULL_ABC_STRUCTURE_AUDIT_SUCCESS"
AXES=("edge_SD","edge_DS","cover_SF","cover_DF","cover_DS","cover_SD",
      "support_DF","support_DS","survival","timing","reverse","behavior",
      "litter","gate_code","refuge_order","strength")
STRATA=("attack","rho","conversion","context_id")

def require(x,message):
    if not bool(x):
        raise AssertionError(message)

def read_source(root):
    root=Path(root)
    receipt=json.loads((root/"source_receipt/r2_original_source_receipt.json").read_text())
    require(receipt["status"]=="FROGCS_MAIN3600_R2_ALL_20000_SOURCE_RATES_STRUCTURES_VERIFIED"
            and receipt["original_main_sha"]=="5e2f0a87c639df373fa2700b29403d2ab417a1cc"
            and receipt["source_draws"]==20000 and receipt["accepted_four_sign"]==794
            and receipt["accepted_after_original_survival_floor"]==426,
            "Original biological source provenance changed")
    paths=sorted((root/"original_20k").glob("shard_*.csv.gz"))
    require(len(paths)==8 and {p.name for p in paths}
            =={f"shard_{i:02d}.csv.gz" for i in range(8)},
            "All eight frozen original 80-year shards required")
    frames=[]
    for p in paths:
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        require(digest==receipt["original_shard_sha256"][p.name],
                "Original 80-year source SHA mismatch: "+p.name)
        q=pd.read_csv(p)
        require(len(q)==2500, "Incorrect size in original biological shard")
        frames.append(q)
    d=pd.concat(frames,ignore_index=True).sort_values("draw_id").reset_index(drop=True)
    require(len(d)==N and np.array_equal(d.draw_id.to_numpy(int),np.arange(N))
            and d.model_id.between(0,3599).all()
            and d.model_id.nunique()==3582, "Original 20k model catalogue or draw IDs drifted")
    z=d[["log_OS","log_OV","log_SV","log_OSV"]].to_numpy(float)
    observed=(z[:,0]<-1e-6)&(z[:,1]<-1e-6)&(z[:,2]>1e-6)&(z[:,3]>1e-6)
    viable=observed & d.floor_ok.to_numpy(bool)
    require(np.array_equal(observed,d.accepted.to_numpy(bool))
            and observed.sum()==794 and viable.sum()==426
            and d.loc[observed,"model_id"].nunique()==647,
            "Original model-native sign acceptance and distinct IDs changed")
    frozen=pd.read_csv(root/"source_receipt/twentyseven_rate_cells.csv")
    check=d.groupby(["attack","rho","conversion"]).accepted.agg(["sum","size"]).reset_index()
    merge=frozen.merge(check,on=["attack","rho","conversion"],validate="one_to_one")
    require(len(merge)==27
            and np.array_equal(merge.n_accepted.to_numpy(int),merge["sum"].to_numpy(int))
            and np.array_equal(merge.n_proposals.to_numpy(int),merge["size"].to_numpy(int)),
            "Original 27-cell R2 source acceptance counts inconsistent")
    require(all(x in d.columns for x in AXES+STRATA),"Source missing a predeclared mechanism axis")
    return d,observed,viable,receipt

def diversity(model_ids,selected):
    counts=np.bincount(model_ids[selected],minlength=3600).astype(float)
    k=counts.sum()
    require(k>0,"Empty accepted set")
    distinct=int((counts>0).sum())
    q=counts[counts>0]/k
    eff=float(np.exp(-np.dot(q,np.log(q))))
    top=np.sort(counts)[::-1]
    return distinct,eff,float(top[:10].sum()/k),float(top[:50].sum()/k)

def build_strata(d,observed):
    labels=d.loc[:,list(STRATA)].to_numpy(float)
    values,inverse=np.unique(labels,axis=0,return_inverse=True)
    require(len(values)==81,"Complete 27 rates × 3 developmental contexts required")
    indices=[np.where(inverse==i)[0] for i in range(81)]
    ks=np.array([int(observed[ix].sum()) for ix in indices],dtype=int)
    require(int(ks.sum())==794
            and sum(len(ix) for ix in indices)==N
            and all(len(ix)>0 for ix in indices),
            "Source conditional accepted strata incomplete")
    return values,indices,ks

def features(d):
    columns=[];binary=[]
    for axis in AXES:
        vals=d[axis].astype(str).to_numpy()
        for lev in sorted(np.unique(vals)):
            columns.append((axis,lev))
            binary.append(vals==lev)
    f=np.stack(binary,axis=1)
    require(len(columns)>=25 and f.shape[0]==len(d) and len(d)>0,
            "Incomplete mechanism/nuisance feature encoding")
    return columns,f

def expectation_by_strata(features,indices,ks):
    expected=np.zeros(features.shape[1],float)
    variance=np.zeros(features.shape[1],float)
    for ix,k in zip(indices,ks):
        n=len(ix)
        p=features[ix].mean(axis=0)
        expected+=k*p
        if n>1:
            variance+=k*p*(1-p)*(n-k)/(n-1)
    return expected,variance

def count_perm(selected_ids,models,feature_matrix):
    ct=np.bincount(models[selected_ids],minlength=3600).astype(float)
    prob=ct[ct>0]/len(selected_ids)
    shannon=float(np.exp(-np.dot(prob,np.log(prob))))
    return int((ct>0).sum()),shannon,feature_matrix[selected_ids].sum(axis=0)

def conditional_permutations(d,observed,viable,*,reps=B,seed=SEED):
    require(reps==B,"G13 permutation count is frozen to 4999")
    models=d.model_id.to_numpy(int)
    values,indices,ks=build_strata(d,observed)
    kv=np.array([int(viable[ix].sum()) for ix in indices],dtype=int)
    require(kv.sum()==426,"Full source original 5%-floor criterion differs")
    names,f=features(d)
    expected,var=expectation_by_strata(f,indices,ks)
    eligible=(expected>=5)&((794-expected)>=5)&(var>1e-8)
    require(int(eligible.sum())>=10,"Too few eligible feature-level null tests")
    observed_counts=f[observed].sum(axis=0).astype(float)
    obs_z=np.divide(observed_counts-expected,np.sqrt(var),
                    out=np.zeros_like(expected),where=var>0)
    d0=diversity(models,observed)
    d1=diversity(models,viable)
    k_null=np.empty(reps,int)
    eff_null=np.empty(reps,float)
    kv_null=np.empty(reps,int)
    effv_null=np.empty(reps,float)
    z_null=np.empty((reps,len(names)),float)
    rng=np.random.default_rng(seed)
    for j in range(reps):
        accepted_ids=np.concatenate([
            rng.choice(ix,size=int(k),replace=False) for ix,k in zip(indices,ks) if k>0])
        viable_ids=np.concatenate([
            rng.choice(ix,size=int(k),replace=False) for ix,k in zip(indices,kv) if k>0])
        require(len(accepted_ids)==794 and len(viable_ids)==426,
                "Null assignment lost conditioned source draws")
        k_null[j],eff_null[j],ct=count_perm(accepted_ids,models,f)
        kv_null[j],effv_null[j],_=count_perm(viable_ids,models,f)
        z_null[j]=np.divide(ct-expected,np.sqrt(var),
                            out=np.zeros(len(names),float),where=var>0)
    maximum=np.max(np.abs(z_null[:,eligible]),axis=1)
    feature_results=[]
    for i,(axis,level) in enumerate(names):
        condition_rate=expected[i]/794
        obsrate=observed_counts[i]/794
        result=dict(feature=axis,level=level,
            original_proposals=int(f[:,i].sum()),
            accepted_proposals=int(observed_counts[i]),
            observed_accepted_share=float(obsrate),
            conditional_null_expected_accepted_share=float(condition_rate),
            accepted_minus_conditional_null_expected_pp=float(100*(obsrate-condition_rate)),
            accepted_enrichment_ratio=float(obsrate/condition_rate) if condition_rate>0 else None,
            expected_accepted_count=float(expected[i]),
            hypergeometric_conditional_variance=float(var[i]),
            conditional_z=float(obs_z[i]) if var[i]>0 else None,
            maxT_family_eligible=bool(eligible[i]),
            permutation_two_sided_p=float((1+np.sum(np.abs(z_null[:,i])>=abs(obs_z[i])))/(reps+1))
                if eligible[i] else None,
            maxT_familywise_adjusted_p=float((1+np.sum(maximum>=abs(obs_z[i])))/(reps+1))
                if eligible[i] else None,
        )
        feature_results.append(result)
    perm=pd.DataFrame({
        "permutation":np.arange(1,reps+1),
        "four_sign_distinct_models":k_null,
        "four_sign_shannon_effective_models":eff_null,
        "four_sign_and_5pct_floor_distinct_models":kv_null,
        "four_sign_and_5pct_floor_shannon_effective_models":effv_null,
    })
    summary=[]
    for outcome,obs_stats,k,eff in [
        ("original_four_sign",d0,k_null,eff_null),
        ("original_sign_and_synthetic_floor",d1,kv_null,effv_null)
    ]:
        naccepted=794 if outcome=="original_four_sign" else 426
        for metric,observed_value,draws in [
            ("distinct_accepted_canonical_IDs",obs_stats[0],k),
            ("Shannon_effective_accepted_IDs",obs_stats[1],eff),
        ]:
            lo,hi=np.quantile(draws,[.025,.975])
            summary.append(dict(
                criterion=outcome,metric=metric,
                original_accepted_proposals=naccepted,
                observed=float(observed_value),
                conditional_null_mean=float(draws.mean()),
                conditional_null_median=float(np.median(draws)),
                conditional_null_95_low=float(lo),conditional_null_95_high=float(hi),
                observed_minus_null_mean=float(observed_value-draws.mean()),
                one_sided_concentration_p=float((1+np.sum(draws<=observed_value))/(reps+1)),
                permutation_draws=reps,
                conditioned_synthetic_strata=81,
            ))
    return pd.DataFrame(summary),pd.DataFrame(feature_results),perm,{
        "original_unique":d0[0],"original_shannon":d0[1],
        "null_eligible_feature_levels":int(eligible.sum()),
        "tested_feature_levels":len(names),
        "rate_context_accepted_counts":ks.tolist(),
        "rate_context_survival_counts":kv.tolist(),
        "rate_context_keys":values.tolist(),
        "null_preserves_exact_source_strata":True,
        "source_accepted_count":int(observed.sum()),
        "source_survival_count":int(viable.sum()),
    }

def run(source=SOURCE,out=OUT):
    source=Path(source);out=Path(out)
    d,accepted,viable,original=read_source(source)
    summary,levels,perms,metadata=conditional_permutations(d,accepted,viable)
    require(len(summary)==4 and len(perms)==B
            and levels.feature.nunique()==len(AXES)
            and int(levels.accepted_proposals.max())<=794,"Incomplete null output")
    out.mkdir(parents=True,exist_ok=True)
    targets={
        "G13_conditional_structure_concentration.csv":summary,
        "G13_all_feature_level_rate_context_adjusted.csv":levels,
        "G13_4999_exact_stratum_permutation_null.csv.gz":perms,
    }
    for name,frame in targets.items():
        if name.endswith(".gz"):
            frame.to_csv(out/name,index=False,compression={"method":"gzip","mtime":0})
        else:
            frame.to_csv(out/name,index=False)
    receipt={
        "status":G13_STATUS,
        "source_run":41262102436,"source_R2_verified_run":41390511365,
        "source_G12_full_audit":42370722253,
        "original_main_sha":original["original_main_sha"],
        "original_eight_shard_sha256":original["original_shard_sha256"],
        "original_proposals":N,"original_four_sign_accepted":794,
        "original_with_5pct_floor":426,"distinct_original_accepted_model_ids":647,
        "original_proposed_distinct_model_ids":3582,
        "synthetic_rate_by_context_strata":81,"null_replicates":B,"seed":SEED,
        "sources_of_statistical_uncertainty":"model-conditional permutation of synthetic proposals, not wild ponds",
        "no_new_biological_model_run":True,
        "posterior_for_natural_field_mechanism":False,
        **metadata,
        "outputs_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(out.iterdir()) if p.is_file()}
    }
    (out/"G13_source_audit_receipt.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("G13_SOURCE_CONDITIONAL_NULL_COMPLETE "+json.dumps({
      "status":G13_STATUS,"summary":summary.to_dict("records"),
      "eligible_feature_levels":metadata["null_eligible_feature_levels"],
      "total_feature_levels":metadata["tested_feature_levels"]}),flush=True)
    return receipt

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,default=SOURCE)
    parser.add_argument("--out",type=Path,default=OUT)
    args=parser.parse_args()
    run(args.source,args.out)
