#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent
BASE_SCRIPT=ROOT/"run_naamp_ecological_pulse.py"
spec=importlib.util.spec_from_file_location("pulse_base",BASE_SCRIPT)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

Q=1.959963984540054
RECENT=["day0","day1","days2_3","days4_7"]

def rain_bin(x):
    x=float(x)
    if x==0:return "day0"
    if x==1:return "day1"
    if 2<=x<=3:return "days2_3"
    if 4<=x<=7:return "days4_7"
    if 8<=x<=180:return "dry"
    raise ValueError(x)

def build_pairs():
    d,sets=base.build_runs(base.load())
    rows=[]
    for _,g in d.groupby(["State","RouteNumber","RunNumber"],sort=False):
        g=g.sort_values(["SurveyYear","RunID"]).reset_index(drop=True)
        for i in range(len(g)-1):
            a=g.iloc[i]; b=g.iloc[i+1]
            ba=rain_bin(a.DaysSinceRain); bb=rain_bin(b.DaysSinceRain)
            if ba=="dry" and bb=="dry":
                cls="dry_dry"; recent=None; dry=None
            elif (ba=="dry") ^ (bb=="dry"):
                recent=a if ba!="dry" else b
                dry=b if ba!="dry" else a
                cls=rain_bin(recent.DaysSinceRain)
            else:
                continue

            A=sets[str(a.RunID)]; B=sets[str(b.RunID)]
            shared=len(A&B); ao=len(A-B); bo=len(B-A)
            sor=(ao+bo)/(2*shared+ao+bo) if (2*shared+ao+bo)>0 else np.nan
            mn=min(ao,bo)
            sim=mn/(shared+mn) if (shared+mn)>0 else (0.0 if (ao+bo)>0 else np.nan)

            row={
                "State":str(a.State),
                "RouteNumber":str(a.RouteNumber),
                "RunNumber":str(a.RunNumber),
                "route_cluster":str(a.route_cluster),
                "year_gap":int(abs(int(a.SurveyYear)-int(b.SurveyYear))),
                "pair_class":cls,
                "simpson_turnover":sim,
                "sorensen_dissimilarity":sor,
                "discordant_species_count":int(ao+bo),
                "abs_temp_difference":float(abs(float(a.mean_temp_c)-float(b.mean_temp_c))),
                "abs_doy_difference":float(abs(float(a.doy)-float(b.doy))),
            }
            if recent is not None:
                row.update({
                    "recent_bin":cls,
                    "recent_days_since_rain":float(recent.DaysSinceRain),
                    "dry_days_since_rain":float(dry.DaysSinceRain),
                    "richness_recent_minus_dry":int(recent.richness-dry.richness),
                    "temp_difference":float(recent.mean_temp_c-dry.mean_temp_c),
                    "doy_difference":float(recent.doy-dry.doy),
                })
            else:
                row.update({
                    "recent_bin":None,
                    "recent_days_since_rain":np.nan,
                    "dry_days_since_rain":np.nan,
                    "richness_recent_minus_dry":np.nan,
                    "temp_difference":np.nan,
                    "doy_difference":np.nan,
                })
            rows.append(row)
    return pd.DataFrame(rows)

