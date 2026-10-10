#!/usr/bin/env python3
"""v5.8 tiny public official metadata-PDF field context inspection (NOT site data).

Requires prior frozen V5_8_MDMS_SOURCE_PDF_CONTEXT_INSPECTION_CONTRACT.md.
"""
from __future__ import annotations
from io import BytesIO
from hashlib import sha256
import json
import re
from pathlib import Path
import urllib.parse
import urllib.error

from pypdf import PdfReader
from audit_mdms_official_metadata_pdf_v57 import (
    API, RESOURCE, MAX_METADATA_BYTES, MAX_PDF_BYTES,
    bounded_get, dictionary_url
)

PIN = "b802f313e58981e6919baa08a300303adeca86ea451a630c06c6b8ba63509b7a"
TARGETS = ("DESCRIPTIO", "DATATYPENA", "SAMPLECOUN")

def safe_excerpt(s: str) -> str:
    s = " ".join(s.split())
    s = re.sub(r"https?://[^\s]+", "[LINK]", s, flags=re.I)
    s = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[EMAIL]", s)
    s = re.sub(r"(?<!\w)[+-]?\d{1,3}\.\d{3,}(?:\s*[,;]\s*[+-]?\d{1,3}\.\d{3,})?", "[DECIMAL_REDACTED]", s)
    return s

def contexts(pdf: bytes) -> dict:
    if sha256(pdf).hexdigest() != PIN or not pdf.startswith(b"%PDF-"):
        raise ValueError("SOURCE_PDF_PIN_OR_TYPE_MISMATCH")
    reader = PdfReader(BytesIO(pdf), strict=False)
    if len(reader.pages) != 2:
        raise ValueError("UNEXPECTED_PDF_LENGTH")
    found = {}
    for name in TARGETS:
        found[name] = []
        pat = re.compile(r"(?<![A-Za-z_])" + re.escape(name) + r"(?![A-Za-z_])", re.I)
        for pi, page in enumerate(reader.pages, 1):
            t = page.extract_text() or ""
            for match in pat.finditer(t):
                # Preserve small public metadata-only context around literal header.
                start, stop = max(0,match.start()-100),min(len(t),match.end()+300)
                excerpt = safe_excerpt(t[start:stop])
                found[name].append({"pdf_page":pi, "source_excerpt":excerpt[:370]})
    return {"status":"OFFICIAL_PUBLIC_PDF_FIELD_CONTEXT_EXTRACTED_NO_UNIT_INFERENCE",
            "source_pdf_sha256":PIN,"n_pages":2,"field_snippets":found,
            "no_geojson_site_values_or_frog_outcomes_accessed":True,
            "independent_wetland_units_confirmed":False}

def tests() -> None:
    assert safe_excerpt("value 146.1234, -35.2345 URL https://example.com/a ") == "value [DECIMAL_REDACTED], [DECIMAL_REDACTED] URL [LINK]"
    try:
        contexts(b"%PDF-1.0 bad")
    except ValueError as exc:
        assert str(exc) == "SOURCE_PDF_PIN_OR_TYPE_MISMATCH"
    else:
        raise AssertionError("source version changed")
    print("PASS: synthetic location pattern redaction and SHA-bound source gate")

def main() -> None:
    tests()
    r = {"status":"SOURCE_UNAVAILABLE", "source_pdf_pin":PIN,
         "no_site_geometry_or_frog_data_accessed":True}
    try:
        meta=json.loads(bounded_get(API+"?"+urllib.parse.urlencode({"id":RESOURCE}),
                                    MAX_METADATA_BYTES,"application/json").decode("utf-8-sig"))
        source=dictionary_url(meta)
        pdf=bounded_get(source,MAX_PDF_BYTES,"application/pdf")
        r=contexts(pdf)
    except urllib.error.HTTPError as exc:
        r.update(status="HTTP_SOURCE_UNAVAILABLE",http_code=exc.code)
    except (urllib.error.URLError,TimeoutError) as exc:
        r.update(status="NETWORK_SOURCE_UNAVAILABLE",error_type=type(exc).__name__)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        r.update(status="SOURCE_FAILED_CLOSED",
                 error_code=str(exc) if str(exc)=="SOURCE_PDF_PIN_OR_TYPE_MISMATCH"
                 else type(exc).__name__)
    p=Path("studies/climate_landscape/receipts/MDMS_PUBLIC_PDF_FIELD_CONTEXT_V58.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,sort_keys=True))

if __name__=="__main__":
    main()
