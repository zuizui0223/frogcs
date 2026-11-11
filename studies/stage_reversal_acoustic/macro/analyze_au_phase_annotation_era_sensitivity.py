#!/usr/bin/env python3
"""Post-hoc adversarial stress-test of the AU 36-band-year occurrence phase atlas.

Primary original atlas was frozen before this test. This script does NOT
turn exploratory occurrence-composition geography into a biological or
causal inference. It tests source-stage annotation and 2018–20 vs 2021–23
sampling-era robustness under the *same original eligibility*.
"""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
INPUT=ROOT/"results"/"ORIGINAL_GBIF_AU_6LAT_6YEAR_3STREAM_MONTHLY_V0_1.json"
REF=ROOT/"results"/"AU_36_PANEL_POSTHOC_STAGE_LABEL_AND_ERA_ROBUSTNESS_V0_1.json"
BANDS=((-44,-38),(-38,-32),(-32,-26),(-26,-20),(-20,-14),(-14,-10))
YEARS=tuple(range(2018,2024))
STREAMS=("frogid_call_positive_species_rows","odonata_stage_adult_rows","odonata_any_stage_rows")

def avg(rows,key):
    return sum(r[key] for r in rows)/len(rows) if rows else None

def p(values):
    s=sum(values)
    if s<=0: raise ValueError("missing month count denominator")
    return [x/s for x in values]

def overlap(a,b):
    return sum(min(x,y) for x,y in zip(a,b))

def rotation_surplus(a,b):
    values=[overlap(a,[b[(i-k)%12] for i in range(12)]) for k in range(12)]
    return values[0]-sum(values)/12

def analyse(s):
    if s.get("all_source_queries_verified") is not True or len(s["source_monthly_rows"])!=108:
        raise ValueError("not frozen AU original 108-source dataset")
    index={}
    for x in s["source_monthly_rows"]:
        key=(x["lat_min"],x["lat_max"],x["year"],x["stream"])
        if key in index: raise ValueError("duplicated original source")
        if sum(x["monthly_counts"])!=x["count"]: raise ValueError("month denominators do not reconcile")
        index[key]=x
    panels=[]
    for lo,hi in BANDS:
        for year in YEARS:
            f,a,o=[index[(lo,hi,year,key)] for key in STREAMS]
            eligibility=(f["count"]>=100 and a["count"]>=30 and o["count"]>=100
                         and sum(v>0 for v in f["monthly_counts"])>=4
                         and sum(v>0 for v in a["monthly_counts"])>=4)
            pf,pa,po=p(f["monthly_counts"]),p(a["monthly_counts"]),p(o["monthly_counts"])
            ra=rotation_surplus(pf,pa)
            ro=rotation_surplus(pf,po)
            panels.append({"lat_band":f"{lo}_{hi}","year":year,"eligible":eligibility,
                           "focal_adult_n":a["count"],"all_odonata_n":o["count"],
                           "stage_annotation_adult_fraction":a["count"]/o["count"],
                           "surplus_explicit_adult":ra,"surplus_all_odonata":ro,
                           "sign_reversed_by_annotation_choice":(ra>=0)!=(ro>=0)})
    eligible=[x for x in panels if x["eligible"]]
    byband=[]
    for lo,hi in BANDS:
        group=[x for x in eligible if x["lat_band"]==f"{lo}_{hi}"]
        early=[x for x in group if x["year"]<=2020]
        late=[x for x in group if x["year"]>=2021]
        loo=[{"heldout_year":x["year"],
              "adult_excess_mean_remaining":avg([z for z in group if z["year"]!=x["year"]],"surplus_explicit_adult"),
              "all_excess_mean_remaining":avg([z for z in group if z["year"]!=x["year"]],"surplus_all_odonata")}
             for x in group]
        byband.append({
          "lat_band":f"{lo}_{hi}","n_eligible":len(group),
          "mean_explicit_adult_surplus":avg(group,"surplus_explicit_adult"),
          "mean_all_odonata_surplus":avg(group,"surplus_all_odonata"),
          "adult_annotation_mean_fraction":avg(group,"stage_annotation_adult_fraction"),
          "n_stage_option_sign_reversals":sum(x["sign_reversed_by_annotation_choice"] for x in group),
          "period_2018_2020":{"n":len(early),"adult":avg(early,"surplus_explicit_adult"),"all":avg(early,"surplus_all_odonata")},
          "period_2021_2023":{"n":len(late),"adult":avg(late,"surplus_explicit_adult"),"all":avg(late,"surplus_all_odonata")},
          "leave_one_year_out":loo
        })
    allmean=avg(eligible,"surplus_all_odonata")
    adultmean=avg(eligible,"surplus_explicit_adult")
    result={
        "status":"POSTHOC_ORIGINAL_AU_DATA_OBSERVATION_BIAS_AND_ERA_STRESS_TEST",
        "source_count":len(s["source_monthly_rows"]),
        "n_original_band_years":len(panels),
        "n_fixed_original_eligible":len(eligible),
        "primary_mean_adult_surplus":adultmean,
        "sensitivity_mean_all_odonata_surplus":allmean,
        "adult_minus_all_surplus":adultmean-allmean,
        "n_sign_reversal_when_swapping_adult_stage_vs_all":sum(x["sign_reversed_by_annotation_choice"] for x in eligible),
        "n_positive_explicit_adult":sum(x["surplus_explicit_adult"]>0 for x in eligible),
        "n_positive_all_odonata":sum(x["surplus_all_odonata"]>0 for x in eligible),
        "band_summary":byband,"original_panels":panels,
        "interpretation_limit":"This is source reporting-season phase and stage labelling sensitivity, not an unbiased adult emergence or trophic direction effect. Band extremes were selected post hoc."
    }
    return result

def validate(result):
    reference=json.loads(REF.read_text(encoding="utf-8"))
    for key in ("n_original_band_years","n_fixed_original_eligible",
       "n_sign_reversal_when_swapping_adult_stage_vs_all",
       "n_positive_explicit_adult","n_positive_all_odonata"):
        if result[key]!=reference[key]:raise ValueError("numeric source drift: "+key)
    for key in ("primary_mean_adult_surplus","sensitivity_mean_all_odonata_surplus","adult_minus_all_surplus"):
        if abs(result[key]-reference[key])>1e-12:raise ValueError("floating point source drift: "+key)
    for band,new in zip(reference["band_summary"],result["band_summary"]):
        if band["lat_band"]!=new["lat_band"] or band["n_eligible"]!=new["n_eligible"]:
            raise ValueError("latitude eligibility mismatch")
        for key in ("mean_explicit_adult_surplus","mean_all_odonata_surplus"):
            if abs(band[key]-new[key])>1e-12:raise ValueError("latitude source readback "+key)
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    src=json.loads(INPUT.read_text(encoding="utf-8"))
    result=analyse(src)
    result["frozen_recalculation_match"]=validate(result)
    Path(args.out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"n_eligible":result["n_fixed_original_eligible"],
       "mean_adult":result["primary_mean_adult_surplus"],
       "mean_all":result["sensitivity_mean_all_odonata_surplus"],
       "n_annotation_sign_flip":result["n_sign_reversal_when_swapping_adult_stage_vs_all"],
       "frozen_recalculation_match":result["frozen_recalculation_match"]}))
if __name__=="__main__":main()
