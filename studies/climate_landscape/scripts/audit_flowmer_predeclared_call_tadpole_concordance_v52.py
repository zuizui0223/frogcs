#!/usr/bin/env python3
"""v5.2: FROZEN descriptive Flow-MER interval-scale calling vs tadpole CPUE.

This is NOT JAE frogcs RC6 and NOT a rain/weather/metamorph mechanism test.
Plan was committed before any Y/N frequencies or CPUE-positive frequencies:
V5_2_PRE_RESPONSE_PERIOD_LEVEL_CALLING_TADPOLE_CONCORDANCE_CONTRACT.md

Only public CKAN fields approved in plan; sensitive coordinates, species names
and free text are never requested; site and species IDs are kept in memory
for clustering, never written to a receipt or printed.
"""
from __future__ import annotations
import collections
import datetime as dt
import json
import math
import random
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE="https://data.gov.au/data/api/3/action/datastore_search"
RESOURCE="70f3b7c9-990b-4770-b306-57c4e7cdac61"
FIELDS=("Program","SamplePoint","SampleDate","sampleDateStart",
        "sampleDateEnd(Date/Time)","speciesCode","callingEvidence","CPUETadpoles")
REGION="Murrumbidgee River"
MAX_ROWS=1500
MAX_BYTES=1_500_000
SEED=20261010
BOOTSTRAP_DRAWS=1000

def timestamp(x):
    raw=str(x if x is not None else "").strip()
    if not raw:
        return None
    text=raw.replace("Z","+00:00")
    try:
        t=dt.datetime.fromisoformat(text)
        return t if t.tzinfo is None else t.astimezone(dt.timezone.utc).replace(tzinfo=None)
    except ValueError:
        pass
    for fmt in ("%d/%m/%Y","%d/%m/%Y %H:%M:%S","%m/%d/%Y %H:%M:%S"):
        try:return dt.datetime.strptime(raw,fmt)
        except ValueError:continue
    return None

def positive_cpue(value):
    try:
        x=float(value)
    except (ValueError,TypeError):
        return None
    return (x>0) if math.isfinite(x) and x>=0 else None

def percentile(sorted_values,fraction):
    if not sorted_values:return None
    idx=(len(sorted_values)-1)*fraction
    lo=int(math.floor(idx))
    hi=int(math.ceil(idx))
    if lo==hi:return sorted_values[lo]
    return sorted_values[lo]*(hi-idx)+sorted_values[hi]*(idx-lo)

