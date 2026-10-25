#!/usr/bin/env python3
"""Build an authenticated-GBIF-download-ready GLOBAL species occurrence cube.

Input is the truly matched GBIF species list from prior GloBI×GBIF pilot.
This script DOES NOT submit a download, request/handle passwords or claim that
any authenticated bulk GBIF export has happened. It creates SQL and JSON
query payloads for 1° and 0.5° monthly/annual occurrence cubes. Use the
official GBIF download service to obtain a citable DOI.
"""
import argparse
import csv
import json
from pathlib import Path

API="https://api.gbif.org/v1/occurrence/download/request"
VALIDATION="https://api.gbif.org/v1/occurrence/download/request/validate"
PERIOD=(2010,2026)
RESOLUTIONS={"global_1deg":3600,"global_0p5deg":1800}


def build_sql(keys,resolution,monthly=True):
    keys=sorted({int(x) for x in keys})
    if not keys or any(x<=0 for x in keys):
        raise ValueError("GBIF species keys must be unique positive ints")
    if len(keys)>10000:
        raise ValueError("Source-matched species list unexpectedly large; inspect")
    codes=", ".join(str(x) for x in keys)
    cell=("GBIF_DMSGCode("+str(resolution)+", decimalLatitude, "
          "decimalLongitude, COALESCE(coordinateUncertaintyInMeters, 1000))")
    grouping=["specieskey",cell,'"year"']
    if monthly: grouping.append('"month"')
    fields=["specieskey AS gbif_species_key",cell+" AS global_gridcell",
            '"year" AS obs_year']
    if monthly: fields.append('"month" AS obs_month')
    fields.append("COUNT(*) AS n_gbif_occurrences")
    return (
        "SELECT "+", ".join(fields)
        +" FROM occurrence WHERE specieskey IN ("+codes+")"
        +" AND hascoordinate = TRUE AND hasgeospatialissues = FALSE"
        +" AND occurrencestatus = 'PRESENT'"
        +f' AND "year" >= {PERIOD[0]} AND "year" <= {PERIOD[1]}'
        +" AND (coordinateUncertaintyInMeters IS NULL"
        +" OR coordinateUncertaintyInMeters <= 10000)"
        +" GROUP BY "+", ".join(grouping)
    )


def create(a):
    csv_path=Path(a.species)
    out=Path(a.out)
    with csv_path.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    if not rows:
        raise RuntimeError("Matched species audit CSV empty")
    matched=[r for r in rows if r["status"]=="accepted"]
    rejected=[r for r in rows if r["status"]!="accepted"]
    keys=sorted({int(r["gbif_taxon_key"]) for r in matched})
    if not keys or len(keys)>150:
        raise RuntimeError(f"Wrong number of GBIF accepted species keys {len(keys)}")
    out.mkdir(parents=True,exist_ok=True)
    by_resolution={}
    for name,grid_size in RESOLUTIONS.items():
        sql=build_sql(keys,grid_size,monthly=True)
        (out/(name+".sql")).write_text(sql+"\n",encoding="utf-8")
        payload={"format":"SQL_TSV_ZIP", "sendNotification":False,
                 "sql":sql}
        (out/(name+".payload.json")).write_text(
            json.dumps(payload,indent=2)+"\n",encoding="utf-8")
        by_resolution[name]={
            "grid_resolution_seconds":grid_size,
            "file":name+".payload.json",
            "source_species_taxon_keys":len(keys),
            "query_api":API,
            "validation_api":VALIDATION,
            "status":"PREPARED_NOT_SUBMITTED",
        }
    metadata={
        "input":str(csv_path),
        "accepted_rows":len(matched),
        "accepted_unique_gbif_species_keys":len(keys),
        "rejected":len(rejected),
        "period":list(PERIOD),
        "resolutions":by_resolution,
        "expected_citation":"GBIF download DOI when user-authorized download succeeds",
        "warnings":[
            "No credentials stored or download initiated.",
            "GBIF aggregated country facet results in earlier pilot are not fine-scale co-occurrence.",
            "A 1° occurrence cube is still not an observation of predator–prey interactions.",
            "Condition monthly / year resolution and taxon season and record effort.",
            "Wetland + emergent cover/hydroperiod raster masks must be independently joined and QAed.",
            "Native versus introduced and presence/range status need external taxonomic/native-range audit.",
        ]
    }
    (out/"manifest.json").write_text(
        json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    print("BEGIN_GBIF_SQL_CUBE_MANIFEST")
    print(json.dumps(metadata,indent=2))
    print("END_GBIF_SQL_CUBE_MANIFEST")


def selftest():
    q=build_sql([111,111,222],3600,True)
    assert q.count("specieskey IN (111, 222)")==1
    assert 'GBIF_DMSGCode(3600,' in q
    assert '"month"' in q and 'hasgeospatialissues = FALSE' in q
    assert "GROUP BY specieskey" in q
    print("SYNTHETIC_GBIF_SQL_CUBE_PREP_PASS")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--species",default="research/results/global_globi_gbif/gbif_species_match_audit.csv")
    p.add_argument("--out",default="research/results/global_globi_gbif/gbif_bulk_cube")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:selftest()
    else:create(a)
