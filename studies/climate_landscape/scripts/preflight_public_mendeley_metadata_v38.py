#!/usr/bin/env python3
"""v3.8 public Mendeley frog hydrology DATASET METADATA preflight.

Does NOT download original response data, read CSV rows, fit models, or alter
the JAE RC6 analysis. Checks only official pinned public dataset file metadata.
Public source: doi:10.17632/p6nbn2hyz9.1 (Nebraska two-wetland study).
"""
from __future__ import annotations
import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DATASET = "p6nbn2hyz9"
VERSION = 1
API = "https://api.data.mendeley.com"
MAX_META_BYTES = 2_000_000
FILE_KEYS = ("filename", "id", "size", "status", "content_details")


def compact_files(payload):
    if isinstance(payload, dict):
        files = payload.get("files")
        if not isinstance(files, list):
            raise ValueError("Expected list of public files, got non-list dict")
    elif isinstance(payload, list):
        files = payload
    else:
        raise ValueError("Unexpected files-list JSON type")
    if len(files) > 500:
        raise ValueError("Unexpectedly large public file list")
    out = []
    for item in files:
        if not isinstance(item, dict) or "filename" not in item:
            raise ValueError("Each file needs official filename field")
        details = item.get("content_details") or {}
        if not isinstance(details, dict):
            raise ValueError("Invalid content_details")
        name = str(item["filename"])
        if not name or len(name) > 500:
            raise ValueError("Invalid source filename")
        out.append({
            "filename": name,
            "id": str(item.get("id") or ""),
            "size_bytes": item.get("size") or details.get("size"),
            "sha256": details.get("sha256_hash"),
            "content_type": details.get("content_type"),
            "status": item.get("status"),
        })
    return sorted(out, key=lambda x: x["filename"])


def fetch_metadata(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "api.data.mendeley.com":
        raise ValueError("Source not official Mendeley metadata API")
    req = urllib.request.Request(
        url, headers={"Accept": "application/json",
                      "User-Agent": "frogcs-public-metadata-preflight/3.8"})
    with urllib.request.urlopen(req, timeout=30) as response:
        code = response.status
        body = response.read(MAX_META_BYTES + 1)
        if len(body) > MAX_META_BYTES:
            raise ValueError("Metadata response unexpectedly large")
        if code != 200:
            raise ValueError(f"Unexpected HTTP {code}")
        ct = response.headers.get("Content-Type", "")
        if "json" not in ct:
            raise ValueError(f"Not JSON response: {ct}")
    return json.loads(body.decode("utf-8"))


def self_test():
    fixture = [
        {"filename": "site.csv", "id": "a",
         "size": 1234,
         "content_details": {"sha256_hash": "ab", "content_type": "text/csv"}},
        {"filename": "README.txt", "id": "b", "size": 44}
    ]
    parsed = compact_files(fixture)
    assert [a["filename"] for a in parsed] == ["README.txt", "site.csv"]
    assert parsed[1]["sha256"] == "ab"
    for bad in (None, 3, [{"name": "missing filename"}], {"files": "wrong"}):
        try:
            compact_files(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("untrusted metadata shape accepted")
    print("PASS: official-source metadata whitelist, sorting and failure guards; no ecological outcomes")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--receipt", default="studies/climate_landscape/receipts/NEBRASKA_OPEN_METADATA_PREFLIGHT_V38.json")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    url = f"{API}/datasets/publics/{DATASET}/files?version={VERSION}"
    receipt = {
        "analysis": "nebraska_published_two_wetland_source_metadata_v3_8",
        "dataset_doi": "10.17632/p6nbn2hyz9.1",
        "dataset_id": DATASET,
        "version": VERSION,
        "endpoint": url,
        "frozen_rule": "metadata only; do not download files or read frog activity values",
        "remote_status": "NOT_ATTEMPTED",
        "file_metadata": [],
        "raw_csv_data_downloaded": False,
        "calling_outcomes_read": False,
        "naamp_outcomes_read": False,
        "iowa_wetdry_read": False,
        "ecological_inference_made": False,
        "rc6_unchanged": True,
    }
    try:
        result = fetch_metadata(url)
        receipt["file_metadata"] = compact_files(result)
        receipt["n_file_records"] = len(receipt["file_metadata"])
        receipt["remote_status"] = "PUBLIC_FILE_METADATA_AVAILABLE"
    except urllib.error.HTTPError as e:
        receipt["remote_status"] = "SOURCE_HTTP_BLOCKED"
        receipt["http_status"] = e.code
    except urllib.error.URLError as e:
        receipt["remote_status"] = "SOURCE_NETWORK_UNAVAILABLE"
        receipt["error_type"] = type(e.reason).__name__
    except (ValueError, json.JSONDecodeError) as e:
        receipt["remote_status"] = "SOURCE_SCHEMA_UNEXPECTED"
        receipt["error_type"] = type(e).__name__
        receipt["error_message"] = str(e)[:200]
    dest = Path(args.receipt)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["remote_status"],
                      "http_status": receipt.get("http_status"),
                      "n_file_records": receipt.get("n_file_records", 0),
                      "outcomes_read": False}, sort_keys=True))


if __name__ == "__main__":
    main()
