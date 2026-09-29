#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_SITE_MEMORY_OPPORTUNITY_NORMALIZED_RECEIPT_V0_1.json"
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

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try:
            ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if ci in (1,2,3):
            vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict)
    for (rid,st,sp),x in vals.items():
        by[(rid,st)][sp]=max(x)
    return by

def stable_pair(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ws=set(sampled[w]); ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def build_strata(runs,sampled,site,ci):
    meta={}
    by_stratum=defaultdict(list)
    pools=defaultdict(set)
    site_species=defaultdict(set)
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        meta[rid]={"key":key,"year":int(r.SurveyYear)}
        by_stratum[key].append(rid)
        for st in sorted(sampled.get(rid,set())):
            sid=site.get((rid,st))
            if sid is None:
                continue
            for sp,val in ci.get((rid,st),{}).items():
                if int(val)>0:
                    pools[key].add(sp)
                    site_species[(rid,sid)].add(sp)
    return meta,by_stratum,{k:sorted(v) for k,v in pools.items()},site_species

def pair_summary(p,sampled,site,ci,meta,by_stratum,pools,site_species):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]
    others=[rid for rid in by_stratum[key] if rid not in (w,d)]

    memory_by_site=defaultdict(set)
    for rid in others:
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is not None:
                memory_by_site[sid].update(site_species.get((rid,sid),set()))

    dry_route=set()
    for st in sampled[d]:
        dry_route.update(ci.get((d,st),{}).keys())

    candidates=[sp for sp in pools.get(key,[]) if sp not in dry_route]
    n_rec=n_non=0
    y3_rec=y3_non=0
    y2_rec=y2_non=0

    for st in sorted(sampled[w]):
        sid=site.get((w,st))
        if sid is None:
            raise RuntimeError("missing SiteID in stable pair")
        wetmap=ci.get((w,st),{})
        mem=memory_by_site.get(sid,set())
        for sp in candidates:
            recurrent=sp in mem
            val=int(wetmap.get(sp,0))
            if recurrent:
                n_rec+=1
                y3_rec+=int(val==3)
                y2_rec+=int(val>=2)
            else:
                n_non+=1
                y3_non+=int(val==3)
                y2_non+=int(val>=2)

    if n_rec<5 or n_non<5:
        return None

    r3=y3_rec/n_rec
    n3=y3_non/n_non
    r2=y2_rec/n_rec
    n2=y2_non/n_non
    weight=(n_rec*n_non)/(n_rec+n_non)
    return {
        "n_recurrent_candidates":float(n_rec),
        "n_nonrecurrent_candidates":float(n_non),
        "ci3_recurrent_rate":float(r3),
        "ci3_nonrecurrent_rate":float(n3),
        "ci3_rate_difference":float(r3-n3),
        "ci2plus_recurrent_rate":float(r2),
        "ci2plus_nonrecurrent_rate":float(n2),
        "ci2plus_rate_difference":float(r2-n2),
        "opportunity_weight":float(weight),
    }

def fit(d,response):
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.wls(form,data=d,weights=d.opportunity_weight).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster}
    )
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {
        "beta_rain":b,"se":se,
        "ci95":[b-Q*se,b+Q*se],
        "p":float(m.pvalues["rain_contrast"]),
        "n_pairs":int(len(d)),
        "n_routes":int(d.route_cluster.nunique()),
        "weighted_mean_rate_difference":float(
            np.average(d[response],weights=d.opportunity_weight)
        )
    }

def package(d):
    primary=fit(d,"ci3_rate_difference")
    strong=fit(d,"ci2plus_rate_difference")
    return {
        "primary_ci3":primary,
        "diagnostic_ci2plus":strong,
        "classification":{
            "rain_selectively_favors_recurrent_ci3_cells":bool(
                primary["beta_rain"]>0 and primary["ci95"][0]>0
            )
        },
        "opportunity":{
            "median_recurrent_candidates":float(d.n_recurrent_candidates.median()),
            "median_nonrecurrent_candidates":float(d.n_nonrecurrent_candidates.median()),
            "mean_weight":float(d.opportunity_weight.mean())
        }
    }

def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci=ci_map(raw,eligible,sampled)

    pairs_all=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    stable_mask=np.asarray([stable_pair(p,sampled,site) for p in pairs_all.itertuples(index=False)],bool)
    pairs=pairs_all.loc[stable_mask].copy().reset_index(drop=True)

    meta,by_stratum,pools,site_species=build_strata(runs,sampled,site,ci)

    rows=[]
    for p in pairs.itertuples(index=False):
        s=pair_summary(p,sampled,site,ci,meta,by_stratum,pools,site_species)
        if s is None:
            continue
        r=p._asdict(); r.update(s); rows.append(r)
    d=pd.DataFrame(rows)

    gate=bool(len(d)>=1500 and d.route_cluster.nunique()>=300)
    if not gate:
        out={
          "analysis":"naamp_site_memory_opportunity_normalized_v0_1",
          "contract":"exploration/NAAMP_SITE_MEMORY_OPPORTUNITY_NORMALIZED_CONTRACT_V0_1.json",
          "status":"not_run_due_to_prefixed_gate",
          "coverage":{"pairs":int(len(d)),"routes":int(d.route_cluster.nunique()) if len(d) else 0}
        }
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    full=package(d)

    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
    dsame=d[
        d.apply(lambda r:(str(r.wet_RunID),str(r.dry_RunID)) in same_keys,axis=1)
    ].copy()
    same_gate=bool(len(dsame)>=1000 and dsame.route_cluster.nunique()>=250)
    same_result=package(dsame) if same_gate else {
        "status":"not_run_due_to_sensitivity_gate",
        "n_pairs":int(len(dsame)),
        "n_routes":int(dsame.route_cluster.nunique()) if len(dsame) else 0
    }

    out={
      "analysis":"naamp_site_memory_opportunity_normalized_v0_1",
      "contract":"exploration/NAAMP_SITE_MEMORY_OPPORTUNITY_NORMALIZED_CONTRACT_V0_1.json",
      "status":"completed_after_prefixed_gate",
      "coverage":{
        "all_pairs":int(len(pairs_all)),
        "physically_stable_pairs":int(len(pairs)),
        "opportunity_eligible_pairs":int(len(d)),
        "opportunity_eligible_routes":int(d.route_cluster.nunique()),
        "same_observer_opportunity_pairs":int(len(dsame)),
        "same_observer_opportunity_routes":int(dsame.route_cluster.nunique())
      },
      "full":full,
      "same_observer_sensitivity":{
        "gate_pass":same_gate,
        "result":same_result
      },
      "interpretation_boundary":{
        "continuous_occupancy_proven":False,
        "reproductive_success_measured":False,
        "cell_opportunity_normalized":True,
        "causal_rainfall_claim":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
