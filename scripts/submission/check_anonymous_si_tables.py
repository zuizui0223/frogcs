#!/usr/bin/env python3
"""Check that every SI Markdown grid is preserved as an editable Word table.

Only presentation / byte fidelity: reads no frog outcomes or source datasets.
The 14-table layout includes the reviewer-question map, null results and
repository-provenance matrix, previously rendered as raw pipe text.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document


def source_cells(raw: str) -> list[str]:
    return [v.strip() for v in raw.strip().strip("|").split("|")]


def expected_tables(source: str) -> list[list[list[str]]]:
    lines=source.splitlines()
    blocks=[]
    i=0
    while i<len(lines):
        if not lines[i].lstrip().startswith("|"):
            i+=1
            continue
        block=[]
        while i<len(lines) and lines[i].lstrip().startswith("|"):
            block.append(source_cells(lines[i]))
            i+=1
        if len(block)<3:
            raise ValueError("Not a valid Markdown table: missing header/body")
        divider=block[1]
        if not all(re.fullmatch(r":?-{2,}:?",x) for x in divider):
            raise ValueError("Missing alignment separator row")
        columns=len(block[0])
        if columns<2 or columns>8 or any(len(r)!=columns for r in block):
            raise ValueError("Markdown table columns changed mid-grid")
        blocks.append(block[:1]+block[2:])
    return blocks


def markdown_plain(text: str) -> str:
    """Same limited inline-markup normalization as anonymous DOCX renderer."""
    return text.replace(chr(96),"").replace("**","").replace("*","")


def check(si_md: Path, si_docx: Path) -> dict:
    source=si_md.read_text(encoding="utf-8")
    expected=expected_tables(source)
    doc=Document(si_docx)
    if len(expected)!=14 or len(doc.tables)!=len(expected):
        raise AssertionError(
            f"expected/document table mismatch: {len(expected)}/{len(doc.tables)}, require 14")
    nrows=0
    for tid,(spec,table) in enumerate(zip(expected,doc.tables),start=1):
        if len(table.rows)!=len(spec) or len(table.columns)!=len(spec[0]):
            raise AssertionError(f"Table {tid} dimensions differ from Markdown")
        for rid,(cells,row) in enumerate(zip(spec,table.rows),start=1):
            for cid,(expected_cell,actual_cell) in enumerate(zip(cells,row.cells),start=1):
                if markdown_plain(expected_cell)!=actual_cell.text:
                    raise AssertionError(
                        f"Table {tid} row {rid} column {cid} lost text fidelity: "
                        f"expected={expected_cell[:65]!r} actual={actual_cell.text[:65]!r}")
        # The first row should repeat on each page in Word.
        trpr=table.rows[0]._tr.trPr
        if trpr is None or not any(
            elem.tag.endswith("}tblHeader") for elem in trpr):
            raise AssertionError(f"Table {tid} header lacks page-repeat property")
        nrows+=len(table.rows)
    if any(p.text.lstrip().startswith("|") for p in doc.paragraphs):
        raise AssertionError("Unconverted SI Markdown table line found in Word paragraphs")
    return {"status":"PASS","table_count":len(expected),
            "total_table_rows":nrows,
            "markdown_pipe_rows_in_word_paragraphs":0,
            "all_cells_exact_after_inline_markdown_cleanup":True,
            "repeat_headers":len(doc.tables)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--md",type=Path,required=True)
    parser.add_argument("--docx",type=Path,required=True)
    args=parser.parse_args()
    print(check(args.md,args.docx))


if __name__=="__main__":
    main()
