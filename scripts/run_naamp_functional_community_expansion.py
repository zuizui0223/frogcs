#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, io, json, math, urllib.request
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("pulse",ROOT/"run_naamp_ecological_pulse.py")
base=importlib.util.module_from_spec(spec);assert spec.loader;spec.loader.exec_module(base)
Q=1.959963984540054
URL="https://raw.githubusercontent.com/rdmpage/amphibio/c437acbc65b51b66e3dc4abd821ebe1cb06b200c/AmphiBIO_v1.csv"
BLOB="f98650972f3266c24962f70738799a39a8310e87"
ALIASES={"Hyla":"Dryophytes","Dryophytes":"Hyla","Lithobates":"Rana","Rana":"Lithobates"}
FIELDS=["Body_size_mm","Litter_size_min_n","Litter_size_max_n",
        "Offspring_size_min_mm","Offspring_size_max_mm","Reproductive_output_y"]
TRAITS=["log_body_size","log_clutch_size","log_offspring_size","log_reproductive_output"]

def getb(u):
    q=urllib.request.Request(u,headers={"User-Agent":"frogcs-functional-community/0.1"})
    with urllib.request.urlopen(q,timeout=120) as r:return r.read()
def blobsha(b):
    h=hashlib.sha1();h.update(f"blob {len(b)}\0".encode());h.update(b);return h.hexdigest()
def norm(x):
    t=str(x or "").strip().split();return " ".join(t[:2]) if len(t)>=2 else str(x or "").strip()

def load_trait_vectors(species_universe):
    b=getb(URL)
    if blobsha(b)!=BLOB:raise SystemExit("AmphiBIO drift")
    try:t=pd.read_csv(io.BytesIO(b),encoding="utf-8")
    except UnicodeDecodeError:t=pd.read_csv(io.BytesIO(b),encoding="cp1252")
    t["sp"]=t["Species"].map(norm); idx={s:i for i,s in enumerate(t.sp)}
    rows=[]
    for sp0 in sorted(species_universe):
        sp=norm(sp0); candidates=[sp];tok=sp.split()
        if len(tok)==2 and tok[0] in ALIASES:candidates.append(ALIASES[tok[0]]+" "+tok[1])
        hits=[c for c in candidates if c in idx]
        chosen=sp if sp in hits else (hits[0] if len(hits)==1 else None)
        if chosen is None:continue
        r=t.iloc[idx[chosen]]
        vals={c:pd.to_numeric(r.get(c,np.nan),errors="coerce") for c in FIELDS}
        if not all(np.isfinite(vals[c]) and vals[c]>0 for c in FIELDS):continue
        rows.append({
          "species":sp,
          "log_body_size":math.log(vals["Body_size_mm"]),
          "log_clutch_size":0.5*(math.log(vals["Litter_size_min_n"])+math.log(vals["Litter_size_max_n"])),
          "log_offspring_size":0.5*(math.log(vals["Offspring_size_min_mm"])+math.log(vals["Offspring_size_max_mm"])),
          "log_reproductive_output":math.log(vals["Reproductive_output_y"])
        })
    d=pd.DataFrame(rows)
    if len(d)!=42:raise SystemExit(f"core trait species drift: {len(d)} != 42")
    for c in TRAITS:
        sd=float(d[c].std(ddof=0))
        if not sd>0:raise SystemExit(f"zero variance {c}")
        d[c+"_z"]=(d[c]-d[c].mean())/sd
    vec={r.species:np.array([getattr(r,c+"_z") for c in TRAITS],float) for r in d.itertuples(index=False)}
    raw={r.species:{c:float(getattr(r,c)) for c in TRAITS} for r in d.itertuples(index=False)}
    return vec,raw

def dist(a,b):return float(np.linalg.norm(a-b)/math.sqrt(len(a)))

def metrics(spp,vec,raw):
    s=sorted({norm(x) for x in spp if norm(x) in vec})
    n=len(s)
    mpd=np.nan
    if n>=2:
        ds=[dist(vec[s[i]],vec[s[j]]) for i in range(n) for j in range(i+1,n)]
        mpd=float(np.mean(ds))
    cwm={c:(float(np.mean([raw[x][c] for x in s])) if n else np.nan) for c in TRAITS}
    return s,{"richness":n,"mpd":mpd,**cwm}

def novelty(exclusive,opposite,vec):
    if len(exclusive)==0:return 0.0
    if len(opposite)==0:return np.nan
    return float(np.mean([min(dist(vec[s],vec[o]) for o in opposite) for s in exclusive]))

