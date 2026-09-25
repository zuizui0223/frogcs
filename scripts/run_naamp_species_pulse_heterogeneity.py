#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import io
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, chi2_contingency

ROOT=Path(__file__).resolve().parent
BASE_SCRIPT=ROOT/"run_naamp_ecological_pulse.py"
spec=importlib.util.spec_from_file_location("pulse_base",BASE_SCRIPT)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

SPECIES_SHA="ac97118a3a1ccd72a94136009e9696173dabd29b042ac63e474a74c5a9fcd1cb"

def load_species_metadata():
    item=base.get_json(base.ITEM_URL)
    b=base.get_bytes(base.find_file(item,"Species.csv"))
    import hashlib
    got=hashlib.sha256(b).hexdigest()
    if got!=SPECIES_SHA:
        raise RuntimeError(f"hash drift Species.csv: {got}")
    rows=list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
    fields=list(rows[0].keys()) if rows else []

    def choose(cands):
        lower={str(k).strip().lower():k for k in fields}
        for c in cands:
            if c.lower() in lower:
                return lower[c.lower()]
        return None

    code_key=choose(["Species","SpeciesCode","Species Code","Code"])
    sci_key=choose(["ScientificName","Scientific Name","Scientific_Name","SpeciesName","Species Name"])
    common_key=choose(["CommonName","Common Name","Common_Name","EnglishName","English Name"])

    mapping={}
    if code_key:
        for r in rows:
            code=(r.get(code_key) or "").strip()
            if not code:
                continue
            mapping[code]={
                "scientific_name":(r.get(sci_key) or "").strip() if sci_key else "",
                "common_name":(r.get(common_key) or "").strip() if common_key else ""
            }
    return mapping,fields,{"code_key":code_key,"scientific_key":sci_key,"common_key":common_key}

def bh_adjust(pairs):
    # pairs: list[(species,p)]
    n=len(pairs)
    order=sorted(range(n),key=lambda i:pairs[i][1])
    q=[None]*n
    running=1.0
    for rank_from_end,pos in enumerate(reversed(order),start=1):
        rank=n-rank_from_end+1
        val=min(1.0,pairs[pos][1]*n/rank)
        running=min(running,val)
        q[pos]=running
    return q

def main():
    raw=base.load()
    d,sets=base.build_runs(raw)
    pairs=base.pair_runs(d,sets)

    counts=defaultdict(lambda:{"wet_gains":0,"dry_losses":0,"routes":set()})
    all_gain=0
    all_loss=0

    for r in pairs.itertuples(index=False):
        W=sets[str(r.wet_RunID)]
        D=sets[str(r.dry_RunID)]
        route=str(r.route_cluster)
        for sp in W-D:
            counts[sp]["wet_gains"]+=1
            counts[sp]["routes"].add(route)
            all_gain+=1
        for sp in D-W:
            counts[sp]["dry_losses"]+=1
            counts[sp]["routes"].add(route)
            all_loss+=1

    mapping,fields,field_choice=load_species_metadata()
    eligible=[]
    for sp,x in counts.items():
        total=x["wet_gains"]+x["dry_losses"]
        nr=len(x["routes"])
        if total<40 or nr<10:
            continue
        bt=binomtest(x["wet_gains"],total,p=.5,alternative="two-sided")
        share=x["wet_gains"]/total
        log_odds=math.log((x["wet_gains"]+0.5)/(x["dry_losses"]+0.5))
        meta=mapping.get(sp,{})
        eligible.append({
            "species_code":sp,
            "scientific_name":meta.get("scientific_name",""),
            "common_name":meta.get("common_name",""),
            "wet_gains":int(x["wet_gains"]),
            "dry_losses":int(x["dry_losses"]),
            "discordant_pairs":int(total),
            "distinct_routes":int(nr),
            "wet_gain_share":float(share),
            "haldane_log_odds_wet_vs_dry":float(log_odds),
            "p_value":float(bt.pvalue)
        })

    q=bh_adjust([(x["species_code"],x["p_value"]) for x in eligible]) if eligible else []
    for x,qq in zip(eligible,q):
        x["fdr_bh"]=float(qq)
        x["direction"]="wet_recruited" if x["wet_gain_share"]>.5 else ("dry_retained" if x["wet_gain_share"]<.5 else "balanced")

    eligible.sort(key=lambda x:(x["fdr_bh"],-abs(x["wet_gain_share"]-.5),x["species_code"]))

    table=np.array([[x["wet_gains"],x["dry_losses"]] for x in eligible],dtype=float) if eligible else np.empty((0,2))
    if len(table)>=2:
        chi2,p_het,dof,expected=chi2_contingency(table,correction=False)
        heterogeneity={
            "chi2":float(chi2),"df":int(dof),"p_value":float(p_het),
            "n_species":int(len(eligible))
        }
    else:
        heterogeneity=None

    elig_gain=sum(x["wet_gains"] for x in eligible)
    elig_loss=sum(x["dry_losses"] for x in eligible)

    result={
        "analysis":"naamp_species_pulse_heterogeneity_v0_1",
        "contract":"NAAMP_SPECIES_PULSE_HETEROGENEITY_CONTRACT_V0_1.json",
        "pair_source":"NAAMP_ECOLOGICAL_PULSE_CONTRACT_V0_1.json",
        "species_metadata":{
            "source_sha256":SPECIES_SHA,
            "fields":fields,
            "selected_fields":field_choice
        },
        "global":{
            "all_species_wet_gains":int(all_gain),
            "all_species_dry_losses":int(all_loss),
            "all_species_gain_share":float(all_gain/(all_gain+all_loss)),
            "eligible_species":int(len(eligible)),
            "eligible_wet_gains":int(elig_gain),
            "eligible_dry_losses":int(elig_loss),
            "eligible_gain_share":float(elig_gain/(elig_gain+elig_loss)) if (elig_gain+elig_loss)>0 else None,
            "fdr_positive_species":int(sum(x["fdr_bh"]<=.05 and x["wet_gain_share"]>.5 for x in eligible)),
            "fdr_negative_species":int(sum(x["fdr_bh"]<=.05 and x["wet_gain_share"]<.5 for x in eligible))
        },
        "heterogeneity_test":heterogeneity,
        "species_results":eligible,
        "top_wet_recruited":sorted(eligible,key=lambda x:x["wet_gain_share"],reverse=True)[:10],
        "top_dry_retained":sorted(eligible,key=lambda x:x["wet_gain_share"])[:10],
        "interpretation_boundary":{
            "activity":"Calling presence across a standardized run, not abundance/occupancy.",
            "status":"Post-opening ecological extension frozen before species-specific readback.",
            "causal_claim_authorized":False
        }
    }

    Path("NAAMP_SPECIES_PULSE_HETEROGENEITY_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
