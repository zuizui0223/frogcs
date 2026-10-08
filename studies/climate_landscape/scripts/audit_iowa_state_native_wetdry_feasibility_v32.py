#!/usr/bin/env python3
"""Source-blind Iowa NAAMP stop wet/dry feasibility census (v3.2).

This code does NOT download or open USGS Counts.csv or Iowa frog responses.
It accepts only an explicitly prepared, metadata-only environmental CSV.
A current/old blank form is not a measurement. Do not synthesize W/D.
No association, p-value or frog endpoint is computed by this program.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED = ("route_id", "route_type", "stop_number", "event_id", "survey_date", "wetdry")
OPTIONAL = ("site_id", "source_form_version", "stop_surveyed")
MISSING = {"", "NA", "N/A", "NULL", "UNKNOWN", "UNK", "U", "?"}


def audit_csv(raw: str) -> dict:
    reader = csv.DictReader(io.StringIO(raw))
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)):
        raise ValueError("duplicate headers")
    if set(REQUIRED) - set(fields) or set(fields) - set(REQUIRED + OPTIONAL):
        raise ValueError("must be metadata-only exact canonical columns; no extra/outcome fields")
    records = list(reader)
    if not records:
        raise ValueError("empty environmental source panel")
    keys = set()
    visits = defaultdict(list)
    survey_keys = {}
    by_route_year = defaultdict(Counter)
    stop_obs = defaultdict(list)
    site_values = defaultdict(set)
    site_id_blank_rows = Counter()
    surveyed_by_event = defaultdict(list)
    n_missing = 0
    for row in records:
        if None in row:
            raise ValueError("more CSV values than header fields")
        route = row["route_id"].strip()
        rtype = row["route_type"].strip().upper()
        stop_text = row["stop_number"].strip()
        event = row["event_id"].strip()
        date_text = row["survey_date"].strip()
        if not re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", date_text):
            raise ValueError("survey_date must be exactly YYYY-MM-DD")
        try:
            date = dt.date.fromisoformat(date_text)
        except ValueError as e:
            raise ValueError("survey_date must be ISO YYYY-MM-DD") from e
        if not (2010 <= date.year <= 2015):
            raise ValueError("data outside frozen Iowa NAAMP historical window 2010–2015")
        if not route or not event or not stop_text.isdigit():
            raise ValueError("invalid route, stop or event key")
        stop = int(stop_text)
        if not 1 <= stop <= 10 or rtype != "NAAMP":
            raise ValueError("requires 10-stop NAAMP route type and stop 1–10")
        identity = (route, event, stop)
        if identity in keys:
            raise ValueError("duplicate route/event/stop (no silent averaging)")
        keys.add(identity)
        skey = (route, event)
        if skey in survey_keys and survey_keys[skey] != date_text:
            raise ValueError("same route/event_id linked to multiple survey dates")
        survey_keys[skey] = date_text
        raw_wd = row["wetdry"].strip().upper()
        if raw_wd in MISSING:
            wd = None
            n_missing += 1
        elif raw_wd in ("W", "WET"):
            wd = "W"
        elif raw_wd in ("D", "DRY"):
            wd = "D"
        else:
            raise ValueError("unknown wetdry code; request original data dictionary")
        visits[skey].append(wd)
        if "stop_surveyed" in row:
            raw_surveyed = str(row["stop_surveyed"] or "").strip().upper()
            if raw_surveyed not in ("Y", "YES", "1", "N", "NO", "0", "UNKNOWN", "NA", ""):
                raise ValueError("unknown stop_surveyed code; request original dictionary")
            surveyed = True if raw_surveyed in ("Y", "YES", "1") else False if raw_surveyed in ("N", "NO", "0") else None
            if surveyed is False and wd is not None:
                raise ValueError("non-surveyed stop cannot have observed W/D under canonical specification")
            surveyed_by_event[skey].append(surveyed)
        by_route_year[(route, date.year)]["visits"] += 1
        if wd:
            by_route_year[(route, date.year)][wd] += 1
        else:
            by_route_year[(route, date.year)]["missing"] += 1
        stop_obs[(route, stop)].append((date, event, wd))
        if "site_id" in row:
            val = row["site_id"].strip()
            if val:
                site_values[(route, stop)].add(val)
            else:
                site_id_blank_rows[(route, stop)] += 1
    n_both = 0
    n_uniform = 0
    n_no_data = 0
    n_complete = 0
    n_complete_both = 0
    n_incomplete = 0
    n_fully_observed = 0
    n_fully_observed_mixed = 0
    n_fully_observed_uniform = 0
    n_full_wd_and_all_stops_surveyed = 0
    for (route, event), states in sorted(visits.items()):
        complete = len(states) == 10
        if complete:
            n_complete += 1
        else:
            n_incomplete += 1
        found = {x for x in states if x is not None}
        fully_observed = complete and all(x in ("W", "D") for x in states)
        if fully_observed:
            n_fully_observed += 1
            if "stop_surveyed" in fields and surveyed_by_event[(route, event)] == [True] * 10:
                n_full_wd_and_all_stops_surveyed += 1
            if found == {"W", "D"}:
                n_fully_observed_mixed += 1
            else:
                n_fully_observed_uniform += 1
        if found == {"W", "D"}:
            n_both += 1
            if complete:
                n_complete_both += 1
        elif not found:
            n_no_data += 1
        else:
            n_uniform += 1
    switches = []
    coherent_recorded_site_switches = []
    ambiguous_recorded_site_switches = []
    for (route, stop), arr in sorted(stop_obs.items()):
        # Distinct dated within-site W and D statuses are a necessary *nominal*
        # temporal contrast; true field-site stability still requires external evidence.
        observed = {wd for _, _, wd in arr if wd is not None}
        if observed == {"W", "D"}:
            item = {"route_id": route, "stop_number": stop,
                    "n_observed": len([x for x in arr if x[2] is not None])}
            switches.append(item)
            # Recorded SiteID consistency is necessary, never sufficient to prove physical continuity.
            if "site_id" in fields and len(site_values[(route, stop)]) == 1 and site_id_blank_rows[(route, stop)] == 0:
                coherent_recorded_site_switches.append(item)
            else:
                ambiguous_recorded_site_switches.append(item)
    site_id_conflicts = [
        {"route_id": r, "stop_number": s, "site_id_values": sorted(vals)}
        for (r, s), vals in sorted(site_values.items()) if len(vals) > 1
    ]
    route_years = [
        {"route_id": r, "year": y, "stop_visits": c["visits"],
         "wet": c["W"], "dry": c["D"], "missing": c["missing"]}
        for (r, y), c in sorted(by_route_year.items())
    ]
    return {
        "analysis": "iowa_naamp_state_native_wetdry_schema_coverage_v3_2",
        "source_scope": "externally prepared metadata-only Iowa-native 2010–2015 NAAMP ten-stop rows",
        "raw_source_discovery_or_authenticity_established": False,
        "n_stop_event_rows": len(records),
        "n_route_event_surveys": len(visits),
        "n_nominal_route_stops": len(stop_obs),
        "n_missing_wetdry": n_missing,
        "n_route_events_with_wet_and_dry_stops_including_incomplete": n_both,
        "n_complete_10_stop_route_events": n_complete,
        "n_incomplete_10_stop_route_events": n_incomplete,
        "n_complete_10_stop_route_events_with_wet_and_dry_stops": n_complete_both,
        "n_fully_observed_10_stop_route_events": n_fully_observed,
        "n_fully_observed_10_stop_route_events_with_wet_and_dry": n_fully_observed_mixed,
        "n_fully_observed_10_stop_route_events_uniform": n_fully_observed_uniform,
        "n_complete_wd_events_with_explicit_all_ten_stops_surveyed": n_full_wd_and_all_stops_surveyed,
        "stop_surveyed_field_available": "stop_surveyed" in fields,
        "site_id_field_available": "site_id" in fields,
        "n_route_events_with_only_one_observed_status": n_uniform,
        "n_route_events_with_all_wetdry_missing": n_no_data,
        "n_nominal_route_stops_with_within_stop_wet_and_dry": len(switches),
        "nominal_route_stops_with_both_statuses": switches,
        "n_recorded_site_id_consistent_switches": len(coherent_recorded_site_switches),
        "n_switches_with_missing_or_conflicting_recorded_site_id": len(ambiguous_recorded_site_switches),
        "recorded_site_id_consistent_switches_not_field_verified": coherent_recorded_site_switches,
        "site_id_conflicts": site_id_conflicts,
        "route_year_coverage": route_years,
        "historical_physical_station_continuity_verified": False,
        "wetdry_original_field_semantics_verified": False,
        "counts_csv_read": False,
        "frog_response_read": False,
        "inferential_model_fitted": False,
        "rc6_unchanged": True,
        "interpretation": (
            "Descriptive source adequacy only; full ten-stop route-event W/D is "
            "evaluated separately from incomplete events; explicit stop_surveyed is "
            "required to count an event with all ten measured stops. Recorded SiteID "
            "consistency alone cannot establish physical continuity. W/D within nominal route stops and "
            "within route events is necessary but not sufficient for a dynamic local "
            "hydrology test. Original field semantics, missingness and dated "
            "physical-site identity must be externally verified before analysis."
        ),
    }


def synthetic_tests():
    header = ",".join(REQUIRED) + "\n"
    ok = header + "\n".join([
        "360104,NAAMP,1,A,2011-04-14,W",
        "360104,NAAMP,2,A,2011-04-14,D",
        "360104,NAAMP,1,B,2013-05-07,D",
        "360104,NAAMP,2,B,2013-05-07,W",
        "360104,NAAMP,1,C,2014-04-21,UNKNOWN",
    ]) + "\n"
    result = audit_csv(ok)
    assert result["n_stop_event_rows"] == 5
    assert result["n_route_events_with_wet_and_dry_stops_including_incomplete"] == 2
    assert result["n_complete_10_stop_route_events"] == 0
    assert result["n_complete_10_stop_route_events_with_wet_and_dry_stops"] == 0
    assert result["n_nominal_route_stops_with_within_stop_wet_and_dry"] == 2
    assert result["n_missing_wetdry"] == 1
    assert result["n_recorded_site_id_consistent_switches"] == 0
    assert result["n_complete_wd_events_with_explicit_all_ten_stops_surveyed"] == 0
    # Complete route opportunities and fully observed W/D are distinct.
    ten = header + "\n".join(
        f"360110,NAAMP,{i},X,2012-06-02,{('W' if i <= 5 else 'D')}"
        for i in range(1, 11)
    ) + "\n"
    full = audit_csv(ten)
    assert full["n_complete_10_stop_route_events"] == 1
    assert full["n_fully_observed_10_stop_route_events"] == 1
    assert full["n_fully_observed_10_stop_route_events_with_wet_and_dry"] == 1
    ten_missing = ten.replace("360110,NAAMP,10,X,2012-06-02,D",
                              "360110,NAAMP,10,X,2012-06-02,UNKNOWN")
    partial = audit_csv(ten_missing)
    assert partial["n_complete_10_stop_route_events"] == 1
    assert partial["n_fully_observed_10_stop_route_events"] == 0
    assert partial["n_complete_10_stop_route_events_with_wet_and_dry_stops"] == 1
    # Explicit surveyed-status and consistent SiteID are separate from nominal stop labels.
    qualified = "route_id,route_type,stop_number,event_id,survey_date,wetdry,site_id,stop_surveyed\n" + "\n".join(
        f"360110,NAAMP,{i},X,2012-06-02,{('W' if i <= 5 else 'D')},SITE{i},Y"
        for i in range(1, 11)
    ) + "\n"
    qa = audit_csv(qualified)
    assert qa["n_complete_wd_events_with_explicit_all_ten_stops_surveyed"] == 1
    assert qa["n_fully_observed_10_stop_route_events"] == 1
    broken_survey = qualified.replace("SITE10,Y", "SITE10,N")
    try:
        audit_csv(broken_survey)
    except ValueError:
        pass
    else:
        raise AssertionError("Non-surveyed stop with wetdry must be rejected")
    two_events = qualified + "\n".join(
        f"360110,NAAMP,{i},Y,2013-06-02,{('D' if i <= 5 else 'W')},SITE{i},Y"
        for i in range(1, 11)
    ) + "\n"
    coherent = audit_csv(two_events)
    assert coherent["n_recorded_site_id_consistent_switches"] == 10
    site_changed = two_events.replace("360110,NAAMP,1,Y,2013-06-02,D,SITE1,Y", "360110,NAAMP,1,Y,2013-06-02,D,OTHER_SITE,Y")
    inconsistent = audit_csv(site_changed)
    assert inconsistent["n_recorded_site_id_consistent_switches"] == 9
    assert inconsistent["n_switches_with_missing_or_conflicting_recorded_site_id"] == 1
    missing_identity = two_events.replace("360110,NAAMP,1,Y,2013-06-02,D,SITE1,Y", "360110,NAAMP,1,Y,2013-06-02,D,,Y")
    assert audit_csv(missing_identity)["n_recorded_site_id_consistent_switches"] == 9
    invalid = [
        ok + "360104,NAAMP,1,A,2011-04-14,W\n",
        ok.replace("2011-04-14", "2009-04-14"),
        ok.replace("360104,NAAMP,1,C,2014-04-21,UNKNOWN",
                   "360104,NAAMP,1,C,2014-04-21,3"),
        ok.replace("NAAMP", "TRADITIONAL"),
        ok.replace("360104,NAAMP,1,C,2014-04-21,UNKNOWN",
                   "360104,NAAMP,11,C,2014-04-21,W"),
        header.replace("wetdry", "wetdry,calling_index") + "360104,NAAMP,1,A,2011-04-14,W,3\n",
    ]
    for i, payload in enumerate(invalid):
        try:
            audit_csv(payload)
        except ValueError:
            continue
        raise AssertionError(f"Invalid fixture {i} did not fail closed")
    print("PASS: synthetic completeness, survey status, recorded SiteID consistency and invalid-field guards; no frog outcomes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-only-csv", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        synthetic_tests()
        return
    if not args.metadata_only_csv or not args.receipt:
        parser.error("provide both metadata-only-csv and receipt (or --self-test)")
    source = args.metadata_only_csv.read_bytes()
    report = audit_csv(source.decode("utf-8-sig"))
    report["provided_environmental_csv_sha256"] = hashlib.sha256(source).hexdigest()
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                            encoding="utf-8")
    print(json.dumps({k: report[k] for k in [
        "n_stop_event_rows", "n_missing_wetdry",
        "n_complete_10_stop_route_events_with_wet_and_dry_stops",
        "n_fully_observed_10_stop_route_events_with_wet_and_dry",
        "n_nominal_route_stops_with_within_stop_wet_and_dry",
        "counts_csv_read", "frog_response_read"]}, sort_keys=True))


if __name__ == "__main__":
    main()
