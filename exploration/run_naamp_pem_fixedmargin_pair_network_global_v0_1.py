#!/usr/bin/env python3
"""Global PEM-conditioned frog pair-identity beyond site taxon-richness margins.

Source: USGS NAAMP 2001–15, response-blind NWI 250m wetland polygons, frozen
route-heldout NWI coefficients and original eligible frog-pair screen.
Ecological post-hoc analysis, NOT species interactions or vegetation causality.
"""
import argparse, hashlib, importlib.util, json, math, random
from collections import Counter
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
B=199; BURN=40; THIN=8; ROUTE_FLIPS=4999; SEED=26010471
MODES=(("any",3659,478,127),("strong",1766,398,57))
SPEC="exploration/NAAMP_PEM_FIXEDMARGIN_PAIR_IDENTITY_GLOBAL_SPEC_2026_10_23.md"

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise RuntimeError("Missing frozen NAAMP source "+str(path))
    o=importlib.util.module_from_spec(s);s.loader.exec_module(o);return o

def matrix(rows):
    x=np.zeros((len(rows),10),float)
    for i,s in enumerate(rows):
        if s:x[i,list(s)]=1.
    return x

def dyad(mat,pos,neg):
    a=mat[:,pos];b=mat[:,neg]
    return (a@a.T)/len(pos)-(b@b.T)/len(neg)

def richness_pairtotal(mat,sites):
    r=mat[:,sites].sum(axis=0)
    return float((r*(r-1)/2).sum()/len(sites))

def qa(prior):
    rows=[{0,1,2},{0,2,4},{1,3,5},{2,3,6},{0,5,7}]
    frozen=prior.fixed_margins(rows)
    original=matrix(rows)
    groups=(np.array([0,2,4]),np.array([1,3,5,6]))
    totals=[richness_pairtotal(original,g) for g in groups]
    rng=random.Random(SEED+1)
    changes=[]
    for it in range(800):
        prior.weighted_trade(rows,np.zeros((5,10)),rng)
        if it%16==0:
            x=matrix(rows)
            assert prior.fixed_margins(rows)==frozen
            for g,expected in zip(groups,totals):
                assert abs(richness_pairtotal(x,g)-expected)<1e-12
                assert abs(float(np.triu(x[:,g]@x[:,g].T,1).sum()/len(g))-expected)<1e-12
            changes.append(dyad(x,*groups)[0,1])
    assert np.ptp(changes)>.01
    return {"status":"PASS","fixed_species_and_site_margins":True,
            "total_all_taxon_pair_co_detection_by_PEM_fixed":True,
            "species_pair_identity_non_invariant":True,
            "synthetic_only_not_animal_outcomes":True}

