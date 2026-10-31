"""Whole-archive 132-case pattern-oriented comparison and conditional toy ABC.

All source cases are included (no screening on observed performance).  Fixes
the biological demographic rates to those ALREADY run in October 2026 and
varies only assumed suitability-to-model transport and synthetic rank noise
in the identifiability exercise. Not biological-rate posterior inference.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import ROOT, SITE, VISITS, load_cohort
from pattern_oriented_abc_pilot import (
    PATTERNS, HOLDOUT, BACKGROUNDS, N_BOOT, SEED, ACCEPT_FRACTION,
    NOISE_RANGE, WARP_RANGE, COV_SHRINK, EIGEN_FLOOR,
    get_design, stats_from_y, compare_frozen_macro, bootstrap_observed,
    group_exact_surfaces, pattern_assessment, prior_reference,
    conditional_abc, recovery_matrix, MACRO,
)

SRC=ROOT/"research/results/literature_extension_20261029"
FILES=tuple(SRC/f"primary_{risk}_{mode}_cells.csv.gz"
            for risk in (0,1) for mode in ("dynamic","frozen"))
DESIGN=SRC/"design.csv"
OUT=ROOT/"research/results/macro_pom_catalog132_20261031"
N_CASES=132
LEVELS=9
N_REF=32
N_PSEUDO=6


def archived_full_catalog(sources,inventory):
    """Validate complete case-grid source, no extras or missing case IDs."""
    if len(sources)!=4:
        raise ValueError("Require all four archived extension sources")
    raw=pd.concat(sources,ignore_index=True)
    if len(inventory)!=N_CASES or inventory.case.duplicated().any():
        raise ValueError("Archived design isn't exactly 132 distinct cases")
    if len(raw)!=N_CASES*2*LEVELS*LEVELS:
        raise ValueError("Missing/extra source grids")
    key=["case","vegetation","S_source","D_source"]
    if raw.duplicated(key).any() or set(raw.case)!=set(inventory.case):
        raise ValueError("Duplicate case/cell or mismatch with archived inventory")
    # Use original CSV case identity and source-native parameters, not fabricated metadata.
    metadata={}
    grids={}
    expected=np.asarray([(v,s,o) for v in (0.,1.) for s in np.linspace(.25,2.,LEVELS)
                         for o in np.linspace(.25,2.,LEVELS)])
    for row in inventory.to_dict("records"):
        case=int(row["case"])
        group=raw[raw.case==case].sort_values(key)
        actual=group[["vegetation","S_source","D_source"]].to_numpy(float)
        if len(group)!=len(expected) or not np.allclose(actual,expected,rtol=0,atol=1e-8):
            raise ValueError(f"Unusable archived axis for {case}")
        for col in ("context","family","edge","risk"):
            a=group[col].unique()
            if len(a)!=1 or a[0]!=row[col]:
                raise AssertionError(f"Original case metadata mismatch {case} {col}")
        y=group.F_B.to_numpy(float)
        if not np.isfinite(y).all() or (y<=0).any():
            raise ValueError("Bad F_B source")
        name=f"case_{case:03d}"
        metadata[name]=row
        grids[name]=y.reshape(2,LEVELS,LEVELS)
    if len(grids)!=N_CASES:
        raise AssertionError("Incomplete scenario array")
    return grids,metadata


def run(n_ref=N_REF,n_pseudo=N_PSEUDO):
    if n_ref<5 or n_pseudo<2:raise ValueError("Insufficient toy reference runs")
    OUT.mkdir(exist_ok=True,parents=True)
    sites=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    if sites.n.sum()!=63180 or int(sites.V.sum())!=506:
        raise AssertionError("Archived field cohort changed")
    original=pd.read_csv(DESIGN)
    sources=[pd.read_csv(p) for p in FILES]
    surfaces,meta=archived_full_catalog(sources,original)
    aliases,groups=group_exact_surfaces(surfaces)
    eq=pd.DataFrame([dict(group=sorted(cases)[0],n_cases=len(cases),cases=";".join(sorted(cases)),
                          source_grid_sha256=h) for h,cases in groups.items()])
    eq.to_csv(OUT/"exact_surface_equivalence.csv",index=False)
    results=[];masses=[];recovered=[];refdata=[];bootdata=[];helddata=[];full=[]
    for background in BACKGROUNDS:
        design=get_design(sites,background)
        observed,heldout=stats_from_y(sites.strong_rate,design,holdout=True)
        compare_frozen_macro(observed,background)
        draws,cov,invcov,meta_cov=bootstrap_observed(
            sites.strong_rate,design,sites.spatial_block,n_boot=N_BOOT)
        boot=pd.DataFrame(draws,columns=PATTERNS);boot["background"]=background
        bootdata.append(boot)
        for k,p in zip(HOLDOUT,heldout):
            helddata.append(dict(background=background,pattern=k,observed=float(p)))
        all_case=pattern_assessment(sites,background,design,surfaces,
                                     observed,heldout,invcov,draws)
        all_case["equivalence_group"]=all_case.case.map(aliases)
        full.append(all_case)
        for row in all_case.to_dict("records"):
            tags=meta[row["case"]]
            results.append(dict(**row,context=tags["context"],family=tags["family"],
                                edge=tags["edge"],risk=bool(tags["risk"]),
                                sa=float(tags["sa"]),da=float(tags["da"]),
                                growth_S=float(tags["sg"]),growth_D=float(tags["dg"]),
                                handling_S=float(tags["hs"]),handling_D=float(tags["hd"])))
        library=prior_reference(sites,background,design,surfaces,aliases,
                                seed=SEED+{"uniform":0,"target_group":10000}[background],
                                per_case=n_ref)
        posterior,accepted,epsilon,min_dist=conditional_abc(library,observed,invcov)
        for cls,prob in posterior.items():
            masses.append(dict(background=background,equivalence_group=cls,
                               illustrative_mass=float(prob),
                               n_equivalent_cases=int(sum(v==cls for v in aliases.values())),
                               n_accepted=int((accepted.equivalence_group==cls).sum()),
                               accepted_fraction=ACCEPT_FRACTION,epsilon_d2=epsilon,
                               minimal_reference_distance2=min_dist,
                               status="CONDITIONAL_NO_BIOLOGICAL_RATE_PRIORS"))
        toy=recovery_matrix(sites,background,design,surfaces,aliases,library,invcov,
                            seed=SEED+{"uniform":0,"target_group":10000}[background],
                            n=n_pseudo)
        toy["background"]=background
        recovered.append(toy)
        library["background"]=background
        refdata.append(library)
        best=all_case.sort_values(["distance_mahalanobis","case"]).iloc[0]
        print("ARCHIVE132",background,"best",best.case,
              "group",best.equivalence_group,
              "distance",float(best.distance_mahalanobis),
              "marginal_pattern_matches",int(best.fitted_patterns_within_marginal_95),
              "distinct_groups",len(groups),"toy_recovery",float(toy.recovered.mean()),
              flush=True)
    table=pd.DataFrame(results)
    table.to_csv(OUT/"all_case_pattern_distances.csv",index=False)
    mass=pd.DataFrame(masses);mass.to_csv(OUT/"toy_conditional_abc_mass.csv",index=False)
    recover=pd.concat(recovered,ignore_index=True)
    recover.to_csv(OUT/"pseudo_recovery_records.csv",index=False)
    pd.concat(bootdata).to_csv(OUT/"observed_bootstrap_patterns.csv",index=False)
    pd.DataFrame(helddata).to_csv(OUT/"heldout_observed_patterns.csv",index=False)
    pd.concat(refdata).to_csv(OUT/"conditional_abc_reference.csv.gz",index=False,
                              compression={"method":"gzip","mtime":0})
    # Compact all-case ranking (every case, shorter columns) and scenario metadata.
    rankcols=["background","case","equivalence_group","context","family","edge","risk",
              "distance_mahalanobis","fitted_patterns_within_marginal_95",
              "model_OS","obs_OS","model_OV","obs_OV","model_SV","obs_SV","model_OSV","obs_OSV",
              "model_O_with_S_low","obs_O_with_S_low",
              "model_O_with_S_high","obs_O_with_S_high"]
    rank=table[rankcols].sort_values(["background","distance_mahalanobis","case"])
    rank.to_csv(OUT/"compact_full_ranking.csv",index=False)
    summary=[]
    for bg in BACKGROUNDS:
        q=rank[rank.background==bg]
        best=q.iloc[0]
        nofit=int((q.fitted_patterns_within_marginal_95<6).all())
        pop=mass[mass.background==bg].sort_values("illustrative_mass",ascending=False)
        diag=recover[recover.background==bg]
        summary.append(dict(background=bg,n_candidates=len(q),n_distinct_groups=len(groups),
                            best_case=best.case,best_group=best.equivalence_group,
                            best_distance=float(best.distance_mahalanobis),
                            best_patterns_within_observed_95=int(best.fitted_patterns_within_marginal_95),
                            n_all_six_patterns_within_95=int((q.fitted_patterns_within_marginal_95==6).sum()),
                            no_adequate_six_pattern_case=bool(nofit),
                            illustrative_top_group=pop.equivalence_group.iloc[0],
                            illustrative_top_mass=float(pop.illustrative_mass.iloc[0]),
                            pseudo_group_recovery=float(diag.recovered.mean()),
                            status="EXPLORATORY_FIXED_BIOLOGICAL_RATES_NOT_CAUSAL"))
    s=pd.DataFrame(summary)
    s.to_csv(OUT/"catalog132_summary.csv",index=False)
    pd.DataFrame(meta).T.rename_axis("case").to_csv(OUT/"archived_case_metadata.csv")
    provenance=dict(status="FULL_ARCHIVE_132_POM_FIXED_RATES_CONDITIONAL_TOY_ABC_ONLY",
                    n_sites=len(sites),n_visits=int(sites.n.sum()),n_cases=len(surfaces),
                    n_source_cells=int(sum(len(a.ravel()) for a in surfaces.values())),
                    n_equivalence_groups=len(groups),n_boot=N_BOOT,n_ref_per_case=n_ref,
                    n_pseudo_per_case=n_pseudo,patterns=list(PATTERNS),
                    heldout=list(HOLDOUT),acceptance_fraction=ACCEPT_FRACTION,
                    biological_parameters_held_fixed=True,
                    model_priors_used={"noise_prior":list(NOISE_RANGE),"proxy_warp_prior":list(WARP_RANGE)},
                    claims=["Descriptive pattern reproduction only; no field causation",
                            "Toy mass is conditional and NOT posterior over biological mechanisms",
                            "Source archive all 132 cases, including failures and structural ablations",
                            "The observed source was used in prior analyses; no independent confirmation",
                            "The adult-call-to-aquatic-cohort mapping is monotone rank-only, not biologically calibrated"],
                    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [SITE,VISITS,MACRO,DESIGN,*FILES]},
                    code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"receipt.json").write_text(json.dumps(provenance,indent=2,ensure_ascii=False)+"\n")
    print("ARCHIVE132 SUMMARY\n"+s.to_string(index=False),flush=True)
    print("ARCHIVE132 TOP 12 EACH\n"+rank.groupby("background").head(12).to_string(index=False),flush=True)
    print("ARCHIVE132 TOY TOP 12\n"+mass.sort_values(
        ["background","illustrative_mass"],ascending=[True,False]).groupby(
            "background").head(12).to_string(index=False),flush=True)
    return s,table,mass,recover


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--run",action="store_true")
    ap.add_argument("--reference-per-case",type=int,default=N_REF)
    ap.add_argument("--pseudo-per-case",type=int,default=N_PSEUDO)
    args=ap.parse_args()
    if not args.run:ap.error("Explicit --run required")
    run(n_ref=args.reference_per_case,n_pseudo=args.pseudo_per_case)
