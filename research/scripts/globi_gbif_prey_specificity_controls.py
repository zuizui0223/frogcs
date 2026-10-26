#!/usr/bin/env python3
"""Matched prey-stage guild control for GloBI×GBIF 1° month synchrony.

Post-readback exploratory specificity check. It is NOT a study of actual
predation, and unrecorded GloBI stage edges are NOT verified non-interactions.
Fixed protocol research/GLOBAL_GLOBI_GBIF_PREY_SPECIFICITY_CONTROL_SPEC_V0_1.md
"""
import argparse
import collections
import csv
import json
import math
import random
import statistics
from pathlib import Path

from fixed_globi_gbif_month_shift_null import (
    read_cell_cubes,read_edges,compare_one,THRESHOLDS
)
SEED=20261025
FOCAL={"Anura","Odonata"}

def prepare_taxa(provenance):
    kinds=collections.defaultdict(set)
    known_pairs=set()
    with Path(provenance).open(newline="",encoding="utf8") as f:
        for r in csv.DictReader(f):
            a,b=r["predator"],r["prey"]
            known_pairs.add((a,b))
            if r["predator_guild"] in FOCAL:
                kinds[a].add(r["predator_guild"])
            if r["prey_guild"] in FOCAL:
                kinds[b].add(r["prey_guild"])
    mapping={}
    for n,values in kinds.items():
        if len(values)==1:
            mapping[n]=next(iter(values))
    return mapping,known_pairs


def footprint_volume(g):
    return sum(mask.bit_count() for mask in g.values())


def candidate_preys(pair,masks,kinds,links,maximum=5):
    pred=(pair["predator"],pair["predator_stage"])
    actual=(pair["prey"],pair["prey_stage"])
    wanted_guild=pair["prey_guild"]
    if wanted_guild not in FOCAL:
        return [],"prey_guild_not_in_scanned_gbif_partition"
    if kinds.get(pair["prey"])!=wanted_guild:
        return [],"original_prey_taxon_guild_not_consistent"
    source=masks.get(pred,{})
    target=masks.get(actual,{})
    pkeys=set(source)
    tgt_vol=footprint_volume(target)
    tgt_year=len(pkeys & set(target))
    if not pkeys or not target or not tgt_year:
        return [],"target_has_no_shared_spatial_year_footprint"
    candidates=[]
    for (species,stage),record in masks.items():
        if (stage!=pair["prey_stage"] or
            species in (pair["prey"],pair["predator"]) or
            kinds.get(species)!=wanted_guild or
            (pair["predator"],species) in links):
            continue
        vol=footprint_volume(record)
        shared=len(pkeys & set(record))
        if not shared:
            continue
        # Match without inspecting month intersection C0 or phase statistic.
        lr_vol=abs(math.log((vol+1)/(tgt_vol+1)))
        lr_spatial=abs(math.log((shared+1)/(tgt_year+1)))
        if lr_vol<=math.log(3) and lr_spatial<=math.log(2):
            candidates.append((
                lr_vol+lr_spatial,species,vol,shared))
    candidates.sort()
    if len(candidates)<2:
        return [],"fewer_than_two_geography_and_effort_matched_undocumented_species"
    return candidates[:maximum],""


