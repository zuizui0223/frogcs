#!/usr/bin/env python3
"""Post-hoc macro frog taxon-pool enrichment specifically *within* mapped wetlands.

Uses fixed original NAAMP 6236 x 10 complete route-night survey population,
USFWS NWI mapped total-wetland and emergent/woody 250-m polygon indicators.
Exact without-replacement gamma; whole physical route is inferential unit.
Taxon-level gamma contributions are deterministic sum decomposition, not
tests for individual biological plant preferences or ecological colonization.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import Counter,defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/"exploration/run_naamp_rarefied_vegetation_gamma_v0_1.py"
POPULATIONS=("wetland_all","wetland_woody_overlap","wetland_no_woody")
MODES=(("any",1),("strong",2))
SOURCE="exploration/NAAMP_PEM_WITHIN_WETLAND_TAXON_HIERARCHY_SPEC_2026_10_23.md"
PERM=4999
SEED=2601240

def module(label,path):
    spec=importlib.util.spec_from_file_location(label,path)
    if spec is None or spec.loader is None:raise RuntimeError("Missing validated NAAMP source")
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def source():
    rare=module("frozen_gamma",REF)
    x=module("source_naamp",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    nwi,audit=x.read_nwi(ROOT/"build/vegetation_context/site_nwi_vegetation_context.csv",
                       ROOT/"build/vegetation_context/geometry_nwi_preflight.json")
    if not audit["preflight_eligible"] or audit["mode"]!="full" or len(audit["overlay"]["shards"])!=12:
        raise RuntimeError("Original NWI geographic gate changed")
    if len(nwi)!=5147 or audit["overlay"]["site_records"]!=5147:
        raise RuntimeError("NWI source original physical-site census changed")
    if audit["matched_route_source_only_audit"]["frog_outcomes_read"] is not False:
        raise RuntimeError("NWI geographic source selected on frog outcome")
    raw=x.hist.load_retry()
    runs,_=x.base.build_runs(raw)
    if len(runs)!=7848:raise RuntimeError("Original 7848 normalized USGS NAAMP route-runs changed")
    valid=set(runs.RunID.astype(str))
    sampled,_=x.spatial.stop_matrix(raw,valid)
    sites=x.hist.site_map(raw,valid)
    ci=x.hist.ci_map(raw,valid,sampled)
    env=x.get_temps_and_detection(raw,runs,sampled)
    output=[]
    contributions={mode:defaultdict(Counter) for mode,_ in MODES}
    route_count={mode:Counter() for mode,_ in MODES}
    auditcounts=Counter()
    route_state={}
    sample_sizes=Counter()
    for run in runs.itertuples(index=False):
        rid=str(run.RunID)
        route=str(run.route_cluster)
        state=str(run.State)
        routenumber=str(run.RouteNumber)
        year=int(run.SurveyYear)
        stops=sorted(sampled[rid],key=int)
        if len(stops)!=10:raise RuntimeError("Standard ten-stop frog survey changed")
        siteids=[sites.get((rid,st)) for st in stops]
        if any(sid is None or (state,routenumber,str(sid)) not in nwi.index
               for sid in siteids):
            auditcounts["unmapped_complete_ten_stops"]+=1;continue
        if len(set(siteids))!=10:
            auditcounts["duplicate_10_stop_SiteID"]+=1;continue
        if any(any(not np.isfinite(env.get((rid,st),{}).get(k,np.nan))
                   for k in ("stop_air_temp_c","stop_sound_index"))
               for st in stops):
            auditcounts["missing_sound_or_temperature"]+=1;continue
        mat=nwi.loc[[(state,routenumber,str(sid)) for sid in siteids],
            ["nwi_emergent_cover_250m","nwi_woody_cover_250m",
             "nwi_all_wetland_cover_250m"]].to_numpy(dtype=float)
        if not np.isfinite(mat).all() or (mat<-1e-8).any() or (mat>1+1e-8).any():
            raise RuntimeError("Static NWI fractional exposure out of range")
        auditcounts["ten_stop_NWI_environment_complete"]+=1
        if route in route_state and route_state[route]!=state:
            raise RuntimeError("Route identity inconsistent with State")
        route_state[route]=state
        pem=mat[:,0]>0
        woody=mat[:,1]>0
        wetland=mat[:,2]>0
        contexts={
            "wetland_all":wetland,
            "wetland_woody_overlap":wetland & woody,
            "wetland_no_woody":wetland & ~woody}
        community={mode:[
             {str(t) for t,c in ci.get((rid,st),{}).items() if int(c)>=threshold}
             for st in stops] for mode,threshold in MODES}
        for popname,mask in contexts.items():
            ip=np.flatnonzero(mask & pem).tolist()
            ineg=np.flatnonzero(mask & ~pem).tolist()
            m=min(len(ip),len(ineg))
            if m<2:
                auditcounts[popname+"_no_2plus_balanced_sites"]+=1
                continue
            sample_sizes[(popname,m)]+=1
            for mode,_ in MODES:
                plus=[community[mode][i] for i in ip]
                minus=[community[mode][i] for i in ineg]
                z=rare.stats_for_pools(plus,minus,m)
                output.append({
                    "state":state,"route":route,"run_id":rid,"year":year,
                    "habitat":popname,"mode":mode,"m":m,
                    "n_plus":len(ip),"n_minus":len(ineg),**z})
                auditcounts["analysed_condition_x_callmode"]+=1
                if popname=="wetland_all":
                    route_count[mode][route]+=1
                    cplus=Counter(t for st in plus for t in st)
                    cminus=Counter(t for st in minus for t in st)
                    p=rare.observed_taxon_prob(cplus,len(plus),m)
                    q=rare.observed_taxon_prob(cminus,len(minus),m)
                    for tax in set(p)|set(q):
                        contributions[mode][route][tax]+=p.get(tax,0.)-q.get(tax,0.)
                    computed=sum(p.get(t,0.)-q.get(t,0.) for t in set(p)|set(q))
                    if not math.isclose(computed,z["delta_gamma"],abs_tol=1e-10):
                        raise RuntimeError("Taxon contribution fails exact route-night gamma identity")
    if auditcounts["ten_stop_NWI_environment_complete"]!=6236:
        raise RuntimeError("Cannot reproduce original 6236 complete NAAMP × NWI nights")
    if len(route_state)!=499:raise RuntimeError("Source geography 499 routes changed")
    cover={
        "initial_USGS_standardized_runs":7848,
        "source_NWI_250m_physical_sites":len(nwi),
        "complete_route_nights":auditcounts["ten_stop_NWI_environment_complete"],
        "complete_site_nights":10*auditcounts["ten_stop_NWI_environment_complete"],
        "physical_routes":len(route_state),"states":len(set(route_state.values())),
        "source":39450277196,
        "eligibility_counts":dict(auditcounts),
        "balanced_n_site_groups":{
            pop:{str(m):int(sample_sizes.get((pop,m),0)) for m in (2,3,4,5)}
            for pop in POPULATIONS}}
    return rare,pd.DataFrame(output),contributions,route_count,cover

def adjust_family(rows):
    if len(rows)!=6:raise ValueError("All six prespecified post-readback tests required")
    ranked=sorted(range(len(rows)),key=lambda i:(
        rows[i]["p_two_sided_route_t"] if rows[i]["status"]=="estimated" else 1.))
    q=1.
    for rank in range(len(rows),0,-1):
        i=ranked[rank-1]
        p=rows[i]["p_two_sided_route_t"] if rows[i]["status"]=="estimated" else 1.
        q=min(q,6*p/rank)
        rows[i]["BH_q_six"]=q
        r=rows[i]
        ci=r.get("ci95_route",[0,0])
        r["observational_enrichment_supported"]=bool(
            r["status"]=="estimated" and q<.05 and ci[0]>0)

def taxon_contribution(mode,data,contributions,route_count):
    q={r:int(n) for r,n in route_count[mode].items() if n>0}
    if len(q)<30:raise ValueError("Too few wetland-conditioned PEM macro route units")
    z=Counter()
    for route,n in q.items():
        for species,impact in contributions[mode][route].items():
            z[species]+=impact/n/len(q)
    sub=data[(data.habitat=="wetland_all") & (data["mode"]==mode)]
    route_mean=sub.groupby("route").delta_gamma.mean()
    observed=float(route_mean.mean())
    if len(route_mean)!=len(q) or not math.isclose(sum(z.values()),observed,abs_tol=1e-10):
        raise RuntimeError("Route-balanced taxon contributions do not reconstruct habitat gamma surplus")
    pos={t:v for t,v in z.items() if v>1e-12}
    neg={t:v for t,v in z.items() if v<-1e-12}
    pos_sorted=sorted(pos.items(),key=lambda v:-v[1])
    neg_sorted=sorted(neg.items(),key=lambda v:v[1])
    positive_total=sum(pos.values())
    negative_total=sum(neg.values())
    genus=Counter()
    for sp,d in z.items():genus[sp.split(" ",1)[0]]+=d
    return {
        "mode":mode,
        "n_source_taxon_labels":len(z),
        "n_positive_contributing_taxa":len(pos),
        "n_negative_contributing_taxa":len(neg),
        "sum_positive_contributions":positive_total,
        "sum_negative_contributions":negative_total,
        "sum_taxon_contributions_matches_route_mean":sum(z.values()),
        "total_wetland_conditioned_gamma_effect":observed,
        "top_positive_taxa":[{"taxon":t,"delta_gamma":float(v)} for t,v in pos_sorted[:15]],
        "top_negative_taxa":[{"taxon":t,"delta_gamma":float(v)} for t,v in neg_sorted[:15]],
        "top_one_fraction_of_sum_positive":pos_sorted[0][1]/positive_total if pos_sorted else None,
        "top_five_fraction_of_sum_positive":sum(v for _,v in pos_sorted[:5])/positive_total if pos_sorted else None,
        "gamma_difference_without_top_contributor":observed-pos_sorted[0][1] if pos_sorted else None,
        "genus_signed_contributions":[{"taxon_prefix":g,"delta_gamma":float(v)} for g,v in genus.most_common()],
        "all_taxa_including_complexes":True,
        "contributions_are_not_taxon_level_statistical_tests":True}

def synth():
    rare=module("exact_validated_rarefaction",REF)
    P=[{"a","b"},{"a","c"}]
    N=[{"a"},{"d"}]
    z=rare.stats_for_pools(P,N,2)
    if not math.isclose(z["gamma_positive"],3.) or not math.isclose(z["gamma_negative"],2.):
        raise ValueError("Known gamma test synthetic failed")
    cp=Counter(t for x in P for t in x)
    cn=Counter(t for x in N for t in x)
    pp=rare.observed_taxon_prob(cp,2,2)
    pn=rare.observed_taxon_prob(cn,2,2)
    contributions={t:pp.get(t,0.)-pn.get(t,0.) for t in set(pp)|set(pn)}
    if not math.isclose(sum(contributions.values()),1.,abs_tol=1e-12):
        raise ValueError("Exact species-decomposition does not sum")
    return {"status":"PASS","equal_effort_habitat_pool_gamma_delta":1.,
            "taxonomic_additivity_identity":True,
            "restricted_groups_require_two_stops_per_habitat":True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",type=Path,
                    default=ROOT/"build/naamp_within_wetland_taxon_gamma")
    ap.add_argument("--synthetic-only",action="store_true")
    args=ap.parse_args()
    qa=synth()
    if args.synthetic_only:
        print(json.dumps(qa,sort_keys=True));return
    rare,df,contributions,route_count,cover=source()
    findings=[]
    idx=0
    for condition in POPULATIONS:
        for mode,_ in MODES:
            sub=df[(df.habitat==condition)&(df["mode"]==mode)]
            record=rare.route_summary(sub,SEED+idx,require_m_two=True)
            record["condition"]=condition;record["mode"]=mode
            findings.append(record)
            idx+=1
    adjust_family(findings)
    taxa={mode:taxon_contribution(mode,df,contributions,route_count) for mode,_ in MODES}
    out={
        "analysis":"NAAMP_macro_nested_wetland_emergent_category_community_gamma_taxon_hierarchy",
        "status":"original_empirical_within_wetland_compositional_hierarchy_computed",
        "date":"2026-10-23",
        "post_readback_plan":"exploration/NAAMP_PEM_WITHIN_WETLAND_TAXON_HIERARCHY_SPEC_2026_10_23.md",
        "exploratory_after_source_peм_positive_gamma":True,
        "source":cover,
        "synthetic_QA":qa,
        "wetland_only_and_woody_context_gamma_contrasts":findings,
        "taxon_specific_exact_gamma_sum_contributions":taxa,
        "scientific_limits":{
            "NWI_zero_not_true_absence_of_botanical_plants":True,
            "mapped_250m_habitat_not_time_matched":True,
            "matched_equal_site_rarefaction_not_independent_replication":True,
            "species_incidence_is_calling_not_stable_occupancy":True,
            "direct_biotic_causality_not_identified":True,
            "higher_order_interspecific_interaction_not_identified":True,
            "JAE_RC6_unmodified":True}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("NAAMP_WITHIN_WETLAND_GAMMA_BEGIN")
    print(json.dumps({"status":out["status"],"QA":qa,
           "source":cover,"comparisons":findings,
           "taxon_hierarchy":taxa},sort_keys=True,allow_nan=False))
    print("NAAMP_WITHIN_WETLAND_GAMMA_END")
if __name__=="__main__":
    main()
