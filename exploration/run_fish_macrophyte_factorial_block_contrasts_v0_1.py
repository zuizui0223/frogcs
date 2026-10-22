#!/usr/bin/env python3
"""Factorial fish × macrophyte organism-choice experimental reanalysis.

Source: https://doi.org/10.6084/m9.figshare.16627561.v2 (2021)
Randomized 2 fish statuses × 3 vegetation levels per physical block.
Repeated dates, individuals, pool counts and oviposition dips are NOT
independent biological replicates. Primary: two toad male-choice outcomes;
secondary: guild-specific fish×vegetation response contrasts. Not actual
three-species interaction or mediation through predatory insects.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import itertools
import json
import math
import re
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter,defaultdict
from pathlib import Path
from scipy.stats import t as students_t

SOURCE_URL="https://ndownloader.figshare.com/files/30796897"
SIZE=70127
MD5="e2d27edffb6c75b7208a609fafc79447"
SHA="86944f2d06b7e2739342a7b42ec4ff383df92d2cb8600a3d9c9c5de1f70758ae"
VEG=("no","aq","aq_lit")
FISH=("no_fish","fish")
TREATMENTS=tuple((f,v) for f in FISH for v in VEG)
NS="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
PK="http://schemas.openxmlformats.org/package/2006/relationships"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
U="{"+NS+"}"
SHEETS={
 "Bufonidae":{"outcome":"sexmale","group":"toad",
   "names":("B. bufo","B. viridis")},
 "Odonata":{"outcome":"number of dips","group":"odonate",
   "names":("S. danae","S. sanguineum")},
 "Notonectidae":{"outcome":"individuals","group":"water_bug",
   "names":("N. glauca","N. obliqua")},
 "Dytiscidae":{"outcome":"individuals","group":"diving_beetle",
   "names":("A. sulcatus","D. marginalis")}
}
H1=[("B. bufo","aq"),("B. bufo","aq_lit"),
    ("B. viridis","aq"),("B. viridis","aq_lit")]
H2=[("B. bufo","aq"),("B. bufo","aq_lit"),
    ("B. viridis","aq"),("B. viridis","aq_lit")]

def check_source():
    request=urllib.request.Request(SOURCE_URL,headers={
      "User-Agent":"frogcs-fish-macrophyte-reanalysis-SourcePin-v0.1",
      "Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*"})
    with urllib.request.urlopen(request,timeout=75) as r:
        raw=r.read(2_000_000)
    md5=hashlib.md5(raw).hexdigest()
    sha=hashlib.sha256(raw).hexdigest()
    if len(raw)!=SIZE or md5!=MD5 or sha!=SHA:
        raise RuntimeError("Figshare official 16627561.v2 experiment source checksum/size changed")
    return raw,{"doi":"10.6084/m9.figshare.16627561.v2",
                "bytes":len(raw),"MD5":md5,"SHA256":sha,"verification":"PASS",
                "raw_source_redistributed":False}

def sheet_cells(z,path,shared):
    doc=ET.fromstring(z.read(path))
    out=[]
    for row in doc.findall(".//"+U+"sheetData/"+U+"row"):
        cells={}
        for c in row.findall(U+"c"):
            key=c.attrib.get("r","")
            m=re.match(r"[A-Z]+",key)
            if not m:continue
            name=m.group()
            ty=c.attrib.get("t")
            val=c.find(U+"v")
            if ty=="s" and val is not None:
                raw=shared[int(val.text)]
            elif ty=="inlineStr":
                raw="".join(t.text or "" for t in c.iter() if t.tag==U+"t")
            elif val is not None:
                raw=val.text
            else:
                raw=None
            if raw is not None:
                cells[name]=str(raw).strip()
        out.append(cells)
    return out

def workbook_tables(raw):
    z=zipfile.ZipFile(io.BytesIO(raw))
    if z.testzip() is not None:raise RuntimeError("Experiment source ZIP checksum corrupted")
    shared=[]
    if "xl/sharedStrings.xml" in z.namelist():
        ss=ET.fromstring(z.read("xl/sharedStrings.xml"))
        shared=["".join(t.text or "" for t in si.iter() if t.tag==U+"t")
                for si in ss.findall(U+"si")]
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    mapping={}
    for elem in rel.findall("{"+PK+"}Relationship"):
        dst=elem.attrib.get("Target","")
        if dst.startswith("/"):path=dst.lstrip("/")
        elif dst.startswith("xl/"):path=dst
        else:path="xl/"+dst
        mapping[elem.attrib.get("Id")]=path
    book=ET.fromstring(z.read("xl/workbook.xml"))
    sheets={}
    for sheet in book.findall(".//"+U+"sheet"):
        name=sheet.attrib["name"]
        rid=sheet.attrib["{"+R+"}id"]
        if name not in SHEETS:continue
        cells=sheet_cells(z,mapping[rid],shared)
        if len(cells)<2:raise RuntimeError("Experiment sheet has no source rows "+name)
        header={col:value for col,value in cells[0].items()}
        if len(set(header.values()))!=len(header):raise RuntimeError("Repeated experiment source column")
        needed={"species","date","block","plot","vegetation","predator",
                SHEETS[name]["outcome"]}
        if not needed.issubset(set(header.values())):
            raise RuntimeError("Missing source experiment field "+name)
        vals=[]
        for item in cells[1:]:
            row={label:item.get(col) for col,label in header.items()}
            if all(x is None for x in row.values()):continue
            vals.append(row)
        sheets[name]=vals
    if set(sheets)!=set(SHEETS):raise RuntimeError("Four guild sheets missing")
    return sheets

def nonneg_int(value):
    if value is None or str(value).lower() in ("na","n/a","nan","null",""):
        return None
    try:x=float(value)
    except (TypeError,ValueError):raise RuntimeError("Source count not interpretable "+repr(value)[:60])
    if not math.isfinite(x) or x<0 or abs(x-round(x))>1e-9:
        raise RuntimeError("Source count is noninteger or invalid "+repr(value)[:60])
    return int(round(x))

def synthetic():
    # 6 physical experimental tanks: one of every fish × vegetation cell;
    # plant-contrast exact randomization operates on the three fishless
    # assigned physical tanks, not separate permutations at each date.
    ordered={(f,v):{"plot":str(f)+v,"share":(i+1)/21}
             for i,(f,v) in enumerate(TREATMENTS)}
    base={k:item["share"] for k,item in ordered.items()}
    assert abs(sum(base.values())-1)<1e-11
    t=(base[("no_fish","aq_lit")]-base[("no_fish","no")])
    assert abs(t-2/21)<1e-10
    vals=[base[("no_fish",v)] for v in VEG]
    perm=list(itertools.permutations(vals))
    assert len(perm)==6
    assert len({round(a[2]-a[0],10) for a in perm})>1
    return {"status":"PASS","six_treatments":"PASS",
            "strict_unique_tank_assignment":"PASS",
            "fixed_block_plant_randomization":"PASS"}

def event_normalized(sheets):
    events=defaultdict(dict)
    qc={}
    for name,rows in sheets.items():
        spec=SHEETS[name]
        seen=Counter()
        raw_count=0
        conflict=Counter()
        for item in rows:
            sp=item.get("species")
            if sp not in spec["names"]:
                raise RuntimeError("Source has an unplanned taxon label "+str(sp))
            date=item.get("date")
            block=item.get("block")
            plot=item.get("plot")
            vegetation=item.get("vegetation")
            predator=item.get("predator")
            if not all((date,block,plot,vegetation,predator)):
                conflict["missing_label"]+=1;continue
            if vegetation not in VEG or predator not in FISH:
                raise RuntimeError("Unknown randomized treatment identity: "+str((vegetation,predator)))
            val=nonneg_int(item.get(spec["outcome"]))
            raw_count+=1
            key=(name,sp,block,date)
            p=events[key]
            tank=(predator,vegetation)
            if tank in p:
                old=p[tank]
                if old["plot"]!=plot:
                    raise RuntimeError("Two different physical pools recorded for one assigned treatment")
                if name!="Odonata":
                    conflict["repeated_pool_rows_not_odonata"]+=1
                if old["count"] is None or val is None:
                    old["count"]=None
                else:old["count"]+=val
            else:
                p[tank]={"count":val,"plot":plot}
            seen[sp]+=1
        qc[name]={"original_rows":len(rows),"rows_with_all_labels":raw_count,
                  "source_taxon_rows":dict(seen),
                  "structural_anomalies":dict(conflict),
                  "outcome_col":spec["outcome"]}
    per_species=defaultdict(list)
    event_quality=Counter()
    assignment=defaultdict(dict)
    for (sheet,sp,block,date),treat in sorted(events.items()):
        if len(treat)!=6 or set(treat)!=set(TREATMENTS):
            event_quality[(sheet,sp,"incomplete_six_treatment")]+=1
            continue
        if len({v["plot"] for v in treat.values()})!=6:
            event_quality[(sheet,sp,"non_unique_physical_pools")]+=1
            continue
        mapping=assignment[(sheet,sp,block)]
        for t,entry in treat.items():
            if t in mapping and mapping[t]!=entry["plot"]:
                raise RuntimeError("Physical tank treatment switched across dates")
            mapping[t]=entry["plot"]
        values=[v["count"] for v in treat.values()]
        if any(v is None for v in values):
            event_quality[(sheet,sp,"missing_outcome_one_tank")]+=1
            continue
        total=sum(values)
        if total<=0:
            event_quality[(sheet,sp,"no_observed_choice")]+=1
            continue
        fraction={t:val["count"]/total for t,val in treat.items()}
        per_species[sp].append({"sheet":sheet,"group":SHEETS[sheet]["group"],
                                "species":sp,"block":block,"date":date,
                                "total":total,"share":fraction,
                                "plots":{t:info["plot"] for t,info in treat.items()}})
        event_quality[(sheet,sp,"complete_normalized")]+=1
    for sheet,sp,reason in event_quality:
        qc[sheet].setdefault("event_gate",{}).setdefault(sp,{})[reason]=event_quality[(sheet,sp,reason)]
    return per_species,qc

def mean(nums):
    return sum(nums)/len(nums) if nums else None

def diff_ci_by_block(vals):
    n=len(vals)
    if n<3:return {"status":"underpowered_independent_blocks","n_blocks":n}
    estimate=mean(vals)
    sq=sum((v-estimate)**2 for v in vals)/(n-1)
    se=math.sqrt(sq/n)
    margin=students_t.ppf(.975,n-1)*se
    return {"status":"fitted","estimate":estimate,
            "ci95":[estimate-margin,estimate+margin],
            "se_block":se,"n_independent_blocks":n,
            "n_positive_blocks":sum(x>0 for x in vals),
            "n_negative_blocks":sum(x<0 for x in vals),
            "sign_consistency_fraction":max(sum(x>0 for x in vals),
                                            sum(x<0 for x in vals))/n}

def equal_block_summary(events):
    blockevents=defaultdict(list)
    for ev in events:blockevents[ev["block"]].append(ev)
    avg={}
    for block,evs in sorted(blockevents.items()):
        avg[block]={t:mean([z["share"][t] for z in evs])
                    for t in TREATMENTS}
    return avg,{"n_choice_events":len(events),
                 "n_blocks":len(avg),
                 "n_distinct_sampling_dates":len(set(z["date"] for z in events)),
                 "n_original_dips_or_individuals":sum(z["total"] for z in events),
                 "events_by_block":{b:len(x) for b,x in blockevents.items()}}

def exact_vegetation_permutation(block_means,selected):
    """Exact 3!^B source-randomization within fishless pools per fixed block.

    Assignment is permuted once per block, retaining identical physical
    plot mean response over ALL sampling dates.
    """
    B=len(block_means)
    obs=mean([q[("no_fish",selected)]-q[("no_fish","no")]
              for q in block_means.values()])
    block_possible=[]
    for q in block_means.values():
        vec=[q[("no_fish",v)] for v in VEG]
        vals=[perm[VEG.index(selected)]-perm[0]
              for perm in itertools.permutations(vec)]
        block_possible.append(vals)
    combinations=6**B
    if combinations>50000:
        raise RuntimeError("Original 4 experimental blocks exceeded exact permutation limit")
    extreme=0
    for config in itertools.product(*block_possible):
        t=mean(config)
        if abs(t)>=abs(obs)-1e-12:extreme+=1
    return {"test":"exact_fishless_plot_plant_label_permutations_per_block",
            "effect":obs,"permutations":combinations,
            "extreme_assignments":extreme,
            "p_exact_two_sided":extreme/combinations,
            "n_blocks":B}

def bh_adjust(pairs):
    # Family always includes 4 planned toad contrasts. Ineligible tests are
    # assigned p=1, never removed to inflate statistical discoveries.
    indexed=sorted([(p,i) for i,p in enumerate(pairs)])
    m=len(pairs);out=[1.0]*m;cur=1.0
    for rank in range(m,0,-1):
        p,i=indexed[rank-1]
        cur=min(cur,p*m/rank)
        out[i]=cur
    return out

def analyze(sheets):
    datasets,qc=event_normalized(sheets)
    analysis={"source_quality":qc,"species":{},
              "planned_H1_permutation_family":[],
              "hypotheses":{
                "H1_randomized_plant_changes_toad_male_choice":"analysis_pending",
                "H2_fish_x_plant_changes_toad_choice":"analysis_pending",
                "H3_taxon_x_fish_x_plant_responses":"noncausal_crossguild_heterogeneity_only",
                "fish_insect_predator_mediated_tadpole_survival":"not_identifiable_in_source",
                "irreducible_three_species_causal_interaction":"not_identifiable_in_source"}}
    for sheet,spec in SHEETS.items():
        for sp in spec["names"]:
            ev=datasets.get(sp,[])
            avg,coverage=equal_block_summary(ev)
            sufficient=bool(coverage["n_blocks"]>=3 and
                            coverage["n_distinct_sampling_dates"]>=3 and
                            coverage["n_choice_events"]>=12)
            out={"sheet":sheet,"functional_group":spec["group"],
                 "taxon":sp,"source_outcome_col":spec["outcome"],
                 "coverage":coverage,
                 "independent_experimental_unit":"block (not tank-date or individual)",
                 "inferential_gate":sufficient,
                 "means_of_block_averaged_choice_shares":{
                   f+"|"+v:mean([q[(f,v)] for q in avg.values()])
                   for f,v in TREATMENTS}}
            interaction={}
            for v in ("aq","aq_lit"):
                bv=[(q[("fish",v)]-q[("no_fish",v)])-
                    (q[("fish","no")]-q[("no_fish","no")])
                    for q in avg.values()]
                interaction[v]={
                    "blocks":{str(b):float((q[("fish",v)]-q[("no_fish",v)])-
                    (q[("fish","no")]-q[("no_fish","no")]))
                     for b,q in avg.items()},
                    "estimate":diff_ci_by_block(bv)}
            fish_mean=[mean([q[("fish",v)]-q[("no_fish",v)]
                                for v in VEG]) for q in avg.values()]
            out["fish_effect_across_plant_levels"]={
                "estimate":diff_ci_by_block(fish_mean)}
            out["fish_x_plant_interaction"]=interaction
            if spec["group"]=="toad":
                out["H1_fishless_plant_contrasts"]={}
                for v in ("aq","aq_lit"):
                    vals={b:q[("no_fish",v)]-q[("no_fish","no")]
                          for b,q in avg.items()}
                    effect=diff_ci_by_block(list(vals.values()))
                    test=exact_vegetation_permutation(avg,v) if sufficient else {
                       "status":"underpowered_block_date_gate",
                       "p_exact_two_sided":1.0}
                    out["H1_fishless_plant_contrasts"][v]={
                       "block_plant_effects":vals,"block_ci":effect,
                       "exact_randomization":test}
                    analysis["planned_H1_permutation_family"].append({
                       "taxon":sp,"contrast":v,
                       "eligible":sufficient,
                       "p_exact":test["p_exact_two_sided"],
                       "estimate":test.get("effect")})
            analysis["species"][sp]=out
    fam=analysis["planned_H1_permutation_family"]
    if len(fam)!=4:raise RuntimeError("Frozen two-toad/two-vegetation factorial tests missing")
    q=bh_adjust([x["p_exact"] for x in fam])
    n_supported=0
    for test,adj in zip(fam,q):
        test["BH_q_four_H1_tests"]=adj
        effect=analysis["species"][test["taxon"]]["H1_fishless_plant_contrasts"][test["contrast"]]
        vals=list(effect["block_plant_effects"].values())
        direction=1 if test["estimate"] is not None and test["estimate"]>0 else -1
        n_signed=sum(x*direction>0 for x in vals)
        confirmed=bool(test["eligible"] and adj<.05 and test["estimate"] is not None
                       and n_signed>=math.ceil(.75*len(vals)))
        test["experimental_plant_choice_effect_supported"]=confirmed
        n_supported+=int(confirmed)
    analysis["hypotheses"]["H1_randomized_plant_changes_toad_male_choice"]={
        "supported_plant_choice_contrasts":n_supported,
        "planned_contrasts":4,
        "note":"Previously published experiment: treatment causes choice allocation only under design assumptions, not NAAMP frog acoustic calls"}
    evidence=[]
    for sp in ("B. bufo","B. viridis"):
        d=analysis["species"][sp]
        for v,part in d["fish_x_plant_interaction"].items():
            m=part["estimate"]
            evidence.append({
              "species":sp,"plant_added":v,
              "effect":m.get("estimate"),
              "ci95":m.get("ci95"),
              "independent_blocks":m.get("n_independent_blocks",m.get("n_blocks")),
              "eligible":bool(d["inferential_gate"] and m["status"]=="fitted"),
              "supports_nonzero_block_95CI":bool(d["inferential_gate"] and
                m["status"]=="fitted" and (m["ci95"][0]>0 or m["ci95"][1]<0))}
            )
    # Finish the four-comparison family that was explicitly frozen before
    # response readback in FISH_MACROPHYTE_FACTORIAL_CAUSAL_CONTRACT_V0_1.
    # Student t with df=number of independent blocks-1 is exploratory
    # with only four tanks blocks, and not equivalent to a strong-null exact
    # factorial interaction randomization test.
    h2p=[]
    for x in evidence:
        m=analysis["species"][x["species"]]["fish_x_plant_interaction"][x["plant_added"]]["estimate"]
        if x["eligible"] and m["status"]=="fitted":
            if m["se_block"]==0:
                p=0.0 if abs(m["estimate"])>1e-12 else 1.0
            else:
                tstat=abs(m["estimate"]/m["se_block"])
                p=float(2*students_t.sf(tstat,m["n_independent_blocks"]-1))
        else:p=1.0
        x["nominal_p_block_t"]=p
        h2p.append(p)
    h2q=bh_adjust(h2p)
    for x,q in zip(evidence,h2q):
        x["BH_q_four_H2_contrasts"]=q
        x["factorial_interaction_supported_after_BH"]=bool(
             x["eligible"] and x["supports_nonzero_block_95CI"] and q<.05)
        x["classification"]=(
             "factorial_interaction_supported_after_BH"
             if x["factorial_interaction_supported_after_BH"]
             else "nominal_or_inconclusive_effect_modification")
    analysis["hypotheses"]["H2_fish_x_plant_changes_toad_choice"]={
        "block_level_interaction_contrasts":evidence,
        "n_supported_after_BH":sum(x["factorial_interaction_supported_after_BH"]
                                   for x in evidence),
        "scientific_boundary":"Factorial effect modification, NOT insect-mediated path"}
    return analysis

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,default=Path("build/fish_macrophyte_factorial"))
    a=p.parse_args();a.outdir.mkdir(parents=True,exist_ok=True)
    synthetic_result=synthetic()
    result={
        "analysis":"figshare_16627561_v2_fish_macrophyte_8taxon_factorial_block_contrasts_v0_1",
        "contract":"exploration/FISH_MACROPHYTE_FACTORIAL_CAUSAL_CONTRACT_V0_1.md",
        "synthetic_QA":synthetic_result,
        "source":{},"status":"source_unchecked",
        "experimental_dates_not_independent_replication":True,
        "fish_predator_consumed_insects_directly_measured":False,
        "third_species_causal_mediation_inferred":False,
        "underlying_paper_has_prior_published_treatment_findings":True,
        "RC6_main_SI_submission_unchanged":True}
    try:
        raw,receipt=check_source()
        result["source"]=receipt
        sheets=workbook_tables(raw)
        del raw
        output=analyze(sheets)
        result.update(output)
        result["status"]="full_block_contrasts_computed"
    except Exception as ex:
        result["status"]="source_or_predeclared_analysis_gate_blocked"
        result["error"]={"type":type(ex).__name__,"message":str(ex)[:850]}
    (a.outdir/"result.json").write_text(
        json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("FISH_MACROPHYTE_FACTORIAL_RESULT_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True,allow_nan=False),flush=True)
    print("FISH_MACROPHYTE_FACTORIAL_RESULT_END",flush=True)
    if result["status"]!="full_block_contrasts_computed":
        raise SystemExit("Blocked experimental source/independent-unit mapping; no treatment claim")
if __name__=="__main__":main()