def compare(records,edges,mapping,known):
    selected={}
    exclusion=collections.Counter()
    for e in edges:
        controls,reason=candidate_preys(e,records[1],mapping,known)
        if not controls:
            exclusion[reason]+=1
            continue
        id=(e["predator"],e["predator_stage"],
            e["prey"],e["prey_stage"])
        selected[id]=controls
    table=[]
    for e in edges:
        edge_key=(e["predator"],e["predator_stage"],
                  e["prey"],e["prey_stage"])
        if edge_key not in selected:
            continue
        choices=selected[edge_key]
        for threshold in THRESHOLDS:
            pred=records[threshold].get((e["predator"],e["predator_stage"]),{})
            prey=records[threshold].get((e["prey"],e["prey_stage"]),{})
            focal=compare_one(pred,prey)
            comparison=[]
            for _,name,prey_volume,shared_years in choices:
                other=records[threshold].get((name,e["prey_stage"]),{})
                current=compare_one(pred,other)
                comparison.append(dict(
                    species=name,
                    q=current["observed_over_shift_mean_plus1"],
                    raw_overlap=current["observed_exact_grid_year_month"],
                    prey_annual_footprint=shared_years,
                    prey_monthly_coverage=prey_volume))
            q_control=statistics.median(x["q"] for x in comparison)
            q_focal=focal["observed_over_shift_mean_plus1"]
            table.append({
                "predator":e["predator"],"predator_stage":e["predator_stage"],
                "prey":e["prey"],"prey_stage":e["prey_stage"],
                "predator_guild":e["predator_guild"],
                "prey_guild":e["prey_guild"],
                "threshold":threshold,
                "focal_reported_same_cell_year_month":
                    focal["observed_exact_grid_year_month"],
                "focal_month_rotation_mean":focal["month_shift_null_mean"],
                "focal_phase_ratio":q_focal,
                "median_control_phase_ratio":q_control,
                "difference_focal_minus_control_phase_ratio":q_focal-q_control,
                "focal_bigger_than_matched_controls":int(q_focal>q_control),
                "controls_n":len(comparison),
                "control_preys":"; ".join(c["species"] for c in comparison),
                "controls_json":json.dumps(comparison,ensure_ascii=False),
                "source_tiers":e["source_tiers"],
                "classification":"POSTHOC_GLOBI_DOCUMENTED_VS_UNDOCUMENTED_STAGE_EDGE"
            })
    return table,exclusion,selected


def summary(table,excluded,all_edges,input_qc,mapped_taxa):
    parts=[]
    for threshold in THRESHOLDS:
        x=[r for r in table if r["threshold"]==threshold]
        distinct_predators=set(r["predator"] for r in x)
        deltas=[r["difference_focal_minus_control_phase_ratio"] for r in x]
        report={
            "minimum_GBIF_records_per_taxon_stage_gridmonth":threshold,
            "matched_GloBI_directed_stage_pairs":len(x),
            "distinct_predator_species":len(distinct_predators),
            "focal_phase_ratio_greater_than_median_control":
                sum(r["focal_bigger_than_matched_controls"] for r in x),
            "focal_phase_ratio_smaller_or_equal_than_controls":
                sum(not r["focal_bigger_than_matched_controls"] for r in x),
            "mean_focal_minus_control_phase_ratio":
                statistics.mean(deltas) if deltas else None,
            "median_focal_minus_control_phase_ratio":
                statistics.median(deltas) if deltas else None,
            "source_tiers":dict(collections.Counter(
                "iNaturalist" if "INAT" in r["source_tiers"] else
                "Quick_Pond" if "QUICK_POND" in r["source_tiers"] else
                "other" for r in x)),
        }
        if len(distinct_predators)>=8:
            rng=random.Random(SEED+threshold)
            by=collections.defaultdict(list)
            for r in x:
                by[r["predator"]].append(r["difference_focal_minus_control_phase_ratio"])
            predators=sorted(by)
            stats=[]
            for _ in range(2000):
                draw=[rng.choice(predators) for _ in predators]
                values=[v for sp in draw for v in by[sp]]
                stats.append(statistics.mean(values))
            stats.sort()
            report["posthoc_predator_cluster_bootstrap_interval_95"]=[
                stats[49],stats[1949]]
            report["bootstrap_qualification"]="conditional on original matched GBIF source and prey control lists, not uncertainty in metaweb truth"
        else:
            report["posthoc_predator_cluster_bootstrap_interval_95"]=None
            report["bootstrap_qualification"]="not estimable with at least 8 independently labeled predator taxa"
        parts.append(report)
    return {
        "method":"Post-readback predator-fixed, guild+prey-stage and footprint matched nondocumented alternative prey; GBIF 1° stage-grid month phase ratio",
        "source_GloBI":"https://doi.org/10.5281/zenodo.22691479",
        "source_GBIF":"https://github.com/zuizui0223/frogcs/actions/runs/40190152042",
        "unconditional_full_GloBI_eligible_stage_patterns":len(all_edges),
        "GBIF_original_cube_QC":input_qc,
        "GBIF_taxa_with_focal_guild_verified":len(mapped_taxa),
        "matched_exclusion_counts":dict(excluded),
        "matched_pairs_each_threshold":parts,
        "boundaries":[
            "These prey controls are UNDOCUMENTED in the available 881 complete-stage GloBI set, not demonstrated ecological non-prey.",
            "Matching used prey-stage report volume and shared grid-year footprint before checking month synchrony.",
            "A 1° cell across one month is not a pond, live attack, species encounter or local food web.",
            "Repeated prey, predator, iNaturalist source and metaweb rows are not independent; phase ratios are observational and highly effort-biased.",
            "Control species and focal interactions were defined using the same curated GloBI/GBIF ecosystem and might reflect unequal reporting.",
            "Plant cover and rain effects are unmeasured here; do not infer causality or true stage-specific reversal.",
            "Small focal set, no global prevalence, no p-value, and comparisons after viewing phase-shift data are exploratory."
        ]
    }


