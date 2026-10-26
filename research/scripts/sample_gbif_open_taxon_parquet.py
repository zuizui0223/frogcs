#!/usr/bin/env python3
"""Read-only S3/HTTPS first-Parquet-row-group GBIF aquatic taxa format test.

Experimental GBIF public August 2026 taxon-partitioned snapshot,
NOT final citable October full snapshot or global stage abundance.
"""
import argparse
import collections
import json
from pathlib import Path
import pyarrow.parquet as pq
import pyarrow.fs as afs

B="gbif-public-data"
BASE="development/2026-08-01-DWCA/p_taxon"
PARTS={
    "Anura":"Animalia_Chordata_Amphibia_Anura",
    "Odonata":"Animalia_Arthropoda_Insecta_Odonata",
}
FIELDS=["gbifID","speciesKey","species","lifeStage","occurrenceStatus",
        "hasCoordinate","hasGeospatialIssues","year","month",
        "decimalLatitude","decimalLongitude",
        "coordinateUncertaintyInMeters",
        "basisOfRecord"]
STAGES={"Adult","Juvenile","Larva","Nymph","Egg","Tadpole",
        "Subadult","Pupa","Imago","Immature"}

def inspect(fs,part):
    key=f"{B}/{BASE}/taxonpartition={part}/data_0.parquet"
    with fs.open_input_file(key) as f:
        obj=pq.ParquetFile(f)
        t=obj.read_row_group(0,columns=FIELDS)
        d=t.to_pydict()
    n=t.num_rows
    example=[]
    count=collections.Counter()
    keyexamples={}
    stages=collections.Counter()
    observed=0
    for i in range(n):
        name=d["species"][i]
        k=d["speciesKey"][i]
        rawstage=d["lifeStage"][i]
        if i<8:
            example.append({
                "gbifID":str(d["gbifID"][i]),
                "species":str(name),
                "speciesKey":str(k),
                "lifeStage":str(rawstage),
                "year":d["year"][i],
                "lat":d["decimalLatitude"][i],
                "lon":d["decimalLongitude"][i],
                "hasGeospatialIssues":d["hasGeospatialIssues"][i],
            })
        if (d["hasGeospatialIssues"][i] is False and
            d["occurrenceStatus"][i]=="PRESENT" and
            isinstance(d["year"][i],int) and
            2010<=d["year"][i]<=2026 and
            d["decimalLatitude"][i] is not None and
            d["decimalLongitude"][i] is not None):
            observed+=1
            if name:
                count[str(name)]+=1
                if str(name) not in keyexamples:
                    keyexamples[str(name)]=str(k)
            if rawstage:stages[str(rawstage)]+=1
    return {
        "read_object":key,
        "file_recorded_rowgroups":obj.metadata.num_row_groups,
        "file_total_records":obj.metadata.num_rows,
        "first_rowgroup_rows":n,
        "selected_cols":t.schema.names,
        "first_rowgroup_valid_present_2010_2026":observed,
        "top_species_names":[dict(species=s,n=n,key=keyexamples.get(s))
                             for s,n in count.most_common(15)],
        "top_lifeStage":[dict(stage=s,n=n) for s,n in stages.most_common(20)],
        "small_first_rows":example,
        "NOT_A_GLOBAL_ESTIMATE":"Only the first row group of one of multiple Parquet files per taxon partition."
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="research/results/gbif_anon_taxon_partition_sample")
    a=parser.parse_args()
    fs=afs.S3FileSystem(anonymous=True,region="us-east-1")
    result={
        "date":"2026-10-25",
        "source":"https://gbif-public-data.s3.amazonaws.com/development/2026-08-01-DWCA/p_taxon/",
        "experimental_public_snapshot":True,
        "citable_full_snapshot_october":"https://doi.org/10.15468/dl.tup2g6",
        "partition_samples":{},
    }
    for name,part in PARTS.items():
        try: result["partition_samples"][name]=inspect(fs,part)
        except Exception as e:result["partition_samples"][name]={"error":str(e)[:700]}
    dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True)
    (dest/"observed_schema_samples.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BEGIN_GBIF_ANON_PARQUET_SAMPLES")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    print("END_GBIF_ANON_PARQUET_SAMPLES")


if __name__=="__main__":
    main()
