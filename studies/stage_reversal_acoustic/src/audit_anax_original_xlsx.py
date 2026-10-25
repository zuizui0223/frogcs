#!/usr/bin/env python3
"""Source-locked audit of Beranek (2023) Anax_emergence.xlsx.

Zero third-party row redistribution: output only aggregate months, weeks and QC.
Uses Python stdlib on Office Open XML; no proprietary Excel or pandas required.
The provided file is expected locally; this program NEVER downloads a source.
"""
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile
import argparse
import hashlib
import json
import re

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
PIN = "25fabdd0df0d8b679ff23033abbb9fc175067c835f1bd1ef41a5fc4890360c74"
MONTHS = ["September","October","November","December","January","February","March","April"]
BASE = datetime(1899, 12, 30)
REF = re.compile(r"^([A-Z]+)([0-9]+)$")


def as_cells(path):
    """Read only source Sheet1 cell values, retaining NA and blank distinctions."""
    with ZipFile(path) as z:
        shared_xml = ET.fromstring(z.read("xl/sharedStrings.xml"))
        strings = ["".join(e.text or "" for e in si.iter(NS + "t"))
                   for si in shared_xml.findall(NS + "si")]
        root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    cells = {}
    for c in root.findall(".//" + NS + "sheetData/" + NS + "row/" + NS + "c"):
        m = REF.fullmatch(c.get("r", ""))
        if not m:
            raise ValueError("invalid cell address")
        label = c.get("r")
        v = c.find(NS + "v")
        inline = c.find(NS + "is")
        if v is None and inline is None:
            continue
        if c.get("t") == "s":
            value = strings[int(v.text)]
        elif c.get("t") == "inlineStr":
            value = "".join(x.text or "" for x in inline.iter(NS + "t"))
        else:
            if v is None or v.text is None:
                continue
            if c.get("t") in ("e", "str"):
                value = v.text
            else:
                value = float(v.text)
        cells[label] = value
    return cells


def audit(path, enforce_pin=True):
    data = Path(path).read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if enforce_pin and sha != PIN:
        raise ValueError("SHA-256 does not match original immutable file")
    cells = as_cells(path)
    expected = {"A1":"Wetland","B1":"Date","C1":"Month",
                "K1":"Month","L1":"Dragonfly emergence","M1":"Predation"}
    if any(cells.get(k) != v for k,v in expected.items()):
        raise ValueError("source header mismatch")
    if "Anax papuensis" not in str(cells.get("D1", "")):
        raise ValueError("wrong species/count column")

    seen = set()
    counts = Counter()
    visits = Counter()
    positive = Counter()
    wetland = Counter()
    wet_counts = Counter()
    weekly = defaultdict(lambda: {"valid_visits":0,"positive_visits":0,"emergence":0})
    all_dates = []
    positives = []
    orphan_dates = 0
    na_rows = 0
    blank_rows = 0
    for row in range(2, 442):
        site = cells.get("A" + str(row))
        when = cells.get("B" + str(row))
        month = cells.get("C" + str(row))
        count = cells.get("D" + str(row))
        if all(v is None for v in [site, when, month, count]):
            blank_rows += 1
            continue
        if site is None:
            if when is not None:
                orphan_dates += 1
                continue
            raise ValueError("unnamed site with populated data")
        if count == "NA" or when is None or not isinstance(count,(float,int)):
            na_rows += 1
            continue
        if not isinstance(when, (float,int)):
            raise ValueError("invalid Excel day serial")
        if count < 0 or int(count) != count:
            raise ValueError("invalid emergence count")
        d = (BASE + timedelta(days=when)).date()
        if d.strftime("%B") != month:
            raise ValueError("month label differs from actual date")
        site = str(int(site)) if isinstance(site,(float,int)) and int(site)==site else str(site)
        unique = (site,d)
        if unique in seen:
            raise ValueError("duplicate physical-code/date")
        seen.add(unique)
        n = int(count)
        all_dates.append(d)
        counts[month] += n
        visits[month] += 1
        positive[month] += n > 0
        wetland[site] += 1
        wet_counts[site] += n
        monday = d-timedelta(days=d.weekday())
        weekly[monday]["valid_visits"] += 1
        weekly[monday]["positive_visits"] += int(n>0)
        weekly[monday]["emergence"] += n
        if n > 0:
            positives.append((d,n))
    summary_months = []
    for row, month in enumerate(MONTHS,2):
        if cells.get("K"+str(row)) != month:
            raise ValueError("monthly summary ordering mismatch")
        emergence = int(cells["L"+str(row)])
        predation = int(cells["M"+str(row)])
        if emergence != counts[month]:
            raise ValueError("original monthly subtotal doesn't agree with dated rows")
        summary_months.append({
            "month":month, "valid_visits":visits[month],
            "emergence_positive_visits":positive[month],
            "emergence":emergence,"predation_monthly_only":predation
        })
    recurring = [s for s,n in wetland.items() if n >= 20]
    nvis = sum(visits.values())
    total = sum(counts.values())
    npred = sum(x["predation_monthly_only"] for x in summary_months)
    cumquant = {}
    for q in (0.10,0.25,0.50,0.75,0.90):
        acc = 0
        for d,n in sorted(positives):
            acc += n
            if acc >= total*q:
                cumquant[str(q)] = d.isoformat()
                break
    result = {
        "status":"ORIGINAL_EMERGENCE_MONTH_AND_WEEK_VERIFIED_ONLY",
        "input_source_sha256":sha,
        "original_data_doi":"10.17632/9swstxknpz.1",
        "source_range":"Sheet1!A1:M441",
        "valid_dated_visits":nvis,
        "unscorable_NA_rows":na_rows,"orphan_date_rows":orphan_dates,
        "blank_grid_rows":blank_rows,
        "first_date":min(all_dates).isoformat(),
        "last_date":max(all_dates).isoformat(),
        "first_positive_date":min(d for d,n in positives).isoformat(),
        "last_positive_date":max(d for d,n in positives).isoformat(),
        "emergence_date_quantiles":cumquant,
        "site_label_count":len(wetland),
        "recurring_labels_count":len(recurring),
        "recurring_label_valid_visits":sum(wetland[s] for s in recurring),
        "recurring_labels_with_positive":sum(wet_counts[s]>0 for s in recurring),
        "single_or_sparse_labels_count":len(wetland)-len(recurring),
        "positive_visits":sum(positive.values()),
        "emergence_total":total,
        "monthly_predation_total":npred,
        "monthly_subtotal_matches_raw":True,
        "months":summary_months,
        "weekly":[{"week_start":d.isoformat(),**stats} for d,stats in sorted(weekly.items())],
        "acoustic_link_status":"NOT_ESTIMABLE_NO_CALLS_OR_INDIVIDUAL_PREDATION_EVENTS",
        "claim_limits":[
            "One available dated season 2018-09 to 2019-04, not author's four-season time series.",
            "Eleven recurring code labels do not uniquely map to the nine wetlands in article.",
            "Predation is monthly-only in the source workbook: 14 records lack date and wetland.",
            "Counted emergence is not a sampling-standardized predation risk, stage-reversal time, or acoustic alarm response."
        ]
    }
    if enforce_pin:
        if (nvis,total,npred,len(wetland),len(weekly),na_rows,orphan_dates,blank_rows) != (298,233,14,27,26,11,2,129):
            raise ValueError("source source-contract invariants unexpectedly changed")
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,help="Locally provided original Anax_emergence.xlsx, not added to Git")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=audit(a.source)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ["status","valid_dated_visits","emergence_total","monthly_predation_total","acoustic_link_status"]}))


if __name__=="__main__":
    main()
