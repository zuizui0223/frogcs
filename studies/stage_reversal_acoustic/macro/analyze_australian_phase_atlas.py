#!/usr/bin/env python3
"""Independent macroecology: original GBIF frog acoustic + adult odonate seasonal overlap.

All quantities are *occurrence-record compositional*; none represents a
predation rate, a true biological stage-switch date, an acoustic alarm, or
detection-corrected occupancy. No external Python dependencies.
"""
import argparse
import csv
import json
import math
from pathlib import Path

SOURCE=Path(__file__).resolve().parent/"results"/"ORIGINAL_GBIF_AU_6LAT_6YEAR_3STREAM_MONTHLY_V0_1.json"
RESULT=Path(__file__).resolve().parent/"results"/"AU_36_PANEL_STAGE_ACOUSTIC_PHASE_RESULTS_V0_1.json"
STREAMS=("frogid_call_positive_species_rows","odonata_stage_adult_rows","odonata_any_stage_rows")
MONTHS=tuple(range(1,13))
LATS=((-44,-38),(-38,-32),(-32,-26),(-26,-20),(-20,-14),(-14,-10))
YEARS=tuple(range(2018,2024))


def rounded(value):
    return None if value is None else round(value,6)


def read_source(path=SOURCE):
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    if obj.get("all_source_queries_verified") is not True:
        raise ValueError("Incomplete original source snapshot")
    original=obj["source_monthly_rows"]
    if len(original)!=len(LATS)*len(YEARS)*len(STREAMS):
        raise ValueError("Incomplete 108 record source grid")
    seen=set()
    for row in original:
        key=(row["lat_min"],row["lat_max"],row["year"],row["stream"])
        if key in seen:
            raise ValueError("Duplicate input latitude-year-stream panel")
        seen.add(key)
        if key[:2] not in LATS or key[2] not in YEARS or key[3] not in STREAMS:
            raise ValueError("Input outside frozen bands, years or sources")
        counts=row["monthly_counts"]
        if len(counts)!=12 or any(type(x) is not int or x<0 for x in counts):
            raise ValueError("Invalid month count vector")
        if sum(counts)!=row["count"]:
            raise ValueError("Known month sums disagree with published source count")
        if row["stream"]=="odonata_stage_adult_rows" and "lifeStage=Adult" not in row["url"]:
            raise ValueError("Adult label filter missing: never impute unlabeled as adult")
        if row["stream"]=="frogid_call_positive_species_rows" and "datasetKey=47c9fee2-619a-481c-a114-386bc4748256" not in row["url"]:
            raise ValueError("Source is not FrogID")
    return obj


def probability(rows):
    n=sum(rows)
    if n<1:
        raise ValueError("Empty source month vector")
    return [a/n for a in rows]


def overlap(p,q):
    return sum(min(a,b) for a,b in zip(p,q))


def circular(p):
    co=sum(v*math.cos(math.pi*i/6) for i,v in enumerate(p))
    si=sum(v*math.sin(math.pi*i/6) for i,v in enumerate(p))
    m=((math.atan2(si,co)*6/math.pi)%12)+1
    return {"mean_month":rounded(m),"resultant_R":rounded(math.hypot(co,si)),
            "peak_month":p.index(max(p))+1}


def average(rows,key):
    return (sum(row[key] for row in rows)/len(rows)) if rows else None


