#!/usr/bin/env python3
"""Outcome-blind habitat x prior-month water observability and identifiability.

Input: independently validated 2001-2015 NAAMP historical original JRC
water 500m physical station x previous-month panel + full USGS NLCD C1V2
year-matched 500m classes. Never reads species/CallingIndex/Counts.csv.
Water value 0 = NO SATELLITE OBSERVATION; not absence of pond water.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

YEAR_START,YEAR_END=2001,2015
JRC_REQUIRE=172153
NLCD_REQUIRE=64779
NO_FROG_FIELDS={"Species","CallingIndex","Abundance","Taxon"}
NLCD_SHA="137ad705641e39b1a43acfb0d1c5c4aef1fce7024ccb788fb1efc67510a2c67a"  # LF-normalized original values
NLCD_CRLF_SHA="b737c1e5d3177c96fd4ea0dcdcc0ceeb31e95a942e566dba6757d6d58bd36b0b"  # canonical csv.DictWriter output
NAMES=("frac_woody_wetland","frac_emergent_wetland","frac_open_water",
       "frac_forest","frac_developed","frac_agriculture")

def habitat_kind(x):
    water=x["frac_open_water"]
    vegetation=x["frac_woody_wetland"]+x["frac_emergent_wetland"]
    return np.select(
      [(water>=.10),(vegetation>=.25)&(water<.01),
       (water<.005)&(vegetation<.05)],
      ["open_water_ge10","vegetated_wetland_ge25","low_mapped_wetland"],
      default="other")

def summarize(dat):
    dat=dat.copy()
    for c in ("n_buffer_pixels","n_valid_pixels","n_water_pixels"):
        dat[c]=pd.to_numeric(dat[c],errors="raise").astype(int)
    if not ((dat.n_buffer_pixels>0)&(dat.n_valid_pixels>=dat.n_water_pixels)&(dat.n_buffer_pixels>=dat.n_valid_pixels)&(dat.n_water_pixels>=0)).all():
        raise ValueError("invalid original observation/land/water counts")
    dat["clear_fraction"]=dat.n_valid_pixels/dat.n_buffer_pixels
    dat["usable50"]=dat.clear_fraction>=.5
    dat["usable80"]=dat.clear_fraction>=.8
    dat["observed_water_fraction"]=np.where(dat.n_valid_pixels>0, dat.n_water_pixels/dat.n_valid_pixels, np.nan)
    if not dat.loc[dat.n_valid_pixels==0,"water_fraction_among_observed"].isna().all():
        raise ValueError("unobserved source pixels incorrectly treated as non-water")
    dat["water_detected"]=dat.usable50&(dat.n_water_pixels>0)
    dat["habitat"]=habitat_kind(dat)
    dat["prior_month_number"]=dat.PreviousMonth.str[-2:]
    dat["year"]=dat.SurveyYear.astype(int)
    if len(dat)!=JRC_REQUIRE or dat[["RouteNumber","SiteID","SurveyYear","PreviousMonth"]].duplicated().any():
        raise RuntimeError("full original JRC panel not present or duplicate keys")
    if dat.year.min()!=YEAR_START or dat.year.max()!=YEAR_END:
        raise RuntimeError("unexpected year range")

    def group_metrics(x):
        valid=x[x.usable50]
        return pd.Series({
            "site_months":len(x),"usable50":len(valid),
            "usable50_fraction":round(len(valid)/len(x),5) if len(x) else None,
            "usable80":int(x.usable80.sum()),
            "with_open_water":int(x.water_detected.sum()),
            "water_positive_fraction_given_usable":round(valid.water_detected.mean(),5) if len(valid) else None,
            "mean_observation_fraction":round(x.clear_fraction.mean(),5) if len(x) else None,
            "median_water_fraction_given_usable":round(valid.observed_water_fraction.median(),5) if len(valid) else None
        })
    by_year=dat.groupby("year",sort=True).apply(group_metrics,include_groups=False).reset_index()
    by_month=dat.groupby("prior_month_number",sort=True).apply(group_metrics,include_groups=False).reset_index()
    by_habitat=dat.groupby("habitat",sort=True).apply(group_metrics,include_groups=False).reset_index()
    by_state=dat.groupby("State",sort=True).apply(group_metrics,include_groups=False).reset_index()
    by_yrhab=dat.groupby(["year","habitat"],sort=True).apply(group_metrics,include_groups=False).reset_index()
    by_habmonth=dat.groupby(["prior_month_number","habitat"],sort=True).apply(group_metrics,include_groups=False).reset_index()

    # Quantify how many repeated, same-physical-site × same-calendar-month
    # observations change water despite season holding constant.
    good=dat[dat.usable50]
    sm=(good.groupby(["RouteNumber","SiteID","prior_month_number"],sort=False)
      .agg(n=("observed_water_fraction","size"),n_years=("year","nunique"),
           low=("observed_water_fraction","min"),high=("observed_water_fraction","max"),
           mean_water=("observed_water_fraction","mean")).reset_index())
    sm=sm[(sm.n>=2)&(sm.n_years>=2)].copy()
    sm["range"]=sm.high-sm.low

    # A site with observations during very different months/year can show
    # seasonal variability; don't collapse those to an interannual effect.
    all_site=(good.groupby(["RouteNumber","SiteID"],sort=False)
      .agg(n_months=("PreviousMonth","nunique"),
           low=("observed_water_fraction","min"),high=("observed_water_fraction","max"))
      .reset_index())
    all_site=all_site[all_site.n_months>=2].copy()
    all_site["range"]=all_site.high-all_site.low

    # Route×survey-year×preceding-month groups, not necessarily
    # verified concurrent route-run observations.
    rm=(dat.groupby(["RouteNumber","year","PreviousMonth"],sort=False)
      .agg(stations=("SiteID","nunique"),valid_sites=("usable50","sum"),
           water_count=("water_detected","sum")).reset_index())
    # Route months with >=6 valid stations. Determine true max/min
    # on the observationally eligible subset.
    ranges=good.groupby(["RouteNumber","year","PreviousMonth"],sort=False).observed_water_fraction.agg(["min","max"])
    rm=rm.merge(ranges,how="left",left_on=["RouteNumber","year","PreviousMonth"],right_index=True,validate="one_to_one")
    rm["range_water"]=rm["max"]-rm["min"]
    elig=rm[(rm.stations>=8)&(rm.valid_sites>=6)].copy()

    nsm=len(sm)
    full={
      "analysis":"NAAMP_full_previous_month_JRC_x_NLCD_environment_identifiability_v0_1",
      "source_scope":"2001-2015 outcome-blind NAAMP station-months",
      "records":len(dat),
      "usable50":int(dat.usable50.sum()),
      "usable80":int(dat.usable80.sum()),
      "water_positive_in_usable":int(dat.water_detected.sum()),
      "physical_sites":int(dat.groupby(["RouteNumber","SiteID"]).ngroups),
      "route_year_previousmonth_support":{
        "groups_ge8_stations_and_ge6_usable":len(elig),
        "groups_with_water_range_ge5pp":int((elig.range_water>=.05).sum()),
        "groups_with_water_range_ge10pp":int((elig.range_water>=.10).sum()),
        "not_true_simultaneous_route_runs":True},
      "same_site_same_calendar_month_across_years":{
        "eligible_groups":nsm,
        "water_range_ge5pp":int((sm.range>=.05).sum()),
        "water_range_ge10pp":int((sm.range>=.10).sum()),
        "water_range_ge5pp_fraction":round((sm.range>=.05).mean(),5) if nsm else None,
        "water_range_ge10pp_fraction":round((sm.range>=.10).mean(),5) if nsm else None,
        "site_month_groups_not_independent":True},
      "same_site_any_two_previous_months":{
        "eligible_sites":len(all_site),
        "water_range_ge5pp":int((all_site.range>=.05).sum()),
        "not_seasonally_matched":True},
      "no_frog_outcomes_read":True,
      "not_hydroperiod_or_day_of_survey":True,
      "missing_water_pixels_not_dry":True
    }
    return full,{
      "by_year":by_year,"by_prior_month":by_month,
      "by_habitat":by_habitat,"by_state":by_state,
      "by_year_habitat":by_yrhab,"by_prior_month_habitat":by_habmonth,
      "same_site_same_month":sm,"route_year_month_support":rm
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jrc",required=True,type=Path)
    parser.add_argument("--nlcd",required=True,type=Path)
    parser.add_argument("--jrc-manifest",required=True,type=Path)
    parser.add_argument("--out-dir",required=True,type=Path)
    args=parser.parse_args()
    m=json.loads(args.jrc_manifest.read_text(encoding="utf-8"))
    if m.get("analysis")!="NAAMP_JRC_GSW_2001_2015_environment_only_full_panel_v0_1" or not m.get("no_frog_outcomes_read"):
        raise ValueError("JRC source provenance absent")
    raw=args.jrc.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=m.get("combined_csv_sha256"):
        raise ValueError("JRC full panel source checksum drift")
    nlcd_bytes=args.nlcd.read_bytes()
    if (hashlib.sha256(nlcd_bytes).hexdigest()!=NLCD_CRLF_SHA or
        hashlib.sha256(nlcd_bytes.replace(b"\r\n",b"\n")).hexdigest()!=NLCD_SHA):
        raise ValueError("NLCD C1V2 data or expected line-ending normalisation drift")
    jrc=pd.read_csv(args.jrc,dtype={"RouteNumber":str,"SiteID":str,"SurveyYear":str,"PreviousMonth":str},low_memory=False)
    nlcd=pd.read_csv(args.nlcd,dtype={"RouteNumber":str,"SiteID":str},low_memory=False)
    if NO_FROG_FIELDS.intersection(jrc.columns)|NO_FROG_FIELDS.intersection(nlcd.columns):
        raise ValueError("forbidden frog outcome columns")
    jrc["SurveyYear"]=pd.to_numeric(jrc["SurveyYear"],errors="raise").astype(int)
    nlcd=nlcd[(nlcd.radius_m==500)&(nlcd.qc_status=="ok")].copy()
    if len(nlcd)!=NLCD_REQUIRE or nlcd[["RouteNumber","SiteID","year"]].duplicated().any():
        raise ValueError("NLCD year site coverage mismatch")
    joined=jrc.merge(nlcd[["RouteNumber","SiteID","year",*NAMES]],
          left_on=["RouteNumber","SiteID","SurveyYear"],
          right_on=["RouteNumber","SiteID","year"],how="left",
          validate="many_to_one",indicator=True)
    if not joined._merge.eq("both").all():
        raise ValueError("missing NLCD site-year context for JRC records")
    joined.drop(columns=["_merge"],inplace=True)
    out, tables=summarize(joined)
    out["source_jrc_sha256"]=m["combined_csv_sha256"]
    out["source_nlcd_sha256"]=NLCD_SHA
    args.out_dir.mkdir(parents=True,exist_ok=True)
    for name,table in tables.items():
        table.to_csv(args.out_dir/f"{name}.csv",index=False)
    (args.out_dir/"full_environment_identifiability.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
