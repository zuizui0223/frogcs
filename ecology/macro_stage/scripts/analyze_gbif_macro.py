#!/usr/bin/env python3
"""15-region macro ecological stage-phenology window audit from original GBIF facets.

One shared iNaturalist GBIF publisher is primary. All-dataset source is only
an observation-method sensitivity. No actual predation or pond co-occurrence
observed. No NAAMP source data read.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from ecology.macro_stage.scripts.run_gbif_region import REGIONS, STAGES, COMMON_INAT_GBIF_DATASET

GUILDS={
 "frog_egg":("frog_egg",),
 "frog_larva":("frog_larva","frog_tadpole"),
 "salamander_egg":("salamander_egg",),
 "salamander_larva":("salamander_larva",),
 "odonate_larva":("odonate_larva","odonate_nymph"),
 "odonate_adult":("odonate_adult","odonate_imago"),
}
TAXON_ALL={
 "frog_egg":"all_frog","frog_larva":"all_frog",
 "salamander_egg":"all_salamander","salamander_larva":"all_salamander",
 "odonate_larva":"all_odonate","odonate_adult":"all_odonate"
}
EDGES=[
 ("frog_larva","salamander_egg","frog_larva__salamander_egg"),
 ("salamander_larva","frog_larva","salamander_larva__frog_larva"),
 ("odonate_larva","frog_larva","odonate_larva__frog_larva")
]
MIN_STAGE_RECORDS=30
MIN_ACTIVE_MONTHS=2

def overlap(p,q):
    pp=np.asarray(p,dtype=float);qq=np.asarray(q,dtype=float)
    if pp.shape!=(12,) or qq.shape!=(12,) or not np.isfinite(pp).all() or not np.isfinite(qq).all():
        raise ValueError("need complete 12-month distributions")
    if abs(pp.sum()-1)>1e-8 or abs(qq.sum()-1)>1e-8:
        raise ValueError("not normalized")
    return float(np.minimum(pp,qq).sum())

def season(count,effort):
    count=np.asarray(count,float);effort=np.asarray(effort,float)
    if count.shape!=(12,) or effort.shape!=(12,) or np.any(count<0) or np.any(effort<count):
        raise ValueError("stage-month counts inconsistent with all-order source")
    n=count.sum()
    if n==0:return None,None
    raw=count/n
    # This is ONLY a sensitivity: sparse months get Jeffreys regularization.
    corrected=(count+.5)/(effort+1.)
    adjusted=corrected/corrected.sum()
    return raw,adjusted

def read_region(path,scope):
    j=json.loads(Path(path).read_text())
    region=j.get("region")
    if region not in REGIONS or j.get("source_restriction","all_publishers")!=scope:
        raise ValueError("wrong region or matched-source scope")
    if scope=="shared_iNaturalist_dataset" and j.get("dataset_key")!=COMMON_INAT_GBIF_DATASET:
        raise ValueError("not the fixed publisher")
    source=j.get("records",[])
    by={x["stage_key"]:x for x in source}
    if set(by)!={x[0] for x in STAGES}:raise ValueError("missing stage source query")
    if len({r["provenance"]["url"] for r in source})!=len(source):
        raise ValueError("duplicate GBIF query URL")
    for r in source:
        if len(r["month_counts"])!=12 or sum(r["month_counts"])!=r["n_with_month"]:
            raise ValueError("month-to-source count mismatch")
        if r["n_with_month"]>r["n_all_stage_query"]:
            raise ValueError("invalid source query count")
        if len(r["provenance"]["source_sha256"])!=64:
            raise ValueError("missing GBIF response hash")
        if scope=="shared_iNaturalist_dataset" and f"datasetKey={COMMON_INAT_GBIF_DATASET}" not in r["provenance"]["url"]:
            raise ValueError("GBIF source query not actually restricted to shared publisher")
    return j,by

def audit_dataset(files,scope):
    rows=[];stages=[];sources=[]
    region_seen=set()
    for fname in sorted(files):
        j,r=read_region(fname,scope)
        region=j["region"]
        if region in region_seen:raise ValueError("duplicate region")
        region_seen.add(region)
        stage_values={}
        for guild,members in GUILDS.items():
            n=np.array([r[x]["month_counts"] for x in members],float).sum(axis=0)
            all_o=np.asarray(r[TAXON_ALL[guild]]["month_counts"],float)
            raw,adj=season(n,all_o)
            ok=n.sum()>=MIN_STAGE_RECORDS and (n>0).sum()>=MIN_ACTIVE_MONTHS
            stage_values[guild]=(n,raw,adj,ok)
            stages.append({"region":region,"country":j["country"],
                "lat_midpoint":(j["lat_min"]+j["lat_max"])/2,
                "guild_stage":guild,"n_records_with_month":int(n.sum()),
                "n_nonempty_months":int((n>0).sum()),"eligible":bool(ok),
                "modal_month":int(n.argmax()+1) if n.sum() else None,
                "year_range":"2015–2025",
                "source_scope":scope,"stage_observations_not_individuals":True})
        for a,b,edge in EDGES:
            na,pa,aa,oka=stage_values[a];nb,pb,ab,okb=stage_values[b]
            row={"region":region,"country":j["country"],"latitude_midpoint":(j["lat_min"]+j["lat_max"])/2,
                "edge":edge,"a_guild":a,"b_guild":b,"n_a":int(na.sum()),"n_b":int(nb.sum()),
                "eligible":bool(oka and okb),"source_scope":scope,
                "not_direct_interaction":True,"not_same_pond_observations":True}
            if row["eligible"]:
                shifts=[overlap(pa,np.roll(pb,shift)) for shift in range(12)]
                row.update(overlap_month_normalized=round(overlap(pa,pb),6),
                    overlap_order_effort_adjusted=round(overlap(aa,ab),6),
                    mean_circularly_rotated_overlap=round(float(np.mean(shifts)),6),
                    overlap_excess_over_mean_rotation=round(overlap(pa,pb)-float(np.mean(shifts)),6),
                    best_shift_months=int(np.argmax(shifts)),
                    overlap_peak_ratio_to_best_shift=round(shifts[0]/max(shifts),6) if max(shifts) else None)
            rows.append(row)
        sources.append({"region":region,"source_scope":scope,"queries":len(r),
            "source_urls_sha256":[r[x]["provenance"]["source_sha256"] for x in sorted(r)],
            "record_count_by_query":{x:r[x]["n_all_stage_query"] for x in sorted(r)}})
    if set(region_seen)!=set(REGIONS):
        raise RuntimeError("15-region macro source incomplete: missing "+str(set(REGIONS)-region_seen))
    return rows,stages,sources

def cross_source_mismatch(primary,mixed):
    mix={(x["region"],x["edge"]):x for x in mixed}
    matched=[]
    for x in primary:
        y=mix.get((x["region"],x["edge"]))
        if y is None:raise ValueError("missing all-source sensitivity region")
        a=dict(x);a["mixed_source_eligible"]=y["eligible"]
        a["mixed_source_raw_overlap"]=y.get("overlap_month_normalized")
        if x["eligible"] and y["eligible"]:
            a["shared_minus_mixed_overlap"]=round(x["overlap_month_normalized"]-y["overlap_month_normalized"],6)
        matched.append(a)
    return matched

def summary(rows):
    by=defaultdict(list)
    for x in rows:
        if x["eligible"]:by[x["edge"]].append(x)
    result={}
    for edge in (x[2] for x in EDGES):
        group=by[edge]
        result[edge]={
            "regions_with_both_stages_ge30":len(group),
            "overlap_month_normalized_equal_region_mean":round(float(np.mean([r["overlap_month_normalized"] for r in group])),5) if group else None,
            "overlap_effort_adjusted_equal_region_mean":round(float(np.mean([r["overlap_order_effort_adjusted"] for r in group])),5) if group else None,
            "regions_where_actual_time_alignment_gt_mean_shift":sum(x["overlap_excess_over_mean_rotation"]>0 for x in group),
            "region_values":[{"region":x["region"],"nA":x["n_a"],"nB":x["n_b"],
                 "raw_overlap":x["overlap_month_normalized"],
                 "effort_adjusted_overlap":x["overlap_order_effort_adjusted"],
                 "minus_month_rotation_mean":x["overlap_excess_over_mean_rotation"]} for x in group]}
    return result

def write_csv(path,rows):
    all_cols=list(dict.fromkeys(k for x in rows for k in x.keys()))
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=all_cols)
        w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--shared",type=Path,required=True)
    p.add_argument("--all-publishers",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    args=p.parse_args()
    # Materialized, unzipped original JSONs; no API/source access at analysis time.
    primary,pst,psource=audit_dataset(args.shared.glob("GBIF_MONTHLY_*_INAT.json"),"shared_iNaturalist_dataset")
    mixed,mst,msource=audit_dataset(args.all_publishers.glob("GBIF_MONTHLY_*.json"),"all_publishers")
    paired=cross_source_mismatch(primary,mixed)
    args.outdir.mkdir(parents=True,exist_ok=True)
    write_csv(args.outdir/"macro_trophic_stage_windows_iNaturalist_vs_mixed.csv",paired)
    write_csv(args.outdir/"macro_stage_geographic_coverage_iNaturalist.csv",pst)
    write_csv(args.outdir/"macro_stage_geographic_coverage_mixed.csv",mst)
    result={"study":"continental_stage_phenology_macro_original_GBIF_2015_2025_v0_1",
            "date_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "source":"GBIF original occurrence month facets",
            "primary_data_source":"iNaturalist research-grade original GBIF dataset "+COMMON_INAT_GBIF_DATASET,
            "regions":len(REGIONS),"stage_definition":GUILDS,
            "minimum_group_occurrences":MIN_STAGE_RECORDS,
            "primary_macroeological_descriptive":summary(primary),
            "sensitivity_all_publishers":summary(mixed),
            "source_metadata_shared":psource,"source_metadata_mixed":msource,
            "biological_claim":"Regional same-season potential stage availability, not pond-level predation or competition",
            "spatial_or_time_sampling_standardized":False,
            "frogcs_naamp_calling_data_read":False}
    (args.outdir/"macro_stage_phenology_summary.json").write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("source_metadata_shared","source_metadata_mixed")},indent=2))

if __name__=="__main__":
    main()
