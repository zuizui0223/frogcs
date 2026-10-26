#!/usr/bin/env python3
"""Project source-authenticated canonical rows to comparable species occurrences.

NO stage in the output observation key. Multiple life-stage rows for one
species in the SAME original event collapse to one assessed species row;
unassessed taxon-event cells are NOT generated or counted as absences.

Raw/source-native site tokens and survey dates stay in ephemeral Actions files.
Only an aggregate profile is suitable for research/results versioning.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import csv
import gzip
import json
import re
import sqlite3
import tempfile
from pathlib import Path

FAKE_TAXON="*ALL_TAXA_SURVEY_OPPORTUNITY*"
HEADER=[
 "source_id","site_token","site_type","source_event_token","date","year","month",
 "taxon","method","occurrence_status","raw_stage_row_count","source_score_max",
 "precip_source_value","water_depth_source_value","source_hydroperiod",
 "emergent_cover_percent","submerged_cover_percent","fish_source_observed",
 "site_management_class","survey_assessment_semantics"]
MONTH_HEADER=[
 "source_id","site_token","year","month","taxon","method",
 "assessed_events","detected_events","protocol_nondetection_events",
 "unknown_events","source_max_acoustic_score"]
EFFORT_HEADER=["source_id","source_event_token","site_token","date","year","month",
               "source_survey_record_type"]

def assert_ok(x,msg):
    if not x:raise ValueError(msg)

def xstr(x):
    return "" if x is None else str(x)

def status(present,absent,unknown):
    if present: return "recorded_present"
    if absent and not unknown:return "protocol_nondetection"
    return "unresolved"

def valid_date(y,m,d):
    try:
        year=int(y);month=int(m)
        assert 2001<=year<=2026 and 1<=month<=12
        assert re.match(r"^\d{4}-\d\d-\d\d$",str(d))
        assert str(year)==str(d)[:4] and month==int(str(d)[5:7])
    except (ValueError,AssertionError,TypeError):
        raise ValueError("Invalid canonical source date/month/year")

def run(events,outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    event_out=outdir/"species_occurrence_events.csv.gz"
    month_out=outdir/"species_occurrence_site_month.csv.gz"
    effort_out=outdir/"naamp_surveyed_stop_opportunities.csv.gz"
    tally=Counter();orig=Counter()
    with tempfile.TemporaryDirectory() as temp:
        db=sqlite3.connect(Path(temp)/"species.sqlite3")
        db.execute("PRAGMA journal_mode=OFF")
        db.execute("PRAGMA synchronous=OFF")
        db.execute("CREATE TABLE t (src TEXT NOT NULL, event TEXT NOT NULL, "
                   "site TEXT NOT NULL, kind TEXT NOT NULL, dt TEXT NOT NULL, "
                   "year INTEGER NOT NULL, mon INTEGER NOT NULL, sp TEXT NOT NULL, "
                   "method TEXT NOT NULL, present INTEGER NOT NULL, "
                   "non_detection INTEGER NOT NULL, unknown INTEGER NOT NULL, "
                   "stage_rows INTEGER NOT NULL, score REAL, rain REAL, depth REAL, "
                   "hydro TEXT, emergent REAL, submerged REAL, fish TEXT, "
                   "management TEXT, PRIMARY KEY (src,event,sp,method))")
        sql=("INSERT INTO t VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
             "ON CONFLICT (src,event,sp,method) DO UPDATE SET "
             "present=present+excluded.present, "
             "non_detection=non_detection+excluded.non_detection, "
             "unknown=unknown+excluded.unknown, "
             "stage_rows=stage_rows+1, "
             "score=CASE WHEN excluded.score IS NULL THEN score "
             "WHEN score IS NULL THEN excluded.score "
             "WHEN score < excluded.score THEN excluded.score ELSE score END")
        with gzip.open(events,"rt",encoding="utf-8",newline="") as f, \
          gzip.open(effort_out,"wt",encoding="utf-8",newline="") as effort_fp:
            reader=csv.DictReader(f)
            writer=csv.writer(effort_fp);writer.writerow(EFFORT_HEADER)
            batch=[]
            for rec in reader:
                src=rec["source_id"];orig[src]+=1
                valid_date(rec["year"],rec["month"],rec["date"])
                if src=="naamp_surveyed_stops":
                    assert_ok(rec["taxon"]==FAKE_TAXON,"Pseudo taxon in source survey effort")
                    writer.writerow([src,rec["source_event_token"],rec["site_token"],
                                     rec["date"],rec["year"],rec["month"],
                                     "completed_stop_no_species_absence_imputed"])
                    tally["naamp_completed_stop_events"]+=1
                    continue
                if not rec["taxon"] or rec["taxon"]==FAKE_TAXON:
                    raise ValueError("Unexpected source fake/non-specific species occurrence")
                raw=rec["status"]
                if raw=="recorded_present":p,a,u=1,0,0
                elif raw in ("recorded_absent","recorded_no_call"):p,a,u=0,1,0
                elif raw=="unknown":p,a,u=0,0,1
                else:raise ValueError("Source status not recognized: "+raw)
                def numeric(k):
                    z=rec.get(k)
                    if z in (None,""):return None
                    try:return float(z)
                    except ValueError:return None
                batch.append((
                    src,rec["source_event_token"],rec["site_token"],rec["site_type"],
                    rec["date"],int(rec["year"]),int(rec["month"]),
                    rec["taxon"],rec["survey_method"],p,a,u,1,numeric("score"),
                    numeric("precip_source_value"),numeric("water_depth_source_value"),
                    xstr(rec["source_hydroperiod"]),numeric("emergent_cover_percent"),
                    numeric("submerged_cover_percent"),xstr(rec["fish_source_observed"]),
                    xstr(rec["site_management_class"])
                ))
                if len(batch)>=5000:
                    with db:db.executemany(sql,batch)
                    batch=[]
            if batch:
                with db:db.executemany(sql,batch)
        assert_ok(orig["nps_glkn"]==147913,"NPS source rows changed")
        assert_ok(orig["hungary_2024"]==3429,"Hungary source rows changed")
        assert_ok(orig["naamp_positive_calls"]==310683,"NAAMP positive rows changed")
        assert_ok(orig["naamp_surveyed_stops"]==198757,"NAAMP survey denominator changed")
        assert_ok(orig["inbo_adult_chorus"]==1436 and orig["inbo_larval_census"]==2995,
                  "INBO original event rows changed")

        source_events=defaultdict(set)
        source_sites=defaultdict(set)
        source_taxa=defaultdict(set)
        source_months=defaultdict(set)
        source_method=defaultdict(Counter)
        source_status=defaultdict(Counter)
        source_meta=defaultdict(Counter)
        stage_extra=defaultdict(int)
        original_native_duplicate_extra=Counter()
        source_status_conflicts=Counter()
        richness=defaultdict(lambda:{"assessed":0,"detected":0,"uncertain":0})
        site_month=defaultdict(lambda:{"assessed":0,"present":0,"nondetect":0,"unknown":0,"max_score":None})
        # A fixed event's source site/date/taxon must be preserved, never
        # merge two unrelated source namespaces even if site hashes coincide.
        with gzip.open(event_out,"wt",encoding="utf-8",newline="") as fo:
            wr=csv.writer(fo);wr.writerow(HEADER)
            for row in db.execute("SELECT src,event,site,kind,dt,year,mon,sp,method,"
                                  "present,non_detection,unknown,stage_rows,score,"
                                  "rain,depth,hydro,emergent,submerged,fish,management "
                                  "FROM t ORDER BY src,event,sp,method"):
                src,eid,site,kind,dt,yr,mon,sp,method,npres,nabs,nunknown,rawrows,score,\
                rain,depth,hydro,emergent,submerged,fish,management=row
                st=status(npres,nabs,nunknown)
                if src=="hungary_2024" and npres>0 and nabs>0:
                    # Native visit ID appears twice with contradictory 0 vs >0
                    # for the same species. Do not select a convenient status.
                    st="unresolved"
                    source_status_conflicts[src]+=1
                if src=="hungary_2024" and rawrows>1:
                    original_native_duplicate_extra[src]+=rawrows-1
                if src.startswith("inbo_") and rawrows>1:stage_extra[src]+=rawrows-1
                sem={
                  "nps_glkn":"species_scored_no_call_not_biological_absence",
                  "hungary_2024":"taxon_assessed_under_its_visit_method",
                  "inbo_adult_chorus":"stage_specific_chorus_assessment_not_biological_absence",
                  "inbo_larval_census":"one_or_more_stage_assessments_not_whole_species_absence",
                  "naamp_positive_calls":"positive_only_no_species_assessed_zeros",
                }[src]
                wr.writerow([src,site,kind,eid,dt,yr,mon,sp,method,st,rawrows,
                             score,rain,depth,hydro,emergent,submerged,fish,management,sem])
                source_events[src].add(eid);source_sites[src].add(site)
                source_taxa[src].add(sp);source_months[src].add((yr,mon))
                source_method[src][method]+=1;source_status[src][st]+=1
                for key,val in [("rain",rain),("depth",depth),("hydroperiod",hydro),
                                ("emergent",emergent),("submerged",submerged),("fish",fish)]:
                    if val not in (None,""):source_meta[src][key]+=1
                rich=richness[(src,eid,method,site,dt)]
                rich["assessed"]+=1
                rich["detected"]+=int(st=="recorded_present")
                rich["uncertain"]+=int(st=="unresolved")
                mm=site_month[(src,site,yr,mon,sp,method)]
                mm["assessed"]+=int(st!="unresolved")
                mm["present"]+=int(st=="recorded_present")
                mm["nondetect"]+=int(st=="protocol_nondetection")
                mm["unknown"]+=int(st=="unresolved")
                if score is not None:mm["max_score"]=score if mm["max_score"] is None else max(score,mm["max_score"])
        with gzip.open(month_out,"wt",encoding="utf-8",newline="") as fo:
            wr=csv.writer(fo);wr.writerow(MONTH_HEADER)
            for (src,site,year,mon,taxon,method),v in sorted(site_month.items()):
                assert_ok(v["assessed"]==v["present"]+v["nondetect"],
                          "Species status numerator/denominator inconsistent")
                wr.writerow([src,site,year,mon,taxon,method,v["assessed"],
                             v["present"],v["nondetect"],v["unknown"],v["max_score"]])
        total_events={src:len(e) for src,e in source_events.items()}
        event_hists=defaultdict(lambda:Counter())
        for (src,eid,method,site,dt),v in richness.items():
            event_hists[src][f"assessed_{v['assessed']}"]+=1
            event_hists[src][f"detected_{v['detected']}"]+=1
        native={s:sorted(v) for s,v in source_taxa.items()}
        # Source taxonomy is retained verbatim; no unsafe mapping of native NAAMP
        # species codes to scientific names, or unverified synonym collapse.
        is_binomial=lambda n: bool(re.match(r"^[A-Z][a-z]+ [a-z][a-z.-]+(?: |$)",n))
        overlaps=[]
        sources=["hungary_2024","inbo_adult_chorus","inbo_larval_census","nps_glkn"]
        for i,a in enumerate(sources):
            for b in sources[i+1:]:
                common=sorted(sp for sp in source_taxa[a]&source_taxa[b] if is_binomial(sp))
                overlaps.append({"source_a":a,"source_b":b,"identical_verbatim_taxon_names":common,
                                 "n":len(common),"taxonomic_synonym_mapping_performed":False,
                                 "same_physical_sites":False})
        profile={
          "status":"VERIFIED_SPECIES_OCCURRENCE_FIRST_CANONICAL",
          "source_records_before_stage_collapse":dict(orig),
          "n_distinct_event_taxon_method_records_by_source":{s:sum(source_method[s].values()) for s in source_method},
          "deduplicated_stage_rows_by_source":dict(stage_extra),
          "duplicate_original_survey_species_rows_by_source":dict(original_native_duplicate_extra),
          "contradictory_present_and_zero_within_original_survey_species_by_source":dict(source_status_conflicts),
          "n_observation_events_by_source":total_events,
          "distinct_original_source_site_tokens_by_source":{s:len(v) for s,v in source_sites.items()},
          "native_taxon_labels_count_by_source":{s:len(v) for s,v in source_taxa.items()},
          "native_taxon_names_by_source":native,
          "year_month_coverage_by_source":{s:len(v) for s,v in source_months.items()},
          "status_by_source":{s:dict(v) for s,v in source_status.items()},
          "method_scoped_species_record_counts":{s:dict(v) for s,v in source_method.items()},
          "environment_field_nonmissing_event_species_rows":{s:dict(v) for s,v in source_meta.items()},
          "original_site_taxon_month_method_cells":len(site_month),
          "source_event_method_richness_histogram":{s:dict(v) for s,v in event_hists.items()},
          "cross_source_exact_name_overlap":overlaps,
          "naamp_completed_stop_survey_opportunities":tally["naamp_completed_stop_events"],
          "no_taxon_absences_generated_from_naamp_positive_only":True,
          "no_native_species_codes_force_matched_to_binomials":True,
          "life_stage_removed_from_occurrence_primary_key":True,
          "underlying_source_stage_labels_still_available_in_upstream_artifact":True,
          "do_not_interpret_shared_taxon_names_as_same_sampling_unit":True,
          "GBIF_1_degree_presence_only_not_merged_with_ponds":True,
          "no_predation_competition_or_persistency_claim_from_source_status":True,
          "raw_location_tokens_committed":False,
          "input":str(events),
          "canonical_event_table_filename":event_out.name,
          "canonical_site_month_table_filename":month_out.name,
          "naamp_survey_opportunities_filename":effort_out.name,
        }
        outf=outdir/"observed_species_occurrence_profile.json"
        outf.write_text(json.dumps(profile,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print("BEGIN_FROGCS_SPECIES_OCCURRENCE_PROFILE")
        print(json.dumps(profile,indent=2,ensure_ascii=False))
        print("END_FROGCS_SPECIES_OCCURRENCE_PROFILE")
        return profile

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--from-units",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    assert_ok(args.from_units.is_file(),"Existing original-source canonical table required")
    run(args.from_units,args.out)

if __name__=="__main__":main()