def build():
    rawdata=base.load();runs,sets=base.build_runs(rawdata)
    universe=set().union(*sets.values())
    vec,raw=load_trait_vectors(universe)
    pairs=base.pair_runs(runs,sets)
    rows=[]
    for p in pairs.itertuples(index=False):
        W,wm=metrics(sets[str(p.wet_RunID)],vec,raw)
        D,dm=metrics(sets[str(p.dry_RunID)],vec,raw)
        ws,ds=set(W),set(D)
        wn=novelty(sorted(ws-ds),D,vec);dn=novelty(sorted(ds-ws),W,vec)
        row=p._asdict()
        row.update({
          "delta_trait_covered_richness":float(wm["richness"]-dm["richness"]),
          "delta_functional_mpd":wm["mpd"]-dm["mpd"] if np.isfinite(wm["mpd"]) and np.isfinite(dm["mpd"]) else np.nan,
          "functional_novelty_balance":wn-dn if np.isfinite(wn) and np.isfinite(dn) else np.nan,
          "wet_functional_novelty":wn,"dry_functional_novelty":dn,
          **{f"delta_cwm_{c}":wm[c]-dm[c] if np.isfinite(wm[c]) and np.isfinite(dm[c]) else np.nan for c in TRAITS}
        })
        rows.append(row)
    return pd.DataFrame(rows)

def fit(d,response,extra=""):
    x=d[np.isfinite(pd.to_numeric(d[response],errors="coerce"))].copy()
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber){extra}"
    f=smf.ols(form,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    b=float(f.params["rain_contrast"]);se=float(f.bse["rain_contrast"])
    return {"response":response,"n_pairs":int(len(x)),"n_routes":int(x.route_cluster.nunique()),
            "beta_rain_contrast":b,"se_cluster":se,"ci95":[b-Q*se,b+Q*se],"p_value":float(f.pvalues["rain_contrast"]),
            "formula":form}

def bh(models):
    items=[(k,v["p_value"]) for k,v in models.items()]
    order=sorted(range(len(items)),key=lambda i:items[i][1]);m=len(items);adj={};run=1.0
    for rr,pos in enumerate(reversed(order),start=1):
        rank=m-rr+1;val=min(1.0,items[pos][1]*m/rank);run=min(run,val);adj[items[pos][0]]=run
    for k in models:models[k]["fdr_bh"]=float(adj[k])
    return models

def pack(d):
    primary={
      "delta_functional_mpd":fit(d,"delta_functional_mpd"),
      "functional_novelty_balance":fit(d,"functional_novelty_balance"),
      "delta_trait_covered_richness":fit(d,"delta_trait_covered_richness")
    }
    cwm=bh({c:fit(d,f"delta_cwm_{c}") for c in TRAITS})
    sens=fit(d,"delta_functional_mpd"," + delta_trait_covered_richness")
    return primary,cwm,sens

def main():
    d=build();p,c,s=pack(d);exact=d[d.year_gap==1].copy();pe,ce,se=pack(exact)
    result={
      "analysis":"naamp_functional_community_expansion_v0_1",
      "contract":"NAAMP_FUNCTIONAL_COMMUNITY_EXPANSION_CONTRACT_V0_1.json",
      "primary_models":p,"cwm_trait_shift_models":c,"mpd_richness_adjusted_sensitivity":s,
      "exact_consecutive_year":{"n_pairs":int(len(exact)),"primary_models":pe,"cwm_trait_shift_models":ce,
                                "mpd_richness_adjusted_sensitivity":se},
      "descriptive":{
        "n_pairs":int(len(d)),
        "mpd_estimable_pairs":int(np.isfinite(d.delta_functional_mpd).sum()),
        "novelty_estimable_pairs":int(np.isfinite(d.functional_novelty_balance).sum()),
        "mean_delta_trait_covered_richness":float(d.delta_trait_covered_richness.mean()),
        "mean_delta_functional_mpd":float(d.delta_functional_mpd.mean()),
        "mean_functional_novelty_balance":float(d.functional_novelty_balance.mean())
      },
      "interpretation_boundary":{
        "functional_space":"Four frozen AmphiBIO life-history/reproductive axes; not exhaustive ecological function.",
        "causal_rainfall_claim_authorized":False,"phylogenetic_mechanism_claim_authorized":False,
        "endpoint_retuning_after_readback_authorized":False
      }}
    Path("NAAMP_FUNCTIONAL_COMMUNITY_EXPANSION_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
