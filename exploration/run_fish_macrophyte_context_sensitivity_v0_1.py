#!/usr/bin/env python3
"""Reproduce exploratory fish-stratum choice-share tests from pinned aggregate JSON.

Uses no raw workbook and never treats repeated dates as independent units.
Fish-present contrasts are post-hoc; they do not prove fish×plant interaction.
"""
import argparse
import itertools
import json
from pathlib import Path

PIN = "86944f2d06b7e2739342a7b42ec4ff383df92d2cb8600a3d9c9c5de1f70758ae"
SPECIES = ("B. bufo", "B. viridis")
PLANTS = ("aq", "aq_lit")
PERMS = tuple(itertools.permutations(range(3)))

def test(vec, k):
    observed = sum(x[k] - x[0] for x in vec) / len(vec)
    extreme = 0
    count = 0
    for combo in itertools.product(PERMS, repeat=len(vec)):
        permuted = sum(x[p[k]] - x[p[0]] for x,p in zip(vec,combo)) / len(vec)
        count += 1
        extreme += (abs(permuted) >= abs(observed) - 1e-12)
    return dict(effect_share_pp=100*observed,p_exact_two_sided=extreme/count,
                extreme_assignments=extreme,permutations=count,n_independent_blocks=len(vec))

def adjust(group):
    ranks = sorted(range(len(group)),key=lambda i:group[i]["p_exact_two_sided"])
    best = 1.
    for k in range(len(ranks)-1,-1,-1):
        j = ranks[k]
        best=min(best,len(group)*group[j]["p_exact_two_sided"]/(k+1))
        group[j]["bh_q"]=best

def analyze(data):
    if data.get("status") != "full_block_contrasts_computed" or data.get("source",{}).get("SHA256") != PIN:
        raise ValueError("Pinned original source / analysis not verified")
    if data.get("third_species_causal_mediation_inferred") is not False:
        raise ValueError("Unsafe mediation claim in source receipt")
    output=dict(status="executed_from_source_verified_block_contrasts",date="2026-10-22",
        input="exploration/FISH_MACROPHYTE_FACTORIAL_BLOCK_RESULT_V0_1.json",
        source_sha256=PIN,independent_blocks=4,
        permutation_rule="3! label relabelings per fish stratum per block; fixed through dates",
        estimand="male observed-use choice share among 6 treatments, not occupancy, survival, or reproduction",
        fish_present_contrasts_posthoc=True,species=[],sensitivity={},
        causal_mediation_identified=False,higher_order_species_interaction_identified=False,
        original_H2_factorial_BH_n_supported=data["hypotheses"]["H2_fish_x_plant_changes_toad_choice"]["n_supported_after_BH"],
        RC6_unchanged=True)
    for fish in ("no_fish","fish"):
        family=[]
        for sp in SPECIES:
            obj=data["species"][sp]
            blocks=sorted(obj["H1_fishless_plant_contrasts"]["aq"]["block_plant_effects"])
            if len(blocks)!=4: raise ValueError("Must have 4 independent physical blocks")
            vec=[[0.]+[
                float(obj["H1_fishless_plant_contrasts"][p]["block_plant_effects"][b])+
                (float(obj["fish_x_plant_interaction"][p]["blocks"][b]) if fish=="fish" else 0.)
                for p in PLANTS] for b in blocks]
            for i,p in enumerate(PLANTS,start=1):
                est=test(vec,i)
                if fish=="no_fish":
                    original=obj["H1_fishless_plant_contrasts"][p]["exact_randomization"]
                    if abs(est["p_exact_two_sided"]-original["p_exact_two_sided"])>1e-12 or abs(est["effect_share_pp"]/100-original["effect"])>1e-12:
                        raise ValueError("Cannot reproduce frozen original H1")
                lobo=[dict(omitted_block=b,**test([v for j,v in enumerate(vec) if j!=idx],i))
                      for idx,b in enumerate(blocks)]
                family.append(dict(taxon=sp,fish_status=fish,plant_level=p,**est,
                      block_effects_pp={b:vec[j][i]*100 for j,b in enumerate(blocks)},
                      positive_blocks=sum(v[i]>1e-12 for v in vec),
                      leave_one_block_out=lobo))
        adjust(family)
        output["species"].extend(family)
    return output

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    assert test([[1/3]*3]*3,1)["p_exact_two_sided"]==1.
    out=analyze(json.loads(args.input.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"status":out["status"],"posthoc_tests":sum(x["fish_status"]=="fish" for x in out["species"])}))

if __name__=="__main__": main()
