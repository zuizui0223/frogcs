"""Independently audit the main #1479/#1455 × plant × stage true80y source.

Never interpret synthetic seed/vertex counts as wild sites or field likelihood.
Only four hypothetical biological rate draws (and four seed labels) are used.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_main_mechanism_ontogeny_demography_80y import (
    STAGES, QS, SEED_STARTS, NETWORKS, ROLES, DRAWS, MODES,
    SOURCE_COMMIT, verify_original_main_catalog,
)

KEY = ["context", "network", "plant_role", "scale", "movement", "seed", "draw"]
FIELD = ("matches_log1p", "matches_raw", "f_year80_occupied_mean",
         "f_v0_occupied", "f_v1_occupied", "f_reoccupation_mean",
         "f_extinction_mean", "beta_log1p_OS", "beta_log1p_OV",
         "beta_log1p_SV", "beta_log1p_OSV")
PAIRS = {
    "litter_given_SF": ("SF1_DF0_DS0_L1", "SF1_DF0_DS0_L0"),
    "frog_shelter_given_litter": ("SF1_DF0_DS0_L1", "SF0_DF0_DS0_L1"),
    "salamander_shelter_no_litter": ("SF0_DF0_DS1_L0", "SF0_DF0_DS0_L0"),
}


def load_complete_source(root):
    paths = sorted(root.glob("frogcs-main-ontogeny-*/receipt.json"))
    if len(paths) != len(STAGES)*len(QS)*len(SEED_STARTS):
        raise AssertionError(f"Missing original 80y shards: {len(paths)} != 12")
    expected = {(s, q, st) for s in STAGES for q in QS for st in SEED_STARTS}
    seen, f_parts, s_parts, receipts = set(), [], [], []
    baseline_sha = verify_original_main_catalog()
    runner_hash = None
    for path in paths:
        d = path.parent
        r = json.loads(path.read_text())
        ids = tuple(r["seed_labels"])
        key = (r["stage"], r["q"], ids[0])
        if key not in expected or key in seen or ids != (ids[0], ids[0]+1):
            raise AssertionError("Duplicate or unexpected stage/q/seed source shard")
        seen.add(key)
        if (r["status"] != "GENUINE_80YEAR_MODEL_NATIVE"
                or r["years"] != 80
                or r["biological_source_commit"] != SOURCE_COMMIT
                or r["original_main_catalog_sha256"] != baseline_sha
                or r["source_rate_draw_ids"] != list(DRAWS)
                or r["model_catalog_ids"] != [1479,1455]
                or r["plant_role_ids"] != list(ROLES)
                or r["movement_modes"] != list(MODES)
                or r["external_immigration"] is not False
                or r["independent_rate_draws"] != 4
                or r["independent_stochastic_seeds"] != 2
                or max(r["original_4y_same_kernel_replay_errors"].values()) > 1e-7):
            raise AssertionError("Scientific-source receipt invalid for " + str(d))
        runner_hash = runner_hash or r["source_script_sha256"]
        if runner_hash != r["source_script_sha256"]:
            raise AssertionError("Source model script varied between biological jobs")
        f = pd.read_csv(d / "original_80y_frog_vertex_demography.csv.gz")
        s = pd.read_csv(d / "same_model_four_sign_and_occupancy.csv")
        grp = pd.read_csv(d / "source_group_accounting.csv")
        if (len(f) != 768 or len(s) != 96 or len(grp) != 48
                or f.duplicated(KEY+["vertex"]).any()
                or s.duplicated(KEY).any()
                or set(f.context) != {r["stage"]}
                or set(s.context) != {r["stage"]}
                or set(f.scale) != {r["q"]}
                or set(s.scale) != {r["q"]}
                or set(f.seed) != set(ids)
                or set(s.seed) != set(ids)
                or set(f.draw) != set(DRAWS)
                or set(s.draw) != set(DRAWS)
                or set(f.network) != set(NETWORKS)
                or set(f.plant_role) != set(ROLES)
                or set(f.movement) != set(MODES)
                or f.n_external_immigrants.ne(0).any()
                or int(f.n_local_returns.sum()) !=
                   r["n_0_to_positive_frog_patch_events"]
                or int(grp.genuine_0_to_positive_frog_events.sum()) !=
                   int(f.n_local_returns.sum())):
            raise AssertionError("Actual 80y source row/vertex/return accounting failed")
        # Readbacks must be reconstructible from actual F vertices, not
        # merely from a saved four-sign summary file.
        ff = f.sort_values(KEY+["vertex"])
        s2 = s.set_index(KEY).sort_index()
        g = ff.groupby(KEY,sort=True)
        occupied = g.final_occupied_patches.mean()
        returns = g.n_local_returns.mean()
        if (not np.allclose(occupied.sort_index().values,
                            s2.f_year80_occupied_mean.values,
                            rtol=0,atol=1e-10)
                or not np.allclose(returns.sort_index().values,
                                   s2.f_reoccupation_mean.values,
                                   rtol=0,atol=1e-10)
                or not g.vertex.nunique().eq(8).all()):
            raise AssertionError("Source F vertex readback differs from saved year80 output")
        # Independently reconstruct the signed 2x2x2 model response from
        # the original saved F aquatic vertices (not the stored sign values).
        recreated=[]
        for identity, subset in g:
            y=subset.sort_values("vertex").mean_cohort_B_last_window.to_numpy(float)
            if len(y)!=8 or not np.isfinite(y).all() or (y<0).any():
                raise AssertionError("Invalid actual original F cohort vertices")
            row=dict(zip(KEY,identity))
            for transform, arr in (("raw",y),("log1p",np.log1p(y))):
                cube=arr.reshape(2,2,2)  # original index order is V,S,D
                dd=cube[:,:,1]-cube[:,:,0]
                ss=cube[:,1,:]-cube[:,0,:]
                contrasts=np.asarray([
                    np.mean(dd[:,1]-dd[:,0]),
                    np.mean(dd[1,:]-dd[0,:]),
                    np.mean(ss[1,:]-ss[0,:]),
                    (dd[1,1]-dd[1,0])-(dd[0,1]-dd[0,0]),
                ],dtype=float)
                signs=np.where(contrasts>1e-9,1,
                               np.where(contrasts<-1e-9,-1,0))
                for name,val in zip(("OS","OV","SV","OSV"),contrasts):
                    row["beta_"+transform+"_"+name]=float(val)
                row["matches_"+transform]=bool(np.array_equal(signs,[-1,-1,1,1]))
            row["f_v0_occupied"]=float(subset.loc[subset.vertex<4,
                                                     "final_occupied_patches"].mean())
            row["f_v1_occupied"]=float(subset.loc[subset.vertex>=4,
                                                     "final_occupied_patches"].mean())
            row["f_v0_returns"]=float(subset.loc[subset.vertex<4,
                                                   "n_local_returns"].mean())
            row["f_v1_returns"]=float(subset.loc[subset.vertex>=4,
                                                   "n_local_returns"].mean())
            recreated.append(row)
        rec=pd.DataFrame(recreated).set_index(KEY).sort_index()
        if not rec.index.equals(s2.index):
            raise AssertionError("Reconstructed source contrast keys disagree")
        for field in (["matches_raw","matches_log1p","f_v0_occupied",
                       "f_v1_occupied","f_v0_returns","f_v1_returns"]+
                      [f"beta_{scale}_{effect}" for scale in ("raw","log1p")
                       for effect in ("OS","OV","SV","OSV")]):
            if pd.api.types.is_bool_dtype(rec[field]):
                if not np.array_equal(rec[field].to_numpy(),
                                      s2[field].to_numpy().astype(bool)):
                    raise AssertionError("Saved four-sign classification differs: "+field)
            elif not np.allclose(rec[field].to_numpy(float),
                                 s2[field].to_numpy(float),rtol=0,atol=1e-10):
                raise AssertionError("Saved source contrast differs: "+field)
        f_parts.append(f)
        s_parts.append(s)
        receipts.append(dict(stage=r["stage"],q=r["q"],seed_start=ids[0],
                             n_F_vertices=len(f),n_original_theta=s.draw.nunique(),
                             n_original_rng_labels=len(ids),
                             F_reoccupations=int(f.n_local_returns.sum())))
    if seen != expected:
        raise AssertionError("Source stage/q/seed factorial incomplete")
    f = pd.concat(f_parts,ignore_index=True)
    s = pd.concat(s_parts,ignore_index=True)
    if (len(f) != 9216 or len(s) != 1152
            or f.duplicated(KEY+["vertex"]).any() or s.duplicated(KEY).any()):
        raise AssertionError("Full original 80y output row inventory incomplete")
    return f,s,pd.DataFrame(receipts)


def matched_arm_differences(scores,*,arms,axis,key):
    """Within-source theta, seed label, stage, movement and q pairing."""
    a,b = arms
    left = scores[scores[axis].eq(a)].copy().set_index(key).sort_index()
    right = scores[scores[axis].eq(b)].copy().set_index(key).sort_index()
    if (not left.index.equals(right.index) or
            len(left) != scores.groupby(key).ngroups):
        raise AssertionError("Cannot pair source intervention with identical covariates")
    out = pd.DataFrame(index=left.index)
    for f in FIELD:
        out["delta_"+f] = left[f].to_numpy(dtype=float)-right[f].to_numpy(dtype=float)
    return out.reset_index()


def make_comparisons(scores):
    role_parts=[]
    for label,(on,off) in PAIRS.items():
        d=matched_arm_differences(
            scores,arms=(on,off),axis="plant_role",
            key=["context","network","scale","movement","seed","draw"])
        d["plant_axis"]=label
        d["on_plant"]=on
        d["off_plant"]=off
        role_parts.append(d)
    role = pd.concat(role_parts,ignore_index=True)
    role_group = ["context","network","plant_axis","scale","movement"]
    role_agg = (role.groupby(role_group,sort=True)
          .agg(n_theta_seed_pairs=("draw","size"),
               n_distinct_theta=("draw","nunique"),
               n_rng_seeds=("seed","nunique"),
               delta_four_sign_rate=("delta_matches_log1p","mean"),
               delta_occupied_patches_year80=("delta_f_year80_occupied_mean","mean"),
               delta_f_v0_occupied=("delta_f_v0_occupied","mean"),
               delta_f_v1_occupied=("delta_f_v1_occupied","mean"),
               delta_f_reoccupations=("delta_f_reoccupation_mean","mean"),
               delta_f_extinctions=("delta_f_extinction_mean","mean"))
          .reset_index())
    if (len(role) != 3*2*2*2*4*4*3 or len(role_agg) != 3*2*3*2*2
            or not role_agg.n_theta_seed_pairs.eq(16).all()):
        raise AssertionError("Cross-stage plant ON/OFF paired response incomplete")
    edge = matched_arm_differences(
        scores,arms=("main1479","main1455"),axis="network",
        key=["context","plant_role","scale","movement","seed","draw"])
    edge_agg = (edge.groupby(["context","plant_role","scale","movement"])
        .agg(n_theta_seed_pairs=("draw","size"),
             delta_four_sign_rate=("delta_matches_log1p","mean"),
             delta_occupied_patches_year80=("delta_f_year80_occupied_mean","mean"),
             delta_f_reoccupations=("delta_f_reoccupation_mean","mean"))
        .reset_index())
    if (len(edge) != 3*6*2*2*4*4 or len(edge_agg) != 3*6*2*2
            or not edge_agg.n_theta_seed_pairs.eq(16).all()):
        raise AssertionError("Main #1479 vs #1455 edge-ablation matching incomplete")
    # Do not force an apparent winner: these are finite-N four-seed,
    # four-HYPOTHETICAL-rate model-native effects and may differ from PR146
    # deterministic results. Preserve all zero/reversed effects.
    return role,role_agg,edge,edge_agg


def audit(root,out):
    f,s,shards = load_complete_source(Path(root))
    roles,role_agg,edge,edge_agg = make_comparisons(s)
    out = Path(out)
    out.mkdir(parents=True,exist_ok=True)
    shards.to_csv(out/"twelve_true80_source_shards.csv",index=False)
    roles.to_csv(out/"same_rate_stage_vegetation_role_pairs.csv",index=False)
    role_agg.to_csv(out/"stage_vegetation_role_effects.csv",index=False)
    edge.to_csv(out/"same_rate_main1479_vs1455_pairs.csv",index=False)
    edge_agg.to_csv(out/"main1479_vs1455_edge_ablation_effects.csv",index=False)
    result = dict(
        status="TRUE80Y_3STAGE_6PLANT_2MAIN_CANDIDATE_SAME_THETA_AUDIT_SUCCESS",
        n_true_source_shards=12, n_frog_source_vertices=len(f),
        n_model_native_four_sign_and_demographic_scores=len(s),
        n_distinct_synthetic_theta=4, n_independent_rng_seed_labels=4,
        n_genuine_0_to_positive_frog_events=int(f.n_local_returns.sum()),
        n_stage_plant_paired_differences=len(roles),
        n_stage_plant_effect_rows=len(role_agg),
        n_main_edge_paired_differences=len(edge),
        n_main_edge_effect_rows=len(edge_agg),
        any_empirical_NAAMP_predation_estimated=False,
        empirical_field_posterior=False,
        comparisons=(["litter_given_SF","frog_shelter_given_litter",
                      "salamander_shelter_no_litter"]),
    )
    (out/"final_source_audit_receipt.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("MAIN_MECHANISM_CROSS_STAGE_80Y_AUDIT",json.dumps(result),flush=True)
    print("PLANT_EFFECTS\n"+role_agg.to_string(index=False),flush=True)
    print("MAIN_EDGE_EFFECTS\n"+edge_agg.to_string(index=False),flush=True)
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    audit(a.input,a.output)
