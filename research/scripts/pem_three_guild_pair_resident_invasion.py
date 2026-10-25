#!/usr/bin/env python3
"""PEM three-guild seasonal roles: a strict synthetic rare-invasion stress test.

Not fitted to NWI PEM, NPS/NAAMP calls, GBIF/GloBI interactions or eDNA.
Main distinction: *same egg-pulse width phase variation* vs *width effects*
without the existing toy's forcibly beneficial cannibalism/satiation bonuses.

Node lineage F (frog), S (salamander), D (odonate); within-year stage kernels
supply attack/opposite-direction motifs, not actual separate demographic
compartments. For each missing lineage test mean log growth when rare into its
other TWO resident lineages. That is much stronger than all-present toy
persistence, but no proof of ecological coexistence outside toy equations.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from simulate_seasonal_trophic_network import draw_parameter_ensemble
from simulate_pem_three_guild_stage_balance import (
    PEM, S_PHASES, D_PHASES, VEGETATION, RISK_REGIMES,
    scenario_edges, rescaled_parameters, net_dragonfly_hazard_derivative
)

SEED=20261025
N_DRAWS=64
YEARS=220
TAIL=40
EPS=1.e-8
MIN_RESIDENT=1.e-4
S_WIDTH=.05
WIDTHS=(.018,.095)
AGG_COSTS=(0.,.3,.8)
PHASE_SWEEPS=[(s,d) for s in S_PHASES for d in D_PHASES]


def annual_map(state,param,edge,vegetation):
    """Positivity-preserving three-guild annual Beverton–Holt map."""
    f,s,d=state[...,0],state[...,1],state[...,2]
    r=param["r"]
    K=param["K"]
    a=param["a"]
    benefit=param["benefit"]
    sf=edge["salamander_larva_eats_frog_tadpole"]
    df=edge["dragonfly_nymph_eats_frog_tadpole"]
    ds=edge["dragonfly_nymph_risk_to_salamander_larva"]
    fd=edge["frog_adult_eats_emerging_dragonfly"]
    shelter=math.exp(-1.3*vegetation)
    # All birth parameters are fixed per parameter draw across phase scenario.
    rf=r[:,0]*(1+benefit[:,0]*d/(50+d)*fd/.18)
    rs=r[:,1]*(1+benefit[:,1]*f/(50+f)*sf/.18)
    rd=r[:,2]*(1+benefit[:,2]*
                (f/(50+f)*df+s/(50+s)*ds)/.18)
    frog_loss=(a[:,0]*s*sf*shelter/
               (1+param["dragonfly_risk"]*d*ds)
               +a[:,1]*d*df*shelter)
    salamander_loss=a[:,2]*d*ds
    dragonfly_loss=a[:,3]*f*fd*(1+.7*vegetation)
    new=np.stack([
        f*rf/(1+f/K[:,0])*np.exp(-np.minimum(frog_loss,700)),
        s*rs/(1+s/K[:,1])*np.exp(-np.minimum(salamander_loss,700)),
        d*rd/(1+d/K[:,2])*np.exp(-np.minimum(dragonfly_loss,700))
    ],axis=-1)
    if np.any(~np.isfinite(new)) or np.any(new<0):
        raise RuntimeError("Nonfinite or negative annual population")
    return np.maximum(new,0)


def rare_invasion_criterion(param,edge,vegetation,
                            years=YEARS,last=TAIL):
    """Simulate exact two-resident systems then geometric rare-invader growth."""
    n=len(param["r"])
    worlds=np.full((3,n,3),45.0)
    for missing in range(3):
        worlds[missing,:,missing]=0.
    lowest=np.full((3,n,3),np.inf)
    logs=np.zeros((3,n))
    for year in range(years):
        if year>=years-last:
            for missing in range(3):
                trial=worlds[missing].copy()
                trial[:,missing]=EPS
                rare_next=annual_map(trial,param,edge,vegetation)[:,missing]
                logs[missing] += np.log(
                    np.maximum(rare_next/EPS,1.e-300))/last
        worlds=annual_map(worlds,param,edge,vegetation)
        if year>=years-last:
            lowest=np.minimum(lowest,worlds)
    for i in range(3):
        lowest[i,:,i]=np.inf
    possible=np.all(lowest>MIN_RESIDENT,axis=(0,2))
    invasion=np.all(logs>0,axis=0)
    return dict(
        resident_pair_viable_parameter_draws=int(possible.sum()),
        all_three_can_invade_pair_residents_draws=int((possible&invasion).sum()),
        conditional_mutual_invasion_fraction=float(
            np.mean(invasion[possible])) if np.any(possible) else None,
        unconditional_mutual_invasion_draw_fraction=float(
            np.mean(possible&invasion)),
        frog_rare_invasion_mean_log_growth=float(np.mean(logs[0])),
        salamander_rare_invasion_mean_log_growth=float(np.mean(logs[1])),
        odonate_rare_invasion_mean_log_growth=float(np.mean(logs[2])),
        mean_species_positive_rare_growth=int(np.sum(np.mean(logs,axis=1)>0)),
    )


def params_for_site(draws,pem,stages,regime,sigma,aggregation_cost=0.):
    p=rescaled_parameters(draws,pem,stages,regime)
    # Only optional *explicit, non-empirical* mass-breeding site crowding cost.
    # The main phase-only and 0-cost width cases have no hard-coded
    # conspecific-cannibalism benefit or predator saturation advantage.
    extra=max(0.,.08/sigma-1.)
    p["r"][:,0] *= math.exp(-aggregation_cost*extra)
    return p


def experiment():
    draws=draw_parameter_ensemble(N_DRAWS)
    result=[]
    for pem in PEM:
        for phase_s,phase_d in PHASE_SWEEPS:
            for cover in VEGETATION:
                for cue in RISK_REGIMES:
                    edges,stages=scenario_edges(
                        pem,S_WIDTH,phase_s,phase_d)
                    p=params_for_site(
                        draws,pem,stages,cue,S_WIDTH,0.)
                    independent=rare_invasion_criterion(p,edges,cover)
                    signed=net_dragonfly_hazard_derivative(
                        p,edges,cover)
                    result.append(dict(
                        scan="fixed_frog_cohort_width_phase_only",
                        pem_scenario=pem,
                        frog_cohort_width_fraction_year=S_WIDTH,
                        salamander_offset_fraction_year=phase_s,
                        odonate_offset_fraction_year=phase_d,
                        submerged_cover_proxy=cover,
                        dragonfly_to_salamander_cue_strength=cue,
                        hypothetical_aggregation_cost=0.,
                        **edges,**stages,
                        local_fraction_parameter_draws_D_direct_minus_indirect_lowers_tadpole_hazard=float(np.mean(signed<0)),
                        local_signed_net_D_to_frog_hazard_derivative_median=float(np.median(signed)),
                        **independent,
                    ))
    widths=[]
    for pem in PEM:
        for phase_s,phase_d in PHASE_SWEEPS:
            for cover in VEGETATION:
                for cue in RISK_REGIMES:
                    for sigma in WIDTHS:
                        for aggregation_cost in AGG_COSTS:
                            edges,stages=scenario_edges(pem,sigma,phase_s,phase_d)
                            p=params_for_site(
                                draws,pem,stages,cue,sigma,aggregation_cost)
                            independent=rare_invasion_criterion(
                                p,edges,cover,years=YEARS,last=TAIL)
                            widths.append(dict(
                                pem_scenario=pem,
                                frog_cohort_width_fraction_year=sigma,
                                salamander_offset_fraction_year=phase_s,
                                odonate_offset_fraction_year=phase_d,
                                submerged_cover_proxy=cover,
                                dragonfly_to_salamander_cue_strength=cue,
                                hypothetical_aggregation_cost=aggregation_cost,
                                **edges,**stages,**independent
                            ))
    return result,widths


def summarize(phase,width):
    out={}
    out["parameter_draws"]=N_DRAWS
    out["phase_scenarios"]=len(phase)
    out["width_scenarios"]=len(width)
    out["wetland_scenarios"]=PEM
    out["phase_only_fixed_frog_cohort_width"]=S_WIDTH
    out["frog_rare_invasion_against_pair_residents"]=dict(
        positive_scenario_count=sum(r["frog_rare_invasion_mean_log_growth"]>0
                                     for r in phase),
        negative_scenario_count=sum(r["frog_rare_invasion_mean_log_growth"]<=0
                                     for r in phase))
    out["direct_plus_indirect_dragonfly_hazard_sensitivity"]=dict(
        contexts_with_some_parameter_draws_D_net_reduces_F_hazard=sum(
            x["local_fraction_parameter_draws_D_direct_minus_indirect_lowers_tadpole_hazard"]>0
            for x in phase),
        contexts_with_any_parameter_draws_D_net_increases_F_hazard=sum(
            x["local_fraction_parameter_draws_D_direct_minus_indirect_lowers_tadpole_hazard"]<1
            for x in phase),
        median_parameter_fraction_net_protection=float(np.median(
            [x["local_fraction_parameter_draws_D_direct_minus_indirect_lowers_tadpole_hazard"]
             for x in phase])))
    out["phase_by_PEM"]= []
    for pem in PEM:
        zz=[r for r in phase if r["pem_scenario"]==pem]
        out["phase_by_PEM"].append(dict(
            scenario=pem,
            sampled_synthetic_phase_contexts=len(zz),
            pair_resident_viable_in_any_draw_scenarios=sum(
                x["resident_pair_viable_parameter_draws"]>0 for x in zz),
            scenarios_with_some_all_three_invasions=sum(
                x["all_three_can_invade_pair_residents_draws"]>0 for x in zz),
            min_to_max_all_three_invader_fraction=[
                float(min(x["unconditional_mutual_invasion_draw_fraction"] for x in zz)),
                float(max(x["unconditional_mutual_invasion_draw_fraction"] for x in zz))],
            med_all_three_invader_fraction=float(np.median(
                [x["unconditional_mutual_invasion_draw_fraction"] for x in zz])),
        ))
    compare=[]
    for cost in AGG_COSTS:
        diffs=[]
        for pem in PEM:
            for ps,pd in PHASE_SWEEPS:
                for veg in VEGETATION:
                    for cue in RISK_REGIMES:
                        cases={r["frog_cohort_width_fraction_year"]:r
                               for r in width if (
                                   r["pem_scenario"]==pem
                                   and r["salamander_offset_fraction_year"]==ps
                                   and r["odonate_offset_fraction_year"]==pd
                                   and r["submerged_cover_proxy"]==veg
                                   and r["dragonfly_to_salamander_cue_strength"]==cue
                                   and r["hypothetical_aggregation_cost"]==cost)}
                        a=cases[WIDTHS[0]]["unconditional_mutual_invasion_draw_fraction"]
                        b=cases[WIDTHS[1]]["unconditional_mutual_invasion_draw_fraction"]
                        diffs.append(a-b)
        compare.append(dict(
            hypothetical_narrow_cohort_cost=cost,
            matched_phase_hydro_cover_cue_contexts=len(diffs),
            narrow_supports_more_all_three_invasion=sum(v>1e-9 for v in diffs),
            diffuse_supports_more_all_three_invasion=sum(v<-1e-9 for v in diffs),
            equal_invasion=sum(abs(v)<=1e-9 for v in diffs),
            median_narrow_minus_diffuse_strict_invasion=float(np.median(diffs)),
            range_narrow_minus_diffuse=[
                float(min(diffs)),float(max(diffs))],
        ))
    # Phase-only comparisons hold PEΜ, plant, dragonfly cue, parameters,
    # frog cohort width and all direct/indirect attack coefficients fixed.
    shifts=[]
    for pem in PEM:
        for cover in VEGETATION:
            for cue in RISK_REGIMES:
                subset={(z["salamander_offset_fraction_year"],
                         z["odonate_offset_fraction_year"]):z
                        for z in phase if (
                            z["pem_scenario"]==pem and
                            z["submerged_cover_proxy"]==cover and
                            z["dragonfly_to_salamander_cue_strength"]==cue)}
                base=subset[(0.,0.)]["unconditional_mutual_invasion_draw_fraction"]
                for ps,pd in PHASE_SWEEPS:
                    if ps==0 and pd==0:
                        continue
                    other=subset[(ps,pd)]["unconditional_mutual_invasion_draw_fraction"]
                    shifts.append(dict(
                        PEM=pem,submerged_cover=cover,dragonfly_cue=cue,
                        salamander_phase=ps,odonate_phase=pd,
                        shifted_minus_synchronous_fraction=other-base))
    out["phase_only_relative_to_zero_offset"]=dict(
        paired_scenario_comparisons=len(shifts),
        shifted_better=sum(z["shifted_minus_synchronous_fraction"]>1e-9
                           for z in shifts),
        synchrony_better=sum(z["shifted_minus_synchronous_fraction"]<-1e-9
                             for z in shifts),
        exact_equal=sum(abs(z["shifted_minus_synchronous_fraction"])<=1e-9
                        for z in shifts),
        median_shifted_minus_synchronized=float(np.median(
            [z["shifted_minus_synchronous_fraction"] for z in shifts])),
        min_to_max=[
            float(min(z["shifted_minus_synchronous_fraction"] for z in shifts)),
            float(max(z["shifted_minus_synchronous_fraction"] for z in shifts)),
        ],
        by_PEM=[
            dict(pem=pem,
                 phase_shift_better=sum(z["shifted_minus_synchronous_fraction"]>1e-9
                    for z in shifts if z["PEM"]==pem),
                 simultaneous_better=sum(z["shifted_minus_synchronous_fraction"]<-1e-9
                    for z in shifts if z["PEM"]==pem))
            for pem in PEM],
        interpretation="Actual toy outcome records the sign in shifted_better/synchrony_better; in the tested parameters, every nonzero predator-stage phase shift raised the strict pair-resident invasion screen relative to zero phase. This is imposed toy behavior, not a universal ecological law or NWI field result."
    )
    out["unbiased_width_vs_explicit_narrow_cost_stress"]=compare
    out["single_case_phase_sign_examples"]={
        "positive_invasion":next((
            {k:z[k] for k in (
                "pem_scenario","salamander_offset_fraction_year",
                "odonate_offset_fraction_year","submerged_cover_proxy",
                "dragonfly_to_salamander_cue_strength",
                "unconditional_mutual_invasion_draw_fraction")}
            for z in phase if z["unconditional_mutual_invasion_draw_fraction"]>0),None),
        "frog_hazard_reducing_dragonfly":next((
            {k:z[k] for k in (
                "pem_scenario","salamander_offset_fraction_year",
                "odonate_offset_fraction_year",
                "local_fraction_parameter_draws_D_direct_minus_indirect_lowers_tadpole_hazard")}
            for z in phase if z[
                "local_fraction_parameter_draws_D_direct_minus_indirect_lowers_tadpole_hazard"]>.4),None),
    }
    return out


def save(out,phase,width):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for name,items in [
        ("phase_only_mutual_invasion_synthetic.csv",phase),
        ("narrow_vs_broad_aggregation_cost_synthetic.csv",width),
    ]:
        with (out/name).open("w",newline="",encoding="utf8") as f:
            writer=csv.DictWriter(f,fieldnames=list(items[0]))
            writer.writeheader()
            writer.writerows(items)
    z={
        "date":"2026-10-25",
        "classification":"SYNTHETIC_INVARIANT_TEST_NOT_EMPIRICAL_PEM_OR_FROGCS_EFFECT",
        "method":"Seasonal named feeding motifs aggregated to annual Beverton-Holt 3lineage toy, missing-species resident pair then rare invasion log growth, no fit",
        "original_model":"research/scripts/simulate_seasonal_trophic_network.py",
        "original_PEM_scenarios":"research/scripts/simulate_pem_three_guild_stage_balance.py",
        "fixed_test_protocol":"research/PEM_TRIAD_MUTUAL_INVASIBILITY_COUNTERFACTUAL_SPEC_2026-10-25.md",
        "primary_tests":summarize(phase,width),
        "limitations":[
            "All hydrology windows, attack strengths, predator phase offsets, plant cover and 64 ensemble draws were invented to challenge hypotheses, not measured at NWI PEM1A/C/F ponds.",
            "Annual state variables F S D are not literal sampled eggs/larvae/adults; stage-specific interactions enter through seasonal overlap kernels.",
            "Two-species resident invasion-when-rare calculations are stronger than starting populations all together, but not a mathematical proof of global permanence with cycles/alternative attractors.",
            "Narrow aggregation-cost parameter is invented and explicitly stress-tested; neither a frog chorus fitness cost nor a measured predator saturation coefficient.",
            "Japanese salamander-dragonfly-frog indirect motif and Australian reverse adult-frog→emerging dragonfly motif are combined as generic theoretical interactions, not asserted for one local observed species assemblage.",
            "GBIF GloBI and NAAMP do not measure attack rates, PEM classification at real audio sites, species-specific recruitment nor emergence density.",
            "Never interpret fractions of arbitrarily drawn parameter sets or scenarios as the fraction of natural wetlands where coexistence occurs.",
        ],
    }
    (out/"synthetic_results.json").write_text(json.dumps(
        z,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_PEM_TRUE_PAIR_RESIDENT_RARE_INVASION_SYNTHETIC")
    print(json.dumps(z,indent=2,ensure_ascii=False))
    print("END_PEM_TRUE_PAIR_RESIDENT_RARE_INVASION_SYNTHETIC")


def selftest():
    draws=draw_parameter_ensemble(8)
    edge,stages=scenario_edges("PEM1C",.05,0,0)
    p=params_for_site(draws,"PEM1C",stages,"weak_dragonfly_cue",.05,0.)
    a=annual_map(np.full((8,3),20.),p,edge,.35)
    assert a.shape==(8,3) and np.all(np.isfinite(a)) and np.all(a>0)
    criterion=rare_invasion_criterion(p,edge,.35,years=55,last=12)
    assert 0<=criterion["all_three_can_invade_pair_residents_draws"]<=8
    assert 0<=criterion["resident_pair_viable_parameter_draws"]<=8
    assert criterion["unconditional_mutual_invasion_draw_fraction"]<=1
    assert set(PEM)=={"PEM1A","PEM1C","PEM1F"}
    p2=params_for_site(draws,"PEM1C",stages,"weak_dragonfly_cue",
                       WIDTHS[0],aggregation_cost=.8)
    p3=params_for_site(draws,"PEM1C",stages,"weak_dragonfly_cue",
                       WIDTHS[0],aggregation_cost=0.)
    assert np.all(p2["r"][:,0]<p3["r"][:,0])
    print("PEM_PAIR_RESIDENT_RARE_INVASION_MODEL_SYNTHETIC_QA_PASS")


if __name__=="__main__":
    arg=argparse.ArgumentParser()
    arg.add_argument("--out",default="research/results/pem_mutual_invasion")
    arg.add_argument("--self-test",action="store_true")
    opts=arg.parse_args()
    if opts.self_test:
        selftest()
    else:
        phase,width=experiment()
        save(opts.out,phase,width)
