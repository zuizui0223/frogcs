#!/usr/bin/env python3
"""v5.4 exploratory source taxon crosswalk of CPUE ties in government Flow-MER.

Plan was COMMITTED before this particular taxonomic CPUE-tie read:
V5_4_TADPOLE_GENUS_POOLING_TAXON_CROSSWALK_GATE.md
All research is post-v5.2 outcome-exposure. NO ecological effect estimated.
Uses speciesName only in memory; outputs non-identifying COUNTS ONLY.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import datetime as dt
import json
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

API="https://data.gov.au/data/api/3/action/datastore_search"
RESOURCE="70f3b7c9-990b-4770-b306-57c4e7cdac61"
FIELDS=("Program","SamplePoint","SampleDate","sampleDateStart",
        "sampleDateEnd(Date/Time)","speciesCode","speciesName",
        "callingEvidence","CPUETadpoles")
REGION="Murrumbidgee River"
EXPECTED_PREVIOUS={"all":673,"region":591,"after_filter":579,
                   "interval_groups":98,"intervals_with_positive_ties":7}

def instant(v):
    x=str(v if v is not None else "").strip().replace("Z","+00:00")
    try:
        t=dt.datetime.fromisoformat(x)
        return t if t.tzinfo is None else t.astimezone(dt.timezone.utc).replace(tzinfo=None)
    except ValueError:
        return None

def genus(name):
    """Parse only defensible canonical genus; unknowns remain unknown."""
    s=str(name or "").strip().replace("×","").strip()
    word=s.split(" ",1)[0] if s else ""
    if not word.isalpha() or not word[0:1].isupper() or not word[1:].islower():
        return None
    return word

def audit(obj):
    if not isinstance(obj,dict) or obj.get("success") is not True:
        raise ValueError("no successful public source")
    result=obj.get("result") or {}
    rows=result.get("records")
    schema={x.get("id") for x in result.get("fields",[]) if isinstance(x,dict)}
    if schema!=set(FIELDS) or not isinstance(rows,list) or len(rows)>1500 or len(rows)!=result.get("total"):
        raise ValueError("wrong data projection or incomplete public source")
    by_species_event=defaultdict(list)
    code_to_names=defaultdict(set)
    anomalies=Counter()
    region_n=0
    for r in rows:
        if not isinstance(r,dict) or set(r)-set(FIELDS)-{"_id"}:
            raise ValueError("unexpected sensitive or unapproved column")
        if str(r.get("Program") or "").strip()!=REGION:
            continue
        region_n+=1
        site=str(r.get("SamplePoint") if r.get("SamplePoint") is not None else "").strip()
        code=str(r.get("speciesCode") if r.get("speciesCode") is not None else "").strip()
        name=str(r.get("speciesName") if r.get("speciesName") is not None else "").strip()
        samp=instant(r.get("SampleDate"))
        start=instant(r.get("sampleDateStart"))
        end=instant(r.get("sampleDateEnd(Date/Time)"))
        if not site or not code or not samp or not start or not end:
            anomalies["missing_source_key_or_datetime"]+=1
            continue
        days=(end-start).total_seconds()/86400
        if days<=0:
            anomalies["nonpositive_duration"]+=1
            continue
        if days<=31:
            anomalies["short_duration"]+=1
            continue
        if name:
            code_to_names[code].add(" ".join(name.split()).casefold())
        else:
            anomalies["blank_speciesName_rows"]+=1
        if genus(name) is None:
            anomalies["genus_unparseable_rows"]+=1
        try:
            cpue=Decimal(str(r.get("CPUETadpoles")))
        except (InvalidOperation,TypeError):
            anomalies["invalid_tadpole_cpue"]+=1
            continue
        if not cpue.is_finite() or cpue<0:
            anomalies["negative_or_nonfinite_tadpole_cpue"]+=1
            continue
        key=(site,code,start.isoformat(),end.isoformat())
        by_species_event[key].append((name,cpue))
    duplicated={k for k,v in by_species_event.items() if len(v)>1}
    anomalies["duplicate_source_species_site_interval_keys"]=len(duplicated)
    anomalies["rows_from_duplicate_keys_removed"]=sum(len(by_species_event[k]) for k in duplicated)
    events=defaultdict(dict)
    for (site,code,start,end),v in by_species_event.items():
        if len(v)==1:
            events[(site,start,end)][code]=v[0]
    positive_tie_intervals=0
    pair_types=Counter()
    events_by_pair_type=Counter()
    n_lg_rows=0
    n_lg_positive=0
    n_lg_interval_groups=set()
    genus_only_name_rows=0
    for event,codes in events.items():
        positives_by_value=defaultdict(list)
        for code,(name,cpue) in codes.items():
            g=genus(name)
            if g=="Limnodynastes":
                n_lg_rows+=1
                n_lg_interval_groups.add(event)
                if cpue>0:n_lg_positive+=1
            if "sp." in name.lower() or "spp." in name.lower():
                genus_only_name_rows+=1
            if cpue>0:
                positives_by_value[cpue].append((code,g))
        interval_types=set()
        for val,entries in positives_by_value.items():
            if len(entries)<2:continue
            for i in range(len(entries)):
                for j in range(i+1,len(entries)):
                    (a,ga),(b,gb)=entries[i],entries[j]
                    if ga is None or gb is None:
                        kind="GENUS_UNDETERMINED"
                    elif ga==gb=="Limnodynastes":
                        kind="BOTH_LIMNODYNSTES_SAME_GENUS"
                    elif ga==gb:
                        kind="BOTH_NON_LIMNODYNSTES_SAME_GENUS"
                    else:
                        kind="CROSS_GENUS"
                    pair_types[kind]+=1
                    interval_types.add(kind)
        if interval_types:
            positive_tie_intervals+=1
            for ty in interval_types:
                events_by_pair_type[ty]+=1
    result={
       "status":"REAL_SOURCE_GENUS_TIE_AUDIT_COMPLETE",
       "original_source_full_record_total":len(rows),
       "region_rows":region_n,
       "records_after_duplicate_and_interval_filter":sum(map(len,events.values())),
       "n_site_interval_groups":len(events),
       "source_positive_CPUE_shared_species_intervals":positive_tie_intervals,
       "positive_tie_species_pair_classifications":dict(sorted(pair_types.items())),
       "positive_tie_interval_classifications_nonexclusive":dict(sorted(events_by_pair_type.items())),
       "source_rows_labeled_Limnodynastes":n_lg_rows,
       "source_positive_CPUE_rows_labeled_Limnodynastes":n_lg_positive,
       "source_interval_groups_containing_Limnodynastes":len(n_lg_interval_groups),
       "genus_only_speciesName_rows":genus_only_name_rows,
       "n_source_speciesCodes_with_multiple_published_speciesNames":sum(len(v)>1 for v in code_to_names.values()),
       "n_source_speciesCodes_with_one_published_speciesName":sum(len(v)==1 for v in code_to_names.values()),
       "source_exclusions_or_quality":dict(sorted(anomalies.items())),
       "published_source_counts_match_prior_v53":all([
           len(rows)==EXPECTED_PREVIOUS["all"],
           region_n==EXPECTED_PREVIOUS["region"],
           sum(map(len,events.values()))==EXPECTED_PREVIOUS["after_filter"],
           len(events)==EXPECTED_PREVIOUS["interval_groups"],
           positive_tie_intervals==EXPECTED_PREVIOUS["intervals_with_positive_ties"]]),
       "data_stage_crosswalk_authenticated":False,
       "equal_positive_CPUE_not_proof_of_taxon_pooling":True,
       "post_outcome_source_QC_not_confirmatory_biological_result":True,
       "new_sign_or_model_fitted":False,
       "no_source_species_names_codes_or_site_identifiers_output":True,
       "no_coordinates_or_free_text_requested":True,
       "JAE_RC6_main_unchanged":True
    }
    return result

def self_test():
    fields=[{"id":f} for f in FIELDS]
    def row(site,code,name,tad):
        return {
            "Program":REGION,"SamplePoint":site,
            "SampleDate":"2018-07-01","sampleDateStart":"2018-01-01",
            "sampleDateEnd(Date/Time)":"2019-01-01",
            "speciesCode":code,"speciesName":name,"callingEvidence":"N",
            "CPUETadpoles":str(tad)
        }
    rs=[
        row("s1","a","Limnodynastes fletcheri","2.5"),
        row("s1","b","Limnodynastes tasmaniensis","2.50"),
        row("s1","c","Litoria peronii","2.5"),
        row("s1","d","Crinia parinsignifera",0),
        row("s2","a","Limnodynastes fletcheri",0),
    ]
    obj={"success":True,"result":{"total":len(rs),"fields":fields,"records":rs}}
    out=audit(obj)
    assert out["source_positive_CPUE_shared_species_intervals"]==1
    assert out["positive_tie_species_pair_classifications"]["BOTH_LIMNODYNSTES_SAME_GENUS"]==1
    assert out["positive_tie_species_pair_classifications"]["CROSS_GENUS"]==2
    assert out["source_rows_labeled_Limnodynastes"]==3
    invalid=[
      {"success":True,"result":{"total":5,"fields":fields+[{"id":"Latitude"}],"records":rs}},
      {"success":True,"result":{"total":6,"fields":fields,"records":rs}},
      {"success":True,"result":{"total":5,"fields":fields,"records":[dict(rs[0],Latitude=1)]+rs[1:]}},
    ]
    for test in invalid:
        try:audit(test)
        except ValueError:pass
        else:raise AssertionError("unsafe schema accepted")
    print("PASS: exact positive CPUE pair genus comparison and source-name mapping; no biological model or raw site outputs")

def main():
    self_test()
    query=urllib.parse.urlencode({
        "resource_id":RESOURCE,"limit":1000,"fields":",".join(FIELDS)})
    receipt={
        "status":"OFFICIAL_SOURCE_NOT_ACCESSED",
        "plan_committed_first":"studies/climate_landscape/V5_4_TADPOLE_GENUS_POOLING_TAXON_CROSSWALK_GATE.md",
        "only_aggregate_taxon_source_QC":True
    }
    try:
        req=urllib.request.Request(API+"?"+query,headers={"Accept":"application/json",
            "User-Agent":"frogcs-FlowMER-v54-genus-taxon-source-QC"})
        with urllib.request.urlopen(req,timeout=40) as resp:
            dat=resp.read(1800000)
            if resp.status!=200 or len(dat)>=1800000:
                raise ValueError("unexpected public source length/status")
        receipt.update(audit(json.loads(dat.decode("utf-8"))))
    except urllib.error.HTTPError as e:
        receipt.update(status="HTTP_UNAVAILABLE",http_code=e.code)
    except (urllib.error.URLError,TimeoutError) as e:
        receipt.update(status="SOURCE_NETWORK_UNAVAILABLE",error_type=type(e).__name__)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:
        receipt.update(status="SOURCE_SCHEMA_QC_FAILED_CLOSED",error_type=type(e).__name__,
                       error=str(e)[:160])
    out=Path("studies/climate_landscape/receipts/FLOWMER_TADPOLE_GENUS_CROSSWALK_V54.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,sort_keys=True))

if __name__=="__main__":
    main()
