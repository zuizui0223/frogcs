"""G9 complete G8 sign-creation/benefit post-hoc audit; no new simulations."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

def run(source, out):
    source, out = Path(source), Path(out)
    raw = source/"g8_all_source_rate_context_paired.csv.gz"
    g8 = json.loads((source/"g8_completion_receipt.json").read_text())
    assert g8["status"] == "G8_27RATE_TRUE80_ALL_256_SOURCE_SUCCESS"
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == g8["output_sha256"][raw.name]
    x = pd.read_csv(raw).sort_values(["source_id","rate_id","context_id"])
    assert len(x) == 20736 and not x.duplicated(["source_id","rate_id","context_id"]).any()
    assert x.source_id.nunique()==256 and x.rate_id.nunique()==27 and x.context_id.nunique()==3
    assert (x.groupby(["source_id","rate_id"]).context_id.nunique()==3).all()
    assert np.allclose(x.arm11_compatibility-x.arm00_compatibility,x.compatibility,atol=0,rtol=0)
    assert abs(x.compatibility.mean()-.027054398148148147)<1e-12
    assert abs(x.frog_log_cohort.mean()+.04029997695177505)<1e-12
    att = pd.read_csv(source/"g8_27rate_descriptive_counts.csv").set_index("rate_id").attack
    x["attack"] = x.rate_id.map(att)
    x["sign_class"] = np.select([x.compatibility==1,x.compatibility==-1],
                                ["new","lost"],default="unchanged")
    x["frog_class"] = np.select([x.frog_log_cohort>0,x.frog_log_cohort<0],
                                ["gain","loss"],default="zero")
    grid = x.groupby(["sign_class","frog_class"],observed=True).size().rename("count").reset_index()
    out.mkdir(parents=True,exist_ok=True)
    grid.to_csv(out/"g9_full_joint_sign_benefit.csv",index=False)
    rates = []
    for (r,c),v in x.groupby(["rate_id","context_id"]):
        yes = v.arm11_compatibility==1
        new = v.compatibility==1
        rates.append({"rate_id":r,"context_id":c,"n":len(v),
                      "n_compatible_11":int(yes.sum()),"n_incompatible_11":int((~yes).sum()),
                      "comparable":bool(yes.any() and (~yes).any()),
                      "new_signs":int(new.sum()),"new_sign_frog_losses":int((new&(v.frog_log_cohort<0)).sum()),
                      "new_sign_frog_gains":int((new&(v.frog_log_cohort>0)).sum())})
    pd.DataFrame(rates).to_csv(out/"g9_rate_context_coverage.csv",index=False)
    sign=x.compatibility.to_numpy().reshape(256,27,3)
    frog=x.frog_log_cohort.to_numpy().reshape(256,27,3)
    accept=x.arm11_compatibility.to_numpy().reshape(256,27,3)
    idx=np.random.default_rng(20261107).integers(0,256,size=(10000,256))
    groups=[("all",np.ones((27,3),bool))]
    groups += [("context_"+str(c),np.broadcast_to(np.arange(3)==c,(27,3))) for c in range(3)]
    groups += [("attack_"+str(a),np.broadcast_to(np.isclose(att.loc[range(27)].to_numpy()[:,None],a),(27,3))) for a in (.5,1.5,3.)]
    rows=[]
    for name,mask in groups:
        new=np.broadcast_to(mask,(256,27,3)) & (sign==1)
        n=new.sum(axis=(1,2))
        num_loss=(new & (frog<0)).sum(axis=(1,2))
        num_gain=(new & (frog>0)).sum(axis=(1,2))
        num_effect=(new*frog).sum(axis=(1,2))
        acc=np.broadcast_to(mask,(256,27,3)) & (accept==1)
        aa=acc.sum(axis=(1,2))
        aaben=(acc & (frog>0)).sum(axis=(1,2))
        for label,num,den in [
            ("loss_fraction_new_sign",num_loss,n),
            ("gain_fraction_new_sign",num_gain,n),
            ("mean_log_frog_change_new_sign",num_effect,n),
            ("gain_fraction_compatible11",aaben,aa)]:
            ns=num[idx].sum(axis=1);ds=den[idx].sum(axis=1)
            boot=ns[ds>0]/ds[ds>0]
            q=np.quantile(boot,[.025,.975]) if len(boot)>0 else [np.nan,np.nan]
            rows.append({"group":name,"metric":label,"numerator":float(num.sum()),
                         "denominator":int(den.sum()),"value":float(num.sum()/den.sum()) if den.sum()>0 else np.nan,
                         "bootstrap_low":float(q[0]),"bootstrap_high":float(q[1]),
                         "valid_bootstrap_draws":len(boot)})
    report=pd.DataFrame(rows)
    report.to_csv(out/"g9_source_cluster_bootstrap.csv",index=False)
    primary=report.set_index(["group","metric"]).loc[("all","loss_fraction_new_sign")]
    assert int(primary.numerator)==571 and int(primary.denominator)==782
    assert int(pd.DataFrame(rates).comparable.sum())==50
    assert int(grid["count"].sum())==20736
    receipt={"status":"G9_ALL_20736_G8_JOINT_DIAGNOSTIC_PASS",
             "input_sha256":hashlib.sha256(raw.read_bytes()).hexdigest(),
             "n_structures":256,"n_rates":27,"n_contexts":3,"n_records":20736,
             "n_new_compatible":782,"new_sign_frog_losses":571,
             "n_strata_both_compatibility_classes":50,"bootstrap":10000,
             "bootstrap_source_cluster_seed":20261107,"posthoc":True,
             "no_new_biological_simulations":True,"not_empirical_field_validation":True,
             "output_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in out.glob("g9_*.csv")}}
    (out/"g9_completion_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"G9":receipt["status"],"loss":float(primary.value),
                      "interval":[float(primary.bootstrap_low),float(primary.bootstrap_high)]}))
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.source,a.out)