def test_stat(obs,ndraw,counts,qual,route_scores,route_ids,fold_data,names,seed):
    sel=np.flatnonzero(qual)
    if len(sel)<20:raise RuntimeError("Fewer than 20 fully eligible dyadic species-pair labels")
    n=counts[sel]
    o=obs[sel]/n
    null=ndraw[sel]/n[:,None]
    expected=null.mean(axis=1)
    delta=o-expected
    T=float(np.mean(delta**2))
    loo=(null.sum(axis=1)[:,None]-null)/(B-1)
    null_T=np.mean((null-loo)**2,axis=0)
    mc_p=(1+int((null_T>=T-1e-15).sum()))/(B+1)
    score=route_scores[:,sel]
    if not np.allclose(score.sum(axis=0)/n,delta,atol=1e-9,rtol=0):
        raise RuntimeError("Physical-route residual aggregation does not conserve observed edge excess")
    rng=np.random.default_rng(seed)
    sign_geq=0;sign_total=0.
    for start in range(0,ROUTE_FLIPS,250):
        k=min(250,ROUTE_FLIPS-start)
        flip=rng.choice(np.array([-1.,1.]),size=(k,len(route_ids)))
        tested=(flip@score)/n
        stats=np.mean(tested**2,axis=1)
        sign_geq+=int((stats>=T-1e-15).sum())
        sign_total+=float(stats.sum())
    sign_p=(1+sign_geq)/(ROUTE_FLIPS+1)
    folds={}
    for f in ("A","B"):
        fobs,fnull,fc=fold_data[f]
        keep=fc[sel]>=10
        if int(keep.sum())<12:
            folds[f]={"status":"insufficient_original_pairs","n_edges":int(keep.sum())}
            continue
        a=fobs[sel][keep]/fc[sel][keep]
        v=fnull[sel][keep]/fc[sel][keep,None]
        d=a-v.mean(axis=1)
        fstat=float(np.mean(d**2))
        fmean=float(np.mean(((v-(v.sum(axis=1)[:,None]-v)/(B-1))**2).mean(axis=0)))
        folds[f]={"status":"descriptive","n_edges":int(keep.sum()),
                  "observed_T":fstat,"mean_null_T":fmean,
                  "above_null_mean":fstat>fmean,
                  "n_positive_conditional_edges":int((d>0).sum()),
                  "n_negative_conditional_edges":int((d<0).sum())}
    joint_edges=[]
    for i in sel:
        if fold_data["A"][2][i]>=10 and fold_data["B"][2][i]>=10:
            ar=fold_data["A"][0][i]/fold_data["A"][2][i]-fold_data["A"][1][i,:].mean()/fold_data["A"][2][i]
            br=fold_data["B"][0][i]/fold_data["B"][2][i]-fold_data["B"][1][i,:].mean()/fold_data["B"][2][i]
            joint_edges.append(bool(ar*br>0))
    top=sorted(range(len(sel)),key=lambda j:-abs(delta[j]))[:10]
    examples=[{"taxon_pair":list(names[sel[j]]),
               "n_same_route_night_mixed_survey_pairs":int(n[j]),
               "mean_observed_PEMminus_nonPEM":float(o[j]),
               "mean_crossfit_weighted_null_PEMminus_nonPEM":float(expected[j]),
               "mean_residual_PEM_context":float(delta[j]),
               "no_individual_edge_statistical_claim":True}
              for j in top]
    lag=float(np.corrcoef(null_T[:-1],null_T[1:])[0,1])
    if not math.isfinite(lag):lag=None
    return {"original_eligible_species_pair_labels":len(names),
      "included_original_labels_with_20_mixed_nights_10_routes_5_null_variable_nights":len(sel),
      "n_edges_positive":int((delta>0).sum()),
      "n_edges_negative":int((delta<0).sum()),
      "mean_signed_pair_network_excess":float(delta.mean()),
      "mean_absolute_pair_network_excess":float(np.mean(np.abs(delta))),
      "T_global_mean_squared_pair_identity_excess":T,
      "mean_null_T":float(null_T.mean()),
      "null_T_quantiles_2p5_50_97p5":[float(q) for q in np.quantile(null_T,[.025,.5,.975])],
      "ratio_observed_to_null_T_mean":T/float(null_T.mean()) if null_T.mean()>0 else None,
      "null_weighted_curveball_draws":B,
      "plus_one_upper_tail_p_weighted_curveball":mc_p,
      "null_T_lag_one_draw_correlation":lag,
      "whole_physical_route_vector_signflips":{
        "n_routes":len(route_ids),"n_draws":ROUTE_FLIPS,
        "plus_one_upper_tail_p":sign_p,
        "mean_signflip_null_T":sign_total/ROUTE_FLIPS,
        "entire_repeated_route_community_flipped_together":True,
        "symmetric_route_contributions_assumed_no_randomized_plant_intervention":True},
      "geographic_original_route_folds":folds,
      "route_fold_edge_sign_stability":{
        "n_preexisting_edge_labels_10plus_runs_per_fold":len(joint_edges),
        "n_matching_signs":int(sum(joint_edges)),
        "fraction_matching_signs":sum(joint_edges)/len(joint_edges) if joint_edges else None},
      "top_ten_descriptive_species_pairs_NOT_significance_tested":examples,
      "classification":("exploratory_global_PEM_conditioned_dyadic_pattern"
        if mc_p<=.05 and sign_p<=.05 and all(f.get("above_null_mean",False) for f in folds.values())
        else "not_supported_by_fixed_margin_and_route_cluster_gates")}

