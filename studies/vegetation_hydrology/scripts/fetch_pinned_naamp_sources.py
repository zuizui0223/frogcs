#!/usr/bin/env python3
"""Fetch only public outcome-blind NAAMP tables and coordinates, enforcing SHA256.

Runs.csv and Stops.csv contain station/weather metadata; Counts.csv is never
requested. URL and digests derive from the frozen parent frogcs source loader.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ITEM_URL = "https://www.sciencebase.gov/catalog/item/583dc314e4b0d1899f9dea8d?format=json"
COORD_URL = "https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
PINS = {
    "Runs.csv": "ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730",
    "Stops.csv": "28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f",
    "NAAMP_SiteCoordinates.csv": "f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83",
}


def fetch_bytes(url, attempts=3):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "frogcs-vegetation-outcome-blind-feasibility/0.1", "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=120) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            if isinstance(e, urllib.error.HTTPError) and e.code not in (403, 429, 500, 502, 503, 504):
                raise
            if i < attempts - 1:
                time.sleep(3 * (i + 1))
    raise RuntimeError(f"public source download failed after {attempts} attempts: {url}: {last}")


def find_file(metadata, name):
    if name == "Counts.csv":
        raise ValueError("Counts.csv is an outcome and forbidden in this stage")
    matches = [f for f in metadata.get("files", []) if f.get("name") == name]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one ScienceBase attachment named {name}, found {len(matches)}")
    url = matches[0].get("downloadUri") or matches[0].get("url") or matches[0].get("uri")
    if not isinstance(url, str) or not url.startswith("https://"):
        raise ValueError(f"no validated HTTPS URL for {name}")
    return url


def checked_write(out, name, payload):
    if name not in PINS:
        raise ValueError("unapproved file")
    got = hashlib.sha256(payload).hexdigest()
    if got != PINS[name]:
        raise ValueError(f"{name} SHA256 mismatch {got}; abort (expected {PINS[name]})")
    out.mkdir(parents=True, exist_ok=True)
    target = out / name
    # Hash check precedes all writes. Never replace verified source with drift.
    target.write_bytes(payload)
    return {"file": name, "bytes": len(payload), "sha256": got}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    metadata = json.loads(fetch_bytes(ITEM_URL))
    downloads = [
        ("Runs.csv", find_file(metadata, "Runs.csv")),
        ("Stops.csv", find_file(metadata, "Stops.csv")),
        ("NAAMP_SiteCoordinates.csv", COORD_URL),
    ]
    receipts = []
    for name, url in downloads:
        receipts.append(checked_write(args.out, name, fetch_bytes(url)))
    (args.out / "source_receipt.json").write_text(json.dumps({"sources": receipts, "counts_csv_downloaded": False}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sources": receipts, "counts_csv_downloaded": False}, indent=2))


if __name__ == "__main__":
    main()
