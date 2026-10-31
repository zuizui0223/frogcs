"""Signed contextual-modulation POM on 4,248 real frog calling sites.

Compare *direction* of high-S minus low-S O-calling association and
V-positive minus V-zero association directly; the former needs no arbitrary
near-zero equivalence threshold. All signs and joint uncertainty use the SAME
spatial-block bootstrap. Real S = suitability, V = 3-km vegetation proxy.

This is conditional descriptive POM, NOT a biological scenario posterior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import ROOT, SITE, VISITS, SEED, load_cohort
from pattern_oriented_abc_pilot import (
    BACKGROUNDS, get_design, rankz, stats_from_y,
    site_response, group_exact_surfaces,
)
from pattern_oriented_archive132 import FILES, DESIGN, archived_full_catalog
from directional_pom_132 import nuisance_draws

OUT = ROOT / "research/results/macro_signed_context_modulation_20261031"
N_BOOT = 999
N_MODEL = 48
N_RECOVERY = 8
CONFIDENCE_CUTOFF = .90
MISMATCH_FACTOR = .25
METRICS = ("OS", "OV", "delta_S_high_minus_low", "delta_V_positive_minus_zero")
STRATA = ("S_low", "S_high", "V_zero", "V_positive")


def contrast_point(y, design):
    """Identical global-rank estimands for observed and simulated Y."""
    primary, holdout = stats_from_y(y, design, holdout=True)
    return np.asarray([primary[0], primary[1],
                       primary[5] - primary[4],
                       holdout[1] - holdout[0]], dtype=float)


def _block_moments(o, y, gid, n_blocks, mask):
    x = o[mask]
    yy = y[mask]
    matrix = np.column_stack([np.ones(len(x)), x, yy, x*x, yy*yy, x*yy])
    moment = np.zeros((n_blocks, 6))
    np.add.at(moment, gid[mask], matrix)
    return moment


def _corr_from_moment(moment):
    n, sx, sy, sxx, syy, sxy = moment
    if n <= 4:
        return np.nan
    vx = sxx - sx*sx/n
    vy = syy - sy*sy/n
    if vx <= 1e-12 or vy <= 1e-12:
        return np.nan
    return float((sxy - sx*sy/n) / np.sqrt(vx*vy))


def joint_observed_bootstrap(y, d, design, n_boot=N_BOOT, seed=SEED):
    """Four correlated signed contrasts from one common whole-block resampling.

    Predictor and response ranks are fixed on the original sites, rather than
    re-ranked after resampling. Original route/site clusters are never split.
    """
    y = rankz(y)
    x = design["x"]
    o = design["o"]
    groups, _ = pd.factorize(d.spatial_block, sort=True)
    n_blocks = int(groups.max() + 1)
    gram = np.zeros((n_blocks, 8, 8))
    rhs = np.zeros((n_blocks, 8))
    np.add.at(gram, groups, x[:, :, None]*x[:, None, :])
    np.add.at(rhs, groups, x*y[:, None])
    moments = {k: _block_moments(o, y, groups, n_blocks,
                                  design["masks"][k]) for k in STRATA}

    rng = np.random.default_rng(seed)
    weights = rng.multinomial(n_blocks,
                              np.repeat(1/n_blocks, n_blocks), size=n_boot)
    samples = []
    for w in weights:
        xx = np.einsum("k,kij->ij", w, gram)
        if np.linalg.matrix_rank(xx, tol=1e-9) < 8:
            continue
        beta = np.linalg.solve(xx, w @ rhs)
        corrs = {name: _corr_from_moment(w @ matrix)
                 for name, matrix in moments.items()}
        if not all(np.isfinite(v) for v in corrs.values()):
            continue
        samples.append([float(beta[4]), float(beta[5]),
                        corrs["S_high"] - corrs["S_low"],
                        corrs["V_positive"] - corrs["V_zero"]])
    a = np.asarray(samples, dtype=float)
    if a.ndim != 2 or a.shape[1] != len(METRICS) or len(a) < .90*n_boot:
        raise ValueError("Insufficient valid joint spatial bootstrap support")
    return a


def selected_observed_signs(observed, bootstrap, confidence=CONFIDENCE_CUTOFF):
    point = np.asarray(observed, dtype=float)
    draws = np.asarray(bootstrap, dtype=float)
    if point.shape != (len(METRICS),) or draws.ndim != 2 or draws.shape[1] != len(METRICS):
        raise ValueError("Wrong joint sign dimensions")
    if not 0.5 < confidence <= 1:
        raise ValueError("Invalid sign confidence cutoff")
    p_neg = np.mean(draws < 0, axis=0)
    p_pos = np.mean(draws > 0, axis=0)
    selected = tuple(np.flatnonzero(np.maximum(p_neg, p_pos) >= confidence).tolist())
    if not len(selected):
        raise ValueError("No robust observed direction under fixed criterion")
    direction = np.sign(point).astype(int)
    for i in selected:
        if direction[i] != (-1 if p_neg[i] > p_pos[i] else 1):
            raise AssertionError("Point estimate conflicts with dominant bootstrap direction")
    low, high = np.quantile(draws, [.025, .975], axis=0)
    rows = [dict(metric=name, observed=float(point[i]),
                 bootstrap_low=float(low[i]), bootstrap_high=float(high[i]),
                 frequency_negative=float(p_neg[i]), frequency_positive=float(p_pos[i]),
                 selected=bool(i in selected), observed_direction=int(direction[i]))
            for i,name in enumerate(METRICS)]
    return selected, direction, pd.DataFrame(rows)


def simulated_contrasts(d, background, design, surface, noise_draws):
    """Shared noise/transport draws for all response surfaces."""
    vectors = []
    for warp_o, warp_s, noise in noise_draws:
        f = site_response(d, background, surface, warps=(warp_o,warp_s))
        y = rankz(np.log(f)) + noise
        vectors.append(contrast_point(y, design))
    a = np.asarray(vectors, dtype=float)
    if a.shape != (len(noise_draws),len(METRICS)) or not np.isfinite(a).all():
        raise ValueError("Malformed synthetic signed contrasts")
    return a


def joint_direction_score(obs_boot, simulation, selected):
    """Joint-category score; not a product-of-correlated-sign likelihood."""
    if not len(selected):
        raise ValueError("Cannot score with zero selected contrasts")
    o = np.sign(np.asarray(obs_boot, dtype=float)[:, selected]).astype(int)
    s = np.sign(np.asarray(simulation, dtype=float)[:, selected]).astype(int)
    if np.any(o == 0) or np.any(s == 0):
        raise ValueError("Exactly zero signs must be disclosed, not silently mapped")
    mismatch = (o[:,None,:] != s[None,:,:]).sum(axis=-1)
    return (float(np.mean(MISMATCH_FACTOR ** mismatch)),
            float(np.mean(mismatch == 0)))


def _signature(vector):
    return ",".join("+" if x > 0 else "-" if x < 0 else "0" for x in vector)


def rank_fixed_132(d, bg, design, observed_boot, selected, observed_dir,
                   surfaces, groups, n_model=N_MODEL, n_recovery=N_RECOVERY):
    """Preserve all cases and collapse exact F_B grids before random draws."""
    noise=nuisance_draws(d,n_model,seed=SEED+(0 if bg=="uniform" else 10000))
    independent=nuisance_draws(d,n_recovery*len(groups),
                               seed=SEED+42200+(0 if bg=="uniform" else 10000))
    case_rows=[]
    sim_by_group={}
    source_signature={}
    for label in sorted(groups):
        cases=sorted(groups[label])
        surface=surfaces[cases[0]]
        deterministic=contrast_point(site_response(d,bg,surface),design)
        sim=simulated_contrasts(d,bg,design,surface,noise)
        sim_by_group[label]=sim
        source_signature[label]=_signature(np.sign(deterministic)[list(selected)])
        soft,exact=joint_direction_score(observed_boot,sim,selected)
        sign=np.sign(deterministic).astype(int)
        passes=bool(np.array_equal(sign[list(selected)],observed_dir[list(selected)]))
        for case in cases:
            row=dict(background=bg,case=case,source_group=label,
                     n_equivalent_source_cases=len(cases),
                     direction_signature=source_signature[label],
                     all_selected_signs_match=passes,
                     n_selected_signs_matching=int(np.sum(
                         sign[list(selected)]==observed_dir[list(selected)])),
                     n_selected=len(selected),
                     joint_soft=soft,joint_exact=exact)
            for i,k in enumerate(METRICS):
                row["model_"+k]=float(deterministic[i])
                row["model_sign_"+k]=int(sign[i])
                row["sim_negative_frequency_"+k]=float((sim[:,i]<0).mean())
            case_rows.append(row)
    cases=pd.DataFrame(case_rows)
    if len(cases)!=len(all_surfaces) or cases.case.nunique()!=len(all_surfaces):
        raise AssertionError("Missing case labels in signed contrast POM")
    # Direction signature groups are much coarser than biological structures.
    by_sign=defaultdict(list)
    for source,sign in source_signature.items():
        by_sign[sign].append(source)
    signature_rows=[]
    for sig, ids in sorted(by_sign.items()):
        labels=[case for ident in ids for case in groups[ident]]
        sources=[cases[(cases.source_group==ident)].iloc[0] for ident in ids]
        signature_rows.append(dict(background=bg,signature=sig,
                                   n_source_groups=len(ids),
                                   n_cases=len(labels),
                                   representative_case=min(labels),
                                   members=";".join(sorted(labels)),
                                   mean_joint_soft=float(np.mean([r.joint_soft for r in sources])),
                                   best_joint_soft=float(max(r.joint_soft for r in sources)),
                                   exactly_observed_compatible=bool(
                                       all(r.all_selected_signs_match for r in sources))))
    signatures=pd.DataFrame(signature_rows)
    # Pseudo targets sampled from completely separate common-nuisance draws.
    # Identify the directional signature, not the physical source-group ID.
    class_signs={}
    for sig, ids in by_sign.items():
        class_signs[sig]=np.vstack([np.sign(sim_by_group[i][:,selected]) for i in ids])
    recovery=[]
    j=0
    for source in sorted(groups):
        for rep in range(n_recovery):
            test=simulated_contrasts(d,bg,design,
                                     surfaces[min(groups[source])],
                                     [independent[j]])[0]
            j+=1
            if np.any(test[list(selected)]==0):
                raise ValueError("Synthetic exact-zero sign not modelled")
            target=np.sign(test[list(selected)])
            ranks=[]
            for signature, ref in class_signs.items():
                mismatch=(ref!=target).sum(axis=1)
                similarity=float(np.mean(MISMATCH_FACTOR ** mismatch))
                ranks.append((similarity,signature))
            predicted=sorted(ranks,key=lambda x:(-x[0],x[1]))[0][1]
            recovery.append(dict(background=bg,source_group=source,
                                 true_signature=source_signature[source],
                                 predicted_signature=predicted,
                                 recovered=predicted==source_signature[source],
                                 replicate=rep))
    rec=pd.DataFrame(recovery)
    if len(rec)!=len(groups)*n_recovery:
        raise AssertionError("Untracked independent pseudo recovery")
    signature_summary=(
        rec.groupby(["background","true_signature","predicted_signature"])
        .size().rename("n").reset_index())
    signature_summary["n_true"]=signature_summary.groupby(
        ["background","true_signature"]).n.transform("sum")
    signature_summary["fraction"]=signature_summary.n/signature_summary.n_true
    return cases,signatures,rec,signature_summary


def analyze_real_rate_cells(d, bg, design, observed_boot, selected, observed_dir,
                            source_cells, model_meta, n_draw=8):
    """Reuse TRUE 80-year source outputs, not the old toy ABC library."""
    from directional_process_rate_8 import recover_grid
    score=[];cases_seen=set()
    noise=nuisance_draws(d,16,seed=SEED+31000+(0 if bg=="uniform" else 10000))
    for (draw,case),group in source_cells.groupby(["draw","case"]):
        grid=recover_grid(group)
        subset=model_meta[(model_meta.background==bg)&
                          (model_meta.draw==draw)&
                          (model_meta.case==f"case_{int(case):03d}")]
        if len(subset)!=1:raise AssertionError("Missing actual biological rate metadata")
        structure=str(subset.iloc[0].structural_group)
        deterministic=contrast_point(site_response(d,bg,grid),design)
        sim=simulated_contrasts(d,bg,design,grid,noise)
        soft,exact=joint_direction_score(observed_boot,sim,selected)
        sign=np.sign(deterministic).astype(int)
        score.append(dict(background=bg,rate_draw=int(draw),case=f"case_{int(case):03d}",
                          structural_group=structure,joint_soft=soft,joint_exact=exact,
                          all_selected_signs_match=bool(np.array_equal(
                              sign[list(selected)],observed_dir[list(selected)])),
                          n_selected_signs_matching=int(np.sum(
                              sign[list(selected)]==observed_dir[list(selected)])),
                          n_selected=len(selected),
                          model_delta_S=float(deterministic[2]),
                          model_delta_V=float(deterministic[3])))
        cases_seen.add((int(draw),int(case)))
    if len(cases_seen)!=n_draw*24:
        raise AssertionError("Incomplete actual-rate source cases")
    rows=pd.DataFrame(score)
    totals=(rows.groupby(["background","structural_group"])
            .agg(n_configurations=("case","size"),
                 complete_direction_fraction=("all_selected_signs_match","mean"),
                 mean_joint_soft=("joint_soft","mean"),
                 maximum_joint_soft=("joint_soft","max"),
                 rate_draw_count=("rate_draw","nunique")).reset_index())
    return rows,totals


def run(n_model=N_MODEL,n_recovery=N_RECOVERY,source_real_dir=None):
    OUT.mkdir(parents=True,exist_ok=True)
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    if len(d)!=4248 or int(d.n.sum())!=63180 or int(d.V.sum())!=506:
        raise AssertionError("Original NAAMP site/visit/vegetation counts changed")
    surfaces,meta=archived_full_catalog([pd.read_csv(p) for p in FILES],
                                         pd.read_csv(DESIGN))
    _,rawgroups=group_exact_surfaces(surfaces)
    groups={min(cases):sorted(cases) for cases in rawgroups.values()}
    if len(groups)!=104 or sum(map(len,groups.values()))!=132:
        raise AssertionError("Unexpected exact response-surface grouping")
    actual_cells=None;actual_meta=None
    actual_paths=[]
    if source_real_dir is not None:
        src=Path(source_real_dir).resolve()
        actual_paths=[src/"real_simulator_F_B_cells.csv.gz",
                      src/"process_prior_predictive_patterns.csv"]
        for p in actual_paths:
            if not p.is_file():raise FileNotFoundError(str(p))
        actual_cells=pd.read_csv(actual_paths[0])
        actual_meta=pd.read_csv(actual_paths[1])

    observations=[];fixed=[];signatures=[];recovery=[];confusion=[]
    rate_cases=[];rate_group=[]
    for bg in BACKGROUNDS:
        design=get_design(d,bg)
        observed=contrast_point(d.strong_rate,design)
        bootstrap=joint_observed_bootstrap(d.strong_rate,d,design)
        selected,direction,obsinfo=selected_observed_signs(observed,bootstrap)
        obsinfo["background"]=bg
        observations.append(obsinfo)
        cases,sigs,rec,conf=rank_fixed_132(
            d,bg,design,bootstrap,selected,direction,surfaces,groups,
            n_model=n_model,n_recovery=n_recovery)
        fixed.append(cases);signatures.append(sigs)
        recovery.append(rec);confusion.append(conf)
        if actual_cells is not None:
            r,g=analyze_real_rate_cells(d,bg,design,bootstrap,selected,direction,
                                        actual_cells,actual_meta)
            rate_cases.append(r);rate_group.append(g)
        accepted=int(cases.all_selected_signs_match.sum())
        unique=int(cases[cases.all_selected_signs_match].source_group.nunique())
        # A candidate-catalog reference, not a hypothesis-testing p-value.
        probability=unique/len(groups)
        top=cases.sort_values(["joint_soft","case"],ascending=[False,True]).iloc[0]
        print("SIGNED_CONTEXT",bg,"observed",observed.tolist(),
              "bootstrap_prob_negative",[(bootstrap[:,i]<0).mean() for i in range(4)],
              "selected",[METRICS[i] for i in selected],
              "matching_case_labels",accepted,
              "matching_source_groups",unique,
              "catalog_reference",probability,
              "best",top.case,"soft",float(top.joint_soft),
              "signature_groups",len(sigs),
              "recovery",float(rec.recovered.mean()),flush=True)

    output=dict(observed_signed_context=pd.concat(observations,ignore_index=True),
                fixed_case_scores=pd.concat(fixed,ignore_index=True),
                directional_signatures=pd.concat(signatures,ignore_index=True),
                pseudo_recovery_records=pd.concat(recovery,ignore_index=True),
                pseudo_recovery_confusion=pd.concat(confusion,ignore_index=True))
    if actual_cells is not None:
        output["real_rate_case_scores"]=pd.concat(rate_cases,ignore_index=True)
        output["real_rate_structural_groups"]=pd.concat(rate_group,ignore_index=True)
    # Cross-background case intersection; never mistake two backgrounds for
    # independent field replications.
    full=output["fixed_case_scores"]
    pivot=full.pivot(index="case",columns="background",
                     values="all_selected_signs_match")
    both=pivot.all(axis=1)
    cross=full.drop_duplicates("case")[["case","source_group"]].set_index("case")
    cross["uniform_pass"]=pivot["uniform"]
    cross["target_group_pass"]=pivot["target_group"]
    cross["both_backgrounds_pass"]=both
    output["cross_background_fixed_cases"]=cross.reset_index()
    summary=[]
    for bg in BACKGROUNDS:
        f=full[full.background==bg]
        o=output["observed_signed_context"]
        observed=o[(o.background==bg)&(o.selected)]
        r=output["pseudo_recovery_records"]
        s=output["directional_signatures"]
        own=r[r.background==bg]
        summary.append(dict(background=bg,n_cases=len(f),n_source_groups=104,
                            n_selected_signs=len(observed),
                            eligible_patterns=";".join(observed.metric),
                            n_cases_all_selected=int(f.all_selected_signs_match.sum()),
                            n_distinct_source_groups_all_selected=int(
                                f[f.all_selected_signs_match].source_group.nunique()),
                            n_signatures=int(len(s[s.background==bg])),
                            best_case=f.sort_values(["joint_soft","case"],
                                ascending=[False,True]).iloc[0].case,
                            best_joint_soft=float(f.joint_soft.max()),
                            pseudo_direction_group_recovery=float(own.recovered.mean()),
                            theoretical_fair_sign_reference=float(2**(-len(observed))),
                            observed_catalog_fraction=float(
                                f[f.all_selected_signs_match].source_group.nunique()/104),
                            n_cross_background_cases=int(both.sum()),
                            status="CONTEXTUAL_DIRECTION_POM_NOT_CAUSAL"))
    output["summary"]=pd.DataFrame(summary)
    for name,data in output.items():
        data.to_csv(OUT/(name+".csv"),index=False)
    p=[SITE,VISITS,DESIGN,*FILES,*actual_paths]
    receipt=dict(status="DIRECTION_CONTEXT_MODULATION_WITH_COMMON_BLOCK_BOOTSTRAP",
                 observed_sites=len(d),surveys=int(d.n.sum()),n_model_reps=n_model,
                 n_recovery_reps=n_recovery,source_cases=132,source_groups=104,
                 metrics=list(METRICS),bootstrap_replicates=N_BOOT,
                 bootstrap_same_integer_block_weights_for_all_metrics=True,
                 target_group_not_independent_data_replication=True,
                 new_biological_process_parameters_fitted=False,
                 no_claims=["No biological scenario probability or ABC posterior",
                            "No demonstrated frog adult acoustic conversion",
                            "Suitability differs from predator density",
                            "V is 3km remote context, not in-pond vegetation",
                            "Rate-draw uncertainty intervals were hypothetical"],
                 sources_sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in p},
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("SIGNED_CONTEXT_SUMMARY\n"+output["summary"].to_string(index=False),flush=True)
    print("OBSERVED_SIGNED_CONTEXT\n"+output["observed_signed_context"].to_string(index=False),flush=True)
    print("BEST_MATCHING_CATALOG_CASES\n"+output["fixed_case_scores"][
        output["fixed_case_scores"].all_selected_signs_match].to_string(index=False),flush=True)
    if actual_cells is not None:
        print("ACTUAL_RATE_DIRECTION_CASE_COUNTS\n"+
              output["real_rate_case_scores"].groupby("background").
              all_selected_signs_match.agg(["sum","size"]).to_string(),flush=True)
    return output


if __name__ == "__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--run",action="store_true")
    a.add_argument("--model-reps",type=int,default=N_MODEL)
    a.add_argument("--recovery-reps",type=int,default=N_RECOVERY)
    a.add_argument("--actual-rate-dir",type=Path,default=None)
    args=a.parse_args()
    if not args.run:a.error("Explicit --run required")
    run(n_model=args.model_reps,n_recovery=args.recovery_reps,
        source_real_dir=args.actual_rate_dir)