def build(payload):
    if not isinstance(payload,dict) or payload.get("success") is not True:
        raise ValueError("official API source not available")
    obj=payload.get("result") or {}
    rows=obj.get("records")
    if not isinstance(rows,list) or not 0<len(rows)<=MAX_ROWS or obj.get("total")!=len(rows):
        raise ValueError("source record count incomplete/unexpected")
    schema={x.get("id") for x in obj.get("fields",[]) if isinstance(x,dict)}
    if schema!=set(FIELDS):
        raise ValueError("unsafe or incomplete source columns")
    parsed=[]
    excluded=collections.Counter()
    by_key=collections.defaultdict(list)
    selected_region=0
    for row in rows:
        if not isinstance(row,dict) or set(row)-set(FIELDS)-{"_id"}:
            raise ValueError("unexpected response or location fields")
        if str(row.get("Program") or "").strip()!=REGION:
            continue
        selected_region+=1
        site=str(row.get("SamplePoint") if row.get("SamplePoint") is not None else "").strip()
        sp=str(row.get("speciesCode") if row.get("speciesCode") is not None else "").strip()
        d=timestamp(row.get("SampleDate"))
        start=timestamp(row.get("sampleDateStart"))
        end=timestamp(row.get("sampleDateEnd(Date/Time)"))
        if start is None or end is None or d is None or not site or not sp:
            excluded["missing_source_key_or_timestamp"]+=1
            continue
        interval=(end-start).total_seconds()/86400.
        if interval<=0:
            excluded["zero_or_reversed_interval"]+=1
            continue
        if interval<=31:
            excluded["nonlong_interval"]+=1
            continue
        c=str(row.get("callingEvidence") or "").strip().upper()
        tad=positive_cpue(row.get("CPUETadpoles"))
        if c not in ("Y","N") or tad is None:
            excluded["invalid_original_YN_or_tadpole_CPUE"]+=1
            continue
        if max(len(site),len(sp))>120:
            raise ValueError("oversized field content")
        record={"site":site,"species":sp,"key":(site,sp,start.isoformat(),end.isoformat()),
                "C":int(c=="Y"),"T":int(tad)}
        by_key[record["key"]].append(record)
    duplicated_keys=[k for k,v in by_key.items() if len(v)>1]
    excluded["nonunique_species_site_interval_groups"]=len(duplicated_keys)
    excluded["records_from_nonunique_groups_removed"]=sum(len(by_key[k]) for k in duplicated_keys)
    for key,group in by_key.items():
        if len(group)==1:
            parsed.append(group[0])

    cells=collections.Counter((r["C"],r["T"]) for r in parsed)
    n_c1=sum(cells[(1,t)] for t in (0,1))
    n_c0=sum(cells[(0,t)] for t in (0,1))
    n_nz=sum(cells[(c,1)] for c in (0,1))
    p_y=cells[(1,1)]/n_c1 if n_c1 else None
    p_n=cells[(0,1)]/n_c0 if n_c0 else None
    delta=p_y-p_n if p_y is not None and p_n is not None else None

    site_rows=collections.defaultdict(list)
    pair_rows=collections.defaultdict(list)
    for r in parsed:
        site_rows[r["site"]].append((r["C"],r["T"]))
        pair_rows[(r["site"],r["species"])].append((r["C"],r["T"]))
    within_pairs=[]
    within_rows=0
    eligible_pair_keys=set()
    within_pairs_by_site=collections.defaultdict(list)
    for key,values in pair_rows.items():
        if {c for c,t in values}=={0,1}:
            t_y=[t for c,t in values if c==1]
            t_n=[t for c,t in values if c==0]
            difference=sum(t_y)/len(t_y)-sum(t_n)/len(t_n)
            within_pairs.append(difference)
            within_pairs_by_site[key[0]].append(difference)
            eligible_pair_keys.add(key)
            within_rows+=len(values)
    within_admissible=(len(within_pairs)>=10 and within_rows>=20)
    # POST-OUTCOME QC ONLY (not an additional frozen main comparison):
    # Compare the pooled sign using the EXACT same 58 both-state pairs to
    # separate target-subpopulation effects from equal-pair weighting effects.
    restricted=[r for r in parsed if (r["site"],r["species"]) in eligible_pair_keys]
    restricted_cells=collections.Counter((r["C"],r["T"]) for r in restricted)
    restricted_y=sum(restricted_cells[(1,t)] for t in (0,1))
    restricted_n=sum(restricted_cells[(0,t)] for t in (0,1))
    restricted_pooled_delta=(restricted_cells[(1,1)]/restricted_y -
                             restricted_cells[(0,1)]/restricted_n) if restricted_y and restricted_n else None
    # Retrospective, explicitly labelled site-resampling sensitivity to
    # paired equally weighted contrast (not a preregistered CI).
    paired_sites=sorted(within_pairs_by_site)
    paired_boot=[]
    rng2=random.Random(SEED)
    if within_admissible and paired_sites:
        for i in range(BOOTSTRAP_DRAWS):
            draw=[paired_sites[rng2.randrange(len(paired_sites))] for _ in paired_sites]
            tmp=[v for site in draw for v in within_pairs_by_site[site]]
            paired_boot.append(sum(tmp)/len(tmp))
    paired_boot.sort()

    # Site-cluster bootstrap as frozen, no p-values and no fitting.
    boot=[]
    sites=sorted(site_rows)
    rng=random.Random(SEED)
    if delta is not None and sites:
        for i in range(BOOTSTRAP_DRAWS):
            draw=[sites[rng.randrange(len(sites))] for _ in sites]
            n1=n0=y1=y0=0
            for key in draw:
                for c,t in site_rows[key]:
                    if c:
                        n1+=1
                        y1+=t
                    else:
                        n0+=1
                        y0+=t
            if n1 and n0:
                boot.append(y1/n1-y0/n0)
    boot.sort()
    return {
        "status":"FROZEN_DESCRIPTIVE_SOURCE_CONCORDANCE_COMPLETE",
        "source":"Australian government Flow-MER Frog Abundance 2014-2022",
        "source_resource_id":RESOURCE,
        "region":REGION,
        "published_rows":len(rows),
        "region_rows_before_exclusions":selected_region,
        "predeclared_long_interval_eligible_rows_after_source_deduplication":len(parsed),
        "excluded_counts":dict(sorted(excluded.items())),
        "n_distinct_sample_sites_anonymized":len(site_rows),
        "n_distinct_species_site_pairs_anonymized":len(pair_rows),
        "n_pairs_with_both_call_Y_and_call_N_on_distinct_intervals":len(within_pairs),
        "n_rows_in_pairs_with_both_call_states":within_rows,
        "n_sample_sites_contributing_eligible_both_state_pairs":len(paired_sites),
        "post_outcome_QC_restricted_to_same_both_state_pairs_pooled_risk_difference":restricted_pooled_delta,
        "post_outcome_QC_restricted_pair_rows_2x2":{
            "call_N_tadpole_zero":restricted_cells[(0,0)],
            "call_N_tadpole_positive":restricted_cells[(0,1)],
            "call_Y_tadpole_zero":restricted_cells[(1,0)],
            "call_Y_tadpole_positive":restricted_cells[(1,1)]
        },
        "post_outcome_QC_within_pair_site_cluster_bootstrap_95pct":[
             percentile(paired_boot,.025),percentile(paired_boot,.975)] if len(paired_boot)>=900 else None,
        "post_outcome_QC_CIs_are_exploratory_not_in_original_frozen_contract":True,
        "two_by_two_source_rows":{
           "call_N_tadpole_zero":cells[(0,0)],
           "call_N_tadpole_positive":cells[(0,1)],
           "call_Y_tadpole_zero":cells[(1,0)],
           "call_Y_tadpole_positive":cells[(1,1)]
        },
        "recorded_tadpole_CPUE_positive_rows":n_nz,
        "proportion_tadpole_positive_given_Y":p_y,
        "proportion_tadpole_positive_given_N":p_n,
        "unadjusted_recorded_interval_risk_difference_Y_minus_N":delta,
        "site_cluster_bootstrap_95pct_interval_for_risk_difference":[
             percentile(boot,.025),percentile(boot,.975)] if len(boot)>=900 else None,
        "valid_bootstrap_draws":len(boot),
        "bootstrap_seed":SEED,
        "within_species_site_equal_pair_weight_mean_risk_difference":
          sum(within_pairs)/len(within_pairs) if within_admissible else None,
        "within_pair_contrast_status":"DESCRIPTIVE_ONLY" if within_admissible else "INSUFFICIENT_WITHIN_PAIR_CALL_VARIATION",
        "claim_scope":"same LONG interval listed-species callingEvidence vs contemporaneous tadpole CPUE-positive index; NOT sequential reproduction, local rain mediation or NAAMP strong chorus",
        "source_missing_species_rows_are_not_zeroes":True,
        "some_intervals_last_over_31_days":True,
        "no_precipitation_or_actual_metamorph_observations":True,
        "no_sensitive_site_coordinates_requested_or_saved":True,
        "no_species_names_codes_or_site_names_published":True,
        "not_a_causal_effect_or_preregistered_confirmation":True,
        "no_p_values_or_posthoc_subgroups":True,
        "JAE_RC6_main_untouched":True
    }

