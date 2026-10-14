#!/usr/bin/env python3
"""v5.7: official government MDMS PDF dictionary presence, no source excerpts.

See V5_7_MDMS_PDF_DICTIONARY_PRESENCE_CONTRACT.md. No frog outcomes.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

from pypdf import PdfReader

API = "https://data.gov.au/data/api/3/action/resource_show"
RESOURCE = "52a2a361-b1a0-466a-a971-8e046bf99e75"
ALLOWED_HOSTS = {"data.gov.au", "www.data.gov.au"}
MAX_METADATA_BYTES = 400_000
MAX_PDF_BYTES = 10_000_000
FIELDS = ("DESCRIPTIO", "ANAE_TYPE", "DATATYPENA", "SystemType",
          "SAMPLECOUN", "COMMENTS", "POINT_CATE", "PROGRAM",
          "SAMO_ID", "NAME")


def bounded_get(url: str, cap: int, accept: str) -> bytes:
    start = urllib.parse.urlparse(url)
    if start.scheme != "https" or start.hostname not in ALLOWED_HOSTS:
        raise ValueError("UNTRUSTED_SOURCE_HOST")
    req = urllib.request.Request(url, headers={
        "Accept": accept, "User-Agent": "frogcs-mdms-dictionary-presence-only-v57"
    })
    with urllib.request.urlopen(req, timeout=40) as response:
        dest = urllib.parse.urlparse(response.geturl())
        if dest.scheme != "https" or dest.hostname not in ALLOWED_HOSTS:
            raise ValueError("UNEXPECTED_SOURCE_REDIRECT")
        raw = response.read(cap+1)
        if response.status != 200 or len(raw) > cap:
            raise ValueError("BAD_RESPONSE_OR_TOO_LARGE")
    return raw


def dictionary_url(meta: dict) -> str:
    if not isinstance(meta, dict) or meta.get("success") is not True:
        raise ValueError("SOURCE_METADATA_INVALID")
    r = meta.get("result") or {}
    if r.get("id") != RESOURCE or "pdf" not in str(r.get("format", "")).lower():
        raise ValueError("WRONG_RESOURCE_OR_FORMAT")
    url = str(r.get("url") or "")
    u = urllib.parse.urlparse(url)
    if u.scheme != "https" or u.hostname not in ALLOWED_HOSTS:
        raise ValueError("UNTRUSTED_PDF_LOCATION")
    return url


def scan_document(data: bytes) -> dict:
    if not data.startswith(b"%PDF-"):
        raise ValueError("SOURCE_NOT_PDF")
    try:
        reader = PdfReader(BytesIO(data), strict=False)
        n_pages = len(reader.pages)
        if not (1 <= n_pages <= 200):
            raise ValueError("BAD_PDF_PAGE_COUNT")
        texts = [(p.extract_text() or "") for p in reader.pages]
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("PDF_TEXT_EXTRACTION_FAILED") from exc

    hits = {}
    for name in FIELDS:
        pat = re.compile(r"(?<![A-Za-z_])" + re.escape(name) + r"(?![A-Za-z_])", flags=re.I)
        hits[name] = sum(len(pat.findall(s)) for s in texts)
    total_text = sum(len(s) for s in texts)
    if total_text == 0:
        signal = "NO_EXTRACTABLE_TEXT_NOT_A_DICTIONARY_NEGATIVE"
    elif any(hits.values()):
        signal = "POSSIBLE_DICTIONARY_NEEDS_MANUAL_REVIEW"
    else:
        signal = "NO_EXACT_FIELD_DICTIONARY_SIGNAL_IN_EXTRACTED_TEXT"
    return {
        "status": "SOURCE_PDF_METADATA_FIELD_PRESENCE_AUDITED",
        "source_resource_id": RESOURCE,
        "source_pdf_byte_length": len(data),
        "source_pdf_sha256": sha256(data).hexdigest(),
        "n_pdf_pages": n_pages,
        "n_extractable_characters_per_page": [len(s) for s in texts],
        "field_name_literal_hit_counts": hits,
        "dictionary_signal_class": signal,
        "printed_source_text_or_site_values": False,
        "accessed_frog_outcomes_or_geometry": False,
        "authenticated_wetland_parent_mapping": False,
        "independent_rc6_unchanged": True,
    }


def self_test() -> None:
    # The token checker must not confuse a longer source property with NAME.
    pat = re.compile(r"(?<![A-Za-z_])NAME(?![A-Za-z_])", re.I)
    assert len(pat.findall("FILENAME OTHER_NAME NAME, name.")) == 2
    try:
        scan_document(b"This is not a PDF.")
    except ValueError as exc:
        assert str(exc) == "SOURCE_NOT_PDF"
    else:
        raise AssertionError("Invalid source accepted")
    print("PASS: synthetic token-boundary and PDF-header fail-closed tests")


def main() -> None:
    self_test()
    result = {
        "status": "SOURCE_UNAVAILABLE",
        "source_resource_id": RESOURCE,
        "field_dictionary_semantics_verified": False,
        "wetland_ecological_unit_verified": False,
        "no_animal_records_or_coordinates_accessed": True,
    }
    try:
        b = bounded_get(API + "?" + urllib.parse.urlencode({"id": RESOURCE}),
                        MAX_METADATA_BYTES, "application/json")
        u = dictionary_url(json.loads(b.decode("utf-8-sig")))
        pdf = bounded_get(u, MAX_PDF_BYTES, "application/pdf")
        result.update(scan_document(pdf))
    except urllib.error.HTTPError as exc:
        result.update(status="HTTP_SOURCE_UNAVAILABLE", http_status=exc.code)
    except (urllib.error.URLError, TimeoutError) as exc:
        result.update(status="NETWORK_SOURCE_UNAVAILABLE", error_type=type(exc).__name__)
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        safe = {"UNTRUSTED_SOURCE_HOST", "UNEXPECTED_SOURCE_REDIRECT",
                "BAD_RESPONSE_OR_TOO_LARGE", "SOURCE_METADATA_INVALID",
                "WRONG_RESOURCE_OR_FORMAT", "UNTRUSTED_PDF_LOCATION",
                "SOURCE_NOT_PDF", "BAD_PDF_PAGE_COUNT", "PDF_TEXT_EXTRACTION_FAILED"}
        result.update(status="DOCUMENT_GATE_FAILED_CLOSED",
                      error_code=str(exc) if str(exc) in safe else "UNRECOGNIZED_DOCUMENT")
    target = Path("studies/climate_landscape/receipts/MDMS_METADATA_PDF_DICTIONARY_PRESENCE_V57.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
