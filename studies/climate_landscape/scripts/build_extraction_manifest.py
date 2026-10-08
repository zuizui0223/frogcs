#!/usr/bin/env python3
"""Response-blind, verified-site manifest of exact satellite image periods."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

BUFFERS=(250,1000)
LEDGER={"route_id","site_id","latitude","longitude","coordinate_qc_status","verification_source_id"}
EVENTS={"run_id","route_id","site_id","survey_date"}


def make(events:pd.DataFrame,ledger:pd.DataFrame):
    missing=EVENTS-set(events.columns)
    if missing: raise ValueError(f"events missing {sorted(missing)}")
    missing=LEDGER-set(ledger.columns)
    if missing: raise ValueError(f"ledger missing {sorted(missing)}")
    ev=events[sorted(EVENTS)].copy()
    coords=ledger[sorted(LEDGER)].copy()
    for df in (ev,coords):
        for col in ("route_id","site_id"):
            df[col]=df[col].astype("string").str.strip()
            if df[col].isna().any() or df[col].eq("").any():
                raise ValueError(f"missing {col}")
    if ev.run_id.astype("string").isna().any(): raise ValueError("missing run ID")
    ev.survey_date=pd.to_datetime(ev.survey_date,errors="raise").dt.normalize()
    if ev.survey_date.isna().any(): raise ValueError("missing survey date")
    if ev.duplicated(["run_id","route_id","site_id"]).any():
        raise ValueError("duplicate survey event")
    if coords.duplicated(["route_id","site_id"]).any():
        raise ValueError("duplicate coordinate ledger identity")
    if not coords.coordinate_qc_status.eq("verified_external").all():
        raise ValueError("coordinate ledger includes non-verified site")
    coords.verification_source_id=coords.verification_source_id.astype("string").str.strip()
    if coords.verification_source_id.isna().any() or coords.verification_source_id.eq("").any():
        raise ValueError("verification source required; geometry QC alone does not qualify")
    for col in ("latitude","longitude"):
        coords[col]=pd.to_numeric(coords[col],errors="raise")
    if not (np.isfinite(coords[["latitude","longitude"]].to_numpy()).all() and
            coords.latitude.between(24,50).all() and coords.longitude.between(-125,-66).all()):
        raise ValueError("coordinate outside predeclared CONUS domain")
    base=ev.merge(coords,on=["route_id","site_id"],how="left",validate="many_to_one",indicator=True)
    if not base._merge.eq("both").all():
        raise ValueError("some surveyed physical sites are not externally verified")
    base=base.drop(columns=["_merge"])
    month_rows={}
    year_rows={}
    for r in base.itertuples(index=False):
        date=pd.Timestamp(r.survey_date)
        for buf in BUFFERS:
            meta={"route_id":str(r.route_id),"site_id":str(r.site_id),
                  "latitude":float(r.latitude),"longitude":float(r.longitude),
                  "verification_source_id":str(r.verification_source_id),
                  "coordinate_qc_status":"verified_external","buffer_m":buf}
            for mon in pd.period_range(end=date.to_period("M")-1,periods=12,freq="M"):
                if mon.year<1984 or mon.year>2021:
                    raise ValueError("JRC month not available")
                key=(meta["route_id"],meta["site_id"],buf,mon.year,mon.month)
                month_rows[key]={**meta,"year":mon.year,"month":mon.month}
            for year in (date.year-1,date.year-6):
                if not 1985<=year<=2025:
                    raise ValueError("Annual NLCD year not available")
                key=(meta["route_id"],meta["site_id"],buf,year)
                year_rows[key]={**meta,"year":year}
    months=pd.DataFrame(list(month_rows.values())).sort_values(
        ["route_id","site_id","buffer_m","year","month"]).reset_index(drop=True)
    years=pd.DataFrame(list(year_rows.values())).sort_values(
        ["route_id","site_id","buffer_m","year"]).reset_index(drop=True)
    resolved=base.copy()
    resolved.survey_date=resolved.survey_date.dt.strftime("%Y-%m-%d")
    return resolved.sort_values(
        ["route_id","site_id","survey_date"]).reset_index(drop=True),months,years


def filehash(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--events",required=True)
    ap.add_argument("--ledger",required=True)
    ap.add_argument("--output-dir",required=True)
    o=ap.parse_args()
    ev=pd.read_csv(o.events,dtype={"run_id":str,"route_id":str,"site_id":str})
    led=pd.read_csv(o.ledger,dtype={"route_id":str,"site_id":str})
    resolved,months,years=make(ev,led)
    dest=Path(o.output_dir)
    dest.mkdir(parents=True,exist_ok=True)
    outputs={"verified_survey_events.csv":resolved,
             "jrc_month_requests.csv":months,
             "nlcd_year_requests.csv":years}
    for path,df in outputs.items():df.to_csv(dest/path,index=False)
    result={"analysis":"response_blind_satellite_extraction_manifest_v0_1",
            "input_sha256":{"events":filehash(o.events),
                            "independent_coordinate_ledger":filehash(o.ledger)},
            "output_sha256":{p:filehash(dest/p) for p in outputs},
            "n_survey_site_events":len(resolved),
            "n_verified_unique_sites":int(resolved[["route_id","site_id"]].drop_duplicates().shape[0]),
            "n_unique_month_buffer_requests":len(months),
            "n_unique_year_buffer_requests":len(years),
            "reads_frog_response":False,
            "does_not_assume_geometry_pass_is_verified":True,
            "all_image_periods_precede_survey":True}
    (dest/"manifest_receipt.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
