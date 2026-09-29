#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_SPATIAL_DEPTH_CHORUS_DECOMPOSITION_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try:
            x=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if x in (1,2,3):
            vals[(rid,st,sp)].append(x)
    by=defaultdict(dict)
    for (rid,st,sp),x in vals.items():
        by[(rid,st)][sp]=max(x)
    return by

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0":
            vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad:
        raise RuntimeError(f"multiple SiteID values: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def stable(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ws=set(sampled[w]); ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def components(p,sampled,by):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    stops=sorted(sampled[w])
    dry_route=set()
    wet_by_species=defaultdict(dict)
    for st in stops:
        for sp,ci in by.get((d,st),{}).items():
            if ci>0:
                dry_route.add(sp)
        for sp,ci in by.get((w,st),{}).items():
            if ci>0:
                wet_by_species[sp][st]=int(ci)

    weak=ci2=ci3=0.0
    for sp,occ in wet_by_species.items():
        if sp in dry_route:
            continue
        k=len(occ)
        depth=max(k-2,0)
        if depth<=0:
            continue
        m=max(occ.values())
        if m==1:
            weak+=depth
        elif m==2:
            ci2+=depth
        elif m==3:
            ci3+=depth
        else:
            raise RuntimeError("unexpected CallingIndex")

    total=weak+ci2+ci3
    return {
        "third_plus_total":total,
        "third_plus_ci1_only":weak,
        "third_plus_ci2_max":ci2,
        "third_plus_ci3_present":ci3,
        "third_plus_strong":ci2+ci3,
    }

def fit(d,response):
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=d).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {
        "beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],
        "p":float(m.pvalues["rain_contrast"]),
        "n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique())
    }

def package(pairs,sampled,by):
    rows=[]
    for p in pairs.itertuples(index=False):
        r=p._asdict(); r.update(components(p,sampled,by)); rows.append(r)
    d=pd.DataFrame(rows)

    err=np.max(np.abs(
        d["third_plus_total"]
        -d["third_plus_ci1_only"]
        -d["third_plus_ci2_max"]
        -d["third_plus_ci3_present"]
    ))
    if err>1e-12:
        raise RuntimeError(f"pair identity failed: {err}")

    names=["third_plus_total","third_plus_ci1_only","third_plus_ci2_max","third_plus_ci3_present","third_plus_strong"]
    models={x:fit(d,x) for x in names}
    total=models["third_plus_total"]["beta"]
    strong=models["third_plus_strong"]["beta"]
    share=float(strong/total) if abs(total)>1e-12 else None
    beta_err=float(
        models["third_plus_total"]["beta"]
        -models["third_plus_ci1_only"]["beta"]
        -models["third_plus_ci2_max"]["beta"]
        -models["third_plus_ci3_present"]["beta"]
    )
    support=bool(
        strong>0
        and models["third_plus_strong"]["ci95"][0]>0
        and share is not None
        and share>0.5
    )
    return {
        "models":models,
        "strong_share_of_total_third_plus_beta":share,
        "identity_checks":{"max_pair_error":float(err),"beta_error":beta_err},
        "classification":{"strong_chorus_spatial_deepening_supported":support}
    }

def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    by=ci_map(raw,eligible,sampled)
    allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)

    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    site=site_map(raw,eligible)
    robust=same.loc[np.asarray([stable(p,sampled,site) for p in same.itertuples(index=False)],bool)].copy().reset_index(drop=True)

    full=package(allpairs,sampled,by)
    rob=package(robust,sampled,by)

    out={
      "analysis":"naamp_spatial_depth_chorus_decomposition_v0_1",
      "contract":"exploration/NAAMP_SPATIAL_DEPTH_CHORUS_DECOMPOSITION_CONTRACT_V0_1.json",
      "coverage":{
        "full_pairs":int(len(allpairs)),
        "robust_pairs":int(len(robust)),
        "robust_routes":int(robust.route_cluster.nunique())
      },
      "full":full,
      "robust_same_observer_physical_stop":rob,
      "classification":{
        "full_support":bool(full["classification"]["strong_chorus_spatial_deepening_supported"]),
        "joint_robust_support":bool(
            full["classification"]["strong_chorus_spatial_deepening_supported"]
            and rob["classification"]["strong_chorus_spatial_deepening_supported"]
        )
      },
      "interpretation_boundary":{
        "calling_index_is_ordinal":True,
        "reproductive_success_measured":False,
        "causal_rainfall_claim":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
