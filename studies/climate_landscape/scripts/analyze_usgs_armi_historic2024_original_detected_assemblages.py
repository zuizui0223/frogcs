#!/usr/bin/env python3
"""Source-pinned USGS 2003–08 and 2024 frog original published survey records:
site & coordinates & same month & microphone & clock-matched species-list
turnover and historical within-night observer variability reference.

FROZEN before frog response read, see:
USGS_ARMI_PUBLIC_FROG_20Y_MATCHED_EPOCH_OBSERVER_FROZEN_CONTRACT.md.
DESCRIPTIVE ONLY, not occupancy, recall, causal hydrology or frog memory.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from dataclasses import dataclass,field
from datetime import datetime,date
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from statistics import median,mean
import csv,io,json,random

import audit_usgs_armi_history2024_public_source_gate as src
import audit_usgs_armi_revisit_source_geo_key as geo
import audit_armi2024_original_visit_observer_v80 as orig

PIN={
 "history_2003_2008":"33bb028cf148a685d8af5a579786ce94bde045fa68d00f8c395713c6c06ae32b",
 "new_2024":"dafd388c7ccb79e08dbadd37a25c604473a8caf4ff5c8318532740acb56a04e4",
}
OUT="studies/climate_landscape/receipts/USGS_ARMI_REAL_20Y_MATCHED_FROG_SPECIES_LISTS.json"
SEED=20261014
B=5000
NO_CALL={"NONE","NO ANURANS HEARD","NO FROGS HEARD","NO FROGS","NO CALLS","NO ANURANS","0","NA","N/A"}

@dataclass
class Event:
    site:str
    day:date
    person:str
    clock:str
    method:str
    times:float
    taxa:set=field(default_factory=set)
    no_frog:int=0
    malformed:int=0

def clean(x):
    return str(x or "").strip()

def original_events(raw,release):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    needed={"Site","Date","Observer","Arrival_time","Method","Species","Number_heard"}
    if not reader.fieldnames or not needed.issubset(reader.fieldnames):
        raise ValueError("SOURCE_SCHEMA_DRIFT")
    events={};keyparts=defaultdict(set);count=Counter()
    taxavocab=set()
    for row in reader:
        count["source_rows"]+=1
        if None in row:raise ValueError("CSV_EXTRA_COLUMN")
        site=clean(row["Site"]);who=clean(row["Observer"])
        clock=clean(row["Arrival_time"]);method=clean(row["Method"])
        if not site or not who or method not in {"Ear","Microphone"}:
            count["excluded_missing_id_or_unknown_method"]+=1;continue
        try: dt=datetime.strptime(row["Date"],"%Y-%m-%d").date()
        except ValueError:
            count["excluded_invalid_source_date"]+=1;continue
        t=orig.to_minutes(clock)
        if t is None:
            count["excluded_invalid_original_clock"]+=1;continue
        key=(site,dt,who,clock,method)
        keyparts[(site,dt,who)].add((clock,method))
        v=events.setdefault(key,Event(site,dt,who,clock,method,t))
        tax=clean(row["Species"])
        num=clean(row["Number_heard"])
        no_number=num.upper() in {"","NA","N/A","NULL"}
        no_tax=tax.upper() in NO_CALL
        if no_tax and no_number:
            v.no_frog+=1;count["no_anuran_heard_source_rows"]+=1
        elif tax and not no_tax and not no_number:
            v.taxa.add(tax)
            taxavocab.add(tax)
            count["positive_source_species_rows"]+=1
        else:
            v.malformed+=1;count["ambiguous_source_species_or_number_rows"]+=1
    ambiguous_keys={k for k,v in keyparts.items() if len(v)>1}
    valid={}
    flags=Counter()
    for k,e in events.items():
        if (e.site,e.day,e.person) in ambiguous_keys:
            flags["multiple_methods_or_start_times_within_one_source_person_day"]+=1;continue
        if e.malformed or e.no_frog>1 or (e.no_frog and e.taxa) or (not e.no_frog and not e.taxa):
            flags["mixed_or_incomplete_source_survey_event"]+=1;continue
        valid[k]=e
    return valid,{
        "release":release,
        "original_rows":count["source_rows"],
        "n_positive_species_rows":count["positive_source_species_rows"],
        "n_no_frogs_heard_rows":count["no_anuran_heard_source_rows"],
        "n_malformed_source_species_number_rows":count["ambiguous_source_species_or_number_rows"],
        "n_distinct_taxon_literal_labels":len(taxavocab),
        "n_valid_event_source_keys":len(valid),
        "n_events_excluded_due_source_ambiguity":dict(flags),
        "n_valid_explicit_no_anuran_heard_events":sum(e.no_frog>0 for e in valid.values()),
        "n_valid_positive_species_list_events":sum(bool(e.taxa) for e in valid.values()),
        "not_independent_territorial_frog_populations":True,
    },taxavocab

def full_originals():
    raw={}
    location={}
    source_profile={}
    vocab={}
    for key,item in src.ITEMS.items():
        meta,data,f=src.public_file(item)
        if not data or f.get("sha256")!=PIN[key]:raise ValueError("UNVERIFIED_RELEASE_CONTENT")
        raw[key]=data
        source_profile[key],location[key]=geo.positive_coordinates(data.decode("utf-8-sig"))
    return raw,source_profile,location

def physical_site_candidates(a,b):
    old=a["site_coords"];new=b["site_coords"]
    ids=set(old)&set(new)
    pair_distance={k:geo.geo_km(old[k],new[k])*1000 for k in ids}
    # Fixed BEFORE seeing any frog species results, not tuned later.
    accepted={k for k,d in pair_distance.items()
          if d<=10 and a["site_spread"][k]*1000<=100 and b["site_spread"][k]*1000<=100}
    return accepted,{
        "n_exact_Site_source_labels":len(ids),
        "n_within_10m_source_medians":sum(d<=10 for d in pair_distance.values()),
        "n_eligible_exact_labels_within_epoch_geometry_guard":len(accepted),
        "max_site_between_epoch_distance_m":round(max(pair_distance.values()),2),
        "source_matches_over_500m_excluded":sum(d>500 for d in pair_distance.values()),
        "uncertified_cross_year_source_site_identification":True,
        "precise_locations_omitted":True
    }

def gap_minutes(a,b):
    x=abs(a.times-b.times)
    return min(x,1440-x)

def month_year_key(v):
    return (v.day.month, v.method)

def eligible_epoch_pairs(old,new,allowed_sites,maxclock):
    aa=defaultdict(list);bb=defaultdict(list)
    for e in old.values():
        if e.site in allowed_sites and e.method=="Microphone" and e.day.month in (6,7,8):
            aa[e.site].append(e)
    for e in new.values():
        if e.site in allowed_sites and e.method=="Microphone" and e.day.month in (6,7,8):
            bb[e.site].append(e)
    out=[]
    for site in sorted(set(aa)&set(bb)):
        choices=[]
        for a in aa[site]:
            for b in bb[site]:
                if a.day.month!=b.day.month:continue
                md=gap_minutes(a,b)
                if maxclock is not None and md>maxclock:continue
                dd=abs(a.day.timetuple().tm_yday-b.day.timetuple().tm_yday)
                # Fixed tie-breaking, and chosen without taxa inspection.
                rank=(dd,md,a.day.isoformat(),b.day.isoformat(),
                      a.times,b.times,a.person,b.person)
                choices.append((rank,a,b))
        if choices:
            _,a,b=min(choices,key=lambda x:x[0])
            out.append((site,a,b))
    return out

def similarity(a,b):
    u=a|b
    return len(a&b)/len(u) if u else None

def observational_summary(pairs):
    vals=[];bothzero=0;onezero=0; bothpos=0
    selected_years=Counter(); selected_month=Counter()
    for site,a,b in pairs:
        selected_years[a.day.year]+=1;selected_month[a.day.month]+=1
        if not a.taxa and not b.taxa:bothzero+=1
        elif not a.taxa or not b.taxa:onezero+=1
        else:bothpos+=1
        s=similarity(a.taxa,b.taxa)
        if s is not None:vals.append(s)
    return {
        "n_original_matched_site_pairs":len(pairs),
        "n_both_genuine_no_anurans_heard_source_pairs":bothzero,
        "n_exactly_one_source_no_call_pair":onezero,
        "n_both_with_source_positive_list":bothpos,
        "n_nonempty_union_evaluable_jaccard_pairs":len(vals),
        "source_detected_species_list_Jaccard_mean":round(mean(vals),6) if vals else None,
        "source_detected_species_list_Jaccard_median":round(median(vals),6) if vals else None,
        "n_nonempty_union_pairs_with_zero_shared_detected_taxa":sum(s==0 for s in vals),
        "n_nonempty_union_pairs_with_complete_detected_taxa_match":sum(s==1 for s in vals),
        "historical_source_year_counts_for_matched_pairs":dict(sorted(selected_years.items())),
        "month_counts_for_matched_pairs":dict(sorted(selected_month.items())),
        "original_site_codes_or_species_labels_emitted":False,
    }

def past_independent_observers(old,allowed_sites):
    by_site_date=defaultdict(list)
    for e in old.values():
        if e.site in allowed_sites and e.method=="Microphone" and e.day.month in (6,7,8):
            by_site_date[(e.site,e.day)].append(e)
    by_site=defaultdict(list)
    for (site,day),visits in by_site_date.items():
        for a,b in combinations(visits,2):
            if a.person==b.person or gap_minutes(a,b)>5:continue
            rank=(day.isoformat(),min(a.times,b.times),
                  min(a.person,b.person),max(a.person,b.person))
            by_site[site].append((rank,a,b))
    pairs=[]
    for site,opts in by_site.items():
        _,a,b=min(opts,key=lambda z:z[0])
        pairs.append((site,a,b))
    return pairs

def site_contrast(pairs,refs):
    by={s:(a,b) for s,a,b in pairs}
    ref={s:(a,b) for s,a,b in refs}
    common=sorted(set(by)&set(ref))
    deltas=[];longs=[];shorts=[]
    for s in common:
        la,lb=by[s];ra,rb=ref[s]
        ls=similarity(la.taxa,lb.taxa)
        rs=similarity(ra.taxa,rb.taxa)
        if ls is not None and rs is not None:
            deltas.append(rs-ls);longs.append(ls);shorts.append(rs)
    res={"n_original_sites_both_study_windows":len(common),
         "n_sites_with_nonempty_taxon_union_in_both_comparisons":len(deltas),
         "relative_same_event_vs_two_decade_difference_IDENTIFIED":False,
         "observer_method_and_year_environment_comparable":False}
    if len(deltas)<10:
        res["status"]="INSUFFICIENT_SAME_SITE_OBSERVER_CALIBRATION"
        res["no_site_bootstrap_claim"]=True
        return res
    rng=random.Random(SEED)
    boots=[mean(rng.choice(deltas) for _ in deltas) for _ in range(B)]
    def quantile(xs,q):
        xs=sorted(xs);p=(len(xs)-1)*q;l=int(p);h=min(l+1,len(xs)-1)
        return xs[l]+(p-l)*(xs[h]-xs[l])
    return {**res,
        "status":"SOURCE_CONSTRAINED_DESCRIPTIVE_BASELINE_CONTRAST",
        "same_event_historical_observer_mean_jaccard_paired_sites":round(mean(shorts),6),
        "same_month_mic_cross_epoch_mean_jaccard_paired_sites":round(mean(longs),6),
        "mean_same_event_minus_cross_epoch_jaccard":round(mean(deltas),6),
        "n_sites_mean_difference_positive":sum(x>0 for x in deltas),
        "n_sites_mean_difference_negative":sum(x<0 for x in deltas),
        "bootstrap_site_95_descriptive":[round(quantile(boots,.025),6),
                                         round(quantile(boots,.975),6)],
        "no_confirmatory_p_values":True,
        "not_true_occupancy_or_species_extinction":True
    }

def tests():
    a=Event("S",date(2004,6,10),"O1","20:00","Microphone",1200,{"sp1"})
    b=Event("S",date(2024,6,11),"O2","20:30","Microphone",1230,{"sp1","sp2"})
    c=Event("S",date(2024,7,10),"O2","20:30","Microphone",1230,{"sp3"})
    pairs=eligible_epoch_pairs({1:a},{2:b,3:c},{"S"},60)
    assert len(pairs)==1
    assert pairs[0][1] is a and pairs[0][2] is b
    assert similarity(a.taxa,b.taxa)==0.5
    assert similarity(set(),set()) is None
    assert gap_minutes(a,b)==30
    assert observational_summary(pairs)["source_detected_species_list_Jaccard_mean"]==0.5
    assert not eligible_epoch_pairs({1:a},{2:b},{"S"},20)
    print("PASS: fixed original physical Site / same-month Mic/clock selection, empty union and no taxon names in receipt")

def main():
    tests()
    raw,sourceprofiles,loc=full_originals()
    accepted,siteQc=physical_site_candidates(loc["history_2003_2008"],loc["new_2024"])
    historical,hprofile,htaxa=original_events(raw["history_2003_2008"],"2003–2008")
    recent,nprofile,ntaxa=original_events(raw["new_2024"],"2024")
    primary=eligible_epoch_pairs(historical,recent,accepted,60)
    diagnostic=eligible_epoch_pairs(historical,recent,accepted,None)
    refs=past_independent_observers(historical,{s for s,a,b in primary})
    if len(primary)<10:
        status="SOURCE_SUPPORT_INSUFFICIENT_FOR_CROSS_EPOCH_COMPARISON"
    else:
        status="ACTUAL_PUBLIC_USGS_FROG_LONGITUDINAL_DETECTED_COMMUNITY_COMPARISON"
    out={
      "status":status,
      "source_history":"https://doi.org/10.5066/P1X9UBHV",
      "source_new":"https://doi.org/10.5066/P19ZCGWM",
      "pinned_original_source_hashes":PIN,
      "frozen_early_scientific_contract":
        "studies/climate_landscape/USGS_ARMI_PUBLIC_FROG_20Y_MATCHED_EPOCH_OBSERVER_FROZEN_CONTRACT.md",
      "original_source_geo_spatial_support":siteQc,
      "historic_original_survey_opportunities":hprofile,
      "recent_original_survey_opportunities":nprofile,
      "n_exact_source_taxon_labels_in_historical":len(htaxa),
      "n_exact_source_taxon_labels_in_new":len(ntaxa),
      "n_taxon_literal_labels_shared_between_epochs":len(htaxa&ntaxa),
      "n_taxon_labels_historical_only":len(htaxa-ntaxa),
      "n_taxon_labels_new_only":len(ntaxa-htaxa),
      "strict_same_month_same_microphone_start_within_60min":observational_summary(primary),
      "same_month_same_microphone_NO_clock_restriction_SOURCE_DIAGNOSTIC":
         observational_summary(diagnostic),
      "historical_same_site_date_two_microphone_observers_within_five_min":
         observational_summary(refs),
      "same_site_source_observer_baseline_vs_cross_epoch":
         site_contrast(primary,refs),
      "source_identity_not_positively_reconciled_by_custodian":True,
      "taxon_synonyms_and_genus_sp_not_reconciled":True,
      "individual_site_observer_taxon_or_coordinate_values_exported":False,
      "historical_occupancy_change_or_true_local_species_loss_claimed":False,
      "causal_wetland_hydrology_frog_memory_or_adaptation_tested":False,
      "unreleased_observation_data_accessed":False,
      "frogs_JAE_main_RC6_unchanged":True
    }
    p=Path(OUT);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("PUBLIC_USGS_ORIGINAL_FROG_EPOCH_RESULT "+json.dumps(out,sort_keys=True),flush=True)
if __name__=="__main__":main()
