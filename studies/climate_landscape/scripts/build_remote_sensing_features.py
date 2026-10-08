#!/usr/bin/env python3
"""Build strictly pre-survey JRC and official Annual NLCD environmental features.

Inputs are response-blind exported area tables. This script does not access
Earth Engine and does not infer breeding or demographic occupancy.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

BUFFER_M=(250,1000)
WATER_MIN_OBSERVED_FRACTION=0.5
MIN_OBSERVED_MONTHS=4
WATER_COLUMNS={"route_id","site_id","buffer_m","year","month","water_area_m2",
               "nonwater_area_m2","nodata_area_m2","source_image_id","source_version"}
LAND_COLUMNS={"route_id","site_id","buffer_m","year","forest_area_m2",
              "agriculture_area_m2","developed_area_m2","wetland_area_m2",
              "openwater_area_m2","other_area_m2","nodata_area_m2",
              "source_image_id","source_version"}
EVENT_COLUMNS={"run_id","route_id","site_id","survey_date","coordinate_qc_status"}
LAND_AREA_COLS=("forest_area_m2","agriculture_area_m2","developed_area_m2",
                "wetland_area_m2","openwater_area_m2","other_area_m2","nodata_area_m2")
WATER_AREA_COLS=("water_area_m2","nonwater_area_m2","nodata_area_m2")


def _prep_keys(df,required,name,keys):
    missing=required-set(df.columns)
    if missing:
        raise ValueError(f"{name} missing columns: {sorted(missing)}")
    d=df[list(sorted(required))].copy()
    for col in ("route_id","site_id"):
        d[col]=d[col].astype("string").str.strip()
        if d[col].isna().any() or d[col].eq("").any():
            raise ValueError(f"{name} has missing {col}")
    if d.duplicated(keys).any():
        raise ValueError(f"duplicate {name} keys {keys}")
    return d


def _prep_pixels(d,cols,name):
    for col in cols:
        d[col]=pd.to_numeric(d[col],errors="raise")
        if not np.isfinite(d[col]).all() or (d[col]<0).any():
            raise ValueError(f"invalid {name} area column: {col}")
    if (d[list(cols)].sum(axis=1)<=0).any():
        raise ValueError(f"empty {name} sampling footprint")
    for col in ("source_image_id","source_version"):
        d[col]=d[col].astype("string").str.strip()
        if d[col].isna().any() or d[col].eq("").any():
            raise ValueError(f"missing {name} provenance field {col}")
    return d


def _prep_events(events):
    e=_prep_keys(events,EVENT_COLUMNS,"events",["run_id","route_id","site_id"])
    e["survey_date"]=pd.to_datetime(e.survey_date,errors="raise").dt.normalize()
    if e.survey_date.isna().any():
        raise ValueError("missing survey date")
    if not e.coordinate_qc_status.eq("verified_external").all():
        raise ValueError("unverified physical site: satellite overlay disabled")
    if e.run_id.isna().any() or e.run_id.astype(str).str.strip().eq("").any():
        raise ValueError("missing run_id")
    return e


def _prep_monthly(monthly):
    w=_prep_keys(monthly,WATER_COLUMNS,"monthly_water",
                 ["route_id","site_id","buffer_m","year","month"])
    for col in ("year","month","buffer_m"):
        w[col]=pd.to_numeric(w[col],errors="raise").astype(int)
    if not w.buffer_m.isin(BUFFER_M).all() or not w.month.between(1,12).all() or not w.year.between(1984,2021).all():
        raise ValueError("invalid JRC buffer or month/year")
    w=_prep_pixels(w,WATER_AREA_COLS,"JRC")
    if not w.source_version.str.contains("JRC_GSW1_4",regex=False).all():
        raise ValueError("monthly water must be JRC_GSW1_4 historical imagery")
    w["period"]=pd.PeriodIndex.from_fields(year=w.year,month=w.month,freq="M")
    w["observed_frac"]=(w.water_area_m2+w.nonwater_area_m2)/w[list(WATER_AREA_COLS)].sum(axis=1)
    w["visible_water_frac"]=np.where(w.observed_frac>=WATER_MIN_OBSERVED_FRACTION,
             w.water_area_m2/(w.water_area_m2+w.nonwater_area_m2).replace(0,np.nan),np.nan)
    return w


def _prep_annual(annual):
    a=_prep_keys(annual,LAND_COLUMNS,"annual_landcover",
                 ["route_id","site_id","buffer_m","year"])
    for col in ("year","buffer_m"):
        a[col]=pd.to_numeric(a[col],errors="raise").astype(int)
    if not a.buffer_m.isin(BUFFER_M).all() or not a.year.between(1985,2025).all():
        raise ValueError("invalid Annual NLCD buffer/year")
    a=_prep_pixels(a,LAND_AREA_COLS,"NLCD")
    if not a.source_version.str.contains("ANNUAL_NLCD_C1_2",regex=False).all():
        raise ValueError("Annual NLCD must identify official Collection 1.2")
    a["observed_frac"]=a[list(LAND_AREA_COLS[:-1])].sum(axis=1)/a[list(LAND_AREA_COLS)].sum(axis=1)
    for kind in ("forest","agriculture","developed","wetland","openwater"):
        a[kind+"_frac"]=np.where(a.observed_frac>=WATER_MIN_OBSERVED_FRACTION,
                    a[kind+"_area_m2"]/a[list(LAND_AREA_COLS[:-1])].sum(axis=1).replace(0,np.nan),
                    np.nan)
    return a


def build(events:pd.DataFrame,monthly:pd.DataFrame,annual:pd.DataFrame)->pd.DataFrame:
    e=_prep_events(events)
    w=_prep_monthly(monthly)
    a=_prep_annual(annual)
    wd={(str(g.route_id.iloc[0]),str(g.site_id.iloc[0]),int(g.buffer_m.iloc[0])):g.set_index("period")
        for _,g in w.groupby(["route_id","site_id","buffer_m"],sort=False)}
    ad={(str(r.route_id),str(r.site_id),int(r.buffer_m),int(r.year)):r
        for r in a.itertuples(index=False)}
    rows=[]
    for row in e.itertuples(index=False):
        key=(str(row.route_id),str(row.site_id))
        day=pd.Timestamp(row.survey_date)
        last_month=day.to_period("M")-1
        cutoff_year=day.year-1
        out={"run_id":str(row.run_id),"route_id":key[0],"site_id":key[1],
             "survey_date":day.date().isoformat(),"coordinate_qc_status":"verified_external",
             "last_eligible_water_month":str(last_month),
             "landcover_antecedent_year":cutoff_year,
             "jrc_nodata_is_dry":False,"current_survey_year_landcover_used":False}
        for buffer in BUFFER_M:
            prefix=f"b{buffer}_"
            sub=wd.get((*key,buffer))
            window=pd.period_range(end=last_month,periods=12,freq="M")
            obs=(pd.DataFrame(index=window) if sub is None else sub.reindex(window))
            observed=obs.get("visible_water_frac",pd.Series(index=window,dtype=float)).astype(float)
            covered=int(observed.notna().sum())
            out[prefix+"water_months_observed_12m"]=covered
            out[prefix+"water_months_missing_12m"]=12-covered
            out[prefix+"water_persistence_12m_frac"]=float(observed.mean()) if covered>=MIN_OBSERVED_MONTHS else np.nan
            last=observed.loc[last_month]
            out[prefix+"water_frac_last_completed_month"]=float(last) if pd.notna(last) else np.nan
            lastrow=obs.loc[last_month]
            out[prefix+"jrc_last_source_image_id"]=(str(lastrow["source_image_id"])
                 if "source_image_id" in lastrow and pd.notna(lastrow["source_image_id"]) else "")
            out[prefix+"jrc_last_observed_pixel_frac"]=(float(lastrow["observed_frac"])
                 if "observed_frac" in lastrow and pd.notna(lastrow["observed_frac"]) else np.nan)
            recent=ad.get((*key,buffer,cutoff_year))
            older=ad.get((*key,buffer,cutoff_year-5))
            out[prefix+"nlcd_last_source_image_id"]=str(recent.source_image_id) if recent is not None else ""
            out[prefix+"landcover_observed_pixel_frac"]=float(recent.observed_frac) if recent is not None else np.nan
            for kind in ("forest","agriculture","developed","wetland","openwater"):
                out[prefix+kind+"_frac_prior_year"]=float(getattr(recent,kind+"_frac")) if recent is not None else np.nan
                out[prefix+kind+"_change_prior5y_frac"]=(float(getattr(recent,kind+"_frac")-getattr(older,kind+"_frac"))
                     if recent is not None and older is not None else np.nan)
        rows.append(out)
    return pd.DataFrame(rows).sort_values(["run_id","route_id","site_id"]).reset_index(drop=True)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--events",required=True)
    p.add_argument("--monthly-water",required=True)
    p.add_argument("--annual-landcover",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--receipt",required=True)
    args=p.parse_args()
    e=pd.read_csv(args.events,dtype={"run_id":str,"route_id":str,"site_id":str})
    w=pd.read_csv(args.monthly_water,dtype={"route_id":str,"site_id":str})
    a=pd.read_csv(args.annual_landcover,dtype={"route_id":str,"site_id":str})
    result=build(e,w,a)
    path=Path(args.out)
    path.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(path,index=False)
    rec={"schema":"climate_landscape_remote_sensing_features_v0_1",
         "response_columns_read":False,
         "all_sites_independently_verified":True,
         "no_future_imagery_used":True,
         "water_min_observed_fraction":WATER_MIN_OBSERVED_FRACTION,
         "water_persistence_min_valid_months":MIN_OBSERVED_MONTHS,
         "n_event_rows":int(len(result)),
         "n_physical_sites":int(result[["route_id","site_id"]].drop_duplicates().shape[0]),
         "no_data_is_not_dry":True,"rc6_manuscript_untouched":True,
         "sha256":{"events":sha(args.events),"monthly_water":sha(args.monthly_water),
                   "annual_landcover":sha(args.annual_landcover),"output":sha(path)},
         "features_with_nonmissing_last_month_water":int(result.b250_water_frac_last_completed_month.notna().sum()),
         "features_with_nonmissing_prior_landcover":int(result.b250_forest_frac_prior_year.notna().sum())}
    rec_path=Path(args.receipt)
    rec_path.parent.mkdir(parents=True,exist_ok=True)
    rec_path.write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(rec,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
