#!/usr/bin/env python3
"""Compare two toads' fish x plant responses across original four blocks.

This is post-hoc cross-experiment effect heterogeneity, NOT frog-frog
competition, predation, mediation, or a simultaneous biological interaction.
Fish and plant treatments were assigned in tank blocks; taxon trial dates
were different. Repeated dates cannot multiply n.
"""
import argparse,json,math
from pathlib import Path
PIN="86944f2d06b7e2739342a7b42ec4ff383df92d2cb8600a3d9c9c5de1f70758ae"
TOADS=("B. bufo","B. viridis")
PLANTS=("aq","aq_lit")
def t3p(t):
    # Exact Student-t(3) two-sided survival from its analytic integral.
    if not math.isfinite(t):return 0.
    u=abs(t)/math.sqrt(3.)
    return max(0.,min(1.,1.-2./math.pi*(u/(1.+u*u)+math.atan(u))))
def t3crit():
    lo,hi=0.,100.
    for _ in range(100):
        mid=(lo+hi)/2
        if t3p(mid)>.05:lo=mid
        else:hi=mid
    return (lo+hi)/2
def mean(v):return sum(v)/len(v)
def summarize_block_differences(values):
    n=len(values)
    if n!=4:raise ValueError("Exactly four original independently randomized blocks required")
    avg=mean(values)
    sd2=sum((v-avg)**2 for v in values)/(n-1)
    se=math.sqrt(sd2/n)
    t=(avg/se if se>0 else 0.)
    if se<=0:raise ValueError("Degenerate block contrast cannot use t reference here")
    critical=t3crit()
    return {"difference_pp":100*avg,"ci95_unadjusted_pp":[100*(avg-critical*se),100*(avg+critical*se)],
            "p_two_sided_block_t3":t3p(t),"test_stat_t3":t,
            "standard_error_pp":100*se,"n_independent_blocks":n,
            "positive_blocks":sum(v>0 for v in values),"negative_blocks":sum(v<0 for v in values)}
def adjust_bh(rows):
    order=sorted(range(len(rows)),key=lambda i:rows[i]["p_two_sided_block_t3"])
    q=1.
    for k in range(len(rows)-1,-1,-1):
        i=order[k]
        q=min(q,len(rows)*rows[i]["p_two_sided_block_t3"]/(k+1))
        rows[i]["BH_q_two_inspected_plants"]=q
        rows[i]["supported_after_BH"]=q<.05

def analyze(data):
    if data.get("status")!="full_block_contrasts_computed" or data.get("source",{}).get("SHA256")!=PIN:
        raise ValueError("Input is not the pinned verified four-block experiment result")
    if data["hypotheses"]["H2_fish_x_plant_changes_toad_choice"]["n_supported_after_BH"]!=0:
        raise ValueError("Source H2 results unexpectedly revised")
    rows=[]
    for plant in PLANTS:
        species_blocks={}
        for sp in TOADS:
            obj=data["species"][sp]
            if obj["coverage"]["n_blocks"]!=4:raise ValueError("Too few independent original blocks")
            species_blocks[sp]=obj["fish_x_plant_interaction"][plant]["blocks"]
        blocks=sorted(species_blocks[TOADS[0]])
        if blocks!=sorted(species_blocks[TOADS[1]]) or blocks!=["A","B","C","D"]:
            raise ValueError("Unmatched four original physical blocks")
        component={sp:{b:float(species_blocks[sp][b]) for b in blocks} for sp in TOADS}
        vals=[component[TOADS[0]][b]-component[TOADS[1]][b] for b in blocks]
        stats=summarize_block_differences(vals)
        rows.append({"plant":plant,"taxon_contrast":"Bufo bufo minus Bufotes viridis in fish×plant choice-share effect",
                     "block_difference_pp":{b:100*v for b,v in zip(blocks,vals)},
                     "species_component_interactions_pp":{sp:{b:100*v for b,v in values.items()} for sp,values in component.items()},
                     "leave_one_block_out_pp":{b:100*mean([v for j,v in enumerate(vals) if j!=i]) for i,b in enumerate(blocks)},
                     **stats})
    adjust_bh(rows)
    return {"status":"posthoc_two_toad_effect_heterogeneity_analyzed","date":"2026-10-23",
            "input":"exploration/FISH_MACROPHYTE_FACTORIAL_BLOCK_RESULT_V0_1.json","source_sha256":PIN,
            "not_predeclared":True,"independent_blocks":4,"repeated_dates_are_not_replicates":True,
            "taxa_assayed_at_different_times":True,
            "inference":"Fish×plant treatment-response heterogeneity BETWEEN separately observed taxa; not a change in their interaction with one another",
            "fdr_family":"two vegetation-level contrasts (aq, aq_lit), BH on block-t two-sided P",
            "unadjusted_ci_not_simultaneous":True,
            "causal_frog_frog_competition_identified":False,
            "mediated_fish_insect_frog_path_identified":False,
            "true_multi_biotaxon_higher_order_identified":False,"RC6_unchanged":True,
            "comparisons":rows}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    assert abs(t3p(0.)-1.)<1e-12
    assert abs(t3crit()-3.182446305284263)<1e-8
    d=json.loads(a.input.read_text())
    out=analyze(d)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CROSS_TAXON_H2_RESULT_BEGIN")
    print(json.dumps(out,sort_keys=True,allow_nan=False))
    print("CROSS_TAXON_H2_RESULT_END")
if __name__=="__main__":main()