def fit_background_contrast(d,response):
    x=d[np.isfinite(pd.to_numeric(d[response],errors="coerce"))].copy()
    counts=x["pair_class"].value_counts().to_dict()
    if counts.get("dry_dry",0)<100 or counts.get("days4_7",0)<50:
        raise SystemExit(f"minimum pair count failed for {response}: {counts}")

    for cls in RECENT:
        x[f"is_{cls}"]=(x["pair_class"]==cls).astype(float)

    formula=(
        f"{response} ~ is_day0 + is_day1 + is_days2_3 + is_days4_7 + "
        "abs_temp_difference + abs_doy_difference + year_gap + C(State) + C(RunNumber)"
    )
    fit=smf.ols(formula,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    effects={}
    for cls in RECENT:
        term=f"is_{cls}"
        b=float(fit.params[term]); se=float(fit.bse[term]); p=float(fit.pvalues[term])
        effects[cls]={
            "difference_vs_dry_dry":b,
            "se_cluster":se,
            "ci95":[b-Q*se,b+Q*se],
            "p_value":p,
        }
    return {
        "response":response,
        "formula":formula,
        "n_pairs":int(len(x)),
        "n_routes":int(x.route_cluster.nunique()),
        "pair_counts":{str(k):int(v) for k,v in counts.items()},
        "effects_vs_dry_dry":effects,
    }

def adjusted_richness_by_bin(d):
    x=d[d["pair_class"].isin(RECENT)].copy()
    x=x[np.isfinite(x["richness_recent_minus_dry"])].copy()
    for c in ["temp_difference","doy_difference","year_gap"]:
        x["c_"+c]=x[c]-x[c].mean()

    formula=(
        "richness_recent_minus_dry ~ C(recent_bin, Treatment(reference='day0')) + "
        "c_temp_difference + c_doy_difference + c_year_gap + C(State, Sum) + C(RunNumber, Sum)"
    )
    fit=smf.ols(formula,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})

    names=list(fit.params.index)
    cov=np.asarray(fit.cov_params(),float)
    params=np.asarray(fit.params,float)
    out={}
    for cls in RECENT:
        L=np.zeros(len(names),float)
        L[names.index("Intercept")]=1.0
        if cls!="day0":
            term=f"C(recent_bin, Treatment(reference='day0'))[T.{cls}]"
            if term not in names:
                raise SystemExit(f"missing richness bin term {term}")
            L[names.index(term)]=1.0
        mean=float(L@params)
        se=float(np.sqrt(L@cov@L))
        z=mean/se if se>0 else np.nan
        out[cls]={
            "adjusted_mean_recent_minus_dry":mean,
            "se_cluster":se,
            "ci95":[mean-Q*se,mean+Q*se],
            "z":z,
        }
    return {
        "formula":formula,
        "n_pairs":int(len(x)),
        "n_routes":int(x.route_cluster.nunique()),
        "bin_counts":{str(k):int(v) for k,v in x.recent_bin.value_counts().to_dict().items()},
        "adjusted_means":out,
    }

def analyze(d):
    primary=fit_background_contrast(d,"simpson_turnover")
    sor=fit_background_contrast(d,"sorensen_dissimilarity")
    disc=fit_background_contrast(d,"discordant_species_count")
    richness=adjusted_richness_by_bin(d)

    mem=primary["effects_vs_dry_dry"]["days4_7"]
    rich=richness["adjusted_means"]["days4_7"]
    return {
        "primary_turnover_background":primary,
        "secondary_sorensen_background":sor,
        "secondary_discordant_species_background":disc,
        "recent_minus_dry_richness_curve":richness,
        "decision":{
            "days4_7_turnover_memory_supported":bool(mem["ci95"][0]>0),
            "days4_7_richness_ci_includes_zero":bool(rich["ci95"][0]<=0<=rich["ci95"][1]),
            "two_phase_language_authorized":bool(mem["ci95"][0]>0 and rich["ci95"][0]<=0<=rich["ci95"][1]),
        }
    }

def main():
    d=build_pairs()
    primary=analyze(d)
    exact=d[d.year_gap==1].copy()
    sensitivity=analyze(exact)

    result={
        "analysis":"naamp_two_phase_community_memory_v0_1",
        "contract":"NAAMP_TWO_PHASE_COMMUNITY_MEMORY_CONTRACT_V0_1.json",
        "all_adjacent_year_pairs":primary,
        "exact_consecutive_year_sensitivity":sensitivity,
        "overall_pair_counts":{str(k):int(v) for k,v in d.pair_class.value_counts().to_dict().items()},
        "interpretation_boundary":{
            "dry_dry_is_background_active_community_turnover":True,
            "post_opening_followup":True,
            "formal_changepoint_test":False,
            "occupancy_turnover_claim":False,
            "causal_claim_authorized":False,
        }
    }
    Path("NAAMP_TWO_PHASE_COMMUNITY_MEMORY_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
