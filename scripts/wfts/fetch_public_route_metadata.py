#!/usr/bin/env python3
"""Fetch/parse public WFTS traditional-route site metadata without frog responses.

Network mode requires explicit RouteIDs. The script intentionally has no route-number
scanner: callers must supply the routes they intend to audit. This avoids hammering the
public WFTS website and keeps this tool strictly in the response-free metadata layer.

Fixture mode (--html) parses a saved HTML page and performs no network access.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html as html_lib
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = (
    "https://wiatri.net/inventory/frogtoadsurvey/Volunteer/Maps/"
    "DrawMap.cfm?RouteID={route_id}"
)
USER_AGENT = "frogcs-wfts-public-metadata-audit/1.0"
COORD_RE = re.compile(
    r"\(\s*(-?\d{1,2}(?:\.\d+)?)\s*,\s*(-?\d{2,3}(?:\.\d+)?)\s*\)"
)
ROUTE_RE = re.compile(r"(?mi)^\s*Route\s+([A-Za-z0-9_-]+)\s*-\s*(.+?)\s*$")
SITE_MARKER_RE = re.compile(r"(?mi)^\s*Site\s+(10|[1-9])\s*$")


def visible_text(raw_html: str) -> str:
    """Convert ordinary WFTS HTML into stable line-oriented visible text."""
    x = re.sub(r"(?is)<(script|style)\b.*?</\1\s*>", " ", raw_html)
    x = re.sub(
        r"(?i)<\s*br\s*/?\s*>|</\s*(?:p|div|li|tr|td|th|h[1-6])\s*>",
        "\n",
        x,
    )
    x = re.sub(r"(?s)<[^>]+>", " ", x)
    x = html_lib.unescape(x).replace("\xa0", " ")
    lines = []
    for line in x.splitlines():
        line = re.sub(r"[ \t\r\f\v]+", " ", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def parse_route_html(raw_html: str, source_url: str = "") -> list[dict[str, object]]:
    text = visible_text(raw_html)
    route_match = ROUTE_RE.search(text)
    if not route_match:
        raise ValueError("could not find 'Route <id> - <county>' header")
    route_id = route_match.group(1).strip()
    county = route_match.group(2).strip()

    markers = list(SITE_MARKER_RE.finditer(text))
    if len(markers) != 10:
        raise ValueError(f"expected 10 site markers, found {len(markers)}")

    rows: list[dict[str, object]] = []
    seen: set[int] = set()
    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    digest = hashlib.sha256(raw_html.encode("utf-8")).hexdigest()

    for i, marker in enumerate(markers):
        site_number = int(marker.group(1))
        if site_number in seen:
            raise ValueError(f"duplicate site number {site_number}")
        seen.add(site_number)
        end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
        block = text[marker.end() : end].strip()
        coord = COORD_RE.search(block)
        if not coord:
            raise ValueError(f"site {site_number}: latitude/longitude not found")
        lat, lon = float(coord.group(1)), float(coord.group(2))
        if not (40 <= lat <= 50 and -95 <= lon <= -85):
            raise ValueError(
                f"site {site_number}: coordinates outside Wisconsin audit bounds: "
                f"{lat}, {lon}"
            )
        description = COORD_RE.sub("", block, count=1)
        description = re.sub(r"\s+", " ", description).strip(" -–—")
        rows.append(
            {
                "route_id": route_id,
                "county": county,
                "site_number": site_number,
                "latitude": lat,
                "longitude": lon,
                "site_description": description,
                "source_url": source_url,
                "retrieved_at_utc": retrieved_at,
                "html_sha256": digest,
            }
        )

    if seen != set(range(1, 11)):
        raise ValueError(f"site numbers are not exactly 1..10: {sorted(seen)}")
    return sorted(rows, key=lambda r: int(r["site_number"]))


def fetch_html(route_id: str, timeout: float) -> tuple[str, str]:
    url = BASE_URL.format(route_id=route_id)
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    try:
        with urlopen(req, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            raw = response.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"failed to fetch RouteID={route_id}: {exc}") from exc
    return raw.decode(charset, errors="replace"), url


def read_route_ids(values: list[str], route_file: Path | None) -> list[str]:
    ids = [v.strip() for v in values if v.strip()]
    if route_file:
        for line in route_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                ids.append(line)
    ids = list(dict.fromkeys(ids))
    if not ids:
        raise ValueError("network mode requires explicit --route-id or --route-file")
    for route_id in ids:
        if not re.fullmatch(r"[0-9A-Za-z_-]+", route_id):
            raise ValueError(f"unsafe RouteID: {route_id!r}")
    return ids


def write_csv(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "route_id",
        "county",
        "site_number",
        "latitude",
        "longitude",
        "site_description",
        "source_url",
        "retrieved_at_utc",
        "html_sha256",
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route-id", action="append", default=[])
    parser.add_argument("--route-file", type=Path)
    parser.add_argument(
        "--html",
        type=Path,
        help="Parse one saved route page instead of using the network (QA/audit mode).",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    if args.html:
        if args.route_id or args.route_file:
            parser.error("--html cannot be combined with network route arguments")
        raw = args.html.read_text(encoding="utf-8")
        rows.extend(parse_route_html(raw, source_url=f"file://{args.html}"))
    else:
        route_ids = read_route_ids(args.route_id, args.route_file)
        if args.delay < 0.5:
            parser.error("--delay must be at least 0.5 seconds in network mode")
        for index, route_id in enumerate(route_ids):
            raw, url = fetch_html(route_id, args.timeout)
            parsed = parse_route_html(raw, source_url=url)
            if str(parsed[0]["route_id"]) != route_id:
                raise RuntimeError(
                    f"requested RouteID={route_id}, page reported "
                    f"RouteID={parsed[0]['route_id']}"
                )
            rows.extend(parsed)
            if index + 1 < len(route_ids):
                time.sleep(args.delay)

    write_csv(rows, args.output)
    print(
        {
            "status": "PASS",
            "routes": len({str(r["route_id"]) for r in rows}),
            "sites": len(rows),
            "output": str(args.output),
            "response_columns_read": False,
        }
    )


if __name__ == "__main__":
    main()