def write_csv(path,rows):
    if not rows:
        raise RuntimeError("No control-matched sources; do not report comparison")
    with open(path,"w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)


def run(gbif,globi,provenance,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    masks,qc=read_cell_cubes(gbif)
    edges,_=read_edges(globi,provenance)
    groups,known=prepare_taxa(provenance)
    rows,exclude,_=compare(masks,edges,groups,known)
    summ=summary(rows,exclude,edges,qc,groups)
    # Explicit fail closed if the available documented stages cannot support
    # minimum matched controls for any truly distinct predator.
    if not rows:
        (out/"coverage_failure.json").write_text(
            json.dumps(summ,indent=2)+"\n",encoding="utf8")
        print("SPECIFICITY_NOT_ESTIMABLE")
        print(json.dumps(summ,indent=2))
        return
    write_csv(out/"matched_comparator_pairs.csv",rows)
    (out/"observed_results.json").write_text(
        json.dumps(summ,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BEGIN_GLOBI_STAGE_PARTNER_SPECIFICITY")
    print(json.dumps(summ,ensure_ascii=False,indent=2))
    print("END_GLOBI_STAGE_PARTNER_SPECIFICITY")


def selftest():
    base=collections.defaultdict(int,{(10,20,2022):1<<4})
    prey=collections.defaultdict(int,{(10,20,2022):1<<4})
    alt=collections.defaultdict(int,{(10,20,2022):1<<6})
    pair=dict(predator="A a",predator_stage="adult",prey="B b",
              prey_stage="adult",prey_guild="Odonata")
    masks={("A a","adult"):base,("B b","adult"):prey,
           ("C c","adult"):alt,("D d","adult"):prey}
    kinds={"B b":"Odonata","C c":"Odonata","D d":"Odonata"}
    choices,err=candidate_preys(pair,masks,kinds,links=set())
    assert len(choices)==2 and not err
    assert compare_one(base,prey)["observed_exact_grid_year_month"]==1
    assert compare_one(base,alt)["observed_exact_grid_year_month"]==0
    print("SPECIFICITY_PREDATOR_PREY_GUILD_STAGE_MATCH_QA_PASS")


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--gbif",default="research/data/gbif_artifact/focal_stage_1deg_month_year.csv")
    ap.add_argument("--globi",default="research/data/globi_artifact/nonself_stage_pair_grid_results.csv")
    ap.add_argument("--provenance",default="research/data/globi_artifact/full_nonself_staged_GloBI_provenance.csv")
    ap.add_argument("--out",default="research/results/guild_matched_specificity")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test:selftest()
    else:run(args.gbif,args.globi,args.provenance,args.out)
