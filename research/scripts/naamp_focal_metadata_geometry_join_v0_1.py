#!/usr/bin/env python3
"""Reproduce NAAMP focal route eligibility with metadata only (NO Counts.csv).

This is a SOURCE-ONLY bridge from the frozen 4,236-pair NAAMP design and
2,916-pair prior-SiteID-history subset to a pinned 10-coordinate source gate.
Do NOT use a frog outcome or an inferred abundance to select routes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import urllib.parse
import urllib.request
import urllib.error
import time
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

import naamp_terrestrial_geometry_preflight_v1 as geometry

ITEM_ID = "583dc314e4b0d1899f9dea8d"
ITEM_URL = f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
SOURCE_PINS = {
    "Runs.csv": "ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730",
    "Stops.csv": "28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f",
}
EXPECTED = {
    "full_pairs": 4236, "full_routes": 585, "full_states": 21,
    "history_pairs": 2916, "history_routes": 439, "history_states": 20,
    "coordinate_10site_routes": 1028
}
ALLOWED_HOSTS = {"www.sciencebase.gov", "sciencebase.gov", "sciencebase.usgs.gov"}

def get_pinned_sources(*, max_bytes=50_000_000):
    req = urllib.request.Request(ITEM_URL, headers={"User-Agent": "frogcs-source-only-focal-join/1.0"})
    with urllib.request.urlopen(req, timeout=75) as f:
        raw = f.read(2_500_001)
    if len(raw) > 2_500_000:
        raise ValueError("ScienceBase metadata too large")
    metadata = json.loads(raw)
    if metadata.get("id") != ITEM_ID:
        raise ValueError("ScienceBase NAAMP item identity drift")
    selected = {}
    for name, pinned in SOURCE_PINS.items():
        records = [v for v in metadata.get("files", []) if v.get("name") == name]
        if len(records) != 1:
            raise ValueError("missing/ambiguous pinned source " + name)
        uri = records[0].get("downloadUri")
        parsed = urllib.parse.urlparse(uri or "")
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError("unverified ScienceBase file host")
        request = urllib.request.Request(uri, headers={"User-Agent": "frogcs-metadata-only-source-v1"})
        last_error = None
        payload = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=150) as f:
                    payload = f.read(max_bytes + 1)
                break
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code not in {429,500,502,503,504} or attempt == 3:
                    raise
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
                if attempt == 3:
                    raise
            time.sleep(2 * (attempt+1))
        if payload is None:
            raise RuntimeError(f"source download failed: {last_error}")
        if len(payload) > max_bytes:
            raise ValueError(f"source size exceeded for {name}")
        actual = hashlib.sha256(payload).hexdigest()
        if actual != pinned:
            raise ValueError(f"sha mismatch for {name}: {actual}")
        selected[name] = list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))
    return selected

def parse_year(x):
    m = re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)", str(x or ""))
    return int(m.group(1)) if m else None

def parse_doy(x):
    value = str(x or "").strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).timetuple().tm_yday
        except ValueError:
            pass
    return None

def eligible_runs(meta):
    """Precisely mirror build_runs metadata/time/temperature gates, no species data."""
    rows = {}
    for x in meta["Runs.csv"]:
        year = parse_year(x.get("SurveyYear")) or parse_year(x.get("SurveyDate"))
        doy = parse_doy(x.get("SurveyDate"))
        if year is None or doy is None or not 2001 <= year <= 2015:
            continue
        if str(x.get("UnifiedProtocol") or "").strip() != "1":
            continue
        rid = str(x.get("RunID") or "").strip()
        runnumber = str(x.get("RunNumber") or "").strip()
        state = str(x.get("State") or "").strip()
        route = str(x.get("RouteNumber") or "").strip()
        rtype = str(x.get("RouteType") or "").strip()
        if not all((rid, state, route, rtype)) or runnumber not in {"1","2","3","4"}:
            continue
        try:
            rain = float(str(x.get("DaysSinceRain") or "").strip())
        except ValueError:
            continue
        if not math.isfinite(rain) or not 0 <= rain <= 180:
            continue
        if rid in rows:
            raise ValueError("RunID duplicate in original Runs.csv")
        rows[rid] = {"rid": rid, "state": state, "route": route,
                     "runnumber": runnumber, "year": year, "doy": doy,
                     "rain": rain, "tempscale": str(x.get("TempScale") or "").strip()}
    sampled = defaultdict(set)
    temps = defaultdict(list)
    siteids = defaultdict(set)
    for x in meta["Stops.csv"]:
        rid = str(x.get("RunID") or "").strip()
        if rid not in rows or str(x.get("SkippedStop") or "").strip() != "0":
            continue
        st = str(x.get("StopNumber") or "").strip()
        sid = str(x.get("SiteID") or "").strip()
        if not st:
            continue
        sampled[rid].add(st)
        if sid:
            siteids[(rid, st)].add(sid)
        try:
            temp = float(str(x.get("AirTemp") or "").strip())
        except ValueError:
            continue
        unit = rows[rid]["tempscale"]
        if unit == "F":
            temp = (temp - 32) * (5 / 9)
        elif unit != "C":
            continue
        if math.isfinite(temp):
            temps[rid].append(temp)
    passing = {}
    for rid, x in rows.items():
        if len(sampled.get(rid, set())) != 10 or len(temps.get(rid, [])) < 8:
            continue
        mean_temp = sum(temps[rid]) / len(temps[rid])
        if not -10 <= mean_temp <= 45:
            continue
        passing[rid] = x
    return passing, sampled, siteids

def metadata_pairs(runs):
    strata = defaultdict(list)
    for rid, x in runs.items():
        strata[(x["state"],x["route"],x["runnumber"])].append(rid)
    pairs = []
    for key, rids in strata.items():
        ordered = sorted(rids,key=lambda rid:(runs[rid]["year"],rid))
        for i in range(len(ordered)-1):
            a, b = runs[ordered[i]],runs[ordered[i+1]]
            if a["rain"] == b["rain"]:
                continue
            pair = {
                "state": key[0], "route": key[1], "runnumber": key[2],
                "route_cluster": f"{key[0]}:{key[1]}",
                "year_earlier": min(a["year"],b["year"]),
                "year_later": max(a["year"],b["year"]),
                "wet_rid": a["rid"] if a["rain"] < b["rain"] else b["rid"],
                "dry_rid": b["rid"] if a["rain"] < b["rain"] else a["rid"]
            }
            pairs.append(pair)
    return pairs, strata

def stable_pair_siteids(pair, sampled, siteids):
    dry, wet = pair["dry_rid"], pair["wet_rid"]
    a, b = sorted(sampled.get(dry,set())), sorted(sampled.get(wet,set()))
    if len(a)!=10 or a!=b:
        return None
    stable = []
    for stop in a:
        ds, ws = siteids.get((dry,stop),set()), siteids.get((wet,stop),set())
        if len(ds)!=1 or ws!=ds:
            return None
        stable.append(next(iter(ds)))
    return stable

def has_prior_site_history(pair, stable_sites, runs, strata, sampled, siteids):
    key=(pair["state"], pair["route"], pair["runnumber"])
    cutoff=pair["year_earlier"]
    target=set(stable_sites)
    for rid in strata[key]:
        if runs[rid]["year"] >= cutoff:
            continue
        prior_sites=set()
        for stop in sampled.get(rid,set()):
            val=siteids.get((rid,stop),set())
            if len(val)==1:
                prior_sites.add(next(iter(val)))
        if len(prior_sites & target)>=8:
            return True
    return False

def produce(meta, coordinates, *, enforce_pins):
    runs, sampled, siteids = eligible_runs(meta)
    pairs, strata = metadata_pairs(runs)
    full_routes={p["route_cluster"] for p in pairs}
    full_states={p["state"] for p in pairs}
    hist=[]
    for pair in pairs:
        ids=stable_pair_siteids(pair,sampled,siteids)
        if ids is None:
            continue
        if has_prior_site_history(pair, ids, runs, strata, sampled, siteids):
            hist.append(pair)
    hist_routes={p["route_cluster"] for p in hist}
    hist_states={p["state"] for p in hist}
    counts={
        "full_pairs":len(pairs),"full_routes":len(full_routes),"full_states":len(full_states),
        "history_pairs":len(hist),"history_routes":len(hist_routes),"history_states":len(hist_states)
    }
    if enforce_pins and any(counts.get(k)!=v for k,v in EXPECTED.items() if k in counts):
        raise ValueError(f"NAAMP metadata reproduction mismatch; DO NOT interpret overlap: {counts}")
    original_coordinate_rows=geometry.read_csv(coordinates)
    geom=geometry.summarize(original_coordinate_rows,enforce_source_size=enforce_pins)
    chosen = {x["route_number"] for x in geom["route_records"]
              if x["complete_10_siteid_source_pass"]}
    if enforce_pins and len(chosen)!=EXPECTED["coordinate_10site_routes"]:
        raise ValueError("ten-SiteID geometry gate drift")
    hist_good = [p for p in hist if p["route"] in chosen]
    good_routes={p["route_cluster"] for p in hist_good}
    good_states={p["state"] for p in hist_good}
    # Route number alone is insufficient: independently check that *each*
    # matched survey pair's physical SiteIDs equal all ten official
    # coordinates on the route. Original survey Runs/Stops only.
    coord_siteids=defaultdict(set)
    for row in original_coordinate_rows:
        route=str(row.get("RouteNumber") or "").strip()
        sid=str(row.get("SiteID") or "").strip()
        if route in chosen and sid:
            coord_siteids[route].add(sid)
    if any(len(coord_siteids[r])!=10 for r in chosen):
        raise ValueError("exact-ten coordinate route lost unique SiteIDs")
    source_pair_siteid_overlap=Counter()
    siteid_identical_pairs=[]
    for p in hist_good:
        survey_ids=stable_pair_siteids(p,sampled,siteids)
        if survey_ids is None or len(set(survey_ids))!=10:
            raise ValueError("paper prior-history pair lost ten stable physical stops")
        n_overlap=len(set(survey_ids) & coord_siteids[p["route"]])
        source_pair_siteid_overlap[n_overlap]+=1
        if n_overlap==10:
            siteid_identical_pairs.append(p)
    exact_siteid_routes={p["route_cluster"] for p in siteid_identical_pairs}
    if len(siteid_identical_pairs)>len(hist_good):
        raise RuntimeError("site-ID pair subset paradox")
    denom={
        "focal_history_pairs":len(hist),"focal_history_routes":len(hist_routes),
        "source_exact10_pairs":len(hist_good),"source_exact10_routes":len(good_routes),
        "source_exact10_states":len(good_states),
        "source_exact10_fraction_focal_pairs":len(hist_good)/len(hist) if hist else 0,
        "source_exact10_fraction_focal_routes":len(good_routes)/len(hist_routes) if hist_routes else 0,
        "focal_routes_excluded":len(hist_routes-good_routes),
        "focal_pairs_excluded":len(hist)-len(hist_good),
        "source_siteid_exact10_pairs":len(siteid_identical_pairs),
        "source_siteid_exact10_routes":len(exact_siteid_routes),
        "source_siteid_exact10_states":len({p["state"] for p in siteid_identical_pairs}),
        "source_siteid_exact10_fraction_focal_pairs":len(siteid_identical_pairs)/len(hist) if hist else 0,
        "source_siteid_exact10_fraction_focal_routes":len(exact_siteid_routes)/len(hist_routes) if hist_routes else 0,
        "source_siteid_exact10_fraction_of_geometry_pairs":
             len(siteid_identical_pairs)/len(hist_good) if hist_good else 0,
        "geometry_pass_but_unmatched_siteid_pairs":len(hist_good)-len(siteid_identical_pairs)
    }
    route_state_counts=Counter(p["state"] for p in hist if p["route_cluster"] in good_routes)
    route_per_state=Counter(k.split(":")[0] for k in good_routes)
    baseline_route_states=Counter(k.split(":")[0] for k in hist_routes)
    baseline_pair_states=Counter(p["state"] for p in hist)
    retention_by_state = {
        state: {
            "focal_routes": baseline_route_states[state],
            "source_exact10_routes": route_per_state[state],
            "route_fraction": route_per_state[state]/baseline_route_states[state],
            "focal_pairs": baseline_pair_states[state],
            "source_exact10_pairs": route_state_counts[state],
            "pair_fraction": route_state_counts[state]/baseline_pair_states[state]
        }
        for state in sorted(baseline_route_states)
    }
    outputs = {
        "study":"naamp_focal_metadata_geometry_join_v0_1",
        "state":"source_only",
        "source_pins":{**SOURCE_PINS,"coordinates":geometry.COORD_SHA256},
        "reproduction":counts,
        "intersection":denom,
        "eligible_state_routes":dict(sorted(route_per_state.items())),
        "state_retention_by_paper_cohort":retention_by_state,
        "eligible_state_pairs":dict(sorted(route_state_counts.items())),
        "coordinate_vs_survey_siteid_overlap_histogram":{
            str(k):int(v) for k,v in sorted(source_pair_siteid_overlap.items())},
        "source_siteid_exact10_routes":sorted(exact_siteid_routes),
        "source_siteid_exact10_pairs":[
            {k:p[k] for k in ("state","route","runnumber","year_earlier","year_later","wet_rid","dry_rid")}
            for p in siteid_identical_pairs],
        "known_coordinate_unsafe_routes_in_focal": sorted(
            set(p["route"] for p in hist) &
            {"270107","270218","350414","720214","880113"}),
        "analysis_caveats":{
            "frog_Counts_csv_opened":False,"calling_index_accessed":False,
            "frog_species_identity_used":False,"frog_effect_estimated":False,
            "spatial_coordinate_precision_300m_proven":False,
            "historical_fixed_site_continuity_proven":False,
            "all_observed_sites_match_geometry_points":False,
            "all_survey_siteids_identical_to_coordinates_in_exact10_subset":True,
            "known_siteid_partial_overlap_excluded_from_exact10_subset":True,
            "source_only_eligibility_not_landcover_pixel_completeness":True,
            "route_numbers_only_not_sufficient_for_identical_historical_station_proof":True,
            "selection_locked_to_paper_metadata_gates":True
        },
        "source_eligible_routes":sorted(good_routes),
        "source_eligible_pairs": [
            {k:p[k] for k in ("state","route","runnumber","year_earlier","year_later","wet_rid","dry_rid")}
            for p in hist_good
        ]
    }
    return outputs

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--metadata-directory",type=Path)
    p.add_argument("--coordinate-csv",type=Path)
    p.add_argument("--output",type=Path,default=Path("research/output/NAAMP_FOCAL_SOURCE_GEOMETRY_JOIN_V0_1.json"))
    args=p.parse_args()
    if args.metadata_directory:
        raw={name:list(csv.DictReader((args.metadata_directory/name).open(encoding="utf8-sig",newline="")))
             for name in SOURCE_PINS}
    else:
        raw=get_pinned_sources()
    coord=args.coordinate_csv.read_bytes() if args.coordinate_csv else geometry.download_pinned_coordinates()
    result=produce(raw,coord,enforce_pins=not(args.metadata_directory or args.coordinate_csv))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({k:result[k] for k in ("study","reproduction","intersection",
                                            "eligible_state_routes","state_retention_by_paper_cohort",
                                            "coordinate_vs_survey_siteid_overlap_histogram",
                                            "analysis_caveats")},
                     indent=2,sort_keys=True))
if __name__=="__main__":
    main()
