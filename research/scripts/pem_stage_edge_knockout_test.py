#!/usr/bin/env python3
"""PEM stage triad mechanistic knockouts: synthetic, never observed predation.

Pre-result contract research/PEM_TRIAD_STAGE_NETWORK_EDGE_ABLATION_SPEC_2026-10-25.md
"""
import argparse,csv,json,statistics
from pathlib import Path
import numpy as np
from simulate_seasonal_trophic_network import draw_parameter_ensemble
from simulate_pem_three_guild_stage_balance import (
    PEM, S_PHASES, D_PHASES, VEGETATION, RISK_REGIMES, scenario_edges
)
from pem_three_guild_pair_resident_invasion import (
    annual_map, rare_invasion_criterion, params_for_site
)

DRAWS=32
SWITCHES={
    "full":{},
    "no_risk_cue":{"use_risk_cue":False},
    "no_reverse_frog_dragonfly":{"use_reverse_frog_dragonfly":False},
    "no_direct_dragonfly_frog":{"use_direct_dragonfly_frog":False},
}


def run():
    params=draw_parameter_ensemble(DRAWS)
    results=[]
    for pem in PEM:
        for sp in S_PHASES:
            for dp in D_PHASES:
                for cover in VEGETATION:
                    for risk in RISK_REGIMES:
                        edge,stage=scenario_edges(pem,.05,sp,dp)
                        p=params_for_site(params,pem,stage,risk,.05,0.)
                        for mechanism,kw in SWITCHES.items():
                            z=rare_invasion_criterion(
                                p,edge,cover,switches=kw,years=220,last=40)
                            results.append(dict(
                                PEM_scenario=pem,
                                salamander_phase=sp,
                                dragonfly_phase=dp,
                                submerged_refuge=cover,
                                odonate_suppression_of_salamander=risk,
                                mechanism=mechanism,
                                sample_draws=DRAWS,
                                fraction_all_three_invasion=z["unconditional_mutual_invasion_draw_fraction"],
                                resident_viable_draws=z["resident_pair_viable_parameter_draws"],
                                all_three_invasion_draws=z["all_three_can_invade_pair_residents_draws"],
                                mean_rare_frog_log_growth=z["frog_rare_invasion_mean_log_growth"],
                                mean_rare_salamander_log_growth=z["salamander_rare_invasion_mean_log_growth"],
                                mean_rare_dragonfly_log_growth=z["odonate_rare_invasion_mean_log_growth"],
                                science_level="SYNTHETIC_HYPOTHESIS_ONLY_NOT_OBSERVED_NETWORK"
                            ))
    return results


