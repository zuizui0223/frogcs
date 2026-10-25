"""Audit parser QA: synthetic XLSX fixtures are NOT original ecological data."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from xml.sax.saxutils import escape

SRC = Path(__file__).resolve().parents[1] / "src" / "audit_anax_original_xlsx.py"
spec = importlib.util.spec_from_file_location("anax_original_xlsx", SRC)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def synthetic_file(path, wrong_subtotal=False):
    """Just enough actual OOXML to test typed shared string, date and NA handling."""
    strings = ["Wetland","Date","Month",
               "Count of Australian Emperor (Anax papuensis) Metamorphasising",
               "Dragonfly emergence","Predation","1A","NA"] + mod.MONTHS
    idx = {v:i for i,v in enumerate(strings)}
    def string(c,v):
        return f'<c r="{c}" t="s"><v>{idx[v]}</v></c>'
    def number(c,v):
        return f'<c r="{c}"><v>{v}</v></c>'
    rows={}
    def set_row(i,*cells):
        rows[i]=list(cells)
    set_row(1,string("A1","Wetland"),string("B1","Date"),string("C1","Month"),
            string("D1",strings[3]),string("K1","Month"),
            string("L1","Dragonfly emergence"),string("M1","Predation"))
    for idx_month,m in enumerate(mod.MONTHS,2):
        rows[idx_month]=[string(f"K{idx_month}",m),
                         number(f"L{idx_month}",9 if wrong_subtotal and idx_month==2 else (1 if idx_month==2 else 0)),
                         number(f"M{idx_month}",0)]
    rows[2]+= [string("A2","1A"),number("B2",43347),string("C2","September"),number("D2",1)]
    rows[3]+= [string("A3","1A"),number("B3",43348),string("C3","September"),number("D3",0)]
    rows[431]=[string("A431","1A"),number("B431",43936),string("D431","NA")]
    shared = '<sst xmlns="'+mod.NS[1:-1]+'">' + "".join("<si><t>"+escape(s)+"</t></si>" for s in strings) + "</sst>"
    sheet = '<worksheet xmlns="'+mod.NS[1:-1]+'"><sheetData>' + "".join(
        f'<row r="{row}">{"".join(cells)}</row>' for row,cells in sorted(rows.items())) + "</sheetData></worksheet>"
    with ZipFile(path,"w") as out:
        out.writestr("xl/sharedStrings.xml",shared)
        out.writestr("xl/worksheets/sheet1.xml",sheet)


class AnaxXlsxAuditTests(unittest.TestCase):
    def test_source_parser_and_monthly_reconstruction(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"fixture.xlsx"
            synthetic_file(p)
            result=mod.audit(p,enforce_pin=False)
            self.assertEqual(result["valid_dated_visits"],2)
            self.assertEqual(result["emergence_total"],1)
            self.assertEqual(result["monthly_predation_total"],0)
            self.assertEqual(result["unscorable_NA_rows"],1)
            self.assertEqual(result["site_label_count"],1)
            self.assertEqual(result["first_positive_date"],"2018-09-04")
            self.assertEqual(result["acoustic_link_status"],
                             "NOT_ESTIMABLE_NO_CALLS_OR_INDIVIDUAL_PREDATION_EVENTS")

    def test_monthly_summary_disagreement_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"bad.xlsx"
            synthetic_file(p,wrong_subtotal=True)
            with self.assertRaisesRegex(ValueError,"monthly subtotal"):
                mod.audit(p,enforce_pin=False)

    def test_sha_gate_fails_for_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"fixture.xlsx"
            synthetic_file(p)
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                mod.audit(p,enforce_pin=True)


if __name__ == "__main__":
    unittest.main()
