#!/usr/bin/env python3
"""Independent Mohonk wood-frog / salamander breeding-stage phenology audit.

Original public GBIF-US IPT Mohonk DwC archive v1.1, DOI 10.15468/dypfbs.
Trophic *opportunity* only: no direct predation, prey survival, or dragonflies.
2016–2021 is used for substantially complete species × stage zero records;
prior years have largely event-positive, noncomparable reporting.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,random,statistics,zipfile
from collections import defaultdict,Counter
from datetime import date
from pathlib import Path

SOURCE_SHA="0309abd9afa4a224287d6853d79ae1f7111a3a7bb19b0d2337f05c280ef12b34"
TSV_SHA="d52b288608a40c3b721f3561a57ace34728975522892a4fdc1d0b4f6ffb3610e"
TAXON={"Lithobates sylvaticus":"frog",
       "Ambystoma maculatum":"spotted","Ambystoma jeffersonianum":"jefferson"}
STAGES=(("frog","egg"),("frog","tadpole"),("spotted","egg"),
        ("spotted","tadpole"),("jefferson","egg"))
SEED=2840223

def load_original(path):
    data=Path(path).read_bytes()
    with zipfile.ZipFile(io.BytesIO(data)) as wrapper:
        if "mohonk_original_dwca.zip" in wrapper.namelist():
            data=wrapper.read("mohonk_original_dwca.zip")
    if hashlib.sha256(data).hexdigest()!=SOURCE_SHA:
        raise ValueError("Publisher original ZIP SHA256 drift")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if "meta.xml" not in archive.namelist():raise ValueError("not a Darwin Core archive")
        t=archive.read("occurrence.txt")
    if hashlib.sha256(t).hexdigest()!=TSV_SHA:
        raise ValueError("Original occurrence TSV SHA256 drift")
    return list(csv.DictReader(io.StringIO(t.decode("utf-8-sig")),delimiter="\t"))

def pond_cluster_ci(rows,n=2000):
    clusters=defaultdict(list)
    for r in rows:clusters[r["pond"]].append(r)
    ponds=list(sorted(clusters))
    if not ponds:return [None,None]
    rng=random.Random(SEED)
    values=[]
    for _ in range(n):
        sample=[r for _ in ponds for r in clusters[rng.choice(ponds)]]
        if sample:values.append(sum(r["egg_gap_days"]>0 for r in sample)/len(sample))
    values.sort()
    return [round(values[int((len(values)-1)*p)],5) for p in (.025,.975)]

def compute(rows):
    all_days=set();stage=defaultdict(list);positive_duplicate_keys=Counter()
    for r in rows:
        try:day=date.fromisoformat(r["eventDate"])
        except Exception as ex:raise ValueError("invalid original date") from ex
        if not 2016<=day.year<=2021:continue
        # Publisher reports generalized coordinates (~100m), not exact nests or GPS.
        pool=(r["decimalLatitude"],r["decimalLongitude"])
        all_days.add((pool,day))
        tax=TAXON.get(r["scientificName"])
        if not tax or (tax,r["lifeStage"]) not in STAGES:continue
        key=(pool,day,tax,r["lifeStage"])
        stage[key].append(int(r["individualCount"]))
        positive_duplicate_keys[key]+=1
    # A valid zero means this species-stage was actually assessed;
    # absent species-stage rows stay unavailable, NEVER imputed absent.
    measured={k:max(v) for k,v in stage.items()}
    ids={key:"P%02d"%(i+1) for i,key in enumerate(sorted({p for p,d in all_days}))}
    visits=defaultdict(set)
    for pool,day in all_days:visits[(pool,day.year)].add(day)
    records=[];event_rows=[]
    for (pool,year),days in sorted(visits.items()):
        days=sorted(days)
        first={}
        for tax,st in STAGES:
            candidates=[d for d in days if measured.get((pool,d,tax,st),0)>0]
            first[(tax,st)]=min(candidates) if candidates else None
        f=first[("frog","egg")];s=first[("spotted","egg")]
        frog_larva_spotted_egg=0;frog_larva_jefferson_egg=0
        for day in days:
            event={"pond":ids[pool],"year":year,"date":day.isoformat()}
            for tax,st in STAGES:
                k=(pool,day,tax,st)
                col=tax+"_"+st
                event[col+"_assessed"]=(k in measured)
                event[col+"_positive"]=(k in measured and measured[k]>0)
            frog_larva_spotted_egg+=int(event["frog_tadpole_positive"] and event["spotted_egg_positive"])
            frog_larva_jefferson_egg+=int(event["frog_tadpole_positive"] and event["jefferson_egg_positive"])
            event_rows.append(event)
        records.append({"pond":ids[pool],"year":year,"n_visits":len(days),
             "first_wood_egg":f.isoformat() if f else "",
             "first_spotted_egg":s.isoformat() if s else "",
             "egg_gap_days":(s-f).days if f and s else None,
             "frog_egg_left_censored":bool(f==days[0]) if f else None,
             "spotted_egg_left_censored":bool(s==days[0]) if s else None,
             "frog_tadpole_spotted_egg_same_day":frog_larva_spotted_egg,
             "frog_tadpole_jefferson_egg_same_day":frog_larva_jefferson_egg})
    both=[r for r in records if r["egg_gap_days"] is not None]
    ordered=[r for r in both if r["egg_gap_days"]!=0]
    positive=sum(r["egg_gap_days"]>0 for r in both)
    co_dates=sum(r["frog_tadpole_spotted_egg_same_day"] for r in records)
    fully_assessed=sum(all(e[t+"_"+s+"_assessed"] for t,s in STAGES[:4]) for e in event_rows)
    eff3=[r for r in both if r["n_visits"]>=3]
    unleft=[r for r in both if not r["frog_egg_left_censored"] and not r["spotted_egg_left_censored"]]
    summary={"source":"Mohonk Preserve GBIF-US IPT DwC-A v1.1 DOI 10.15468/dypfbs",
      "source_zip_sha256":SOURCE_SHA,"source_occurrence_tsv_sha256":TSV_SHA,
      "original_rows":len(rows),"study_years":[2016,2021],
      "ponds":len(ids),"pond_years":len(records),"pond_dates":len(event_rows),
      "pond_dates_both_four_target_stages_assessed":fully_assessed,
      "both_species_eggs_detected_pond_years":len(both),
      "wood_frog_egg_first":positive,
      "same_first_detection_date":sum(r["egg_gap_days"]==0 for r in both),
      "spotted_salamander_egg_first":sum(r["egg_gap_days"]<0 for r in both),
      "median_gap_days_spotted_minus_wood":statistics.median(r["egg_gap_days"] for r in both),
      "strict_order_pondyears":len(ordered),
      "wood_first_among_strict_orders":positive/len(ordered) if ordered else None,
      "pond_cluster_bootstrap_95ci":pond_cluster_ci(ordered),
      "pondyears_frog_tadpole_and_spotted_egg_codetected":sum(r["frog_tadpole_spotted_egg_same_day"]>0 for r in records),
      "pond_dates_frog_tadpole_and_spotted_egg_codetected":co_dates,
      "pond_dates_frog_tadpole_and_jefferson_egg_codetected":sum(r["frog_tadpole_jefferson_egg_same_day"] for r in records),
      "pond_dates_spotted_salamander_larvae_recorded_positive":sum(e["spotted_tadpole_positive"] for e in event_rows),
      "egg_pairs_at_least_three_visits":len(eff3),
      "wood_first_egg_pairs_at_least_three_visits":sum(r["egg_gap_days"]>0 for r in eff3),
      "egg_pairs_both_first_eggs_after_initial_visit":len(unleft),
      "wood_first_egg_pairs_both_after_initial_visit":sum(r["egg_gap_days"]>0 for r in unleft),
      "duplicate_target_stage_day_keys":sum(n>1 for n in positive_duplicate_keys.values()),
      "outcome_label":"first egg DETECTION and within-day stage CO-DETECTION",
      "not_observed":["actual egg laying date","predation attack","embryo mortality","dragonfly life stages","salamander larval presence after later spring"],
      "independent_of_NAAMP":True,"hypothesis_test_status":"exploratory observational, not preregistered"}
    years=[]
    for y in range(2016,2022):
        these=[r for r in both if r["year"]==y]
        years.append({"year":y,"pondyears_both_eggs":len(these),
          "frog_egg_first":sum(r["egg_gap_days"]>0 for r in these),
          "same_day":sum(r["egg_gap_days"]==0 for r in these),
          "salamander_egg_first":sum(r["egg_gap_days"]<0 for r in these),
          "frog_tadpole_spotted_egg_same_day":sum(r["frog_tadpole_spotted_egg_same_day"] for r in records if r["year"]==y)})
    return summary,records,years,event_rows

def write_csv(path,rows):
    if not rows:return
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    args=p.parse_args()
    result,pondyears,annual,events=compute(load_original(args.source))
    args.out_dir.mkdir(parents=True,exist_ok=True)
    write_csv(args.out_dir/"mohonk_egg_stage_priority_by_pondyear.csv",pondyears)
    write_csv(args.out_dir/"mohonk_egg_stage_priority_by_year.csv",annual)
    (args.out_dir/"mohonk_egg_stage_priority_result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
