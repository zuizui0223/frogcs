#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
SCHEMA_PATH=ROOT/"revision"/"WFTS_CANONICAL_SCHEMA_V0_2.json"


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def fold_for_route(route_id: str) -> str:
    b=hashlib.sha256(str(route_id).encode("utf-8")).digest()[0]
    return "A" if b<128 else "B"


def run_key(route,period,year):
    return (str(route),str(period),int(year))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runs",required=True)
    ap.add_argument("--matrix",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    runs_path=Path(args.runs)
    matrix_path=Path(args.matrix)
    schema=json.loads(SCHEMA_PATH.read_text())

    run_usecols=list(schema["preflight"]["parsed_runs_columns"])
    matrix_usecols=list(schema["preflight"]["parsed_matrix_columns"])

    # Parse only design/weather/site-identity columns. taxon_key and call_index
    # are intentionally not read before the structural gate is frozen.
    runs=pd.read_csv(runs_path,usecols=run_usecols)
    matrix=pd.read_csv(matrix_path,usecols=matrix_usecols)

    runs=runs.copy()
    matrix=matrix.copy()
    runs["route_id"]=runs["route_id"].astype(str)
    matrix["route_id"]=matrix["route_id"].astype(str)
    runs["survey_period"]=runs["survey_period"].astype(str)
    matrix["survey_period"]=matrix["survey_period"].astype(str)
    runs["survey_year"]=runs["survey_year"].astype(int)
    matrix["survey_year"]=matrix["survey_year"].astype(int)
    runs["survey_date"]=pd.to_datetime(runs["survey_date"],errors="raise")
    matrix["survey_date"]=pd.to_datetime(matrix["survey_date"],errors="raise")
    matrix["station_order"]=matrix["station_order"].astype(int)
    matrix["physical_site_id"]=matrix["physical_site_id"].astype(str)

    key=["route_id","survey_period","survey_year"]
    if runs.duplicated(key).any():
        raise RuntimeError("duplicate route-period-year in runs")

    allowed_periods=set(schema["runs_file"]["survey_period_levels"])
    if not set(runs.survey_period.unique())<=allowed_periods:
        raise RuntimeError("unexpected survey_period level in runs")
    if not set(matrix.survey_period.unique())<=allowed_periods:
        raise RuntimeError("unexpected survey_period level in matrix structural columns")

    if not set(matrix.station_order.unique())<=set(range(1,11)):
        raise RuntimeError("station_order outside 1..10")

    # Multiple taxon rows per station are expected. Collapse only after checking
    # that one route-period-year-station maps to one physical SiteID/date.
    skey=key+["station_order"]
    site_counts=matrix.groupby(skey,dropna=False)["physical_site_id"].nunique()
    if (site_counts!=1).any():
        bad=site_counts[site_counts!=1].head().to_dict()
        raise RuntimeError(f"ambiguous physical_site_id in structural matrix: {bad}")

    date_counts=matrix.groupby(skey,dropna=False)["survey_date"].nunique()
    if (date_counts!=1).any():
        bad=date_counts[date_counts!=1].head().to_dict()
        raise RuntimeError(f"ambiguous survey_date in structural matrix: {bad}")

    stations=(
        matrix[skey+["physical_site_id","survey_date"]]
        .drop_duplicates()
        .sort_values(skey)
        .reset_index(drop=True)
    )

    expected_station_rows=len(runs)*10
    if len(stations)!=expected_station_rows:
        raise RuntimeError(
            f"structural matrix does not contain exactly 10 station rows per run: "
            f"{len(stations)} vs {expected_station_rows}"
        )

    sites={}
    for r in runs.itertuples(index=False):
        rk=run_key(r.route_id,r.survey_period,r.survey_year)
        sub=stations[
            (stations.route_id==str(r.route_id))&
            (stations.survey_period==str(r.survey_period))&
            (stations.survey_year==int(r.survey_year))
        ].sort_values("station_order")
        if sub.station_order.tolist()!=list(range(1,11)):
            raise RuntimeError(f"run lacks exact station orders 1..10: {rk}")
        if not (sub.survey_date.dt.normalize()==pd.Timestamp(r.survey_date).normalize()).all():
            raise RuntimeError(f"runs/matrix survey_date mismatch: {rk}")
        sites[rk]=sub.physical_site_id.astype(str).tolist()

    pair_rows=[]
    for (route,period),g in runs.groupby(["route_id","survey_period"],sort=True):
        g=g.sort_values(["survey_year","survey_date"]).reset_index(drop=True)
        for i in range(len(g)-1):
            a,b=g.iloc[i],g.iloc[i+1]
            if float(a.rain_recency)==float(b.rain_recency):
                continue
            ka=run_key(route,period,int(a.survey_year))
            kb=run_key(route,period,int(b.survey_year))
            # Primary WFTS confirmation requires the same ten physical sites.
            if sites[ka]!=sites[kb]:
                continue
            wet,dry=(a,b) if float(a.rain_recency)<float(b.rain_recency) else (b,a)
            pair_rows.append({
                "route_id":str(route),
                "survey_period":str(period),
                "year_earlier":int(min(a.survey_year,b.survey_year)),
                "wet_key":run_key(route,period,int(wet.survey_year)),
                "dry_key":run_key(route,period,int(dry.survey_year)),
            })

    pairs=pd.DataFrame(pair_rows)
    if len(pairs)==0:
        principal=pairs.copy()
    else:
        keep=[]
        by_group={
            (str(route),str(period)):g.sort_values("survey_year")
            for (route,period),g in runs.groupby(["route_id","survey_period"],sort=False)
        }
        for p in pairs.itertuples(index=False):
            g=by_group[(str(p.route_id),str(p.survey_period))]
            wanted=set(sites[p.wet_key])
            prior_ok=False
            for r in g.itertuples(index=False):
                if int(r.survey_year)>=int(p.year_earlier):
                    continue
                rk=run_key(r.route_id,r.survey_period,r.survey_year)
                # Frozen to match the NAAMP prior-site implementation.
                if len(wanted & set(sites[rk]))>=8:
                    prior_ok=True
                    break
            keep.append(prior_ok)
        principal=pairs.loc[pd.Series(keep,index=pairs.index,dtype=bool)].copy()

    principal_routes=int(principal.route_id.nunique()) if len(principal) else 0
    fold_counts={
        fold:int(principal.loc[
            principal.route_id.astype(str).map(fold_for_route)==fold,
            "route_id"
        ].nunique()) if len(principal) else 0
        for fold in ("A","B")
    }

    cg=schema["coverage_gate"]
    gate=bool(
        principal_routes>=int(cg["minimum_routes"]) and
        len(principal)>=int(cg["minimum_principal_pairs"]) and
        min(fold_counts.values())>=int(cg["minimum_routes_per_fold"])
    )

    output={
        "analysis":"wfts_structural_preflight_v0_1",
        "schema":"revision/WFTS_CANONICAL_SCHEMA_V0_2.json",
        "schema_sha256":sha256_file(SCHEMA_PATH),
        "input_sha256":{
            "runs":sha256_file(runs_path),
            "matrix":sha256_file(matrix_path),
        },
        "parsed_columns":{
            "runs":run_usecols,
            "matrix":matrix_usecols,
        },
        "response_columns_read":False,
        "call_index_read":False,
        "taxon_key_read":False,
        "coverage":{
            "eligible_complete_runs":int(len(runs)),
            "all_matched_pairs":int(len(pairs)),
            "principal_history_pairs":int(len(principal)),
            "principal_routes":principal_routes,
            "routes_by_fold":fold_counts,
            "gate_pass":gate,
        },
        "decision":"STRUCTURALLY_ELIGIBLE" if gate else "STRUCTURAL_OR_COVERAGE_GATE_FAILED",
    }

    Path(args.output).write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
