#!/usr/bin/env python3
"""Recompute ONE-season coarse frog-call × dragonfly-emergence lag diagnostics.

Observation units remain nonexchangeable across databases. All output is
explicitly exploratory, never a true matched-wetland prediction or warning test.
"""
import argparse
from datetime import date,timedelta
import json
import math
from pathlib import Path

LAGS=(0,1,2,4,8)


def pearson(values):
    if len(values)<4:
        return None
    mx=sum(x for x,y in values)/len(values)
    my=sum(y for x,y in values)/len(values)
    xx=sum((x-mx)**2 for x,y in values)
    yy=sum((y-my)**2 for x,y in values)
    if xx<=1e-16 or yy<=1e-16:
        return None
    return sum((x-mx)*(y-my) for x,y in values)/math.sqrt(xx*yy)


def classify(rows):
    seen=set()
    data={}
    for entry in rows:
        key=entry["week_start"]
        if key in seen:
            raise ValueError("duplicate week")
        seen.add(key)
        when=date.fromisoformat(key)
        if when.weekday()!=0:
            raise ValueError("week must start on Monday")
        n=entry["unique_recording_events"]
        focal=entry["focal_positive_recording_events"]
        if n<1 or focal<0 or focal>n:
            raise ValueError("invalid audio positive/denominator")
        amount=entry.get("anax_emergers")
        effort=entry.get("anax_valid_wetland_visits")
        if (amount is None)!=(effort is None):
            raise ValueError("unobserved Anax week must have BOTH missing fields")
        if effort is not None and (effort<=0 or amount<0):
            raise ValueError("invalid Anax visit/emergence")
        data[when]=(focal/n,(amount/effort if effort else None),focal)
    return data


def run(source):
    data=classify(source["weekly_source_aggregate"])
    if len(data)!=32:
        raise ValueError("input is not the frozen 32-week source coverage")
    original_years=len({d.year for d,(x,y,f) in data.items() if y is not None})
    direct=[]
    same_anchor=[]
    for lag in LAGS:
        out=[];back=[]
        matched_f=[];matched_b=[]
        positive_count=0
        for when,(x,y,focal) in sorted(data.items()):
            fw=data.get(when+timedelta(weeks=lag))
            bw=data.get(when-timedelta(weeks=lag))
            if fw and fw[1] is not None:
                out.append((x,fw[1]))
            if bw and bw[1] is not None:
                back.append((x,bw[1]))
            if lag and fw and bw and fw[1] is not None and bw[1] is not None:
                matched_f.append((x,fw[1]))
                matched_b.append((x,bw[1]))
                positive_count+=int(focal>0)
        direct.append({"lag_weeks":lag,"orientation":"CALLS_T_VS_EMERGENCE_T" if not lag else "CALLS_T_VS_EMERGENCE_T_PLUS_LAG",
                       "n_pairs":len(out),"r":round(pearson(out),5) if pearson(out) is not None else None})
        if lag:
            direct.append({"lag_weeks":lag,"orientation":"CALLS_T_VS_EMERGENCE_T_MINUS_LAG_NEGATIVE_TIME_CONTROL",
                           "n_pairs":len(back),"r":round(pearson(back),5) if pearson(back) is not None else None})
            rp=pearson(matched_f)
            rn=pearson(matched_b)
            same_anchor.append({"lag_weeks":lag,"n_same_anchor_weeks":len(matched_f),
                "n_focal_call_positive_anchor_weeks":positive_count,
                "forward_r":round(rp,4) if rp is not None else None,
                "reverse_r":round(rn,4) if rn is not None else None,
                "forward_minus_reverse_r":round(rp-rn,4) if rp is not None and rn is not None else None})
    return {"status":"ONE_SEASON_UNMATCHED_REGION_DESCRIPTIVE_ONLY",
            "n_frogid_recording_events":sum(r["unique_recording_events"] for r in source["weekly_source_aggregate"]),
            "n_focal_call_positive_events":sum(r["focal_positive_recording_events"] for r in source["weekly_source_aggregate"]),
            "n_anax_surveyed_weeks_including_zero_emergence":sum(r.get("anax_emergers") is not None for r in source["weekly_source_aggregate"]),
            "calendar_years_within_single_breeding_season":original_years,
            "forward_and_reverse_lag_diagnostics":direct,"same_anchor_directional_diagnostics":same_anchor,
            "identification":"Cannot infer true warning, seasonally validated leading prediction, or predator/prey reversal date."}


def validate(output,source):
    stored=source["exploratory_temporal_correlations"]
    for val in output["forward_and_reverse_lag_diagnostics"]:
        match=next((v for v in stored if v["lag_weeks"]==val["lag_weeks"] and v["orientation"]==val["orientation"]),None)
        if match is None or val["n_pairs"]!=match["n_pairs"] or val["r"]!=match["r"]:
            raise ValueError("time-lag source readback mismatch")
    frozen=source["matched_same_call_anchor_forward_vs_reverse_lags"]
    for val,reference in zip(output["same_anchor_directional_diagnostics"],frozen):
        if val!=reference:
            raise ValueError("matched-anchor sensitivity not reproduced")
    return True


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--receipt",default=str(Path(__file__).resolve().parents[1]/"results"/"FROGID_ANAX_COARSE_WEEKLY_REAL_2018_2019_V1.json"))
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    source=json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    result=run(source)
    result["matches_locked_real_source_aggregate"]=validate(result,source)
    Path(args.out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
