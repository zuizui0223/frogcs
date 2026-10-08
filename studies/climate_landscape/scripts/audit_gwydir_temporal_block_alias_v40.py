#!/usr/bin/env python3
"""v4.0 Gwydir six-site publication-exposure design audit.

Reads ONLY the manually transcribed, paper-published Table 2 environmental
exposure summary. It does NOT access original frog chorusing outcomes, original
nightly precipitation, recordings or any NAAMP source. Site-level rain entries
are 24-hour summaries, NOT sums over all four recording nights.
"""
from __future__ import annotations
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

SOURCE=Path("studies/climate_landscape/reference_routes/GWYDIR_SARKER_2022_SIX_SITE_EXPOSURE_TABLE2_V39.csv")
OUT=Path("studies/climate_landscape/receipts/GWYDIR_TABLE2_WEATHER_BLOCK_AND_FLOW_TIME_IDENTIFIABILITY_V40.json")
EXPECTED={"ALLB","CARC","CMBD","GINW","GNDR","TYRL"}
COLS={"site_id","site_name","site_type","hydroperiod_class",
      "rain_before_24h_mm","rain_after_24h_mm",
      "min_temp_before_c","min_temp_after_c",
      "recording_before","recording_after","post_nights_reported","exposure_only"}


def rank(matrix, tol=1e-10):
    """Elementary Gaussian elimination for a deliberately tiny design."""
    if not matrix:
        return 0
    m=[list(map(float,x)) for x in matrix]
    n=len(m[0])
    if any(len(x)!=n for x in m):
        raise ValueError("ragged design")
    row=0
    for c in range(n):
        if row==len(m):
            break
        pivot=max(range(row,len(m)),key=lambda r:abs(m[r][c]))
        if abs(m[pivot][c])<=tol:
            continue
        m[row],m[pivot]=m[pivot],m[row]
        v=m[row][c]
        for j in range(c,n):
            m[row][j]/=v
        for r in range(row+1,len(m)):
            factor=m[r][c]
            for j in range(c,n):
                m[r][j]-=factor*m[row][j]
        row+=1
    return row


def audit(rows):
    if len(rows)!=6 or {r["site_id"] for r in rows}!=EXPECTED:
        raise ValueError("not six exact published sites")
    if set(rows[0])!=COLS:
        raise ValueError("source-only fields changed")
    if any(r.get("exposure_only")!="true" for r in rows):
        raise ValueError("non-exposure data encountered")
    blocks=defaultdict(list)
    for r in rows:
        for k in ("rain_before_24h_mm","rain_after_24h_mm",
                  "min_temp_before_c","min_temp_after_c"):
            float(r[k])
        block=(r["recording_before"],r["recording_after"],
               r["rain_before_24h_mm"],r["rain_after_24h_mm"],
               r["min_temp_before_c"],r["min_temp_after_c"])
        blocks[block].append(r["site_id"])
    block_lists=sorted((sorted(v) for v in blocks.values()),key=lambda s:s[0])
    if block_lists!=[["ALLB"],["CARC","CMBD","TYRL"],["GINW"],["GNDR"]]:
        raise ValueError(f"published weather/time block identity changed: {block_lists}")
    zero_rain=sorted(r["site_id"] for r in rows
        if float(r["rain_before_24h_mm"])==0 and float(r["rain_after_24h_mm"])==0)
    if zero_rain!=["ALLB","GNDR"]:
        raise ValueError("zero-rain 24-hour site group changed")

    # Table 2 represents each site as one pre-flow and one post-flow period.
    # A hypothetical model with an indicator for post-period plus site FE
    # cannot add an independent coefficient for post-flow arrival: the two
    # columns are exactly identical in this two-period summary.
    sites=sorted(EXPECTED)
    base=[]
    with_flow=[]
    for r in rows:
        for after in (0,1):
            site_dummies=[int(r["site_id"]==sid) for sid in sites[1:]]
            x=[1]+site_dummies+[after]
            base.append(x)
            with_flow.append(x+[after])
    rank_base=rank(base)
    rank_flow=rank(with_flow)
    if rank_base!=7 or rank_flow!=7:
        raise ValueError("unexpected site + relative-period alias rank")
    return {
        "analysis":"gywdir_published_six_site_weather_block_rank_v4_0",
        "source":"Sarker et al. 2022 Table 2, DOI 10.1016/j.ecolind.2022.109640",
        "source_type":"manually transcribed published environmental table; no acoustic response",
        "n_sites":6,
        "n_unique_weather_date_context_blocks":len(blocks),
        "sites_per_shared_block":block_lists,
        "n_sites_sharing_one_date_weather_block":3,
        "zero_reported_rain_in_both_24_hour_contexts":zero_rain,
        "n_distinct_zero_rain_date_contexts":2,
        "n_pre_post_period_rows_for_design_illustration":len(base),
        "rank_site_plus_relative_period":rank_base,
        "rank_after_adding_identical_flow_after_indicator":rank_flow,
        "flow_arrival_identifiable_separately_from_relative_time":False,
        "comparison_note":"All sites have one before/after flow contrast; no contemporaneous unexposed counterfactual here. Original paper used richer nightly data not contained in Table 2.",
        "rain_window_note":"Table 2 rainfall is tied to 24h-before/after flow contexts; zero != no rain on every night or no audible flow/sound.",
        "no_frog_outcomes_read":True,
        "no_new_ecological_effect_estimated":True,
        "naamp_rc6_unchanged":True
    }


def main():
    raw=SOURCE.read_bytes()
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if not rows or len(rows[0])!=len(COLS):
        raise ValueError("wrong header")
    result=audit(rows)
    result["transcribed_table_sha256"]=hashlib.sha256(raw).hexdigest()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in (
        "n_sites","n_unique_weather_date_context_blocks",
        "sites_per_shared_block","zero_reported_rain_in_both_24_hour_contexts",
        "rank_site_plus_relative_period",
        "rank_after_adding_identical_flow_after_indicator",
        "flow_arrival_identifiable_separately_from_relative_time",
        "no_frog_outcomes_read")},sort_keys=True))
if __name__=="__main__":
    main()
