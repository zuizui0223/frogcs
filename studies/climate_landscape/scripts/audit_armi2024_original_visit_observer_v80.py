#!/usr/bin/env python3
"""Original USGS April 2026 v1.1 frog call survey design audit, no ecological effect.

Source predeclared in USGS_ARMI_2024_PUBLIC_SURVEY_OBSERVER_OPPORTUNITY_GATE.md.
No individual site, location, observer, exact timestamp or frog taxon identity
is emitted. All data from original public USGS ScienceBase and USGS metadata.
"""
from __future__ import annotations
import csv,hashlib,io,json,re,statistics
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree
import audit_usgs_armi2024_public_survey_schema_v80 as src

METADATA_XML=f"https://data.usgs.gov/datacatalog/metadata/USGS.{src.ITEM}.xml"
OUTPUT="studies/climate_landscape/receipts/USGS_ARMI2024_PUBLIC_OBSERVER_VISIT_GRAIN_V80.json"
SPECIES_NO_CALL_ALIASES={"NONE","NO FROGS","NO FROGS HEARD","NO CALLS","NO FROGS DETECTED",
                         "NO SPECIES","NONE HEARD","0","NO FROG"}
EXPECTED_SHA256="dafd388c7ccb79e08dbadd37a25c604473a8caf4ff5c8318532740acb56a04e4"

def get_source():
    raw_meta=src.get_public(src.META,1000000)
    item=json.loads(raw_meta)
    if item.get("id")!=src.ITEM: raise ValueError("SOURCE_ID_CHANGED")
    files=[f for f in item.get("files",[]) if f.get("name")==src.FILENAME]
    if len(files)!=1 or files[0].get("size")!=src.EXPECTED_BYTES:
        raise ValueError("SOURCE_FILE_ID_CHANGED")
    raw=src.get_public(files[0]["downloadUri"],src.MAX_SIZE)
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA256:
        raise ValueError("ORIGINAL_RELEASE_DATA_CHANGED")
    return raw

def codebook(xml_bytes):
    root=ElementTree.fromstring(xml_bytes)
    requested={"Date","Arrival_time","Project","Site","Site_original",
               "Observer","Method","Species","Number_heard","Wind_Beaufort",
               "Cloud_cover_percent","Compass_direction"}
    result={}
    for attr in root.findall(".//attr"):
        def elem(name):
            a=attr.find(name)
            return "".join(a.itertext()).strip() if a is not None else ""
        label=elem("attrlabl")
        if label not in requested: continue
        defval=elem("attrdef")
        source=elem("attrdefs")
        allowed=[]
        for edom in attr.findall(".//edom"):
            v="".join(edom.find("edomv").itertext()).strip() if edom.find("edomv") is not None else ""
            desc="".join(edom.find("edomvd").itertext()).strip() if edom.find("edomvd") is not None else ""
            if label in {"Number_heard","Method"} and len(allowed)<25:
                allowed.append({"value":v[:100],"definition":desc[:180]})
        result[label]={"source_definition":defval[:700],
                       "definition_source":source[:200],
                       "allowed_value_definitions":allowed}
    return result

def to_minutes(v):
    s=(v or "").strip()
    for fmt in ("%H:%M","%H:%M:%S","%I:%M %p","%I:%M:%S %p"):
        try:
            dt=datetime.strptime(s,fmt)
            return dt.hour*60+dt.minute+dt.second/60
        except ValueError:
            pass
    return None