def mode_analysis(prior,records,ref,coefs,net,mode,n_runs,n_routes,n_edges):
    frozen=sorted([p for p in net["modes"][mode]["all_pairs"] if p.get("status")=="fitted"],
                   key=lambda r:r["pair_label"])
    if len(frozen)!=n_edges or net["modes"][mode]["coverage"]["n_eligible_species_pairs"]!=n_edges:
        raise RuntimeError("Original source pair eligibility drift")
    names=[tuple(p["pair"]) for p in frozen]
    ids={x:i for i,x in enumerate(names)}
    ref=ref.set_index("RunID")
    checked=sorted(set(records)&set(ref.index.astype(str)))
    routes=sorted({records[rid]["route"] for rid in checked})
    if len(checked)!=n_runs or len(routes)!=n_routes:
        raise RuntimeError("Original route-crossfitted NWI C-score sample drift")
    routeidx={name:i for i,name in enumerate(routes)}
    obs=np.zeros(n_edges,float);sim=np.zeros((n_edges,B),float)
    count=np.zeros(n_edges,dtype=int);variable=np.zeros(n_edges,dtype=int)
    used_routes=[set() for _ in range(n_edges)]
    fold={f:(np.zeros(n_edges,float),np.zeros((n_edges,B),float),np.zeros(n_edges,dtype=int)) for f in ("A","B")}
    routescore=np.zeros((len(routes),n_edges),float)
    checks=Counter();accept=[]
    for rid in checked:
        run=records[rid]
        names_here,rows=prior.ref_rows(run,mode)
        if len(names_here)<3 or not prior.exchangeable(rows):
            raise RuntimeError("Expected exchangeable 10-stop frog community")
        if not np.isclose(prior.cscore(rows),float(ref.loc[rid,"observed"]),atol=1e-8,rtol=0):
            raise RuntimeError("Frozen source RunID observation mismatch")
        checks["original_Cscore_matrices_validated"]+=1
        wet=np.asarray(run["v"][:,0])>0
        pem=np.asarray(run["v"][:,1])>0
        pos=np.flatnonzero(wet&pem);neg=np.flatnonzero(wet&~pem)
        if len(pos)<2 or len(neg)<2:
            checks["NWI_mapped_PEM_geography_ineligible"]+=1
            continue
        checks["NWI_mixed_geography_2plus_each"]+=1
        loc=[(i,j,ids[(names_here[i],names_here[j])])
             for i in range(len(names_here)) for j in range(i+1,len(names_here))
             if (names_here[i],names_here[j]) in ids]
        if not loc:
            checks["no_original_eligible_species_pairs_present"]+=1
            continue
        ii=np.array([a for a,b,k in loc],int)
        jj=np.array([b for a,b,k in loc],int)
        idx=np.array([k for a,b,k in loc],int)
        O=matrix(rows)
        o=dyad(O,pos,neg)[ii,jj]
        for group in (pos,neg):
            total=float(np.triu(O[:,group]@O[:,group].T,1).sum()/len(group))
            assert math.isclose(total,richness_pairtotal(O,group),abs_tol=1e-12)
        betas=np.stack([np.asarray(coefs[prior.complementary(run["fold"])].get(sp,{}).get(
                       "wetland_and_emergent",np.zeros(2)),float) for sp in names_here])
        if betas.shape!=(len(names_here),2):
            raise RuntimeError("Original heldout NWI taxon coefficients changed")
        score=betas@run["v"][:,[0,1]].T
        current=[set(s) for s in rows]
        fixed=prior.fixed_margins(current)
        seed=int.from_bytes(hashlib.sha256(f"{SEED}|{mode}|{rid}".encode()).digest()[:8],"big")
        rng=random.Random(seed)
        naccepted=nfeasible=0
        for _ in range(BURN*len(rows)):
            z,a=prior.weighted_trade(current,score,rng);nfeasible+=z;naccepted+=a
        draws=np.empty((len(loc),B))
        for k in range(B):
            for _ in range(THIN*len(rows)):
                z,a=prior.weighted_trade(current,score,rng);nfeasible+=z;naccepted+=a
            M=matrix(current)
            draws[:,k]=dyad(M,pos,neg)[ii,jj]
            if k in (0,B//2,B-1):
                if prior.fixed_margins(current)!=fixed:
                    raise RuntimeError("Fixed-margin weighted MCMC changed row/column totals")
                for group in (pos,neg):
                    assert math.isclose(richness_pairtotal(M,group),richness_pairtotal(O,group),abs_tol=1e-12)
        if not naccepted:raise RuntimeError("No accepted moves in matched amphibian matrix")
        accept.append(naccepted/nfeasible)
        obs[idx]+=o
        sim[idx,:]+=draws
        count[idx]+=1
        variable[idx]+=draws.var(axis=1)>1e-14
        f=run["fold"]
        fold[f][0][idx]+=o
        fold[f][1][idx,:]+=draws
        fold[f][2][idx]+=1
        routescore[routeidx[run["route"]],idx]+=o-draws.mean(axis=1)
        for edge in idx:used_routes[edge].add(run["route"])
        checks["NWI_mixed_pair_null_matrices_simulated"]+=1
        if checks["NWI_mixed_pair_null_matrices_simulated"]%250==0:
            print(f"{mode} plant-conditioned {checks['NWI_mixed_pair_null_matrices_simulated']} matrices of {n_runs} original route-nights, {B} weighted fixed-margin draws",flush=True)
    if checks["original_Cscore_matrices_validated"]!=n_runs:
        raise RuntimeError("Original community sample no longer matches")
    coverage=np.array([count[i]>=20 and len(used_routes[i])>=10 and variable[i]>=5
                       for i in range(n_edges)],bool)
    active_routes=sorted({route for i in np.flatnonzero(coverage) for route in used_routes[i]})
    if len(active_routes)<50:raise RuntimeError("Fewer than 50 physical routes in PEM network")
    location=np.array([routeidx[x] for x in active_routes],int)
    result=test_stat(obs,sim,count,coverage,routescore[location,:],active_routes,fold,names,SEED+(1 if mode=="any" else 2))
    result.update({"mode":mode,"original_reference_route_nights":n_runs,"original_reference_routes":n_routes,
       "NWI_PEM_two_vs_two_mixed_route_nights":checks["NWI_mixed_geography_2plus_each"],
       "simulated_mixed_route_nights_with_preexisting_labels":checks["NWI_mixed_pair_null_matrices_simulated"],
       "prelocked_pair_inclusion":{"min_mixed_coactive_nights":20,"min_routes":10,
                                   "min_matrices_variable_under_null":5},
       "excluded_previous_pair_labels_without_new_mixed_PEM_coverage":int(n_edges-coverage.sum()),
       "eligible_pair_run_counts_min_median_max":[float(x) for x in np.quantile(count[coverage],[0,.5,1])],
       "mean_accepted_feasible_weighted_trade_fraction":float(np.mean(accept)),
       "matrix_sample_QA_counts":dict(checks),
       "sum_of_all_taxon_pair_co_detection_conserved_by_fixed_site_richness":True})
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--previous-nwi",type=Path)
    p.add_argument("--outdir",type=Path,default=ROOT/"build/naamp_pem_fixedmargin_pair_network")
    p.add_argument("--synthetic-only",action="store_true")
    args=p.parse_args()
    prior=load("original_NWI_weighted_sampler",ROOT/"exploration/run_naamp_nwi_conditional_checkerboard_v0_1.py")
    quality=qa(prior)
    if args.synthetic_only:
        print(json.dumps(quality,sort_keys=True));return
    if args.previous_nwi is None:raise RuntimeError("Frozen original NWI coefficient artifact missing")
    original=load("existing_pair_screen",ROOT/"exploration/run_naamp_plant_conditioned_pair_network_v0_1.py")
    records,refs,coefs,source=original.prior_inputs(args.previous_nwi)
    if source["ten_stop_vegetation_plus_observation_runs"]!=6236:
        raise RuntimeError("Original NWI complete ten-stop source sample changed")
    network=json.loads((ROOT/"exploration/NAAMP_PLANT_CONDITIONED_FROG_PAIR_NETWORK_RESULT_V0_1.json").read_text())
    if network["analysis"]!="naamp_nwi_pair_identity_acoustic_network_v0_1":
        raise RuntimeError("Previous pair identity authority mismatch")
    results={}
    for mode,n_runs,n_routes,n_edges in MODES:
        results[mode]=mode_analysis(prior,records,refs[mode],coefs[mode],network,
                                    mode,n_runs,n_routes,n_edges)
    out={"analysis":"NAAMP_NWI_vegetation_pair_identity_global_fixed_margin_ecological_network",
         "status":"real_source_fixedmargin_PEM_conditioned_acoustic_pair_network_executed",
         "date":"2026-10-23","protocol":SPEC,
         "source_NWI_workflow":39450277196,
         "source_crossfit_NWI_model_workflow":39516056663,
         "NWI_10stop_complete_run_nights":6236,
         "post_hoc_motivated_by_positive_mapped_PEM_gamma":True,
         "mathematical_QA":quality,"modes":results,
         "inferential_limits":{
             "not_a_richness_contrast":True,
             "acoustic_co_detection_not_species_species_interaction":True,
             "direct_causal_plant_habitat_effect_not_identified":True,
             "NWI_not_historical_2001_2015_actual_plants":True,
             "frozen_crossfit_weights_trained_on_both_eras":True,
             "third_party_predator_and_fish_records_absent":True,
             "not_prediction":True,"JAE_RC6_main_SI_untouched":True}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("NAAMP_GLOBAL_PEM_PAIR_IDENTITY_BEGIN",flush=True)
    print(json.dumps({"status":out["status"],"mathematical_QA":quality,"modes":results},sort_keys=True,allow_nan=False),flush=True)
    print("NAAMP_GLOBAL_PEM_PAIR_IDENTITY_END",flush=True)

if __name__=="__main__":
    main()
