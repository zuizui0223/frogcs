#!/usr/bin/env python3
"""Create an immutable receipt for raw WFTS files without parsing response values.

This utility hashes bytes and records filesystem metadata only. It deliberately does not
open CSV/XLSX/database contents, infer schemas, or inspect frog-response values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+", type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--source-note", default="")
    p.add_argument("--received-at-utc", default="")
    args = p.parse_args()

    received_at = args.received_at_utc.strip() or datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat()

    rows = []
    seen = set()
    for path in args.files:
        if not path.exists() or not path.is_file():
            raise SystemExit(f"not a regular file: {path}")
        resolved = path.resolve()
        if resolved in seen:
            raise SystemExit(f"duplicate input file: {path}")
        seen.add(resolved)
        stat = path.stat()
        rows.append(
            {
                "filename": path.name,
                "input_path": str(path),
                "byte_size": stat.st_size,
                "sha256": sha256_file(path),
            }
        )

    receipt = {
        "receipt_type": "wfts_raw_file_bytes_v0_1",
        "received_at_utc": received_at,
        "source_note": args.source_note,
        "files": rows,
        "file_count": len(rows),
        "response_values_interpreted": False,
        "schema_interpreted": False,
        "note": (
            "This receipt records bytes only. Creating it does not authorize opening or "
            "interpreting frog-response values before the response-blind structural preflight."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        {
            "status": "PASS",
            "files": len(rows),
            "response_values_interpreted": False,
            "output": str(args.output),
        }
    )


if __name__ == "__main__":
    main()