def summarize(rows):
    indexed={}
    for r in rows:
        base=(r["PEM_scenario"],r["salamander_phase"],
              r["dragonfly_phase"],r["submerged_refuge"],
              r["odonate_suppression_of_salamander"])
        indexed[base+(r["mechanism"],)]=r
    cases=sorted(set(r[:5] for r in indexed))
    core=[]
    for alternative in [x for x in SWITCHES if x!="full"]:
        differences=[]
        rare_frog_differences=[]
        for k in cases:
            base=indexed[k+("full",)]
            other=indexed[k+(alternative,)]
            differences.append(
                base["fraction_all_three_invasion"] -
                other["fraction_all_three_invasion"])
            rare_frog_differences.append(
                base["mean_rare_frog_log_growth"]-
                other["mean_rare_frog_log_growth"])
        core.append(dict(
            knockout=alternative,
            matched_synthetic_settings=len(differences),
            removing_this_edge_hurts_all_three_invasion=sum(d>1e-9 for d in differences),
            removing_this_edge_helps_all_three_invasion=sum(d<-1e-9 for d in differences),
            removing_this_edge_changes_nothing=sum(abs(d)<=1e-9 for d in differences),
            full_minus_knockout_median_invasion=statistics.median(differences),
            full_minus_knockout_range=[min(differences),max(differences)],
            full_minus_knockout_median_rare_frog_log_growth=statistics.median(rare_frog_differences)))
    phase=[]
    for mechanism in SWITCHES:
        delta=[]
        for pem in PEM:
            for cover in VEGETATION:
                for risk in RISK_REGIMES:
                    origin=indexed[(pem,0.,0.,cover,risk,mechanism)]
                    for ps in S_PHASES:
                        for dp in D_PHASES:
                            if ps==0 and dp==0:
                                continue
                            other=indexed[(pem,ps,dp,cover,risk,mechanism)]
                            delta.append(other["fraction_all_three_invasion"]-
                                         origin["fraction_all_three_invasion"])
        phase.append(dict(
            mechanism=mechanism,
            same_draw_comparisons=len(delta),
            nonzero_phase_offset_increases_invasion=sum(d>1e-9 for d in delta),
            zero_phase_synchrony_better=sum(d<-1e-9 for d in delta),
            ties=sum(abs(d)<=1e-9 for d in delta),
            median_shift_minus_synchronized=statistics.median(delta),
            min_max=[min(delta),max(delta)]))
    return dict(
        classification="ONLY_SYNTHETIC_MECHANISTIC_CONSTRAINT_NOT_REAL_PEM_WETLAND",
        study="Causal knockouts of the chosen seasonal toy map to test whether three trophic motifs are needed for phase asymmetry",
        source_protocol="research/PEM_TRIAD_STAGE_NETWORK_EDGE_ABLATION_SPEC_2026-10-25.md",
        settings={"wetland_windows":list(PEM),
                  "stage_phase_salamander":list(S_PHASES),
                  "stage_phase_odonate":list(D_PHASES),
                  "shelter":list(VEGETATION),
                  "risk_regime":list(RISK_REGIMES),
                  "n_shared_synthetic_parameter_draws":DRAWS,
                  "frog_breeding_width":.05},
        total_synthetic_model_cases=len(rows),
        matched_setting_count=len(cases),
        knockouts=core,
        relative_phenology_results_by_knockout=phase,
        warnings=[
            "All network growth/attack and hydrology parameters are chosen for conceptual sensitivity, not calibrated NWI, NAAMP, NPS or GloBI predation data.",
            "Removing one edge also removes its trophic contribution in the annual map; effects are model-specific and not a causal experiment with real biota.",
            "Reverse frog to emerging odonate link comes from an Australian species pair, while D→S→F behavioural effect comes from Japanese system; toy merges generic motifs only.",
            "This pair-resident rarity screen is stronger than nonzero counts, but by itself not a global mathematical theorem for robust coexistence.",
            "Identical generic annual populations and stage activity kernels are not an individual-based or PDE stage-structured demographic calibration.",
        ])


def check():
    p=draw_parameter_ensemble(5)
    e,stage=scenario_edges("PEM1C",.05,0.,0.)
    t=params_for_site(p,"PEM1C",stage,"strong_dragonfly_cue",.05,0.)
    q=np.full((5,3),40.)
    base=annual_map(q,t,e,.35)
    assert base.shape==(5,3) and np.isfinite(base).all()
    assert not np.allclose(base,annual_map(q,t,e,.35,use_risk_cue=False))
    assert not np.allclose(base,annual_map(q,t,e,.35,use_reverse_frog_dragonfly=False))
    assert not np.allclose(base,annual_map(q,t,e,.35,use_direct_dragonfly_frog=False))
    for kwargs in SWITCHES.values():
        r=rare_invasion_criterion(t,e,.35,years=50,last=10,switches=kwargs)
        assert 0<=r["unconditional_mutual_invasion_draw_fraction"]<=1
    print("PEM_THREE_GUILD_MECHANISM_ABLATION_SYNTHETIC_QA_PASS")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="research/results/pem_stage_edge_ablations")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:check()
    else:
        z=run();report=summarize(z)
        out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
        with (out/"synthetic_full_edge_ablation_cases.csv").open("w",newline="",encoding="utf8") as f:
            w=csv.DictWriter(f,fieldnames=list(z[0]))
            w.writeheader();w.writerows(z)
        (out/"synthetic_results.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
        print("BEGIN_PEM_STAGE_NETWORK_ABLATION_RESULTS")
        print(json.dumps(report,indent=2))
        print("END_PEM_STAGE_NETWORK_ABLATION_RESULTS")