def fake_test():
    meta=[{"id":s,"type":"text"} for s in FIELDS]
    def r(site,sp,year,c,t):
        return {"Program":REGION,"SamplePoint":site,"SampleDate":f"{year}-07-07",
                "sampleDateStart":f"{year}-01-01","sampleDateEnd(Date/Time)":f"{year+1}-01-01",
                "speciesCode":sp,"callingEvidence":c,"CPUETadpoles":t}
    payload={"success":True,"result":{"fields":meta,"total":5,"records":[
        r("A","s1",2017,"Y",1.2),r("A","s1",2018,"N",0),
        r("B","s2",2018,"Y",0),r("B","s2",2019,"N",3),
        r("B","s2",2019,"N",3)]}}
    q=build(payload)
    assert q["region_rows_before_exclusions"]==5
    assert q["excluded_counts"]["nonunique_species_site_interval_groups"]==1
    assert q["excluded_counts"]["records_from_nonunique_groups_removed"]==2
    assert q["predeclared_long_interval_eligible_rows_after_source_deduplication"]==3
    assert q["two_by_two_source_rows"]["call_Y_tadpole_positive"]==1
    assert q["two_by_two_source_rows"]["call_N_tadpole_zero"]==1
    assert q["n_pairs_with_both_call_Y_and_call_N_on_distinct_intervals"]==1
    assert q["within_pair_contrast_status"]=="INSUFFICIENT_WITHIN_PAIR_CALL_VARIATION"
    assert q["post_outcome_QC_restricted_to_same_both_state_pairs_pooled_risk_difference"]==1
    fail={"success":True,"result":{"fields":meta+[{"id":"Latitude"}],"total":5,
            "records":payload["result"]["records"]}}
    try:build(fail)
    except ValueError:pass
    else:raise AssertionError("unapproved precise-coordinate field accepted")
    print("PASS: frozen exclusion/duplicate/2x2 and within-pair gate; no raw frog/site records emitted")

