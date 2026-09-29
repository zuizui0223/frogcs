#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_STRONG_ACTIVATION_SPECIES_CONCENTRATION_RECEIPT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
    assert s.loader;s.loader.exec_module(m);return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip();st=(r.get("StopNumber") or "").strip();sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:continue
        try:x=int(float((r.get("CallingIndex") or "").strip()))
        except:continue
        if x in (1,2,3):vals[(rid,st,sp)].append(x)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():by[(rid,st)][sp]=max(v)
    return by

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip();st=(s.get("StopNumber") or "").strip();sid=(s.get("SiteID") or "").strip()
        if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0":vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad:raise RuntimeError(f"site conflict {list(bad)[:5]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def stable(p,sampled,site):
    w=str(p.wet_RunID);d=str(p.dry_RunID);ws=set(sampled[w]);ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(site.get((w,st)) and site.get((w,st))==site.get((d,st)) for st in ws)

def concentration(pairs,sampled,by):
    species=sorted({sp for m in by.values() for sp in m})
    idx={sp:i for i,sp in enumerate(species)}
    r,den=uniform.design_residual(pairs)
    num=np.zeros(len(species),float)
    for i,p in enumerate(pairs.itertuples(index=False)):
        w=str(p.wet_RunID);d=str(p.dry_RunID)
        for st in sorted(sampled[w]):
            wm=by.get((w,st),{});dm=by.get((d,st),{})
            for sp in set(wm)|set(dm):
                wi=int(wm.get(sp,0));di=int(dm.get(sp,0))
                if di==0 and wi>=2:num[idx[sp]]+=r[i]*wi
    betas=num/den;total=float(betas.sum());pos=np.maximum(betas,0);psum=float(pos.sum())
    sh=pos/psum if psum>0 else np.zeros_like(pos);order=np.argsort(-sh)
    top1=float(sh[order[0]]) if psum>0 else 0;top5=float(sh[order[:5]].sum()) if psum>0 else 0;hhi=float((sh**2).sum()) if psum>0 else 0
    loo=total-betas;allpos=bool(np.all(loo>0));mi=int(np.argmin(loo))
    diffuse=bool(top1<=.25 and top5<=.60 and hhi<=.10 and allpos)
    return {
      "n_pairs":int(len(pairs)),"n_routes":int(pairs.route_cluster.nunique()),
      "decomposition":{"total_strong_new_score_beta":total,"sum_species_betas":float(betas.sum())},
      "concentration":{"n_species":len(species),"n_species_positive_beta":int((betas>0).sum()),
        "n_species_positive_share_ge_1pct":int((sh>=.01).sum()),"top1_positive_share":top1,"top5_positive_share":top5,
        "hhi_positive_shares":hhi,"all_leave_one_species_out_betas_positive":allpos,
        "minimum_leave_one_species_out_beta":float(loo[mi]),"species_causing_minimum_loo":species[mi]},
      "classification":{"diffuse_across_taxa_under_prefixed_rule":diffuse},
      "top_positive_species":[{"species":species[int(i)],"beta":float(betas[int(i)]),"positive_share":float(sh[int(i)])} for i in order[:15] if sh[int(i)]>0]
    }

def main():
    raw=base.load();runs,sets=base.build_runs(raw);eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible);by=ci_map(raw,eligible,sampled)
    allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets);site=site_map(raw,eligible)
    robust=same.loc[np.asarray([stable(p,sampled,site) for p in same.itertuples(index=False)],bool)].copy().reset_index(drop=True)
    out={"analysis":"naamp_strong_activation_species_concentration_v0_1",
         "contract":"exploration/NAAMP_STRONG_ACTIVATION_SPECIES_CONCENTRATION_CONTRACT_V0_1.json",
         "full":concentration(allpairs,sampled,by),"robust_same_observer_physical_stop":concentration(robust,sampled,by),
         "interpretation_boundary":{"every_species_responds":False,"shared_physiological_mechanism_identified":False,"universal_claim":False}}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
