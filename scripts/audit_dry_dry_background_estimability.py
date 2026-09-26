#!/usr/bin/env python3
import importlib.util, json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("pulse_base",ROOT/"run_naamp_ecological_pulse.py")
base=importlib.util.module_from_spec(spec); spec.loader.exec_module(base)

d,_=base.build_runs(base.load())
dry=d[d["DaysSinceRain"]>=8].copy()
out={"total_dry_runs":int(len(dry)),"rules":{}}
strata=0
for _,g in dry.groupby(["State","RouteNumber","RunNumber"],sort=False):
    if len(g)>=2: strata+=1
out["strata_with_ge2_dry_runs"]=strata

def summarize(pairs):
    if not pairs:return {"pairs":0,"routes":0}
    x=pd.DataFrame(pairs)
    return {
      "pairs":int(len(x)),
      "routes":int(x.route_cluster.nunique()),
      "year_gap_min":int(x.year_gap.min()),
      "year_gap_median":float(x.year_gap.median()),
      "year_gap_max":int(x.year_gap.max())
    }

pairsA=[];pairsB=[];pairsC=[];pairsD=[]
for _,g in dry.groupby(["State","RouteNumber","RunNumber"],sort=False):
    g=g.sort_values(["SurveyYear","RunID"]).reset_index(drop=True)
    rc=str(g["route_cluster"].iloc[0]) if len(g) else ""
    for i in range(len(g)-1):
        gap=int(g.loc[i+1,"SurveyYear"]-g.loc[i,"SurveyYear"])
        rec={"route_cluster":rc,"year_gap":gap}
        pairsA.append(rec)
        if gap<=3:pairsB.append(rec)
    for i in range(len(g)):
      for j in range(i+1,len(g)):
        gap=int(g.loc[j,"SurveyYear"]-g.loc[i,"SurveyYear"])
        if gap<=3:pairsC.append({"route_cluster":rc,"year_gap":gap})
    i=0
    while i+1<len(g):
        gap=int(g.loc[i+1,"SurveyYear"]-g.loc[i,"SurveyYear"])
        pairsD.append({"route_cluster":rc,"year_gap":gap})
        i+=2

out["rules"]["A_adjacent_dry_observations"]=summarize(pairsA)
out["rules"]["B_adjacent_dry_yeargap_le3"]=summarize(pairsB)
out["rules"]["C_all_unique_yeargap_le3"]=summarize(pairsC)
out["rules"]["D_greedy_nonoverlap_adjacent_dry"]=summarize(pairsD)

Path("DRY_DRY_BACKGROUND_ESTIMABILITY_AUDIT_RECEIPT_V0_1.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