def main():
    fake_test()
    url=BASE+"?"+urllib.parse.urlencode({"resource_id":RESOURCE,
        "limit":1000,"fields":",".join(FIELDS)})
    receipt={"status":"NO_RESPONSE_DATA_ANALYZED","source_resource_id":RESOURCE,
             "plan_frozen_before_YN_or_tadpole_values":
              "studies/climate_landscape/V5_2_PRE_RESPONSE_PERIOD_LEVEL_CALLING_TADPOLE_CONCORDANCE_CONTRACT.md"}
    try:
        req=urllib.request.Request(url,headers={"Accept":"application/json",
            "User-Agent":"frogcs-FlowMER-predeclared-interval-concordance-v52"})
        with urllib.request.urlopen(req,timeout=40) as response:
            buf=response.read(MAX_BYTES+1)
            if response.status!=200 or len(buf)>MAX_BYTES:
                raise ValueError("invalid length or status")
        receipt.update(build(json.loads(buf.decode("utf-8"))))
    except urllib.error.HTTPError as ex:
        receipt.update(status="HTTP_UNAVAILABLE",http_status=ex.code)
    except (urllib.error.URLError,TimeoutError) as ex:
        receipt.update(status="SOURCE_NETWORK_UNAVAILABLE",error_type=type(ex).__name__)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as ex:
        receipt.update(status="FAILED_CLOSED_SCHEMA_OR_RECORD_QC",
                       error_type=type(ex).__name__,error_detail=str(ex)[:150])
    out=Path("studies/climate_landscape/receipts/FLOW_MER_LONG_INTERVAL_CONCORDANCE_V52.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,sort_keys=True))

if __name__=="__main__":
    main()
