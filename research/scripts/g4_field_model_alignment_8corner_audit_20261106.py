"""G4: field / model eight-corner source overlap + structural identifiability.

This is a *response-blind preflight* for a later mechanism-constrained acoustic
predictive test; it neither fits wild predation nor validates F_B-to-calling.
It checks R1 field eight-corner support before comparing model 2x2x2 signs and
shows that any 8-corner source surface multilinearly interpolated on O/S/V is
an algebraic combination of the saturated empirical O/S/V interaction basis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from acoustic_mechanism_cv import prepare_sites, BACKGROUNDS
from naamp_odonata_caudata_associations import tertiles

SOURCE_MAIN_SHA = "5e2f0a87c639df373fa2700b29403d2ab417a1cc"
OLD_TRUE80_SOURCE_RUN = 41408471121
SITE_N = 4248
SURVEYS_N = 63180
ROUTES_N = 432
BLOCKS_N = 56
VEGETATED_N = 506
SOURCE_MODEL_BACKGROUNDS = 256
SOURCE_STAGE_CONTEXTS = 3
SURFACES = ("00", "11")
CORNERS = tuple((v,s,d) for v in (0,1) for s in (0,1) for d in (0,1))
MIN_SITES, MIN_ROUTES, MIN_BLOCKS, MIN_VISITS = 20,5,3,200


def require(v,msg):
    if not bool(v):
        raise AssertionError(msg)


def sha(file):
    return hashlib.sha256(Path(file).read_bytes()).hexdigest()


def predictor_basis(o,s,v):
    """Unrestricted multilinear basis; model F_B covariate cannot transcend it."""
    o=np.asarray(o,dtype=float)
    s=np.asarray(s,dtype=float)
    v=np.asarray(v,dtype=float)
    require(o.shape==s.shape==v.shape,"Source predictor dimensions changed")
    return np.column_stack((np.ones(len(o)),o,s,v,o*s,o*v,s*v,o*s*v))


def surface_interpolation(corners, o,s,v):
    """Exact trilinear interpolation of eight SOURCE log aquatic F_B means."""
    o=np.asarray(o,dtype=float)
    s=np.asarray(s,dtype=float)
    v=np.asarray(v,dtype=float)
    require(len(corners)==8 and set(corners)==set(CORNERS),
            "Not a legal complete source 2x2x2 response surface")
    require(np.isfinite([*o,*s,*v]).all() and
            np.all((o>=0)&(o<=1)) and np.all((s>=0)&(s<=1)) and
            np.isin(v,[0,1]).all(),"Original source rank and binary vegetation invalid")
    result=np.zeros(len(o),dtype=float)
    for (vv,ss,dd),value in corners.items():
        term=(v if vv else (1-v))*(s if ss else (1-s))*(o if dd else (1-o))
        result+=term*value
    return result


def original_site_source(sites_path,visits_path):
    sites=pd.read_csv(sites_path)
    visits=pd.read_csv(visits_path)
    d=prepare_sites(sites,visits,expected_sites=SITE_N)
    require(len(d)==SITE_N and d.site.is_unique and
            int(d.n.sum())==SURVEYS_N and
            int(d.k.sum())==36554 and
            int(d.V.sum())==VEGETATED_N and
            d.route.nunique()==ROUTES_N and
            d.spatial_block.nunique()==BLOCKS_N,
            "Original NAAMP 4248/63180 56-block field dataset changed")
    return d


def field_corner_support(d):
    rows=[]
    classified=[]
    for background in BACKGROUNDS:
        s_col="mean_suitability_pond_breeding_Caudata_"+background
        o_col="mean_suitability_Odonata_"+background
        s_bin,s_cut=tertiles(d[s_col].to_numpy(float))
        o_bin,o_cut=tertiles(d[o_col].to_numpy(float))
        require(set(s_bin)=={0,1,2} and set(o_bin)=={0,1,2},
                "Original predictor-only tertile definition has drifted")
        for v,ss,dd in CORNERS:
            selected=(d.V.eq(v).to_numpy() & (s_bin==ss*2) & (o_bin==dd*2))
            sub=d.loc[selected]
            row=dict(background=background,vegetation=v,caudata=ss,odonata=dd,
                     sites=int(len(sub)),routes=int(sub.route.nunique()),
                     geographic_blocks=int(sub.spatial_block.nunique()),
                     completed_visits=int(sub.n.sum()),strong_events=int(sub.k.sum()),
                     mean_strong_call_rate=float(sub.k.sum()/sub.n.sum()) if len(sub) else np.nan,
                     minimum_sites=MIN_SITES,minimum_routes=MIN_ROUTES,
                     minimum_blocks=MIN_BLOCKS,minimum_visits=MIN_VISITS)
            row["sufficient_geometry"]=bool(row["sites"]>=MIN_SITES and
                   row["routes"]>=MIN_ROUTES and
                   row["geographic_blocks"]>=MIN_BLOCKS and
                   row["completed_visits"]>=MIN_VISITS)
            rows.append(row)
        records=pd.DataFrame({
            "site":d.site.to_numpy(),"route":d.route.to_numpy(),
            "spatial_block":d.spatial_block.to_numpy(),
            "background":background,"vegetation":d.V.to_numpy(),
            "caudata_tertile":s_bin,"odonata_tertile":o_bin,
            "in_low_high_eight_corner":np.isin(s_bin,[0,2]) & np.isin(o_bin,[0,2]),
            "n_completed":d.n.to_numpy(dtype=int),
            "n_strong":d.k.to_numpy(dtype=int)
        })
        classified.append(records)
    result=pd.DataFrame(rows)
    sites=pd.concat(classified,ignore_index=True)
    require(len(result)==16 and len(sites)==SITE_N*2 and
            not sites.duplicated(["site","background"]).any(),
            "Missing complete source eight-corner real observation inventory")
    return result,sites


def synthetic_source_surfaces(archive):
    x=pd.read_csv(archive,dtype={"arm":str})
    required={"source_id","context_id","arm","draw_id","vegetation",
              "S_source","D_source","F_B"}
    require(required.issubset(x.columns) and len(x)==24576,
            "Not original PR161 24,576 synthetic eight-corner source vertices")
    require(x.source_id.nunique()==SOURCE_MODEL_BACKGROUNDS and
            x.context_id.nunique()==SOURCE_STAGE_CONTEXTS and
            set(x.arm)=={"00","10","01","11"},
            "Original synthetic model-background or stage source has changed")
    require(not x.duplicated(["draw_id","vegetation","S_source","D_source"]).any() and
            x.groupby("draw_id").size().eq(8).all() and
            np.isfinite(x.F_B).all() and (x.F_B>0).all(),
            "Source model is missing physical 2x2x2 output vertices")
    sources={}
    for arm in SURFACES:
        a=x[x.arm.eq(arm)].copy()
        a["s_idx"]=a.S_source.map({.25:0,2.:1})
        a["d_idx"]=a.D_source.map({.25:0,2.:1})
        require(a[["s_idx","d_idx"]].notna().all().all() and
                a.vegetation.isin([0,1]).all(),
                "PR161 original low/high predator source levels changed")
        a["log_F_B"]=np.log(a.F_B.to_numpy(dtype=float))
        means=a.groupby(["vegetation","s_idx","d_idx"]).agg(
            log_F_mean=("log_F_B","mean"),
            source_vertices=("log_F_B","size")
        ).reset_index()
        require(len(means)==8 and means.source_vertices.eq(
            SOURCE_MODEL_BACKGROUNDS*SOURCE_STAGE_CONTEXTS).all(),
            "Incomplete original 256x3 synthetic source-prior corner averaging")
        v={(int(r.vegetation),int(r.s_idx),int(r.d_idx)):float(r.log_F_mean)
           for r in means.itertuples(index=False)}
        require(set(v)==set(CORNERS),"Eight original predator source corners missing")
        sources[arm]=v
    return sources


def original_rank01(values):
    a=rankdata(np.asarray(values,dtype=float))
    result=(a-1)/(len(a)-1)
    require(result.min()>=0 and result.max()<=1,"Original field SDM rank conversion failed")
    return result


def check_empirical_redundancy(d,surfaces):
    rows=[]
    for bg in BACKGROUNDS:
        o=original_rank01(d["mean_suitability_Odonata_"+bg])
        s=original_rank01(d["mean_suitability_pond_breeding_Caudata_"+bg])
        v=d.V.to_numpy(dtype=int)
        X=predictor_basis(o,s,v)
        require(np.linalg.matrix_rank(X)==8,
                "Field original O/S/V unrestricted eight-term basis lacks full rank")
        for arm in SURFACES:
            model_signal=surface_interpolation(surfaces[arm],o,s,v)
            coef,*_=np.linalg.lstsq(X,model_signal,rcond=None)
            reconstructed=X@coef
            maxdiff=float(np.max(np.abs(reconstructed-model_signal)))
            require(maxdiff<=1e-9,
                    "A source model response contained information not spanned by O/S/V factorial terms")
            rows.append(dict(background=bg,model_plant_arm=arm,
                 original_site_count=len(d),basis_rank=int(np.linalg.matrix_rank(X)),
                 max_absolute_source_projection_residual=maxdiff,
                 mechanism_feature_adds_independent_linear_dimension=False,
                 source_interpolation="trilinear in field suitability rank O,S and binary landscape vegetation V",
                 wild_predator_density_measured=False))
    return pd.DataFrame(rows)


def run(sites,visits,vertices,out):
    d=original_site_source(sites,visits)
    corners,sites_long=field_corner_support(d)
    source=synthetic_source_surfaces(vertices)
    redundant=check_empirical_redundancy(d,source)
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    corners.to_csv(out/"G4_original_field_eight_corner_support.csv",index=False)
    sites_long.to_csv(out/"G4_all_4248_site_source_tertile_assignments.csv.gz",
                      index=False,compression={"method":"gzip","mtime":0})
    redundant.to_csv(out/"G4_source_surface_collinearity_audit.csv",index=False)
    surface_rows=[dict(arm=arm,vegetation=v,caudata=s,odonata=o,
                      mean_log_F_B=value,source_backgrounds=SOURCE_MODEL_BACKGROUNDS,
                      stage_repeats=SOURCE_STAGE_CONTEXTS)
             for arm,axis in source.items() for (v,s,o),value in sorted(axis.items())]
    pd.DataFrame(surface_rows).to_csv(out/"G4_predirected_source_priors_two_plant_arms.csv",index=False)
    gate=bool(corners.sufficient_geometry.all())
    receipt=dict(
        status="G4_ORIGINAL_FIELD_EIGHT_CORNER_AND_MODEL_SPAN_AUDIT_SUCCESS",
        original_main_SHA=SOURCE_MAIN_SHA,
        original_pr161_source_run=OLD_TRUE80_SOURCE_RUN,
        original_field_sites=SITE_N,original_survey_visits=SURVEYS_N,
        original_vegetated_sites=VEGETATED_N,original_routes=ROUTES_N,
        original_spatial_blocks=BLOCKS_N,
        observed_field_cells=len(corners),
        observed_cells_supported=int(corners.sufficient_geometry.sum()),
        both_SDM_backgrounds_all_eight_corners_supported=gate,
        observed_eight_corner_direct_sign_inference_allowed=gate,
        original_model_backgrounds=SOURCE_MODEL_BACKGROUNDS,
        original_model_stage_repeats=SOURCE_STAGE_CONTEXTS,
        original_model_arms_averaged=list(SURFACES),
        saturated_basis_contains_original_model_interpolated_surfaces=bool(
            redundant.max_absolute_source_projection_residual.le(1e-9).all()),
        independent_field_model_predation_causal_link_identified=False,
        ecological_predator_mechanism_model_comparison_fitted=False,
        requires_G5_out_of_block_prediction_and_actual_pond_predator_measurements=True,
        original_input_SHA256={Path(z).name:sha(z) for z in (sites,visits,vertices)}
    )
    (out/"G4_source_geometry_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("G4_FIELD_MODEL_OBSERVABLE_ALIGNMENT_AUDIT_SUCCESS",
          json.dumps({k:v for k,v in receipt.items() if k!="original_input_SHA256"}),flush=True)
    print("G4_ORIGINAL_FIELD_CORNER_SUPPORT\n"+
          corners.to_string(index=False),flush=True)
    print("G4_ORIGINAL_MODEL_EMPIRICAL_BASIS_REDUNDANCY\n"+
          redundant.to_string(index=False),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--sites",type=Path,required=True)
    p.add_argument("--visits",type=Path,required=True)
    p.add_argument("--vertices",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.sites,a.visits,a.vertices,a.out)
