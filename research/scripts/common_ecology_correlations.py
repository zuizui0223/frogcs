#!/usr/bin/env python3
"""Compare REAL frog chorus phenology, stage-report overlap, and vegetation/hydrology correlations.

Read canonical original source-native site×date×taxon×stage events, never join
an audio station to a pond by a 1° grid, km proximity, or common scientificName.
All conclusions here are descriptive/post-readback. The original NPS, INBO,
Hungary and NAAMP sample denominators/source QA remain in the parent profile.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from datetime import date
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

CONTRACT="research/CANONICAL_SITE_TIME_STAGE_OBSERVATION_CONTRACT_V1.md"
SEED=20261026
FROG_PAIRS=["Bufo bufo","Epidalea calamita","Hyla arborea","Pelobates fuscus",
 "Pelophylax esculenta synklepton","Pelophylax kl. esculentus",
 "Pelophylax lessonae","Pelophylax lessonae/ kl. esculentus",
 "Pelophylax ridibundus","Rana arvalis","Rana temporaria"]
CAUDATA=("Ichthyosaura","Lissotriton","Triturus","Salamandra","Ambystoma")
FROGS_HUN=("Pelobates fuscus","Rana dalmatina","Bombina bombina",
           "Hyla arborea","Pelophylax ridibundus","Bufotes viridis","Bufo bufo")

def safe_float(x):
    try:return float(x) if math.isfinite(float(x)) else None
    except(TypeError,ValueError):return None

def spearman_stat(x,y):
    a=np.asarray(x,float);b=np.asarray(y,float)
    valid=np.isfinite(a)&np.isfinite(b)
    a=a[valid];b=b[valid]
    if len(a)<8 or len(set(a))<2 or len(set(b))<2:return None
    r=spearmanr(a,b).statistic
    return float(r) if math.isfinite(r) else None

def cluster_interval(frame,xcol,ycol,groupcol,reps=2000):
    grp={k:z for k,z in frame.groupby(groupcol,sort=True)}
    keys=sorted(grp)
    if len(keys)<8:return {"estimable":False,"reason":"Under 8 independent source location groups"}
    rng=np.random.default_rng(SEED+len(frame)+len(keys))
    bs=[]
    for i in range(reps):
        selected=rng.choice(keys,size=len(keys),replace=True)
        x=[];y=[]
        for k in selected:
            g=grp[k]
            x.extend(g[xcol].tolist());y.extend(g[ycol].tolist())
        rho=spearman_stat(x,y)
        if rho is not None:bs.append(rho)
    return {
        "estimable":len(bs)>=1000,
        "source_site_groups":len(keys),
        "conditional_site_bootstrap_valid_reps":len(bs),
        "conditional_site_bootstrap_CI95":[float(z) for z in np.quantile(bs,[.025,.975])] if len(bs)>=1000 else None,
        "random_seed":SEED
    }

def correlation(frame,xcol,ycol,groupcol,description,bootstrap=True):
    n=len(frame);rho=spearman_stat(frame[xcol],frame[ycol])
    res={"description":description,"n_site_or_siteyears":int(n),
         "independent_sites":int(frame[groupcol].nunique()),
         "spearman_rho":rho,
         "statistic_is_exploratory_observational":True}
    if rho is None:
        res["status"]="NONESTIMABLE_CONSTANT_OR_SMALL"
    else:
        res["status"]="DESCRIPTIVE_ESTIMABLE"
        if bootstrap:
            res["site_cluster_uncertainty"]=cluster_interval(frame,xcol,ycol,groupcol)
    return res

def partial_rank_correlation_site(frame, response, factor, controls, category):
    """Rank-residualized association after fixed source wetland class and abiotic/effort covariates.

    This is a descriptive source-29-wetland sensitivity and deliberately not
    a partial causal effect of dynamic macrophyte architecture.
    """
    d=frame.dropna(subset=[response,factor]+controls+[category]).copy()
    n=len(d)
    if n<15:return {"status":"NONESTIMABLE_TOO_FEW_SOURCE_SITES","n":n}
    x=rankdata(pd.to_numeric(d[factor]).to_numpy(dtype=float))
    y=rankdata(pd.to_numeric(d[response]).to_numpy(dtype=float))
    mats=[np.ones(n)]
    for ctrl in controls:
        vec=pd.to_numeric(d[ctrl]).to_numpy(dtype=float)
        if not np.isfinite(vec).all():return{"status":"NONESTIMABLE_MISSING_COVARIATES"}
        mats.append(rankdata(vec))
    cls=sorted(set(d[category].astype(str)))
    for level in cls[1:]:
        mats.append(np.array((d[category].astype(str)==level),dtype=float))
    Z=np.stack(mats,axis=1)
    if np.linalg.matrix_rank(Z)<len(mats):
        return {"status":"NONESTIMABLE_RANK_DEFICIENT","n":n}
    xres=x-Z@np.linalg.lstsq(Z,x,rcond=None)[0]
    yres=y-Z@np.linalg.lstsq(Z,y,rcond=None)[0]
    if np.std(xres)<1e-8 or np.std(yres)<1e-8:
        return {"status":"NONESTIMABLE_AFTER_CONDITIONING"}
    return {
        "status":"DESCRIPTIVE_ADJUSTED_RANK_ASSOCIATION",
        "n_independent_original_wetlands":n,
        "rank_residualized_pearson_r":float(np.corrcoef(xres,yres)[0,1]),
        "fixed_nuisances":[*controls,category],
        "note":"Postreadback descriptive partial rank; 29 single-year sites, no within-site plant changes or stem structure"
    }

def hunt_hungary(raw):
    d=raw[raw.source_id=="hungary_2024"].copy()
    if d.empty:return {"status":"UNAVAILABLE"}
    d["present"]=(d.status=="recorded_present").astype(int)
    a=d[(d.survey_method=="acoustic")&(d.taxon.isin(FROGS_HUN))].copy()
    v=d[(d.survey_method=="visual")&(d.taxon.isin(FROGS_HUN))].copy()
    assert a.source_event_token.nunique()==129
    def per_pond(source):
        events=source.groupby(["site_token","source_event_token","date"],as_index=False).agg(
          any_frog=("present","max"),
          n_called_frog_species=("present","sum"),
          avg_source_precip=("precip_source_value","first"),
          depth=("water_depth_source_value","first"),
          emerged=("emergent_cover_percent","first"),
          submerged=("submerged_cover_percent","first"),
          management=("site_management_class","first"),
          fish=("fish_source_observed","first"),
          month=("month","first"))
        pond=events.groupby("site_token",as_index=False).agg(
          frog_detect_fraction=("any_frog","mean"),
          max_called_species_at_single_visit=("n_called_frog_species","max"),
          mean_called_species_per_visit=("n_called_frog_species","mean"),
          measured_water_depth=("depth","first"),
          emergent_percent=("emerged","first"),
          submerged_percent=("submerged","first"),
          mean_spring_source_precip=("avg_source_precip","mean"),
          fish=("fish","first"),
          management=("management","first"),
          n_audio_visits=("source_event_token","nunique"))
        return events,pond
    audio_ev,pond=per_pond(a)
    visual_ev,visual_pond=per_pond(v)
    result={"status":"MEASURED_WETLAND_ACOUSTIC_CORRELATION_EXPLORATORY",
      "original_site_count":len(pond),"acoustic_visit_count":len(audio_ev),
      "one_year_only":2024,
      "acoustic_site_fraction_range":[float(pond.frog_detect_fraction.min()),float(pond.frog_detect_fraction.max())],
      "fish_recorded_site_count":int((pond.fish.astype(str).isin(["1","1.0"])).sum()),
      "emergent_cover_is_static_site_percent_not_sprouting_time":True,
      "water_depth_unit_is_source_unknown":True,
      "precip_unit_is_source_unknown":True,
      "correlations":{},
      "month_acoustic_fraction":[],
      "source_methods_cannot_be_pooled_as_the_same_detection_endpoint":True}
    for x,desc in [
      ("measured_water_depth","depth observed at site vs fraction of adult acoustic surveys positive"),
      ("emergent_percent","static emergent plant percent vs acoustic frog-positive fraction"),
      ("submerged_percent","static submerged plant percent vs acoustic frog-positive fraction"),
      ("mean_spring_source_precip","mean recorded spring precip value at visits vs acoustic frog-positive fraction"),
    ]:
      result["correlations"][x]=correlation(pond,x,"frog_detect_fraction","site_token",desc)
    vis=visual_pond.set_index("site_token")["frog_detect_fraction"]
    join=pond.assign(visual_positive_fraction=pond.site_token.map(vis)).dropna(subset=["visual_positive_fraction"])
    result["acoustic_vs_visual_site_fraction_correlation"]=correlation(
       join,"frog_detect_fraction","visual_positive_fraction","site_token",
       "Different sampling methods, not identical true animal populations")
    for mon,g in audio_ev.groupby("month"):
      result["month_acoustic_fraction"].append({"month":int(mon),"visits":len(g),
                "distinct_wetlands":int(g.site_token.nunique()),
                "acoustic_positive_fraction":float(g.any_frog.mean()),
                "mean_frog_species_per_audio_survey":float(g.n_called_frog_species.mean())})
    result["emergent_plant_partial_acoustic_rank_after_depth_rain_class_effort"]=partial_rank_correlation_site(
        pond,"frog_detect_fraction","emergent_percent",
        ["measured_water_depth","mean_spring_source_precip","n_audio_visits"],"management")
    first_audio=audio_ev.loc[audio_ev.any_frog>0].copy()
    first_audio["doy"]=pd.to_datetime(first_audio.date).dt.dayofyear
    first_dates=first_audio.groupby("site_token",as_index=False).agg(
         first_positive_acoustic_DOY=("doy","min"))
    timing=pond.merge(first_dates,on="site_token",how="inner",validate="one_to_one")
    result["emergent_static_cover_vs_first_observed_call_day"]=correlation(
        timing,"emergent_percent","first_positive_acoustic_DOY","site_token",
        "Static emergent percent vs first POSITIVELY RECORDED chorus survey day; not plant sprouting and not species first actual breeding date")
    result["source_plant_phenophase_not_measured"]=True
    result["fish_x_emergent_shelter_effect_estimable"]=False
    result["fish_habitat_reason"]="Only 2/29 field wetland sites have fish reported: site-level intervention is extremely sparse"
    return result

def hunt_nps(raw):
    z=raw[raw.source_id=="nps_glkn"].copy()
    if z.empty:return{"status":"UNAVAILABLE"}
    z["score"]=pd.to_numeric(z.score,errors="coerce")
    z=z.loc[z.score.isin([0,1,2,3])].copy()
    z["strong"]=(z.score>=2).astype(int)
    per_audio=z.groupby(["site_token","source_event_token","year","month","date"],as_index=False).agg(
       n_species_scored=("taxon","nunique"),
       n_species_strong=("strong","sum"),
       hydroperiod=("source_hydroperiod","first"))
    enough=per_audio.loc[per_audio.n_species_scored>=5].copy()
    enough["multispecies_strong"]=(enough.n_species_strong>=2).astype(int)
    site=enough.groupby("site_token",as_index=False).agg(
       recordings=("source_event_token","nunique"),
       multi_strong_fraction=("multispecies_strong","mean"),
       hydroperiod=("hydroperiod","first"))
    mapping={"Ephemeral":0,"Semi-permanent":1,"Permanent":2}
    site["water_persistence_order"]=site.hydroperiod.map(mapping)
    elig=site.dropna(subset=["water_persistence_order"])
    seasonal=[]
    for (hyd,mon),g in enough.groupby(["hydroperiod","month"]):
        seasonal.append({"hydroperiod":str(hyd),"month":int(mon),
                         "source_audio_files":len(g),
                         "source_sites":int(g.site_token.nunique()),
                         "fraction_audio_with_atleast2_simultaneous_CI2":float(g.multispecies_strong.mean())})
    month=sorted(seasonal,key=lambda a:(a["hydroperiod"],a["month"]))
    return {
       "status":"OBSERVED_MULTI_TAXON_SAME_AUDIO_CHORUS_PHENOLOGY",
       "original_species_audio_rows":len(z),
       "unique_original_soundfile_events":len(per_audio),
       "audio_events_with_5plus_species_scored":len(enough),
       "physical_acoustic_stations":int(enough.site_token.nunique()),
       "source_hydroperiod_known_site_groups":len(elig),
       "site_multi_species_strong_fraction_vs_hydroperiod_order_correlation":correlation(
           elig,"water_persistence_order","multi_strong_fraction","site_token",
           "Static source broad water-persistence class vs fraction of same-source audio with ≥2 taxa CI≥2"),
       "month_by_broad_hydroperiod":month,
       "life_stage":"adult_acoustic_only",
       "simultaneous_same_soundfile_co_chorus_not_larval_overlap":True,
       "effort_gate":"Only source soundfiles with >=5 distinct manually scored species included; no frog absent imputation at unknown source"
    }

def phi_binary(x,y):
    x=np.asarray(x,int);y=np.asarray(y,int)
    if len(x)<8 or len(set(x))<2 or len(set(y))<2:return None
    return float(np.corrcoef(x,y)[0,1])

def hunt_inbo(raw):
    c=raw[raw.source_id=="inbo_adult_chorus"].copy()
    l=raw[raw.source_id=="inbo_larval_census"].copy()
    if c.empty or l.empty:return{"status":"UNAVAILABLE"}
    a=c[(c.taxon=="Hyla arborea")&(c.stage=="adult_acoustic")&
        c.status.isin(["recorded_present","recorded_absent"])].copy()
    b=l[(l.taxon=="Hyla arborea")&(l.stage=="aquatic_immature")&
        l.status.isin(["recorded_present","recorded_absent"])].copy()
    c["positive"]=c.status.eq("recorded_present")
    a["positive"]=a.status.eq("recorded_present")
    b["positive"]=b.status.eq("recorded_present")
    a["dt"]=pd.to_datetime(a.date)
    b["dt"]=pd.to_datetime(b.date)
    # Event-level source sites and calendar-years are common within published
    # locationID namespace. Do not spatially infer same actual single pond.
    chorus_by=defaultdict(list)
    for row in a.itertuples(index=False):
        chorus_by[(row.site_token,int(row.year))].append((row.dt,bool(row.positive),row.source_event_token))
    larva_by=defaultdict(list)
    for row in b.itertuples(index=False):
        larva_by[(row.site_token,int(row.year))].append((row.dt,bool(row.positive),row.source_event_token))
    other=c[(c.taxon.isin(FROG_PAIRS))&c.status.eq("recorded_present")&
            (c.taxon!="Hyla arborea")].copy()
    other_by=defaultdict(list)
    for row in other.itertuples(index=False):
        other_by[(row.site_token,int(row.year))].append((pd.Timestamp(row.date),row.taxon))
    pair_rows=[]; positive_lags=[]
    for key in sorted(set(chorus_by)&set(larva_by)):
        adult=sorted(chorus_by[key])
        larvae=sorted(larva_by[key])
        eligible=None
        for dt,st,eid in larvae:
            prior=[x for x in adult if x[0]<dt]
            if prior:
                eligible=(dt,st,eid,prior);break
        if eligible is None:continue
        dt,larval_present,eid,prior=eligible
        past_positive=int(any(x[1] for x in prior))
        potential_competitor_labels={taxon for day,taxon in other_by.get(key,[]) if day<dt}
        if larval_present and past_positive:
            positives=[day for day,flag,ev in prior if flag]
            if positives:
                positive_lags.append(int((dt-min(positives)).days))
        pair_rows.append({"site_token":key[0],"year":int(key[1]),
            "later_Hyla_larva_present":int(larval_present),
            "earlier_Hyla_chorus_present":past_positive,
            "prior_other_anuran_chorus_richness":len(potential_competitor_labels),
            "days_last_adult_survey_to_larva":int((dt-max(z[0] for z in prior)).days),
            "prior_adult_surveys":len(set(z[2] for z in prior)),
            "larval_census_DOY":int(dt.dayofyear)})
    frame=pd.DataFrame(pair_rows)
    cont={}
    for x in (0,1):
      for y in (0,1):
        cont[f"prior_chorus_{x}|later_larva_{y}"]=int(((frame.earlier_Hyla_chorus_present==x)&
              (frame.later_Hyla_larva_present==y)).sum())
    hx=frame.earlier_Hyla_chorus_present.astype(int).to_numpy()
    hy=frame.later_Hyla_larva_present.astype(int).to_numpy()
    phi=phi_binary(hx,hy)
    if len(frame)<10:raise ValueError("Cross-stage pairing unexpectedly empty")
    othercorr=correlation(frame,"prior_other_anuran_chorus_richness","later_Hyla_larva_present",
       "site_token","Previously acoustically reported other anuran species richness vs later focal larva detection; NOT underwater competitor density")
    n_exposure=int((frame.prior_other_anuran_chorus_richness>0).sum())
    othercorr["site_years_with_any_other_frog_chorus_reported"]=n_exposure
    othercorr["effective_competition_hypothesis_estimable"]=n_exposure>=10
    if n_exposure<10:
        othercorr["scientific_decision"]="SPARSE_EXPOSURE_ONLY_SIX_SITEYEARS_DO_NOT_CLAIM_ENEMY_RELEASE_CORRELATION"
        othercorr["raw_rank_correlation_exploratory_diagnostic_only"]=True
    # Additional phenological overlap of the larval stages from different
    # species: first positive observation by the same source location-year.
    # Frequently the same sampling visit is responsible for both, so this
    # is NOT true biological developmental synchrony.
    cpos=l[(l.stage=="aquatic_immature")&l.taxon.str.startswith(CAUDATA)&
             (l.status=="recorded_present")].copy()
    hpos=l[(l.stage=="aquatic_immature")&(l.taxon=="Hyla arborea")&
             (l.status=="recorded_present")].copy()
    cpos["date_parsed"]=pd.to_datetime(cpos.date)
    hpos["date_parsed"]=pd.to_datetime(hpos.date)
    cfirst=cpos.groupby(["site_token","year"],as_index=False).agg(
        first_other_caudata_larva=("date_parsed","min"))
    hfirst=hpos.groupby(["site_token","year"],as_index=False).agg(
        first_Hyla_larva=("date_parsed","min"))
    both_first=hfirst.merge(cfirst,on=["site_token","year"],how="inner",validate="one_to_one")
    signed=(both_first.first_other_caudata_larva-both_first.first_Hyla_larva).dt.days
    abs_days=np.abs(signed.to_numpy(dtype=float))
    paired_stage_first={
        "same_original_location_years_with_both_positive_stage_records":len(both_first),
        "first_larva_positive_dates_equal_count":int((abs_days==0).sum()),
        "first_larva_record_absolute_day_diff_median":float(np.median(abs_days)) if len(abs_days) else None,
        "first_larva_record_abs_day_diff_iqr":
            [float(x) for x in np.quantile(abs_days,[.25,.75])] if len(abs_days) else None,
        "reported_within_7_days":int((abs_days<=7).sum()),
        "reported_within_30_days":int((abs_days<=30).sum()),
        "shared_protocol_survey_schedule_may_explain_date_overlap":True,
        "actual_gosner_stage_size_or_cross_species_developmental_rate_measured":False
    }
    # Deliberately predeclared pseudo-predator guild: same source event
    # Caudata larva can be an aquatic competitor, prey or predator; no diet
    # relationship is claimed and a missing row ≠ absent.
    e=l[l.stage=="aquatic_immature"].copy()
    e["present"]=e.status.eq("recorded_present")
    e["valid"]=e.status.isin(["recorded_present","recorded_absent"])
    e=e.loc[e.valid]
    audit={}
    for event, group in e.groupby("source_event_token"):
        focal=group[group.taxon=="Hyla arborea"]
        cdat=group[group.taxon.str.startswith(CAUDATA)]
        if focal.empty or cdat.empty:continue
        k=(int(focal.present.max()),int(cdat.present.max()))
        audit[event]=k
    ct=Counter(audit.values())
    q=[(v[0],v[1]) for v in audit.values()]
    cphi=phi_binary([z[0] for z in q],[z[1] for z in q]) if q else None
    return {
      "status":"INBO_SAME_SOURCE_LOCATION_STAGE_CORRELATION_EXPLORATORY",
      "same_species_exact_site_year_pairs":len(frame),
      "different_unique_original_sites":int(frame.site_token.nunique()),
      "contingency_strict_adult_prior_to_first_larva":{
        "cell_counts":cont,"phi":phi,"direction":"past recorded adult calling vs later explicitly assessed larva, not reproduction success",
        "risk_difference":float(frame.loc[frame.earlier_Hyla_chorus_present==1,
                                          "later_Hyla_larva_present"].mean()
              -frame.loc[frame.earlier_Hyla_chorus_present==0,
                                          "later_Hyla_larva_present"].mean()) if len(set(hx))==2 else None
      },
      "other_anuran_adult_chorus_richness_vs_next_focal_larva":othercorr,
      "two_species_larval_first_positive_survey_date_phase_comparison":paired_stage_first,
      "documented_other_anuran_prior_chorus_richness_distribution":
        dict(Counter(frame.prior_other_anuran_chorus_richness)),
      "positive_adult_to_positive_larva_report_lags":{
         "eligible_source_site_years":len(positive_lags),
         "median_days":float(np.median(positive_lags)) if positive_lags else None,
         "iqr_days":[float(z) for z in np.quantile(positive_lags,[.25,.75])] if positive_lags else None,
         "within_7_days":sum(z<=7 for z in positive_lags),
         "within_14_days":sum(z<=14 for z in positive_lags),
         "within_30_days":sum(z<=30 for z in positive_lags),
         "within_60_days":sum(z<=60 for z in positive_lags),
         "warning":"Detected dates of different stage records; not individual Gosner development speed or proven egg→larva cohorts"},
      "Hyla_larval_source_event_with_explicit_Caudata_larval_assessment":{
         "event_count":len(audit),
         "two_by_two":{f"focal_Hyla_{a}|other_Caudata_{b}":int(ct[(a,b)]) for a in (0,1) for b in (0,1)},
         "phi_binary_co_detection":cphi,
         "caudata_not_diet_qualified_true_predator":True,
         "same_event_not_synchronous_actual_feeding":True
      },
      "source_missing_physical_pond_confirmed":True,
      "source_monthly_phenology_reporting_by_stages":month_counts(c,l),
      "stage_community_co_presence_not_species_interactions":True
    }

def month_counts(c,l):
    res=[]
    for tag,df in [("source_adult_chorus",c),("source_larval_census",l)]:
        g=df[(df.taxon=="Hyla arborea")&
             df.status.isin(["recorded_present","recorded_absent"])].copy()
        for (st,mon),part in g.groupby(["stage","month"]):
            res.append({"protocol":tag,"stage":st,"month":int(mon),
                        "assessed_records":int(len(part)),
                        "recorded_present":int(part.status.eq("recorded_present").sum()),
                        "recorded_absent":int(part.status.eq("recorded_absent").sum())})
    return sorted(res,key=lambda z:(z["protocol"],z["stage"],z["month"]))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--from-units",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if not args.from_units.is_file():raise ValueError("Canonical common native source events absent")
    raw=pd.read_csv(args.from_units,low_memory=False)
    profile=json.loads((args.from_units.parent/"observed_profile.json").read_text(encoding="utf8"))
    for source in ("hungary","inbo","nps"):
        if profile["sources"][source]["status"]!="SOURCE_AUTHENTICATED_CROSSWALK_BUILT":
            raise ValueError("Pinned authentic source failed: "+source)
    reports={
      "analysis_protocol":CONTRACT,
      "status":"OBSERVATIONAL_CORRELATIONS_COMPUTED_POSTHOC_NO_JOINT_CAUSAL_G2",
      "site_key_provenance":"source-namespaced hashed original wetland or recorder identifiers",
      "source_site_year_month_primary_grain":True,
      "correlations":{
        "Hungary_real_water_and_static_emergent_vegetation_vs_acoustic":hunt_hungary(raw),
        "NPS_same_original_soundfile_multitaxon_chorus_vs_hydroperiod":hunt_nps(raw),
        "INBO_original_event_exact_location_phenology_and_other_species":hunt_inbo(raw),
      },
      "wetland_macrophyte_sprouting_dates_measured":False,
      "wetland_plant_stem_height_density_and_actual_predation_refuge_measured":False,
      "frog_RC6_rain_concentration_caused_by_aquatic_predators_identified":False,
      "GBIF_reports_used_as_source_potential_stage_not_local_absence":True,
      "joint_physical_pond_egg_survival_predator_size_water_drying_dataset_qualified":False,
      "cross_study_effects_pooled_as_same_estimand":False,
      "interpretation_note":"Within-source co-reporting/rank correlations, not field trophic causation; local rain and vegetation observations are incomplete and not shared with NPS or NAAMP acoustic stops.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(reports,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BEGIN_FROGCS_COMMON_UNIT_REAL_CORRELATIONS")
    print(json.dumps(reports,ensure_ascii=False,indent=2))
    print("END_FROGCS_COMMON_UNIT_REAL_CORRELATIONS")

if __name__=="__main__":
    main()