def analyze(source):
    rows=source["source_monthly_rows"]
    lookup={(r["lat_min"],r["lat_max"],r["year"],r["stream"]):r for r in rows}
    panels=[]
    for low,high in LATS:
        for year in YEARS:
            f,a,o=[lookup[low,high,year,st] for st in STREAMS]
            fp=probability(f["monthly_counts"])
            ap=probability(a["monthly_counts"])
            op=probability(o["monthly_counts"])
            shifts=[overlap(fp, [ap[(i-d)%12] for i in range(12)]) for d in range(12)]
            rotmean=sum(shifts)/12
            fc,ac=circular(fp),circular(ap)
            eligible=(f["count"]>=100 and a["count"]>=30 and o["count"]>=100
                      and sum(x>0 for x in f["monthly_counts"])>=4
                      and sum(x>0 for x in a["monthly_counts"])>=4)
            true_overlap=overlap(fp,ap)
            adult_minus_all=true_overlap-overlap(fp,op)
            diff=(ac["mean_month"]-fc["mean_month"]+6)%12-6 if (
                  fc["resultant_R"]>=.15 and ac["resultant_R"]>=.15) else None
            panels.append({
                "band":f"{low}_{high}","latitude_center":(low+high)/2,"year":year,
                "frog_rows":f["count"],"odonata_adult_rows":a["count"],"odonata_all_month_known_rows":o["count"],
                "adult_labelling_share":a["count"]/o["count"],
                "eligible":eligible,"monthly_overlap_adult":rounded(true_overlap),
                "rotation_null_mean":rounded(rotmean),
                "observed_minus_rotmean":rounded(true_overlap-rotmean),
                "phase_rank_ge12":sum(x>=shifts[0]-1e-12 for x in shifts),
                "all_odonata_overlap":rounded(overlap(fp,op)),
                "adult_minus_all_overlap":rounded(adult_minus_all),
                "frog_peak_month":fc["peak_month"],"adult_peak_month":ac["peak_month"],
                "frog_circ_R":fc["resultant_R"],"adult_circ_R":ac["resultant_R"],
                "circular_odonata_minus_frog_months":rounded(diff)
            })
    ok=[p for p in panels if p["eligible"]]
    bands=[]
    for low,high in LATS:
        label=f"{low}_{high}"
        eligible=[r for r in ok if r["band"]==label]
        all_rows=[r for r in panels if r["band"]==label]
        bands.append({
            "band":label,"latitude_center":(low+high)/2,"n_eligible":len(eligible),"n_total":len(all_rows),
            "frog_rows":sum(x["frog_rows"] for x in all_rows),
            "adult_rows":sum(x["odonata_adult_rows"] for x in all_rows),
            "mean_overlap":rounded(average(eligible,"monthly_overlap_adult")),
            "mean_rotmean":rounded(average(eligible,"rotation_null_mean")),
            "mean_excess":rounded(average(eligible,"observed_minus_rotmean")),
            "mean_odonata_adult_minus_all":rounded(average(eligible,"adult_minus_all_overlap")),
            "n_positive_excess":sum(x["observed_minus_rotmean"]>0 for x in eligible)
        })
    central=[x for x in ok if x["band"]=="-32_-26"]
    north={x["year"]:x for x in ok if x["band"]=="-14_-10"}
    matched=[{"year":x["year"],"central":x["observed_minus_rotmean"],
              "northern":north[x["year"]]["observed_minus_rotmean"],
              "central_minus_north":rounded(x["observed_minus_rotmean"]-north[x["year"]]["observed_minus_rotmean"])}
             for x in central if x["year"] in north]
    leave=[{"excludedBand":b["band"],"mean_excess":rounded(average(
            [x for x in ok if x["band"]!=b["band"]],"observed_minus_rotmean"))}
           for b in bands]
    return {"version":"0.1","n_panels_total":len(panels),"n_eligible":len(ok),
            "main":{"mean_adult_frog_monthly_overlap":rounded(average(ok,"monthly_overlap_adult")),
                    "mean_rotated_reference_overlap":rounded(average(ok,"rotation_null_mean")),
                    "mean_excess_vs_12month_rotation":rounded(average(ok,"observed_minus_rotmean")),
                    "panels_excess_positive":sum(x["observed_minus_rotmean"]>0 for x in ok),
                    "panels_excess_nonpositive":sum(x["observed_minus_rotmean"]<=0 for x in ok),
                    "mean_observation_stage_annotation_sensitivity":rounded(average(ok,"adult_minus_all_overlap")),
                    "equal_lat_band_mean_excess":rounded(average(bands,"mean_excess"))},
            "group_panels":panels,"band_summaries":bands,
            "yearmatched_central_vs_northern":matched,"leave_one_band_out":leave,
            "claim_ceiling":"Exploratory occurrence phenology only: no predation-reversal date, no causal alarm response."}


def validate(result, frozen):
    source=json.loads(Path(frozen).read_text(encoding="utf-8"))
    if result["n_eligible"]!=source["n_eligible"]:
        raise ValueError("Eligibility mismatch")
    for k,v in result["main"].items():
        if abs(v-source["main"][k])>1.5e-6:
            raise ValueError(f"Macro mean mismatch {k}: {v} vs {source['main'][k]}")
    for new,old in zip(result["band_summaries"],source["band_summaries"]):
        for k in ("n_eligible","n_total","mean_overlap","mean_rotmean","mean_excess","n_positive_excess"):
            if abs(new[k]-old[k])>1.5e-6:
                raise ValueError(f"Regional macro mismatch {old['band']} {k}")
    for new,old in zip(result["group_panels"],source["group_panels"]):
        for k in ("monthly_overlap_adult","rotation_null_mean","observed_minus_rotmean",
                  "adult_minus_all_overlap","phase_rank_ge12"):
            if abs(new[k]-old[k])>2e-6:
                raise ValueError(f"Group macro mismatch {old['band']} {old['year']} {k}")
    return True


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",default=str(SOURCE))
    p.add_argument("--reference",default=str(RESULT))
    p.add_argument("--out",required=True)
    a=p.parse_args()
    obj=read_source(a.source)
    result=analyze(obj)
    result["exact_calculation_readback"]=validate(result,a.reference)
    Path(a.out).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"n_panels":result["n_panels_total"],"n_eligible":result["n_eligible"],
      "main":result["main"],"exact_calculation_readback":result["exact_calculation_readback"]}))


if __name__=="__main__":
    main()
