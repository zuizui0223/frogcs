#!/usr/bin/env python3
"""v5.3 source-unit reuse audit: actual public Murrumbidgee Flow-MER.

Exploratory post-outcome source quality only; source protocol frozen in
V5_3_CEWO_FIELD_PROTOCOL_AND_SPECIES_STAGE_GRAIN_QA_CONTRACT.md.
Never reports raw site/species IDs or individual CPUE/calling values.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from decimal import Decimal,InvalidOperation
import datetime as dt
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

RESOURCE="70f3b7c9-990b-4770-b306-57c4e7cdac61"
API="https://data.gov.au/data/api/3/action/datastore_search"
FIELDS=["Program","SamplePoint","SampleDate","sampleDateStart",
        "sampleDateEnd(Date/Time)","speciesCode","callingEvidence","CPUETadpoles"]
ALLOWED=set(FIELDS)
REGION="Murrumbidgee River"

def parse(x):
    try:
        val=str(x or "").replace("Z","+00:00")
        d=dt.datetime.fromisoformat(val)
        return d.replace(tzinfo=None) if not d.tzinfo else d.astimezone(dt.timezone.utc).replace(tzinfo=None)
    except (ValueError,TypeError):
        return None

def audit(payload):
    if payload.get("success") is not True:
        raise ValueError("source not available")
    result=payload.get("result") or {}
    rec=result.get("records")
    if not isinstance(rec,list) or len(rec)==0 or len(rec)!=result.get("total") or len(rec)>1500:
        raise ValueError("incomplete source record set")
    seen_fields={f.get("id") for f in result.get("fields",[]) if isinstance(f,dict)}
    if seen_fields!=ALLOWED:
        raise ValueError("wrong source projection; refuse geocoded or extra fields")
    one_key=defaultdict(list)
    reg_n=0
    excluded=Counter()
    for r in rec:
        if not isinstance(r,dict) or set(r)-ALLOWED-{"_id"}:
            raise ValueError("row unexpected fields")
        if str(r.get("Program") or "").strip()!=REGION:
            continue
        reg_n+=1
        site=str(r.get("SamplePoint") if r.get("SamplePoint") is not None else "").strip()
        species=str(r.get("speciesCode") if r.get("speciesCode") is not None else "").strip()
        stamp=parse(r.get("SampleDate"))
        start=parse(r.get("sampleDateStart"))
        end=parse(r.get("sampleDateEnd(Date/Time)"))
        if not site or not species or stamp is None or start is None or end is None:
            excluded["missing_original_key_or_dates"]+=1
            continue
        length=(end-start).total_seconds()/86400
        if length<=0:
            excluded["zero_or_negative_period"]+=1
            continue
        if length<=31:
            excluded["short_or_31_day_period"]+=1
            continue
        status=str(r.get("callingEvidence") or "").strip().upper()
        if status not in {"Y","N"}:
            excluded["invalid_calling_code"]+=1
            continue
        try:
            cpue=Decimal(str(r.get("CPUETadpoles")))
        except (InvalidOperation,TypeError):
            excluded["invalid_cpue"]+=1
            continue
        if not cpue.is_finite() or cpue<0:
            excluded["invalid_cpue"]+=1
            continue
        key=(site,species,start.isoformat(),end.isoformat())
        one_key[key].append((status,cpue))
    duplicates={key for key,val in one_key.items() if len(val)>1}
    excluded["duplicate_site_species_interval_keys"]=len(duplicates)
    excluded["rows_removed_duplicate_site_species_interval"]=sum(len(one_key[k]) for k in duplicates)

    events=defaultdict(dict)
    for (site,sp,start,end),rows in one_key.items():
        if len(rows)!=1:
            continue
        events[(site,start,end)][sp]=rows[0]

    n_species_per_event=Counter()
    kinds=Counter()
    tadpole_positive_interval=0
    y_n_mixed_and_cpue_positive=0
    for event, species in events.items():
        n=len(species)
        n_species_per_event[n]+=1
        values=[entry[1] for entry in species.values()]
        statuses=[entry[0] for entry in species.values()]
        positives=[v for v in values if v>0]
        if positives:
            tadpole_positive_interval+=1
        if n>=2:
            kinds["multi_species_intervals"]+=1
            if len(set(values))==1:
                kinds["all_species_cpue_equal_including_zero"]+=1
                if values[0]>0:
                    kinds["all_species_cpue_equal_POSITIVE"]+=1
                else:
                    kinds["all_species_cpue_equal_ALL_ZERO"]+=1
            else:
                kinds["species_cpue_heterogeneous"]+=1
            pos_counts=Counter(positives)
            if any(c>=2 for c in pos_counts.values()):
                kinds["positive_cpue_shared_by_2plus_species"]+=1
            if len(set(statuses))>1:
                kinds["both_call_Y_and_N_species_in_same_interval"]+=1
                if positives:
                    y_n_mixed_and_cpue_positive+=1

    return {
        "status":"REAL_SOURCE_SITE_INTERVAL_SPECIES_GRAIN_QA_COMPLETE",
        "dataset":"Australian Government Flow-MER Frog Abundance 2014-2022",
        "n_government_rows_total":len(rec),
        "n_murrumbidgee_rows_before_exclusion":reg_n,
        "n_unique_species_site_interval_keys_post_exclusion":sum(map(len,events.values())),
        "n_unique_site_intervals_post_exclusion":len(events),
        "interval_n_listed_species_histogram":dict(sorted(n_species_per_event.items())),
        "source_interval_with_any_positive_tadpole_cpue_count":tadpole_positive_interval,
        "multi_species_interval_equality_counters":dict(sorted(kinds.items())),
        "mixed_call_status_and_positive_cpue_intervals":y_n_mixed_and_cpue_positive,
        "excluded_source_rows_or_keys":dict(sorted(excluded.items())),
        "no_individual_species_or_site_ids_output":True,
        "no_per_record_cpue_or_calling_values_output":True,
        "positive_equal_cpue_across_species_is_NOT_PROOF_of_taxon_misassignment":True,
        "historical_genus_pooled_tadpole_source_requires_crosswalk":True,
        "no_rain_or_breeding_success_effect_fit":True,
        "JAE_RC6_main_unchanged":True
    }

def synthetic_tests():
    headers=[{"id":v} for v in FIELDS]
    def record(site,sp,c,t):
        return {"Program":REGION,"SamplePoint":site,"speciesCode":sp,
                "SampleDate":"2018-05-01T00:00:00",
                "sampleDateStart":"2018-01-01T00:00:00",
                "sampleDateEnd(Date/Time)":"2019-01-01T00:00:00",
                "callingEvidence":c,"CPUETadpoles":str(t)}
    rows=[record("A","sp1","Y",2.5),record("A","sp2","N",2.5),
          record("A","sp3","Y",0),record("B","sp1","Y",0),
          record("B","sp2","N",0)]
    x={"success":True,"result":{"total":len(rows),"records":rows,"fields":headers}}
    q=audit(x)
    assert q["n_unique_site_intervals_post_exclusion"]==2
    assert q["multi_species_interval_equality_counters"]["positive_cpue_shared_by_2plus_species"]==1
    assert q["multi_species_interval_equality_counters"]["all_species_cpue_equal_ALL_ZERO"]==1
    for bad in (
        {"success":True,"result":{"total":len(rows)+1,"records":rows,"fields":headers}},
        {"success":True,"result":{"total":len(rows),"records":rows,
                                    "fields":headers+[{"id":"Latitude"}]}},
        {"success":True,"result":{"total":len(rows),"records":[dict(rows[0],Latitude=1)]+rows[1:],
                                    "fields":headers}},
    ):
        try:audit(bad)
        except ValueError:pass
        else:raise AssertionError("invalid payload allowed")
    print("PASS: source species×site×long-interval duplicates, positive-CPUE ties, no sensitive fields, no ecological inference")

def main():
    synthetic_tests()
    query=urllib.parse.urlencode({"resource_id":RESOURCE,"limit":1000,"fields":",".join(FIELDS)})
    receipt={"status":"PUBLIC_SOURCE_NOT_CONFIRMED",
             "source_frozen_plan":"studies/climate_landscape/V5_3_CEWO_FIELD_PROTOCOL_AND_SPECIES_STAGE_GRAIN_QA_CONTRACT.md"}
    try:
        request=urllib.request.Request(API+"?"+query,headers={
           "Accept":"application/json","User-Agent":"frogcs-study-v5.3-origin-unit-audit"})
        with urllib.request.urlopen(request,timeout=45) as resp:
            raw=resp.read(1600000)
            if resp.status!=200 or len(raw)>=1600000:
                raise ValueError("size or status")
        receipt.update(audit(json.loads(raw.decode("utf-8"))))
    except urllib.error.HTTPError as e:
        receipt.update(status="HTTP_SOURCE_UNAVAILABLE",http_code=e.code)
    except (urllib.error.URLError,TimeoutError) as e:
        receipt.update(status="NETWORK_SOURCE_UNAVAILABLE",error_type=type(e).__name__)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:
        receipt.update(status="SOURCE_GRAIN_QA_FAILED_CLOSED",error_type=type(e).__name__,
                       note=str(e)[:120])
    output=Path("studies/climate_landscape/receipts/FLOWMER_REAL_REPEATED_CPUE_SPECIES_GRAIN_V53.json")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,sort_keys=True))

if __name__=="__main__":
    main()