def survey_grain(raw):
    rd=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    required={"Site","Date","Observer","Arrival_time","Method",
              "Species","Number_heard","Wind_Beaufort","Cloud_cover_percent"}
    if not rd.fieldnames or not required.issubset(rd.fieldnames):
        raise ValueError("ORIGINAL_REQUIRED_FIELDS_MISSING")
    rows=0
    cell=defaultdict(lambda:{"n":0,"methods":set(),"times":set(),"species":set(),"numbers":[]})
    site_days=defaultdict(set)
    site_dates=defaultdict(set)
    original_site_map=defaultdict(set)
    by_date=Counter(); methods=Counter(); number_counts=Counter()
    species_no_call_literal=Counter()
    observer_counts=Counter()
    unique_species=set()
    for r in rd:
        rows+=1
        if rows>100000 or None in r: raise ValueError("SOURCE_ROWS_INVALID")
        site=r["Site"].strip()
        day=r["Date"].strip()
        observer=r["Observer"].strip()
        if not site or not day or not observer:raise ValueError("MISSING_EVENT_ID_SOURCE")
        if not re.fullmatch(r"2024[-/]\d\d[-/]\d\d",day):
            raise ValueError("DATE_FORMAT_NOT_AS_EXPECTED")
        key=(site,day,observer)
        cur=cell[key]
        cur["n"]+=1
        cur["methods"].add((r["Method"] or "").strip())
        cur["times"].add((r["Arrival_time"] or "").strip())
        cur["species"].add((r["Species"] or "").strip())
        site_days[site].add(day)
        site_dates[(site,day)].add(observer)
        original_site_map[site].add((r["Site_original"] or "").strip())
        observer_counts[observer]+=1
        meth=(r["Method"] or "").strip(); methods[meth]+=1
        spe=(r["Species"] or "").strip()
        if spe:
            unique_species.add(spe)
        if spe.upper() in SPECIES_NO_CALL_ALIASES:
            species_no_call_literal["known_generic_no_call_alias"]+=1
        n=(r["Number_heard"] or "").strip()
        if n in {"", "NA", "N/A"}:
            number_counts["MISSING"]+=1
        else:
            try:
                num=float(n)
                if num==0:number_counts["EXPLICIT_ZERO"]+=1
                elif num>0:number_counts["POSITIVE_NUMBER"]+=1
                else:number_counts["NEGATIVE_NUMBER"]+=1
            except ValueError:
                number_counts["OTHER_TEXT_NUMBER"]+=1
    if rows!=1934 or len(site_days)!=343 or len(by_date)>100000:
        raise ValueError("SOURCE_ROW_OR_SITE_COUNT_CHANGED")
    counts=Counter()
    time_gap_pairs=[]
    methods_diff_pairs=0
    paired=0
    time_unparsable=0
    extra_time_keys=0
    multi_method_keys=0
    site_day_key_count=len(site_dates)
    # Observer-A/B same site and date can be different actual listening time.
    for (site,day),obs_set in site_dates.items():
        if len(obs_set)>=2:
            paired+=1
            if len(obs_set)!=2:
                counts["three_or_more_observer_names_per_site_day"]+=1
            obs=list(obs_set)
            aa=cell[(site,day,obs[0])]
            bb=cell[(site,day,obs[1])]
            if aa["methods"] != bb["methods"]:
                methods_diff_pairs+=1
            if len(aa["times"])==1 and len(bb["times"])==1:
                t1=to_minutes(next(iter(aa["times"])))
                t2=to_minutes(next(iter(bb["times"])))
                if t1 is None or t2 is None:time_unparsable+=1
                else:time_gap_pairs.append(min(abs(t1-t2),1440-abs(t1-t2)))
            else:time_unparsable+=1
    counts_event_rows=Counter(cur["n"] for cur in cell.values())
    site_days_lengths=list(map(len,site_days.values()))
    pairs_per_site=Counter(site for site,day in site_dates if len(site_dates[(site,day)])>=2)
    all_time_multisets=sum(len(cur["times"])>1 for cur in cell.values())
    all_method_multisets=sum(len(cur["methods"])>1 for cur in cell.values())
    across_site_date_repeats=sum(n>=2 for n in site_days_lengths)
    category_dates=Counter()
    for site,dates in site_days.items():
        for day in dates:category_dates[day[5:7]]+=1
    return {
      "status":"SURVEY_DESIGN_SOURCE_GRAIN_ONLY_NO_ANIMAL_RESPONSE_TEST",
      "n_source_species_rows":rows,
      "n_original_field_site_ids":len(site_days),
      "n_distinct_survey_calendar_dates":len(set(day for _,day in site_dates)),
      "n_distinct_site_x_date_source_keys":site_day_key_count,
      "n_distinct_site_x_date_x_observer_source_keys":len(cell),
      "n_source_observer_name_categories":len(observer_counts),
      "n_site_dates_with_2plus_observers":paired,
      "n_sites_with_2plus_distinct_survey_dates":across_site_date_repeats,
      "n_sites_with_at_least_one_pair_of_observers":len(pairs_per_site),
      "n_site_dates_where_two_observers_have_different_methods":methods_diff_pairs,
      "n_site_dates_paired_with_parseable_separate_arrival_times":len(time_gap_pairs),
      "n_site_dates_paired_with_unparseable_or_ambiguous_arrival_times":time_unparsable,
      "paired_observer_arrival_minute_gaps_minmedianmax":
         [min(time_gap_pairs),statistics.median(time_gap_pairs),max(time_gap_pairs)]
         if time_gap_pairs else [None,None,None],
      "n_source_keys_with_multiple_arrival_times":all_time_multisets,
      "n_source_keys_with_multiple_methods":all_method_multisets,
      "rows_per_site_date_observer_key_minmedianmax":
          [min(c["n"] for c in cell.values()),
           statistics.median(c["n"] for c in cell.values()),
           max(c["n"] for c in cell.values())],
      "n_original_site_labels_with_multiple_SourceSite_original_labels":sum(
          len(vals)>1 for vals in original_site_map.values()),
      "n_original_species_field_distinct_literal_values":len(unique_species),
      "species_field_recognized_generic_no_call_literal_rows":
         sum(species_no_call_literal.values()),
      "number_heard_value_format_counts":dict(number_counts),
      "method_literal_counts_not_personal_identifiers":dict(sorted(methods.items())),
      "site_date_opportunity_month_histogram":dict(sorted(category_dates.items())),
      "n_original_site_labels_and_observer_labels_published":0,
      "site_x_date_x_observer_is_a_COMPLETE_VISIT_LEDGER":"PENDING_DICTIONARY_INTERPRETATION",
      "n_deduplicated_observer_pair_species_agreements_computed":0,
      "all_zero_and_blank_source_species_not_inferred":True,
    }

