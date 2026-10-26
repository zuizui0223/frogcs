#!/usr/bin/env python3
"""Build one comparable, *source-namespaced* amphibian site×month×taxon×stage data layer.

Raw sources are read-only and have pinned digests. All source-specific biology,
sampling effort, stage, dates and zero semantics remain preserved: no GBIF
presence becomes predator density and no acoustic station becomes a pond.
Only aggregate receipts are committed; the rows are workflow artifacts.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import csv
from datetime import date
import gzip
import hashlib
from io import BytesIO,StringIO
import json
from pathlib import Path
import tempfile
from urllib.request import Request,urlopen
from xml.etree import ElementTree as ET

from inbo_stage_taxon_g0 import SOURCES as INBO_SOURCES,part_rows
from part2_published_source_g0 import fetch as inbo_fetch
from nps_glkn_strict_history import fetch_csv as nps_fetch
from nps_glkn_strict_history import SHA256 as NPS_SHA

ROOT=Path(__file__).resolve().parents[2]
HG=ROOT/"research/external/zenodo_15044115"
MD5={"wetland_amp_site_data.csv":"795da443249760fbc0bf30249910a4ef",
     "wetland_amp_surv_data.csv":"edcd6f12518192c01e3dbae8521c16c9"}
FROGS=["Pelobates fuscus","Rana dalmatina","Bombina bombina","Hyla arborea",
       "Pelophylax ridibundus","Bufotes viridis","Bufo bufo"]
NEWTS=["Lissotriton vulgaris","Triturus dobrogicus"]
NAAMP_ITEM="https://www.sciencebase.gov/catalog/item/583dc314e4b0d1899f9dea8d?format=json"
NAAMP_PINS={
 "Runs.csv":"ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730",
 "Stops.csv":"28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f",
 "Counts.csv":"60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086",
}
FIELDS=["source_id","site_token","site_type","location_verification","source_event_token",
 "date","year","month","day_of_year","taxon","stage","survey_method","status",
 "score","source_count_value","effort_n","effort_unit","zero_semantics","source_hydroperiod",
 "rain_days_since","precip_source_value","precip_source_unit","temperature_C",
 "water_depth_source_value","water_depth_source_unit","emergent_cover_percent",
 "submerged_cover_percent","fish_source_observed","site_management_class",
 "original_measurement_scope"]

def check(condition,what):
    if not condition:raise ValueError(what)

def hashed(prefix,raw):
    return prefix+":"+hashlib.sha256((prefix+"|"+str(raw)).encode("utf8")).hexdigest()[:16]

def normalize_status(raw,source):
    s=str(raw or "").strip().lower()
    if s=="present":return "recorded_present"
    if s=="absent":return "recorded_absent"
    return "unknown"

def stage(raw,method):
    if method in ("acoustic","manual_audio","naamp_acoustic","chorus"):return "adult_acoustic"
    s=str(raw or "").strip().lower()
    if s in ("larva","larvae","tadpole","tadpoles","nymph"):return "aquatic_immature"
    if s in ("adult","imago"):return "adult"
    if s in ("metamorph","metamorphosed"):return "metamorph"
    if s in ("egg","eggs","ovum"):return "egg"
    return "unspecified"

def event_date(s):
    try: return date.fromisoformat(str(s)[:10])
    except (ValueError,TypeError):return None

def as_float(x):
    try:
        val=float(x)
        return val if val==val and abs(val)<1e15 else None
    except (TypeError,ValueError):return None

class Sink:
    def __init__(self,target):
        self.fp=gzip.open(target,"wt",encoding="utf8",newline="",compresslevel=6)
        self.writer=csv.DictWriter(self.fp,fieldnames=FIELDS,extrasaction="raise")
        self.writer.writeheader()
        self.count=Counter();self.site=defaultdict(set);self.month=defaultdict(set)
        self.valid=Counter();self.stage_counts=Counter()
        self.status=defaultdict(Counter)
        self.site_month_taxon=defaultdict(lambda:{"total":0,"detected":0,"no_call_or_absent":0,"unknown":0,"max_score":None})
    def emit(self,r):
        for item in ("source_id","site_token","site_type","survey_method","taxon","stage","status","year","month"):
            check(r.get(item) is not None and str(r[item])!="","Missing required canonical field: "+item)
        year=int(r["year"]);mon=int(r["month"])
        check(2000<=year<=2026 and 1<=mon<=12,"Invalid time coordinates")
        d={k:r.get(k) for k in FIELDS}
        self.writer.writerow(d)
        src=r["source_id"]
        self.count[src]+=1;self.site[src].add(r["site_token"]);self.month[src].add((year,mon))
        self.stage_counts[(src,r["stage"],r["survey_method"])]+=1
        self.status[src][r["status"]]+=1
        for key in ("rain_days_since","precip_source_value","water_depth_source_value",
                    "emergent_cover_percent","submerged_cover_percent",
                    "source_hydroperiod","fish_source_observed","temperature_C"):
            if r.get(key) not in (None,""):self.valid[(src,key)]+=1
        k=(src,r["site_token"],year,mon,r["taxon"],r["stage"],r["survey_method"])
        z=self.site_month_taxon[k];z["total"]+=1
        if r["status"]=="recorded_present":z["detected"]+=1
        elif r["status"] in ("recorded_absent","recorded_no_call"):z["no_call_or_absent"]+=1
        else:z["unknown"]+=1
        q=as_float(r.get("score"))
        if q is not None:z["max_score"]=q if z["max_score"] is None else max(q,z["max_score"])
    def finish(self,yearmonth_path):
        self.fp.close()
        with gzip.open(yearmonth_path,"wt",encoding="utf8",newline="",compresslevel=6) as f:
            writer=csv.writer(f)
            writer.writerow(["source_id","source_site_token","year","month","taxon","stage","method",
                             "n_event_species_records","n_recorded_present",
                             "n_recorded_absent_or_no_call","n_unknown","max_recorded_score"])
            for key,counts in sorted(self.site_month_taxon.items()):
                writer.writerow(list(key)+[counts["total"],counts["detected"],counts["no_call_or_absent"],
                                           counts["unknown"],counts["max_score"]])
        return {
            "total_source_specific_observation_rows":dict(self.count),
            "unique_native_site_tokens_by_source":{k:len(v) for k,v in self.site.items()},
            "unique_year_months_by_source":{k:len(v) for k,v in self.month.items()},
            "recorded_status_counts_by_source":{k:dict(v) for k,v in self.status.items()},
            "stage_and_method_row_counts":[
              {"source":a,"stage":b,"method":c,"rows":n}
              for (a,b,c),n in sorted(self.stage_counts.items())],
            "environment_covariate_nonmissing_row_counts":[
              {"source":a,"field":b,"n_record_rows":n}
              for (a,b),n in sorted(self.valid.items())],
            "site_year_month_taxon_stage_method_cells":len(self.site_month_taxon)
        }

def load_hungary(sink):
    originals={}
    for fn,expected in MD5.items():
        data=(HG/fn).read_bytes()
        got=hashlib.md5(data).hexdigest()
        check(got==expected,"Hungarian original MD5 mismatch")
        originals[fn]={"bytes":len(data),"md5":got}
    with (HG/"wetland_amp_site_data.csv").open(encoding="utf-8",newline="") as f:
        sites={s["site"]:s for s in csv.DictReader(f)}
    with (HG/"wetland_amp_surv_data.csv").open(encoding="utf-8",newline="") as f:
        visits=list(csv.DictReader(f))
    check(len(sites)==29 and len(visits)==381,"Hungarian source size drift")
    for row in visits:
        ds=event_date(row["date"])
        if ds is None:raise ValueError("Hungary date missing")
        site=row["site"];ctx=sites.get(site)
        check(ctx is not None,"Hungary source foreign site missing")
        srcid=hashed("HUN2024",site)
        for taxon in FROGS+NEWTS:
            qty=as_float(row.get(taxon))
            if qty is None or qty<0:raise ValueError("Hungary species effort/status invalid")
            method=row["method"]
            check(method in ("acoustic","visual","dipnet","bottletrap"),"Unknown survey method")
            sink.emit({
              "source_id":"hungary_2024","site_token":srcid,"site_type":"field_wetland",
              "location_verification":"source_measured_field_site","source_event_token":hashed("HUNevent",row["surv"]),
              "date":str(ds),"year":ds.year,"month":ds.month,"day_of_year":ds.timetuple().tm_yday,
              "taxon":taxon,"stage":stage("",method),"survey_method":method,
              "status":"recorded_present" if qty>0 else "recorded_absent",
              "source_count_value":qty,"effort_n":1,"effort_unit":"method_specific_visit",
              "zero_semantics":"source_zero_under_visit_protocol_not_biological_absence",
              "precip_source_value":as_float(row["prec"]),"precip_source_unit":"original_prec_unverified",
              "temperature_C":as_float(row["temp"]),
              "water_depth_source_value":as_float(ctx["depth"]),"water_depth_source_unit":"source_depth_units_unverified",
              "emergent_cover_percent":as_float(ctx["cover_emerged"]),
              "submerged_cover_percent":as_float(ctx["cover_submers"]),
              "fish_source_observed":ctx["fish"],"site_management_class":ctx["ci"],
              "original_measurement_scope":"static_2024_wetland_covariates_plus_method_specific_survey"
            })
    return {"original_files":originals,"original_site_rows":29,"original_survey_rows":381}

def fetch_inbo_archive(name):
    spec=INBO_SOURCES[name]
    b,_=inbo_fetch(spec["url"])
    sh=hashlib.sha256(b).hexdigest()
    check(sh==spec["sha256"],"Original INBO archive source SHA drift")
    return b,{"doi":spec["doi"],"sha256":sh,"bytes":len(b)}

def load_inbo(sink):
    rec={}
    for kind in ("adult_chorus","larval_census"):
        b,receipt=fetch_inbo_archive(kind)
        rec[kind]=receipt
        with __import__("zipfile").ZipFile(BytesIO(b)) as z:
            root=ET.fromstring(z.read("meta.xml"))
            core=next(x for x in root if x.tag.rsplit("}",1)[-1]=="core")
            exts=[x for x in root if x.tag.rsplit("}",1)[-1]=="extension"]
            ev={}
            for r in part_rows(z,core):
                eid=r.get("eventID") or r.get("sourceCoreID")
                sid=r.get("locationID")
                dt=event_date(r.get("eventDate",""))
                if eid and sid and dt:
                    check(eid not in ev,"Duplicate INBO source event IDs")
                    ev[eid]=(sid,dt,r.get("samplingProtocol",""))
            measurements=defaultdict(lambda:defaultdict(list))
            species=[]
            for ext in exts:
                e=iter(part_rows(z,ext))
                fst=next(e,None)
                if fst is None:continue
                if "measurementType" in fst:
                    for r in __import__("itertools").chain([fst],e):
                        eid=r.get("eventID") or r.get("linkedCoreID")
                        if eid in ev:
                            measurements[eid][r.get("measurementType","").strip().lower()].append(
                                r.get("measurementValue"))
                elif "scientificName" in fst:
                    species+=list(__import__("itertools").chain([fst],e))
            for r in species:
                eid=r.get("eventID") or r.get("linkedCoreID")
                if eid not in ev:continue
                sid,day,proto=ev[eid]
                method="chorus" if kind=="adult_chorus" else "larval_census"
                status=normalize_status(r.get("occurrenceStatus"),kind)
                life=stage(r.get("lifeStage"),method)
                taxon=(r.get("scientificName") or "").strip()
                if not taxon:continue
                count=as_float(r.get("individualCount"))
                measured=measurements.get(eid,{})
                permanence=measured.get("permanente waterkolom",[])
                sink.emit({
                    "source_id":"inbo_"+kind,
                    "site_token":hashed("INBO_LOCATION",sid),
                    "site_type":"publisher_location_not_independently_pond_verified",
                    "location_verification":"same_exact_source_location_ID_across_inbo_archives",
                    "source_event_token":hashed("INBO_EVENT",kind+":"+eid),
                    "date":str(day),"year":day.year,"month":day.month,
                    "day_of_year":day.timetuple().tm_yday,
                    "taxon":taxon,"stage":life,"survey_method":method,
                    "status":status,"source_count_value":count,
                    "effort_n":1,"effort_unit":"source_taxon_stage_event_assessment",
                    "zero_semantics":"only_explicit_absent_not_missing_taxon",
                    "source_hydroperiod":str(permanence[0]) if len(permanence)==1 else None,
                    "original_measurement_scope":"species_stage_assessment_source_event"
                })
            rec[kind]["read_species_stage_rows"]=len(species)
            rec[kind]["event_records"]=len(ev)
    return rec

def load_nps(sink):
    import pandas as pd
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"NPS_GLKN_2016_2023.csv"
        readbytes=nps_fetch(path)
        cols=["ParkCode","SiteLocation","StartTime","EventYear","ScientificName",
              "ManualCIV","Hydroperiod","FileName"]
        d=pd.read_csv(path,usecols=cols,low_memory=False)
    check(len(d)==147913,"Original NPS source record count drift")
    ts=pd.to_datetime(d.StartTime,errors="coerce")
    bad=int(ts.isna().sum())
    for row,day in zip(d.itertuples(index=False),ts):
        if pd.isna(day):continue
        v=as_float(row.ManualCIV)
        if v not in (0,1,2,3):raise ValueError("Invalid NPS original manually scored audio CIV")
        dt=day.date()
        if dt.year<2016 or dt.year>2023:raise ValueError("NPS source year drift")
        sink.emit({
          "source_id":"nps_glkn","site_token":hashed("NPS_STATION",str(row.ParkCode)+"|"+str(row.SiteLocation)),
          "site_type":"acoustic_recorder_station_not_pond",
          "location_verification":"original_NPS_recorder_station_ID",
          "source_event_token":hashed("NPS_soundfile",str(row.ParkCode)+"|"+str(row.SiteLocation)+"|"+str(row.FileName)),
          "date":str(dt),"year":dt.year,"month":dt.month,"day_of_year":dt.timetuple().tm_yday,
          "taxon":str(row.ScientificName),"stage":"adult_acoustic",
          "survey_method":"manual_audio",
          "status":"recorded_no_call" if v==0 else "recorded_present",
          "score":int(v),"effort_n":1,"effort_unit":"scored_taxon_audio_file",
          "zero_semantics":"explicit_zero_manual_civ_not_species_absence",
          "source_hydroperiod":str(row.Hydroperiod) if pd.notna(row.Hydroperiod) else None,
          "original_measurement_scope":"manually_scored_audio_species_one_file",
        })
    return {"download_bytes":readbytes,"source_sha256":NPS_SHA,
            "raw_source_rows":len(d),"unparseable_source_start_times":bad}

def pull_sciencebase():
    req=Request(NAAMP_ITEM,headers={"User-Agent":"frogcs-canonical-observation-G0/1.0","Accept":"application/json"})
    with urlopen(req,timeout=35) as response:
        meta=json.loads(response.read().decode("utf-8"))
    urls={}
    for f in meta.get("files",[]):
        name=f.get("name")
        if name in NAAMP_PINS:urls[name]=f.get("downloadUri") or f.get("url") or f.get("uri")
    check(len(urls)==len(NAAMP_PINS),"Missing original NAAMP file URLs")
    b={}
    for name,url in urls.items():
        req=Request(url,headers={"User-Agent":"frogcs-canonical-observation-G0/1.0"})
        with urlopen(req,timeout=120) as response:
            z=response.read(45000000)
        d=hashlib.sha256(z).hexdigest()
        check(d==NAAMP_PINS[name],"Original NAAMP pinned digest drift: "+name)
        b[name]=list(csv.DictReader(StringIO(z.decode("utf-8-sig"))))
    return b

def load_naamp(sink):
    raw=pull_sciencebase()
    runs={}
    for r in raw["Runs.csv"]:
        rid=(r.get("RunID") or "").strip()
        if not rid or str(r.get("UnifiedProtocol","")).strip()!="1":continue
        try:
            dt=__import__("pandas").to_datetime(r.get("SurveyDate"),errors="coerce")
            if __import__("pandas").isna(dt):continue
            day=dt.date()
        except Exception:continue
        if not (2001<=day.year<=2015):continue
        runs[rid]=(day,r.get("DaysSinceRain"),r.get("State"),r.get("RouteNumber"))
    stops={}
    visitct=0
    for row in raw["Stops.csv"]:
        rid=(row.get("RunID") or "").strip()
        if rid not in runs or str(row.get("SkippedStop","")).strip()!="0":continue
        no=(row.get("StopNumber") or "").strip()
        if not no:continue
        sid=(row.get("SiteID") or "").strip()
        day,rain,state,rt=runs[rid]
        sitetoken=hashed("NAAMP_STOP",sid if sid else f"{state}|{rt}|{no}")
        stops[(rid,no)]=(sitetoken,day,rain)
        visitct+=1
        sink.emit({
          "source_id":"naamp_surveyed_stops","site_token":sitetoken,
          "site_type":"roadside_acoustic_listening_stop_not_pond",
          "location_verification":"source_siteID_only_not_independently_repaired",
          "source_event_token":hashed("NAAMP_RUN_STOP",rid+"|"+no),
          "date":str(day),"year":day.year,"month":day.month,
          "day_of_year":day.timetuple().tm_yday,
          "taxon":"*ALL_TAXA_SURVEY_OPPORTUNITY*","stage":"adult_acoustic",
          "survey_method":"naamp_acoustic","status":"unknown",
          "effort_n":1,"effort_unit":"completed_listening_stop_survey",
          "zero_semantics":"surveyed_stop_not_explicit_absence_of_each_taxon",
          "rain_days_since":as_float(rain),
          "original_measurement_scope":"original_stop_site_observation_opportunity_not_RC6_pair_sample"
        })
    accepted=0
    for row in raw["Counts.csv"]:
        rid=(row.get("RunID") or "").strip()
        stop=(row.get("StopNumber") or "").strip()
        if (rid,stop) not in stops:continue
        score=as_float(row.get("CallingIndex"))
        if score not in (1,2,3):continue
        species=(row.get("Species") or "").strip()
        if not species:continue
        token,day,rain=stops[(rid,stop)]
        accepted+=1
        sink.emit({
          "source_id":"naamp_positive_calls","site_token":token,
          "site_type":"roadside_acoustic_listening_stop_not_pond",
          "location_verification":"source_siteID_only_not_independently_repaired",
          "source_event_token":hashed("NAAMP_RUN_STOP",rid+"|"+stop),
          "date":str(day),"year":day.year,"month":day.month,
          "day_of_year":day.timetuple().tm_yday,
          "taxon":"NAAMP_CODE:"+species,"stage":"adult_acoustic",
          "survey_method":"naamp_acoustic","status":"recorded_present",
          "score":int(score),"effort_n":1,"effort_unit":"positive_taxon_call_record",
          "zero_semantics":"no_species_specific_zeros_encoded",
          "rain_days_since":as_float(rain),
          "original_measurement_scope":"positive_call_source_not_RC6_spatial_null_fit"
        })
    return {"original_sha256":NAAMP_PINS,"original_source_counts":{k:len(v) for k,v in raw.items()},
       "standardized_completed_stop_opportunities":visitct,
       "positive_standardized_call_rows":accepted,
       "exact_RC6_4236_paired_outcome_recomputed":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--omit-naamp",action="store_true",help="Explicitly report NAAMP source unavailable in this run")
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    sink=Sink(args.out/"common_observation_events.csv.gz")
    receipts={}
    for name,load in [("hungary",load_hungary),("inbo",load_inbo),
                      ("nps",load_nps),("naamp",load_naamp)]:
        try:
            if name=="naamp" and args.omit_naamp:
                receipts[name]={"status":"OMITTED_BY_EXPLICIT_ARGUMENT"}
            else:
                receipts[name]={"status":"SOURCE_AUTHENTICATED_CROSSWALK_BUILT","details":load(sink)}
        except Exception as ex:
            receipts[name]={"status":"SOURCE_BLOCKED_MISSING_FROM_CANONICAL_EVENTS",
                             "error":type(ex).__name__+": "+str(ex)[:350]}
    profile=sink.finish(args.out/"common_site_month_taxon_stage.csv.gz")
    report={
        "schema":"frogcs-common-site×year×month×taxon×stage×method/1.0",
        "contract":"research/CANONICAL_SITE_TIME_STAGE_OBSERVATION_CONTRACT_V1.md",
        "sources":receipts,
        "profile":profile,
        "source_namespace_disjoint_even_when_taxa_names_equal":True,
        "raw_wildlife_source_site_ids_exported":False,
        "naamp_rc6_spatial_metric_recomputed":False,
        "GBIF_1degree_stage_grid_mixed_with_real_ponds":False,
        "GBIF_macro_module_source":"research/manuscript/GLOBAL_STAGE_MACRO_EVIDENCE_GATE_V1.md",
        "common_water_plant_predator_stage_cohort_fate_measured_in_one_original_unit":False,
        "source_data_artifact_only_not_committed":True,
        "same_species_monthly_records_are_observation_effort_not_population_counts":True
    }
    (args.out/"observed_profile.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BEGIN_FROGCS_CANONICAL_SOURCE_PROFILE")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print("END_FROGCS_CANONICAL_SOURCE_PROFILE")
    if any(x["status"]!="SOURCE_AUTHENTICATED_CROSSWALK_BUILT" for name,x in receipts.items() if name!="naamp"):
        raise SystemExit(3)

if __name__=="__main__":main()
