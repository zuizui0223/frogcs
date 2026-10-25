#!/usr/bin/env python3
"""PEM1A/C/F × three-guild developmental timing × trophic-restraint simulation.

A SYNTHETIC theoretical exploration — not fitted NWI, NAAMP, GBIF, GloBI,
field predation, mutual invasibility, or empirical coexistence frequencies.

A frog egg pulse produces tadpoles, which can be attacked by salamander
larvae and odonate nymphs. Odonate risk suppresses salamander tadpole attack.
Postmetamorphic frogs can feed on vulnerable emerging odonates in a DISTINCT
empirical species pair; model integrates those motifs as generic mechanisms,
NOT a claim that all interactions occur in the Hokkaido species trio.

PEM1A/C/F are categorical wetland inundation proxy scenarios, not historical
measurements at NAAMP SiteIDs. A plant shelter coefficient is hypothetical.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

from simulate_seasonal_trophic_network import (
    SEED, draw_parameter_ensemble, integrate_years
)

T = np.linspace(0, 1, 240, endpoint=False)
DT = 1.0 / len(T)
PEM = {
    "PEM1A": dict(wet_start=.105, wet_end=.44,
                  salamander_background_recruit=.88,
                  odonate_background_recruit=.62),
    "PEM1C": dict(wet_start=.08, wet_end=.73,
                  salamander_background_recruit=.98,
                  odonate_background_recruit=.85),
    "PEM1F": dict(wet_start=.045, wet_end=.94,
                  salamander_background_recruit=1.,
                  odonate_background_recruit=1.),
}
BREEDING = {
    "narrow_cohort":.018,
    "broad_cohort":.095,
}
S_PHASES = (-.12, 0., .12)
D_PHASES = (-.18, 0., .18)
VEGETATION = (.15, .7)
RISK_REGIMES = {
    "weak_dragonfly_cue":(.008,.055),
    "strong_dragonfly_cue":(.13,.28),
}
NUM_DRAWS=128
YEARS=250
LAST_YEARS=30


def seasonal_kernel(phase,width):
    z=np.abs(T-phase)%1
    z=np.minimum(z,1-z)
    return np.exp(-.5*(z/width)**2)


def normalized_births(sigma):
    p=seasonal_kernel(.215,sigma)
    return p/p.sum()


def water_mask(pem):
    site=PEM[pem]
    return np.asarray(
        (T >= site["wet_start"]) & (T <= site["wet_end"]),
        dtype=float)


def water_to_metamorph(births,water,larval_duration=.18):
    """Assume larval development requires continuous water through ~.18 yr."""
    n=len(water)
    steps=max(1,round(larval_duration*n))
    meets=np.empty(n,dtype=bool)
    for i in range(n):
        meets[i]=bool(np.all(water[(i+np.arange(steps))%n]))
    return float(np.sum(births*meets))


def old_tadpole_cohort_size_mismatch(sigma,age_threshold=.05):
    """P(older cohort > late cohort by threshold): Gaussian paired pulses."""
    return .5*math.erfc(age_threshold/(2*sigma))


def scenario_edges(pem,bsigma,sphase,dphase):
    water=water_mask(pem)
    q=normalized_births(bsigma)
    vulnerability=np.zeros(len(T),dtype=float)
    for age in range(5,51):
        delay=age*DT
        ageweight=math.exp(-age/35)
        vulnerability+=np.roll(q,age)*ageweight
    vulnerability/=max(vulnerability.max(),1e-12)
    frog_post=seasonal_kernel(.67,.075+bsigma)
    salamander=seasonal_kernel(.34+sphase,.11)*water
    dragonfly=seasonal_kernel(.37+dphase,.11)*water
    dragonfly_emergence=seasonal_kernel(.69+dphase,.075)*water
    tadpole=vulnerability*water
    def x(a,b):
        return float(np.mean(a*b))
    pairs={
        "salamander_larva_eats_frog_tadpole":x(salamander,tadpole),
        "dragonfly_nymph_eats_frog_tadpole":x(dragonfly,tadpole),
        "dragonfly_nymph_risk_to_salamander_larva":x(dragonfly,salamander),
        "frog_adult_eats_emerging_dragonfly":x(
            frog_post,dragonfly_emergence),
    }
    egg_completion=water_to_metamorph(q,water)
    conspecific_mismatch=old_tadpole_cohort_size_mismatch(bsigma)
    # Narrower pulse generates more individual prey in a short period;
    # fixed-capacity attack causes per-capita saturation, here stylized.
    adult_capacity=1/(1+ .4*(.09/max(bsigma,.015)-1))
    adult_capacity=min(1.,max(.25,adult_capacity))
    return pairs,dict(
        frog_egg_to_metamorph_wet_window_fraction=egg_completion,
        frog_older_to_younger_size_mismatch_pair_probability=conspecific_mismatch,
        predator_satiation_attack_factor=adult_capacity,
        annual_flooded_fraction=float(water.mean()),
        annual_available_emergence_exposure=float(dragonfly_emergence.sum()/len(T)),
    )


def rescaled_parameters(original,site,stage,weak_or_strong):
    low,hi=RISK_REGIMES[weak_or_strong]
    n=original["r"].shape[0]
    params={k:np.array(v,copy=True) for k,v in original.items()}
    # Strictly synthetic: reproductive success declines if wetland dries
    # before frog transformation; D uses long-hydroperiod recruitment cue.
    # Compensatory generalist feeding is already in original annual toy.
    params["r"][:,0]*=max(.05,stage["frog_egg_to_metamorph_wet_window_fraction"])
    params["r"][:,1]*=PEM[site]["salamander_background_recruit"]
    params["r"][:,2]*=PEM[site]["odonate_background_recruit"]
    params["dragonfly_risk"]=np.linspace(low,hi,n)
    return params


def net_dragonfly_hazard_derivative(p,edge,vegetation=.35):
    """Derivative of tadpole killing hazard with increasing D at fixed S."""
    df=edge["dragonfly_nymph_eats_frog_tadpole"]
    sf=edge["salamander_larva_eats_frog_tadpole"]
    ds=edge["dragonfly_nymph_risk_to_salamander_larva"]
    s=30.
    d=12.
    shelter=math.exp(-1.3*vegetation)
    direct=p["a"][:,1]*df*shelter
    indirect=-p["a"][:,0]*s*sf*shelter*p["dragonfly_risk"]*ds/(1+p["dragonfly_risk"]*d*ds)**2
    return direct+indirect


def scenarios():
    params=draw_parameter_ensemble(NUM_DRAWS)
    series=[]
    for pem in PEM:
        for breed_name,sigma in BREEDING.items():
            for vegetation in VEGETATION:
                for sp in S_PHASES:
                    for dp in D_PHASES:
                        edge,stage=scenario_edges(pem,sigma,sp,dp)
                        for cue in RISK_REGIMES:
                            p=rescaled_parameters(params,pem,stage,cue)
                            # Source annual model avoids a literal per-stage demographic
                            # compartment model; it is only a persistence heuristic.
                            conditioned={**edge}
                            # Satiation and cohort-size mismatch affect F
                            # via stage-overlap rate and reproductive success.
                            # Capacity scales F exposure to two larval predators.
                            conditioned["salamander_larva_eats_frog_tadpole"]*=(
                                stage["predator_satiation_attack_factor"])
                            conditioned["dragonfly_nymph_eats_frog_tadpole"]*=(
                                stage["predator_satiation_attack_factor"])
                            p["r"][:,0]*=math.exp(-1.2*stage[
                                "frog_older_to_younger_size_mismatch_pair_probability"])
                            sim=integrate_years(
                                p,conditioned,vegetation=vegetation,
                                years=YEARS,last=LAST_YEARS)
                            deriv=net_dragonfly_hazard_derivative(
                                p,conditioned,vegetation)
                            series.append(dict(
                                site_class=pem,
                                breeding_cohort_timing=breed_name,
                                frog_breeding_std_fraction_year=sigma,
                                vegetation_refuge_proxy=vegetation,
                                salamander_larval_shift_fraction_year=sp,
                                dragonfly_larval_shift_fraction_year=dp,
                                odonate_suppression_of_salamander=cue,
                                **stage,**edge,
                                net_dragonfly_effect_lowers_frog_hazard_fraction_synthetic=float(np.mean(deriv<0)),
                                median_signed_derivative_of_frog_kill_hazard_synthetic=float(np.median(deriv)),
                                **{
                                    "synthetic_3guild_persistence_fraction_from_four_initial_conditions":sim["fraction_persistent_draws"],
                                    "synthetic_3guild_persistence_parameter_draws":sim["persistent_draws"],
                                }
                            ))
    return series


def summarize(rows):
    out=[]
    for pem in PEM:
        for label in BREEDING:
            ss=[x for x in rows
                if x["site_class"]==pem and x["breeding_cohort_timing"]==label]
            out.append(dict(
                PEM_class=pem,
                frog_breeding=label,
                number_synthetic_scenarios=len(ss),
                median_breeding_egg_to_metamorph_water_window_fraction=float(np.median(
                    [x["frog_egg_to_metamorph_wet_window_fraction"] for x in ss])),
                median_cohort_size_mismatch=float(np.median(
                    [x["frog_older_to_younger_size_mismatch_pair_probability"] for x in ss])),
                min_apparent_persistence_fraction=float(np.min([
                    x["synthetic_3guild_persistence_fraction_from_four_initial_conditions"]
                    for x in ss])),
                max_apparent_persistence_fraction=float(np.max([
                    x["synthetic_3guild_persistence_fraction_from_four_initial_conditions"]
                    for x in ss])),
                median_apparent_persistence_fraction=float(np.median([
                    x["synthetic_3guild_persistence_fraction_from_four_initial_conditions"]
                    for x in ss])),
                scenario_fraction_with_some_parameter_draws_showing_indirect_protective_dragonfly_hazard=float(np.mean(
                    [x["net_dragonfly_effect_lowers_frog_hazard_fraction_synthetic"]>0
                     for x in ss])),
            ))
    # Focus does synchrony always improve 3guild persistence?
    f={}
    for (pem,vegetation,sphase,dphase,cue) in {
        (x["site_class"],x["vegetation_refuge_proxy"],
         x["salamander_larval_shift_fraction_year"],
         x["dragonfly_larval_shift_fraction_year"],
         x["odonate_suppression_of_salamander"]) for x in rows
    }:
        key=(pem,vegetation,sphase,dphase,cue)
        items={x["breeding_cohort_timing"]:x for x in rows if (
            x["site_class"],x["vegetation_refuge_proxy"],
            x["salamander_larval_shift_fraction_year"],
            x["dragonfly_larval_shift_fraction_year"],
            x["odonate_suppression_of_salamander"])==key}
        a=items["narrow_cohort"]["synthetic_3guild_persistence_fraction_from_four_initial_conditions"]
        b=items["broad_cohort"]["synthetic_3guild_persistence_fraction_from_four_initial_conditions"]
        f[key]=a-b
    diffs=list(f.values())
    return out,dict(
        comparison_scenarios=len(diffs),
        narrow_more_three_guild_persistence=sum(x>1e-9 for x in diffs),
        diffuse_more_three_guild_persistence=sum(x< -1e-9 for x in diffs),
        tied_three_guild_persistence=sum(abs(x)<=1e-9 for x in diffs),
        range_narrow_minus_diffuse=list(map(float,[min(diffs),max(diffs)])),
        interpretation="Synthetic parameter ensemble may show different signs, not actual wetland frequencies.")


def write(out,all_rows,table,phase_comparison):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for file,rows in [
        ("pem_three_guild_all_synthetic_cases.csv",all_rows),
        ("pem_three_guild_synthetic_summary.csv",table)]:
        with (out/file).open("w",encoding="utf8",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
    result=dict(
        type="SYNTHETIC_ONLY_NOT_OBSERVED_PEM_OR_GLOBI_OUTCOME",
        model="Beverton-Holt 3annual lineages with fixed within-year stage-specific interaction kernels, weak/strong dragonfly cues, PEM hydrology windows, frog size mismatch and stylized predator satiation",
        seed=SEED,draws=NUM_DRAWS,years=YEARS,
        source_code_in_repo="research/scripts/simulate_pem_three_guild_stage_balance.py",
        parameter_origin="USER-HYPOTHESIS_MOTIVATED_TOY_VALUES_NO_FITTED_PARAMETERS",
        PEM_scenarios=PEM,per_class_breeding=table,
        cohort_synchrony_persistence_comparison=phase_comparison,
        sample_case_with_dragonfly_net_frog_hazard_reduction=next(
            (x for x in all_rows if x[
                "net_dragonfly_effect_lowers_frog_hazard_fraction_synthetic"]>.2),None),
        positive_reverse_edge_window_examples=sorted(
            (x for x in all_rows if x["frog_adult_eats_emerging_dragonfly"]>0),
            key=lambda x:-x["frog_adult_eats_emerging_dragonfly"])[:2],
        strict_limits=[
            "This is not measured NAAMP/NPS habitat classification, actual frog breeding, GloBI encounters, GBIF population statistics or real coexistence.",
            "PEM water windows and 128 parameter draws are illustrative and physically imposed; they do not come from actual NWI wetlands.",
            "Frog tadpoles and salamander/odonate larvae are seasonal activity kernels, not independent age-structured cohort census compartments.",
            "Beverton-Holt persistence from all-present and rare-start initial conditions is NOT mathematical mutual invasion growth of each focal species into independent two-species resident attractors.",
            "A formula-induced positive/negative dragonfly effect reflects the presence of direct D→F attacks and indirect D⊣S⊣F suppression; not a real population benefit.",
            "Frog cohort age-size mismatch cannibalism comes from Gaussian brood timing illustrative formula, not empirically measured genotype/stage distributions.",
            "Do not transport the Australian frog/dragonfly species-pair direction reversal into the Japanese Rana/Hynobius/Aeshna identity.",
            "PEM1A/C/F are NWI classifications, not verified locations of any current frogcs acoustic stop; fixed 1990s-2000s EarthEnv is not same as PEM polygons.",
            "No field-calibrated plant refuge, dragonfly emergence, salamander attack, social chorus benefits, aquatic eDNA, or variation in water temperature is modeled.",
        ]
    )
    (out/"synthetic_results.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_PEM_SYNTHETIC_TRIAD_RESULTS")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("END_PEM_SYNTHETIC_TRIAD_RESULTS")


def selftest():
    assert set(PEM)=={"PEM1A","PEM1C","PEM1F"}
    eggs_n=normalized_births(BREEDING["narrow_cohort"])
    eggs_w=normalized_births(BREEDING["broad_cohort"])
    assert abs(eggs_n.sum()-1)<1e-10 and abs(eggs_w.sum()-1)<1e-10
    assert old_tadpole_cohort_size_mismatch(BREEDING["narrow_cohort"]) < (
        old_tadpole_cohort_size_mismatch(BREEDING["broad_cohort"]))
    edge_short,meta_short=scenario_edges("PEM1A",.018,0.,0.)
    edge_long,meta_long=scenario_edges("PEM1F",.018,0.,0.)
    assert meta_short["annual_flooded_fraction"]<meta_long["annual_flooded_fraction"]
    assert meta_short["frog_egg_to_metamorph_wet_window_fraction"] <= (
        meta_long["frog_egg_to_metamorph_wet_window_fraction"])
    assert all(v>=0 for v in edge_short.values())
    params=draw_parameter_ensemble(8)
    p=rescaled_parameters(params,"PEM1C",meta_long,"strong_dragonfly_cue")
    assert (p["r"][:,0]>0).all()
    rate=net_dragonfly_hazard_derivative(p,edge_long)
    assert rate.size==8 and np.all(np.isfinite(rate))
    # In this toy model, a phase shift away from tadpole season MUST reduce
    # the dragonfly/tadpole larval stage overlap, all else fixed.
    far,_=scenario_edges("PEM1F",.018,0.,.18)
    assert edge_long["dragonfly_nymph_eats_frog_tadpole"] > far[
        "dragonfly_nymph_eats_frog_tadpole"]
    print("PEM_STAGE_TRIAD_SYNTHETIC_WETLAND_AND_COHORT_QA_PASS")


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",default="research/results/pem_three_guild_stage_balance")
    a.add_argument("--self-test",action="store_true")
    options=a.parse_args()
    if options.self_test:
        selftest()
    else:
        rows=scenarios()
        groups,phase=summarize(rows)
        write(options.out,rows,groups,phase)


if __name__=="__main__":
    main()