def tests():
    mock="Site,Site_original,Date,Observer,Arrival_time,Method,Species,Number_heard,Wind_Beaufort,Cloud_cover_percent\n"
    mock+="a,a,2024-06-06,SECRET_1,20:12,ear,Frog1,2,1,20\n"
    mock+="a,a,2024-06-06,SECRET_1,20:12,ear,Frog2,0,1,20\n"
    mock+="a,a,2024-06-06,SECRET_2,20:18,ear,Frog1,1,1,20\n"
    mock+="b,b,2024-06-07,SECRET_1,20:44,microphone,Frog3,1,1,20\n"
    # test helpers without asserting the 1934-row original source guard
    assert to_minutes("20:12")==1212
    assert to_minutes("08:12 PM")==1212
    assert to_minutes("??") is None
    tmp=list(csv.DictReader(io.StringIO(mock)))
    assert len({(r["Site"],r["Date"],r["Observer"]) for r in tmp})==3
    assert len({(r["Site"],r["Date"]) for r in tmp})==2
    assert len({r["Observer"] for r in tmp})==2
    print("PASS: survey key grain mock and clock conversion, no source biology outcome selected")

def main():
    tests()
    raw=get_source()
    # Original government FGDC dictionary may use different vocabulary;
    # stop before interpreting species zeros without observed source terms.
    from urllib.request import Request,urlopen
    with urlopen(Request(METADATA_XML,headers={"User-Agent":"frogcs-original-FGDC-schema-only/8.0"}),
                timeout=35) as r:
        if r.status!=200:raise ValueError("USGS_DICTIONARY_HTTP_STOP")
        xml=r.read(350000)
    if not xml or len(xml)>=350000:raise ValueError("SOURCE_XML_CAP_STOP")
    dictionary=codebook(xml)
    result={
      "version":"2024 USGS ARMI cricket frog public v1.1 April 2026",
      "doi":"https://doi.org/10.5066/P19ZCGWM",
      "release_item_id":src.ITEM,
      "input_original_csv_sha256":hashlib.sha256(raw).hexdigest(),
      "input_original_fgdc_sha256":hashlib.sha256(xml).hexdigest(),
      "original_attribute_definitions_selected_no_individual_values":dictionary,
      "source_grain":survey_grain(raw),
      "survey_no_frog_opportunity_ledger_validated":False,
      "any_NA_used_as_negative":False,
      "no_coordinates_or_personal_names_exported":True,
      "no_ecological_effect_test_or_specification_refit":True,
      "rc6_main_not_changed":True
    }
    p=Path(OUTPUT);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SURVEY_GRANULARITY "+json.dumps(result,sort_keys=True))

if __name__=="__main__":main()
