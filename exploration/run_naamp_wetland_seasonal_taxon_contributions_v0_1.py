#!/usr/bin/env python3
"""Post-readback frog temporal taxon BONUS decomposition + relative-bonus audit.

The original route/year/site cohort and already-supported absolute PEM acoustic
temporal bonus remain frozen. This script does NOT rerun hypothesis selection
nor claim independently significant taxa; it decomposes deterministic expected
species-pool temporal complementarity by original NAAMP monitoring taxon label.

NWI 250m mapped PEM/other wetlands != live plant species field measurements.
Taxon "new later" labels != colonization, "early only" != extinction.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
ANALYSIS=ROOT/"exploration/run_naamp_wetland_seasonal_complementarity_v0_1.py"
PINNED=ROOT/"exploration/NAAMP_PEM_WETLAND_TWO_ROUND_TEMPORAL_COMPLEMENTARITY_AGGREGATE_2026_10_23.json"
SPEC="exploration/NAAMP_PEM_SEASONAL_TAXON_CONTRIBUTION_POSTREADBACK_SPEC_2026_10_23.md"
MODES=(("any",1),("strong",2))

def src():
    s=importlib.util.spec_from_file_location("naamp_exact_seasonal",ANALYSIS)
    if s is None or s.loader is None:
        raise RuntimeError("Original verified NAAMP seasonal diversity code not found")
    m=importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

def per_taxon(A,B,m,base):
    """Taxon-specific exact bonus, later-only and earlier-only expectations."""
    n=len(A)
    if n!=len(B) or not 2<=m<=n:
        raise ValueError("Invalid site group/matched m")
    taxa=set().union(*[set(a)|set(b) for a,b in zip(A,B)])
    contributions={}
    for tax in taxa:
        ke=sum(tax in v for v in A)
        kl=sum(tax in v for v in B)
        ku=sum(tax in A[k] or tax in B[k] for k in range(n))
        p0early=base.absence_probability(n,ke,m)
        p0late=base.absence_probability(n,kl,m)
        p0union=base.absence_probability(n,ku,m)
        bonus=.5*(p0early+p0late)-p0union
        later=p0early-p0union
        early=p0late-p0union
        if min(bonus,later,early)<-1e-12:
            raise RuntimeError("Negative exact within-habitat per-label temporal bonus")
        if not math.isclose(bonus,.5*(later+early),abs_tol=1e-12):
            raise RuntimeError("Per-taxon time complementarity identity failed")
        contributions[tax]={
          "bonus":bonus,"later_only":later,"earlier_only":early,
          "gamma_two":1-p0union,
          "gamma_one":1-.5*(p0early+p0late)}
    gross=base.exact_two_round_pool(A,B,m)
    for fld,ref in (("bonus","bonus_temporal_complementarity"),
                    ("later_only","first_heard_only_later_round"),
                    ("earlier_only","heard_only_earlier_round"),
                    ("gamma_two","gamma_union_two_rounds"),
                    ("gamma_one","gamma_single_round_mean")):
        if not math.isclose(sum(d[fld] for d in contributions.values()),
                            gross[ref],abs_tol=1e-10):
            raise RuntimeError("Independent taxon-sum decomposition disagrees with original exact rarefaction")
    return contributions

def synthetic():
    base=src()
    A=[{"a","b"},{"a"},{"c"},{},set()]
    B=[{"a"},{"d"},{"b","c"},{"d"},{"a"}]
    z=per_taxon(A,B,3,base)
    assert all(math.isfinite(v["bonus"]) and v["bonus"]>=0 for v in z.values())
    assert math.isclose(sum(v["bonus"] for v in z.values()),
                        base.exact_two_round_pool(A,B,3)["bonus_temporal_complementarity"],
                        abs_tol=1e-12)
    assert sum(v["later_only"] for v in z.values())>=0
    return {"status":"PASS","taxon_exact_temporal_bonus_conservation":True,
            "later_only_and_earlier_only_exact":True,
            "same_m_physical_site_no_replacement":True,
            "source_biological_data_not_used_in_math_QA":True}

def ratios(pairs):
    result={}
    for mode,_ in MODES:
        a=pairs[f"PEM_normalized_bonus_{mode}"]
        b=pairs[f"other_normalized_bonus_{mode}"]
        valid=np.isfinite(a.to_numpy(float))&np.isfinite(b.to_numpy(float))
        data=pairs.loc[valid,["state","route","route_year_id"]].copy()
        data["delta"]=a[valid].to_numpy(float)-b[valid].to_numpy(float)
        groups=data.groupby(["state","route","route_year_id"],sort=False).delta.mean().reset_index()
        routes=groups.groupby(["state","route"],sort=False).delta.mean().reset_index()
        state=routes.groupby("state").delta.mean()
        result[mode]={
          "n_paired_round_pairs_both_habitat_pools_nonempty":int(len(data)),
          "n_all_original_round_pairs":int(len(pairs)),
          "excluded_due_to_zero_pool_either_habitat":int(len(pairs)-len(data)),
          "fraction_valid":float(len(data)/len(pairs)),
          "n_route_year_groups_both_nonempty":int(len(groups)),
          "n_independent_physical_routes":int(len(routes)),
          "n_States":int(len(state)),
          "route_equal_mean_normalized_bonus_PEM_minus_other":float(routes.delta.mean()),
          "State_equal_mean_normalized_bonus_PEM_minus_other":float(state.mean()),
          "n_positive_State_means":int((state>0).sum()),
          "n_negative_State_means":int((state<0).sum()),
          "no_new_significance_tests_or_causal_effect_claims":True}
    return result

def compute():
    base=src()
    pinned=json.loads(PINNED.read_text())
    if (pinned["source_verified_GitHub_Action_run"]!=39905766189
        or pinned["eligible_site_temporal_hierarchy"]["source_round_pairs_all_combinations"]!=2475
        or pinned["eligible_site_temporal_hierarchy"]["source_same_site_same_year_route_groups"]!=1115
        or pinned["original_four_fixed_route_robust_tests"]["delta_bonus_any"]["supported_positive_observational_PEM_ecological_context"] is not True):
        raise RuntimeError("Original independently executed positive source numerical authority changed")
    good,ci,original,scope,cohort=base.original_cohort()
    pairdf,audit=base.make_pairs(good,ci,original)
    if (len(pairdf)!=2475 or pairdf.route_year_id.nunique()!=1115
        or pairdf.route.nunique()!=274 or pairdf.state.nunique()!=20):
        raise RuntimeError("Original route-year-roundpair source drift")
    lookup={(str(row.route_year_id),int(row["round"])):str(row.rid)
            for _,row in original.iterrows()}
    if len(lookup)!=len(original):
        raise RuntimeError("Original each route/year/round had duplicate run IDs")
    # one aggregate Counter per physical route-year, then one per route, then
    # a nationwide equal-route mean. Do not omit taxon-absent route-years.
    routeyear_counters={mode:defaultdict(Counter) for mode,_ in MODES}
    routeyear_delta={mode:defaultdict(float) for mode,_ in MODES}
    routeyear_pair_count=Counter()
    contributions_by_context={mode:defaultdict(Counter) for mode,_ in MODES}
    component_fields=("bonus","later_only","earlier_only","gamma_two","gamma_one")
    for rec in pairdf.itertuples(index=False):
        group=str(rec.route_year_id);round1=int(rec.earlier_round);round2=int(rec.later_round)
        before=good[lookup[(group,round1)]]
        after=good[lookup[(group,round2)]]
        if before["physical_sites"]!=after["physical_sites"] or before["pem"]!=after["pem"] or before["wet"]!=after["wet"]:
            raise RuntimeError("Original fixed route-year observation changed physical monitored sites")
        wet=np.asarray(before["wet"],bool)
        pem=np.asarray(before["pem"],bool)
        masks={"PEM":np.flatnonzero(wet&pem).tolist(),
               "other":np.flatnonzero(wet&~pem).tolist()}
        m=min(len(masks["PEM"]),len(masks["other"]))
        if m!=rec.m_matched_physical_sites or m<2 or m>5:
            raise RuntimeError("Source geographical PEM matched site count changed")
        key=(str(rec.state),str(rec.route),group)
        routeyear_pair_count[key]+=1
        for mode,threshold in MODES:
            delta=Counter()
            context={}
            for hab,indices in masks.items():
                A=[{str(t) for t,c in ci.get((before["rid"],before["stoplabels"][i]),{}).items() if int(c)>=threshold}
                   for i in indices]
                B=[{str(t) for t,c in ci.get((after["rid"],after["stoplabels"][i]),{}).items() if int(c)>=threshold}
                   for i in indices]
                context[hab]=per_taxon(A,B,m,base)
            for tax in set(context["PEM"])|set(context["other"]):
                for field in component_fields:
                    value=context["PEM"].get(tax,{}).get(field,0.)-context["other"].get(tax,{}).get(field,0.)
                    delta[(tax,field)]+=value
            aggregate_bonus=sum(v for (tax,field),v in delta.items() if field=="bonus")
            if not math.isclose(aggregate_bonus,getattr(rec,"delta_bonus_"+mode),abs_tol=1e-10):
                raise RuntimeError("Recomputed signed taxon bonus does not match original verified full-community result")
            for key2,v in delta.items():routeyear_counters[mode][key][key2]+=v
            routeyear_delta[mode][key]+=float(aggregate_bonus)
    if len(routeyear_pair_count)!=1115 or sum(routeyear_pair_count.values())!=2475:
        raise RuntimeError("Original source group counts not conserved")
    grouped_yrs=original.groupby("route").route_year_id.nunique().to_dict()
    grouped_routes=set(grouped_yrs)
    if len(grouped_routes)!=274:raise RuntimeError("Physical route unique source selection drift")
    result={}
    for mode,th in MODES:
        route_counter=defaultdict(Counter)
        for (state,route,group),counter in routeyear_counters[mode].items():
            n=routeyear_pair_count[(state,route,group)]
            if n<1:raise RuntimeError("Empty complete route-year group")
            for (tax,field),x in counter.items():
                route_counter[route][(tax,field)]+=x/n/grouped_yrs[route]
        national=Counter()
        for route in grouped_routes:
            for key,x in route_counter[route].items():
                national[key]+=x/len(grouped_routes)
        if len(route_counter)!=274:raise RuntimeError("Missing routes with taxonomic accounting")
        taxbonus={t:v for (t,field),v in national.items() if field=="bonus"}
        plus={t:v for t,v in taxbonus.items() if v>1e-11}
        minus={t:v for t,v in taxbonus.items() if v<-1e-11}
        pos=sorted(plus.items(),key=lambda z:-z[1])
        neg=sorted(minus.items(),key=lambda z:z[1])
        target=pinned["original_four_fixed_route_robust_tests"]["delta_bonus_"+mode]["route_equal_delta"]
        recovered=sum(taxbonus.values())
        if not math.isclose(recovered,target,rel_tol=0,abs_tol=1e-10):
            raise RuntimeError("Cross-route taxon decomposition does not exactly reproduce original main treatment effect")
        # Also exact source count identities for temporal directions and pooled gamma.
        summary={field:float(sum(v for (tax,col),v in national.items() if col==field))
                 for field in component_fields}
        if not math.isclose(summary["bonus"],.5*(summary["later_only"]+summary["earlier_only"]),abs_tol=1e-10):
            raise RuntimeError("Cross-route temporal gain/loss identity does not hold")
        if not math.isclose(summary["gamma_two"]-summary["gamma_one"],summary["bonus"],abs_tol=1e-10):
            raise RuntimeError("Cross-route cumulative pool size does not equal one-visit plus complementarity")
        genus=Counter()
        for name,value in taxbonus.items():
            genus[name.split(" ",1)[0]]+=value
        result[mode]={
            "source_original_monitoring_taxon_labels_with_nonzero_components":len(taxbonus),
            "source_taxa_positive_contributions":len(plus),
            "source_taxa_negative_contributions":len(minus),
            "sum_positive_taxon_contributions":float(sum(plus.values())),
            "sum_negative_taxon_contributions":float(sum(minus.values())),
            "all_taxon_contributions_sum_original_effect":float(recovered),
            "original_primary_effect_pinned":float(target),
            "temporal_direction_components_PEM_minus_other":summary,
            "largest_one_fraction_of_positive_component":float(pos[0][1]/sum(plus.values())) if pos else None,
            "largest_five_fraction_of_positive_component":float(sum(x for _,x in pos[:5])/sum(plus.values())) if pos else None,
            "net_temporal_bonus_without_biggest_taxon_descriptive":float(recovered-pos[0][1]) if pos else None,
            "top_positive_original_taxon_labels":[{"taxon":tax,"delta_bonus":float(value)}
                                             for tax,value in pos[:15]],
            "top_negative_original_taxon_labels":[{"taxon":tax,"delta_bonus":float(value)}
                                             for tax,value in neg[:15]],
            "genus_prefix_aggregate_descriptive":[{"taxon_prefix":k,"delta_bonus":float(v)}
                                                for k,v in genus.most_common()],
            "n_source_physical_routes_equal_weight":274,
            "no_individual_species_statistical_tests":True,
            "taxon_complexes_are_original_unmodified_acoustic_labels":True
        }
    return result,ratios(pairdf),audit

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,default=ROOT/"build/naamp_vegetation_seasonal_taxa")
    p.add_argument("--synthetic-only",action="store_true")
    args=p.parse_args()
    QA=synthetic()
    if args.synthetic_only:
        print(json.dumps(QA,sort_keys=True));return
    results,relative,cohort=compute()
    out={
       "analysis":"NAAMP_PEM_acoustic_taxon_temporal_bonus_source_additive_species_hierarchy",
       "status":"executed_observational_taxonomic_and_relative_complementarity_postreadback_audit",
       "date":"2026-10-23","source_original_complementarity_action_run":39905766189,
       "source_positive_absolute_bonus_previously_observed":True,
       "plan":SPEC,"source_mathematical_QA":QA,
       "source_original_274_route_round_pairs":cohort,
       "taxon_label_exact_contributions":results,
       "matched_normalized_bonus_descriptive_only":relative,
       "scientific_limits":{
         "all_taxon_explanatory_accounting_selected_after_positive_macro_result":True,
         "relative_ratio_question_exploratory_no_new_statistical_tests":True,
         "taxon_labels_not_independent_phylogenetic_lineages":True,
         "NWI_mapped_wetland_PEM_not_contemporaneous_botanical_plant_species":True,
         "acoustic_temporal_new_label_not_true_colonization":True,
         "acoustic_early_only_label_not_true_extinction":True,
         "no_direct_biotic_interspecific_interaction_measured":True,
         "not_a_prediction_or_forecast":True,
         "frozen_main_JAE_RC6_SI_original_unmodified":True}}
    args.outdir.mkdir(exist_ok=True,parents=True)
    (args.outdir/"result.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("NAAMP_SEASONAL_TAXON_BONUS_BEGIN",flush=True)
    print(json.dumps({"status":out["status"],"original_source":cohort,
       "QA":QA,"taxon_bonus":results,"relative":relative},sort_keys=True,allow_nan=False),flush=True)
    print("NAAMP_SEASONAL_TAXON_BONUS_END",flush=True)

if __name__=="__main__":
    main()
