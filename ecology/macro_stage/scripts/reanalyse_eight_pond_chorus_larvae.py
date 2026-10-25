#!/usr/bin/env python3
"""Reproduce eight-pond frog chorus-to-tadpole and larval enemy windows.

Carter et al 2018 male calls XLSX, Carroll et al 2023 funnel-trap XLSX.
STREAM original OOXML (~125MB decompressed), do not use Excel rendered charts.
No frogs are assumed to spawn the day of the chorus; no predation measured.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,json,math,statistics,zipfile,xml.etree.ElementTree as ET
from collections import Counter,defaultdict
from pathlib import Path

NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
STAGE_CODES={"R.sph":"RS","R.cla":"RCL","R.cat":"RCA","P.cru":"PC",
             "H.ver":"HV","R.pal":"RP","H.cin":"HC","G.car":"GC",
             "B.woo":"BW","B.val":"BV","P.tri":"PT"}
SOURCE_LARVA_SHA="302f1d976725ff926c682331a34e302262adbdb3be1f80fc67c1ccc990343f6f"
SOURCE_CALL_MD5="37dd4dc8289f0c1ce8d249791b3df558"
START,END=2002,2006

def excel_date(serial):
    return (dt.datetime(1899,12,30)+dt.timedelta(days=int(serial))).date()

def xml_rows(path,sheet):
    with zipfile.ZipFile(path) as z:
        strings=[]
        if "xl/sharedStrings.xml" in z.namelist():
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            strings=["".join(t.text or "" for t in si.iter(NS+"t")) for si in root.iter(NS+"si")]
        with z.open(sheet) as fh:
            for evt,elem in ET.iterparse(fh,events=("end",)):
                if elem.tag!=NS+"row":continue
                data={}
                for cell in elem.findall(NS+"c"):
                    ref=cell.get("r","A")
                    label="".join(c for c in ref if c.isalpha())
                    idx=0
                    for c in label:idx=idx*26+ord(c)-64
                    v=cell.find(NS+"v")
                    content=v.text if v is not None else None
                    typ=cell.get("t")
                    if typ=="s" and content is not None:content=strings[int(content)]
                    elif typ=="inlineStr":content="".join(e.text or "" for e in cell.iter(NS+"t"))
                    elif content is not None and typ not in ("str","e"):
                        try:content=float(content)
                        except ValueError:pass
                    data[idx-1]=content
                elem.clear()
                yield data

def validate_and_read(root):
    a=root/"funneltrapdata.xlsx";b=root/"dailycalls_dryad.xlsx"
    if hashlib.sha256(a.read_bytes()).hexdigest()!=SOURCE_LARVA_SHA:
        raise ValueError("Carroll original source digest changed")
    if hashlib.md5(b.read_bytes()).hexdigest()!=SOURCE_CALL_MD5:
        raise ValueError("Carter original source digest changed")
    traps=[];calls=defaultdict(dict);audit=Counter();historical_positive_calls=defaultdict(list)
    for pond in range(1,9):
        it=xml_rows(a,f"xl/worksheets/sheet{pond}.xml")
        header=next(it);labels={j:str(v) for j,v in header.items()}
        for row in it:
            stamp=row.get(0)
            if not isinstance(stamp,(int,float)):continue
            when=excel_date(stamp)
            if not START<=when.year<=END:continue
            d={"pond":pond,"year":when.year,"date":when}
            for j,label in labels.items():
                if j==0:continue
                v=row.get(j)
                d[label]=float(v) if isinstance(v,(float,int)) else None
            d["frog_larvae"]=sum(d.get(s) or 0 for s in STAGE_CODES)
            traps.append(d)
    for i,row in enumerate(xml_rows(b,"xl/worksheets/sheet1.xml")):
        if i==0:continue
        pond,yr,stamp,sp,count=row.get(0),row.get(1),row.get(2),row.get(4),row.get(5)
        if not all(isinstance(x,(float,int)) for x in (pond,yr,stamp)):
            audit["original_non_numeric_row"]+=1
            continue
        if not 1<=pond<=8 or not START-1<=yr<=END:continue
        when=excel_date(stamp)
        if when.year!=yr:
            audit["original_year_calendar_conflict"]+=1
            continue
        if sp not in list(STAGE_CODES.values())+["AC"]:
            audit["unknown_species_token"]+=1
            continue
        if not isinstance(count,(int,float)) or not 0<=count<=30:
            audit["missing_or_invalid_call_score"]+=1
            continue
        if count>0:historical_positive_calls[int(pond),int(yr),sp].append(when)
        if yr<START:continue
        day=(int(pond),when)
        if sp in calls[day]:raise ValueError("duplicate original calling taxon-day")
        calls[day][sp]=float(count)
    if len(traps)!=2080 or len(calls)!=13045:
        raise ValueError(f"source survey grain changed: weekly={len(traps)} call days={len(calls)}")
    return traps,calls,dict(audit),historical_positive_calls

def convolve(left,right):
    out=[0.]*(len(left)+len(right)-1)
    for i,v in enumerate(left):
        if v==0:continue
        for j,w in enumerate(right):out[i+j]+=v*w
    return out

def hypergeom(a,b):
    n=len(a);na=sum(a);nb=sum(b)
    out=[0.]*(min(na,nb)+1)
    for j in range(max(0,na+nb-n),min(na,nb)+1):
        out[j]=math.comb(na,j)*math.comb(n-na,nb-j)/math.comb(n,nb)
    return out

def circular(a,b):
    n=len(a);out=[0.]*(min(sum(a),sum(b))+1)
    for shift in range(n):
        co=sum(a[(i+shift)%n] and b[i] for i in range(n))
        out[co]+=1/n
    return out

def enemy_reference(traps,enemy):
    groups=defaultdict(list)
    for r in traps:groups[(r["pond"],r["year"])].append(r)
    result={};cellrows=[]
    for mode in ("fixed","circular"):
        law=[1.];obs=0;ex=0.
        for (pond,year),data in sorted(groups.items()):
            data=sorted(data,key=lambda r:r["date"])
            frog=[r["frog_larvae"]>0 for r in data]
            partner=[(r.get(enemy) or 0)>0 for r in data]
            co=sum(x and y for x,y in zip(frog,partner))
            marginal=sum(frog)*sum(partner)/len(data)
            pmf=hypergeom(frog,partner) if mode=="fixed" else circular(frog,partner)
            law=convolve(law,pmf)
            obs+=co;ex+=marginal
            if mode=="fixed":
                cellrows.append({"pond":pond,"year":year,"n_weeks":len(data),
                  "frog_weeks":sum(frog),"partner_weeks":sum(partner),
                  "co_captured_weeks":co,"margin_expected":marginal,
                  "partner":enemy})
        total=sum(law)
        law=[x/total for x in law]
        result[mode]={"observed":obs,"expected":round(ex,6),
          "observed_over_expected":round(obs/ex,5) if ex else None,
          "conditional_upper_tail":round(sum(law[obs:]),8)}
    return result,cellrows

def summarize(traps,calls,audit,historical_positive_calls,out):
    out.mkdir(parents=True,exist_ok=True)
    adults=defaultdict(list); weekly_calls=0
    for (pond,day),taxa in calls.items():
        for sp,n in taxa.items():
            if n>0:adults[pond,day.year,sp].append(day)
    by=defaultdict(list)
    for r in traps:by[r["pond"],r["year"]].append(r)
    lags=[];paired=0
    for (pond,year),rs in sorted(by.items()):
        rs.sort(key=lambda x:x["date"])
        for tad,sp in STAGE_CODES.items():
            assessed=[r for r in rs if r.get(tad) is not None]
            positive=[r for r in assessed if r[tad]>0]
            ac=adults.get((pond,year,sp),[])
            if positive and ac:
                first_l=min(r["date"] for r in positive)
                first_c=min(ac)
                prior=historical_positive_calls.get((pond,year-1,sp),[])
                last_prior=max(prior) if prior else None
                lags.append({"pond":pond,"year":year,"species_code":sp,
                  "last_previous_year_adult_call":str(last_prior) if last_prior else "",
                  "days_first_larva_after_last_prior_year_call":(first_l-last_prior).days if last_prior else "",
                  "days_first_larva_minus_first_chorus":(first_l-first_c).days,
                  "first_larva_at_year_initial_trap":first_l==min(r["date"] for r in assessed),
                  "first_larval_catch":str(first_l),"first_adult_call":str(first_c)})
            for r in assessed:
                valid=0
                for d in range(1,8):
                    if sp in calls.get((pond,r["date"]-dt.timedelta(days=d)),{}):
                        valid+=1
                if valid>=5:paired+=1
    guild={};cells=[]
    for source in ("Naiad","mole.sala.larvae","fish"):
        if source=="fish":
            for r in traps:
                r["fish"]=(r.get("Bass") or 0)+(r.get("GreenSunfish") or 0)
        guild[source],arr=enemy_reference(traps,source)
        cells.extend(arr)
    taxon={}
    for sp in sorted(STAGE_CODES.values()):
        vv=[x for x in lags if x["species_code"]==sp]
        if not vv:continue
        t=[x["days_first_larva_minus_first_chorus"] for x in vv]
        unleft=[x for x in vv if not x["first_larva_at_year_initial_trap"]]
        taxon[sp]={"n_pond_taxon_years":len(vv),"median_larva_minus_call_days":statistics.median(t),
          "larva_detected_before_call_n":sum(x<0 for x in t),
          "non_left_censored_groups_n":len(unleft),
          "non_left_censored_larva_before_call_n":sum(x["days_first_larva_minus_first_chorus"]<0 for x in unleft)}
    prechorus_rcl=[r for r in lags if r["species_code"]=="RCL" and r["days_first_larva_minus_first_chorus"]<0]
    valid_previous=[r for r in prechorus_rcl if r["last_previous_year_adult_call"]]
    rcl_lag=[r["days_first_larva_after_last_prior_year_call"] for r in valid_previous]
    carryover={"rcl_prior_larva_before_current_call_n":len(prechorus_rcl),
        "rcl_prior_year_chorus_observed_for_prechorus_larva_n":len(valid_previous),
        "rcl_median_days_since_prior_year_last_call":statistics.median(rcl_lag) if rcl_lag else None,
        "rcl_prior_year_to_current_larva_interval_days_minmax":[min(rcl_lag),max(rcl_lag)] if rcl_lag else None,
        "not_tracking_individual_cohorts":True}
    result={"analysis":"eight_pond_carter_carroll_2002_2006_exploratory_chorus_larva_enemy_windows",
            "source_Carroll_sha256":SOURCE_LARVA_SHA,"source_Carter_md5":SOURCE_CALL_MD5,
            "n_independent_ponds":8,"n_pondyears":len(by),
            "weekly_aquatic_trap_visits":len(traps),"daily_pond_acoustic_assessments_with_at_least_one_valid_taxon":len(calls),
            "pond_week_x_taxon_acoustic_trap_matches_ge5of7":paired,
            "pond_year_species_first_call_first_larva_pairs":len(lags),
            "source_qc":audit,"species_stage_lag":taxon,"cross_year_larval_carryover":carryover,"guild_week_alignment":guild,
            "aquatic_vegetation_measured":False,
            "co_captures_are_predation":False,
            "adult_chorus_equals_true_laying_date":False,
            "lag_is_egg_hatch_duration":False,
            "interpretation":"Life-history stage carry-over can uncouple current male chorus and aquatic prey/enemy exposure."}
    def write_csv(name,rows):
        with (out/name).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write_csv("frog_chorus_first_larva_by_pond_year_species.csv",lags)
    write_csv("aquatic_pondyear_guild_cocapture.csv",cells)
    (out/"ecological_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    if len(lags)!=102 or guild["Naiad"]["fixed"]["observed"]!=303 or len(valid_previous)!=20:
        raise RuntimeError("original-source analysis failed previously observed group counts")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",required=True,type=Path)
    p.add_argument("--outdir",required=True,type=Path)
    a=p.parse_args()
    summarize(*validate_and_read(a.source_dir),a.outdir)
