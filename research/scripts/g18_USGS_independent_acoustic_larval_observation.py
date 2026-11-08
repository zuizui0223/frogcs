"""G18: independent USGS adult acoustic / tadpole detection and lagged observation bridge.

USGS Glorioso & Waddle (2025), DOI 10.5066/P9T71JCO, CC0. Original
ScienceBase files and FGDC codebook checked byte-for-byte against response-blind
source manifest. Stage presence, NOT larval abundance/survival or predator causality.
G18a/b/c protocols were fixed before opening response columns.
"""
from __future__ import annotations

import argparse,hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler

SOURCE_ITEM="5eb5880c82ce25b5135ae784"
DOI="10.5066/P9T71JCO"
FGDC_SHA="990d0c3fbc8cc05f97cc458911342aea4e74a05088ce81c65fbae99a5a933a11"
SEED=20261108
BOOT=10000
TAXA=(
    "Acris blanchardi","Anaxyrus fowleri","Gastrophryne carolinensis",
    "Hyla chrysoscelis","Hyla cinerea","Hyla squirella",
    "Incilius nebulifer","Lithobates catesbeianus","Lithobates clamitans",
    "Lithobates grylio","Lithobates sphenocephalus",
    "Pseudacris crucifer","Pseudacris fouquettei",
)
FILES={
    "sample":"USGS_original_03_Sample_Data.csv",
    "vocal":"USGS_original_07_Vocalizations.csv",
    "larvae":"USGS_original_06_Tadpoles_Larvae.csv",
    "fgdc":"USGS_original_00_ATCH_Metadata.xml",
}
METADATA={
    "sample":"Sample_Data.csv",
    "vocal":"Vocalizations.csv",
    "larvae":"Tadpoles_Larvae.csv",
    "fgdc":"ATCH_Metadata.xml",
}
SOURCE_EXPECT={
    "sample":"24fed6f95e262cb287f755a7782b2ee213f59b81d869bfde7d8060705b839da8",
    "vocal":"e776f9baaf3f972edfa3fe302501a8721d954bc820effb096ef106a9b22be9af",
    "larvae":"274914675782cd241ce10878faaf932be4baee8c6c023f82ba244fcd4d8487b4",
    "fgdc":FGDC_SHA,
}
MAX_ITER=2000
RIDERIDGE=1.0

def require(ok,message):
    if not bool(ok):raise AssertionError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_original(source):
    source=Path(source)
    provenance=json.loads((source/"G18_USGS_SOURCE_ACCESS_PREFLIGHT.json").read_text())
    require(provenance["status"]=="SCHEMA_READY" and
            provenance["source_item_id"]==SOURCE_ITEM and
            provenance["source_doi"]==DOI and
            not provenance["taxon_species_stage_response_values_inspected"],
            "Invalid response-blind original USGS source access receipt")
    folder=source/"original_ephemeral"
    original={k:folder/v for k,v in FILES.items()}
    for k,path in original.items():
        require(path.is_file() and sha(path)==SOURCE_EXPECT[k],
                "Original USGS published data/codebook SHA changed: "+k)
    declared={x["name"]:x for x in provenance["source_file_manifest"]}
    for k in original:
        row=declared[METADATA[k]]
        require(row["status"]=="DOWNLOADED_ORIGINAL" and
                row["sha256"]==SOURCE_EXPECT[k], "Source digest does not match response-blind manifest")
    xml=ET.parse(original["fgdc"]).getroot()
    entities={
        e.findtext("enttyp/enttypl",""):e
        for e in xml.findall(".//detailed")
    }
    require("Vocalizations.csv" in entities and "Tadpoles_Larvae.csv" in entities,
            "Official USGS original FGDC field dictionaries missing")
    larval=entities["Tadpoles_Larvae.csv"]
    vocal=entities["Vocalizations.csv"]
    lad={a.findtext("attrlabl","").strip():a for a in larval.findall("attr")}
    vad={a.findtext("attrlabl","").strip():a for a in vocal.findall("attr")}
    for taxon in TAXA:
        require(taxon in lad and taxon+"_In" in vad and taxon+"_Out" in vad,
                "Official codebook does not list one of the 13 predeclared source taxa")
        ldesc=lad[taxon].findtext("attrdef","").lower()
        require(("absence" in ldesc and "presence" in ldesc),
                "USGS original larval column not defined as absence/presence: "+taxon)
        vcodes={x.findtext("edomv","") for x in
                vad[taxon+"_In"].findall(".//edom")}
        require(vcodes=={"0","1","2","3"},
                "USGS published vocalization 0/1/2/3 coding changed: "+taxon)
        desc=vad[taxon+"_In"].findtext("attrdef","").lower()
        require("within" in desc or "in the" in desc,
                "Original adult call IN plot definition missing")
    shared_desc=entities["Tadpoles_Larvae.csv"].findtext("enttyp/enttypd","").lower()
    require("absence or presence" in shared_desc,
            "Original tadpoles/larvae sheet has no explicit absence protocol")
    sample_desc={a.findtext("attrlabl",""):a for a in
                entities["Sample_Data.csv"].findall("attr")}
    sample_def=sample_desc["Sample #"]
    null_def=" ".join((z.findtext("edomvd","") for z in sample_def.findall(".//edom")
                       if z.findtext("edomv","")=="NULL")).lower()
    require("mistake" in null_def and "not be used" in null_def,
            "Original USGS Sample # NULL exclusion definition absent")

    sm=pd.read_csv(original["sample"])
    vo=pd.read_csv(original["vocal"])
    la=pd.read_csv(original["larvae"])
    require((len(sm),len(vo),len(la))==(2221,2222,1055),
            "Original USGS 3-table row coverage changed")
    require(sm["Sample ID"].is_unique and vo["Sample ID"].is_unique
            and la["Sample ID"].is_unique,"Source Sample IDs not unique")
    sm["DateParsed"]=pd.to_datetime(sm.Date,errors="coerce")
    require(sm.DateParsed.notna().all() and sm.Site.notna().all(),
            "Original site dates or names incomplete")
    invalid=int(sm["Sample #"].isna().sum())
    require(invalid==5, "Original USGS invalid Sample # source QC drift")
    valid=sm.dropna(subset=["Sample #"]).copy()
    require(valid["Sample ID"].is_unique,"Duplicate valid original sample")
    joined_v=vo.merge(valid[["Sample ID","Site","DateParsed"]],
                      on="Sample ID",how="inner",validate="one_to_one")
    joined_l=la.merge(valid[["Sample ID","Site","DateParsed"]],
                      on="Sample ID",how="inner",validate="one_to_one")
    merged=joined_v.merge(
        joined_l.drop(columns=["Site","DateParsed"]),on="Sample ID",
        how="inner",suffixes=("_v","_larva"),validate="one_to_one")
    require(len(merged)==1054 and merged.Site.nunique()==64,
            "Original same-sample acoustic/larval overlap changed")
    year=merged.DateParsed.dt.year
    require(set(year)==set(range(2012,2017)) and
            merged.assign(year=year).groupby(["Site","year"]).ngroups==230,
            "Original 2012–2016 paired site/year support altered")
    names={x.strip():x for x in la.columns if x!="Sample ID"}
    require(all(t in names for t in TAXA),"Exact source taxon names lost")
    for t in TAXA:
        a=pd.to_numeric(merged[t+"_In"],errors="raise")
        b=pd.to_numeric(merged[t+"_Out"],errors="raise")
        c=pd.to_numeric(merged[names[t]],errors="raise")
        require(a.notna().all() and b.notna().all() and c.notna().all()
                and a.isin((0,1,2,3)).all() and b.isin((0,1,2,3)).all()
                and c.isin((0,1)).all(),
                "Observed source coded response outside exact USGS FGDC 0–3 / 0–1")
    return valid,joined_v,joined_l,merged,names,provenance,invalid


def contemporaneous(merged,names):
    obs=[]
    for t in TAXA:
        x=merged[["Sample ID","Site","DateParsed",t+"_In",t+"_Out",names[t]]].copy()
        x.columns=["sample_id","site","date","acoustic_in","acoustic_out","larval"]
        x["taxon"]=t
        x["call_in"]=x.acoustic_in>0
        x["call_out"]=x.acoustic_out>0
        obs.append(x)
    records=pd.concat(obs,ignore_index=True)
    require(len(records)==1054*len(TAXA),"Missing same-sample exact-taxon cells")
    table=[]
    for guild in ("call_in","call_out"):
        for t,g in records.groupby("taxon"):
            v=g[guild].to_numpy(bool)
            y=g.larval.to_numpy(int)
            table.append(dict(taxon=t,call_scope=guild,
                 call_and_larva=int(np.sum(v&(y==1))),
                 call_only=int(np.sum(v&(y==0))),
                 larva_only=int(np.sum((~v)&(y==1))),
                 both_explicit_nondetection=int(np.sum((~v)&(y==0))),
                 source_samples=len(g),
                 sites=g.site.nunique()))
    full=pd.DataFrame(table)
    primary=records
    group=[]
    for site,g in primary.groupby("site",sort=True):
        a=g.call_in.to_numpy(bool);b=g.larval.to_numpy(int)
        group.append([
            int(np.sum(a&(b==1))),int(np.sum(a&(b==0))),
            int(np.sum((~a)&(b==1))),int(np.sum((~a)&(b==0)))])
    cluster=np.asarray(group,dtype=int)
    require(cluster.shape==(64,4),"Original independent site clusters lost")
    c=cluster.sum(axis=0)
    require(c.sum()==1054*13 and c[0]+c[2]>10
            and c[1]+c[3]>10,"Insufficient original paired source class support")
    with np.errstate(invalid="ignore",divide="ignore"):
        risk1=c[0]/(c[0]+c[1])
        risk0=c[2]/(c[2]+c[3])
    rng=np.random.default_rng(SEED)
    ix=rng.integers(0,len(cluster),size=(BOOT,len(cluster)))
    p=cluster[ix].sum(axis=1)
    with np.errstate(invalid="ignore",divide="ignore"):
        d=p[:,0]/(p[:,0]+p[:,1])-p[:,2]/(p[:,2]+p[:,3])
        rr=(p[:,0]/(p[:,0]+p[:,1]))/(p[:,2]/(p[:,2]+p[:,3]))
    require(np.isfinite(d).all() and np.isfinite(rr).all(),
            "Source site-bootstrap missing positive/negative classes")
    return records,full,dict(
        source_sites=64,paired_source_samples=1054,
        matched_species=len(TAXA),species_by_sample_opportunities=1054*13,
        in_call_and_larva=int(c[0]),in_call_only=int(c[1]),
        in_larva_only=int(c[2]),both_explicit_nondetection=int(c[3]),
        larva_detection_given_in_call=float(risk1),
        larva_detection_given_in_nocall=float(risk0),
        raw_paired_risk_difference=float(risk1-risk0),
        original_site_resampled_95_low=float(np.quantile(d,.025)),
        original_site_resampled_95_high=float(np.quantile(d,.975)),
        raw_paired_risk_ratio=float(risk1/risk0),
        ratio_source_bootstrap_95_low=float(np.quantile(rr,.025)),
        ratio_source_bootstrap_95_high=float(np.quantile(rr,.975)),
        source_original_site_bootstraps=BOOT,
        source_original_site_bootstrap_seed=SEED,
        not_larval_survival=True,
    )


def chronological(joined_v,joined_l,names):
    v=joined_v.copy();l=joined_l.copy()
    v["year"]=v.DateParsed.dt.year
    l["year"]=l.DateParsed.dt.year
    result=[]
    for (site,year),lg in l.groupby(["Site","year"],sort=True):
        vg=v[(v.Site==site)&(v.year==year)].copy()
        lg=lg.sort_values(["DateParsed","Sample ID"])
        # The first larval sample is selected using dates and *not its outcome*.
        eligible=lg[lg.DateParsed.map(lambda day:(vg.DateParsed<day).any())]
        if eligible.empty:continue
        first=eligible.iloc[0]
        prior=vg[vg.DateParsed<first.DateParsed]
        require(len(prior)>0 and
                (prior.DateParsed<first.DateParsed).all(),
                "Same-day or future acoustic observation leakage")
        for t in TAXA:
            result.append(dict(site=site,year=str(year),taxon=t,
                original_first_qualifying_larval_sample=int(first["Sample ID"]),
                larva=int(first[names[t]]),
                prior_call=int((prior[t+"_In"]>0).any()),
                n_prior=len(prior),
                doy=int(first.DateParsed.dayofyear),
                lag_since_last_prior_days=int((first.DateParsed-
                                               prior.DateParsed.max()).days)))
    x=pd.DataFrame(result)
    require(len(x)==2990 and x.site.nunique()==64
            and len(x.groupby(["site","year"]))==230
            and set(x.year)=={str(y) for y in range(2012,2017)}
            and x.lag_since_last_prior_days.ge(1).all(),
            "Original strictly earlier same-site/year/taxon stage support changed")
    x["logprior"]=np.log1p(x.n_prior)
    sites=sorted(x.site.unique(),
        key=lambda name:(hashlib.sha256(str(name).encode()).hexdigest(),str(name)))
    source_fold={site:i%5 for i,site in enumerate(sites)}
    x["fold"]=x.site.map(source_fold).astype(int)
    require(x.groupby("site").fold.nunique().eq(1).all()
            and x.fold.nunique()==5,"Site leakage in fixed fivefold stage prediction")
    return x


def fixed_logistic(withcall):
    processors=[
        ("categorical",OneHotEncoder(handle_unknown="ignore"),["taxon","year"]),
        ("scaled",StandardScaler(),["doy","logprior"]),
    ]
    if withcall:processors.append(("calling","passthrough",["prior_call"]))
    return Pipeline([
        ("columns",ColumnTransformer(processors,remainder="drop")),
        ("regression",LogisticRegression(C=RIDERIDGE,solver="lbfgs",max_iter=MAX_ITER)),
    ])


def validation(x):
    x=x.copy()
    y=x.larva.to_numpy(dtype=int)
    require(y.sum()>=10 and (y==0).sum()>=10,
            "Original future stage classes not eligible")
    for name,call in [("M0",False),("M1",True)]:
        fitted=np.zeros(len(x))
        for f in range(5):
            train=x.fold!=f;test=~train
            require(x.loc[train,"larva"].nunique()==2
                    and x.loc[test].site.nunique()>0,
                    "Original site CV split missing source endpoint class")
            model=fixed_logistic(call)
            model.fit(x.loc[train],x.loc[train,"larva"])
            fitted[test]=model.predict_proba(x.loc[test])[:,1]
        pp=np.clip(fitted,1e-7,1-1e-7)
        x["p_"+name]=pp
        x["brier_"+name]=(y-pp)**2
        x["logloss_"+name]=-(y*np.log(pp)+(1-y)*np.log1p(-pp))
    site=x.groupby("site")[
        ["brier_M0","brier_M1","logloss_M0","logloss_M1"]].mean().sort_index()
    result={}
    for metric in ("brier","logloss"):
        a=site[metric+"_M0"].to_numpy(float)
        b=site[metric+"_M1"].to_numpy(float)
        rng=np.random.default_rng(SEED)
        ix=rng.integers(0,len(site),size=(BOOT,len(site)))
        scores=a[ix].mean(axis=1)-b[ix].mean(axis=1)
        low,hi=np.quantile(scores,[.025,.975])
        result[metric]=dict(site_equal_M0=float(a.mean()),
          site_equal_M1=float(b.mean()),added_prior_call_gain=float((a-b).mean()),
          source_site_bootstrap95=[float(low),float(hi)],
          pooled_original_M0=float(x[metric+"_M0"].mean()),
          pooled_original_M1=float(x[metric+"_M1"].mean()))
    result.update(n_source_lag_rows=len(x),source_sites=int(x.site.nunique()),
        source_siteyears=int(len(x.groupby(["site","year"]))),
        larval_positives=int(y.sum()),larval_explicit_negatives=int(len(y)-y.sum()),
        prior_call_positives=int(x.prior_call.sum()),
        n_original_geographic_site_folds=5,
        fixed_site_bootstrap_source_units=len(site),
        bootstrap_draws=BOOT,bootstrap_seed=SEED,
        original_source_year_counts={year:int(n) for year,n in
            x.groupby("year").size().items()})
    before=x.year.isin(("2012","2013","2014"))
    future=x.year.isin(("2015","2016"))
    require(before.sum()>0 and future.sum()>0
            and x.loc[before,"larva"].nunique()==2
            and x.loc[future,"larva"].nunique()==2
            and x.loc[future,"larva"].sum()>=10
            and x.loc[future,"site"].nunique()>=10,
            "Original pre-fixed 2015–2016 source year holdout support missing")
    yf=x.loc[future,"larva"].to_numpy(dtype=int)
    forward={}
    for name,call in (("M0",False),("M1",True)):
        model=fixed_logistic(call)
        model.fit(x.loc[before],x.loc[before,"larva"])
        pred=np.clip(model.predict_proba(x.loc[future])[:,1],1e-7,1-1e-7)
        loss=-(yf*np.log(pred)+(1-yf)*np.log1p(-pred))
        forward[name]=dict(brier=float(np.mean((yf-pred)**2)),
                           logloss=float(loss.mean()),mean_predicted_presence=float(pred.mean()))
    result["forward_2015_2016"]=dict(
        source_training_2012_2014_rows=int(before.sum()),
        source_test_2015_2016_rows=int(future.sum()),
        future_source_sites=int(x.loc[future,"site"].nunique()),
        future_larval_positives=int(yf.sum()),
        models=forward,
        brier_added_prior_call_gain=float(forward["M0"]["brier"]-forward["M1"]["brier"]),
        logloss_added_prior_call_gain=float(forward["M0"]["logloss"]-forward["M1"]["logloss"]),
        no_larval_survival_interpretation=True,
    )
    x["opaque_site_group"]=x.site.map(lambda s:
        hashlib.sha256(("G18-USGS-stage-site-"+str(s)).encode()).hexdigest()[:16])
    x=x.drop(columns=["site","original_first_qualifying_larval_sample"])
    return x,result


def run(source,out):
    valid,vo,la,merged,names,meta,ninvalid=read_original(source)
    paired,per_tax,pairedstats=contemporaneous(merged,names)
    chrono=chronological(vo,la,names)
    validated,holdout=validation(chrono)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    result=dict(
        status="G18_USGS_INDEPENDENT_ACOUSTIC_LARVAL_SOURCE_AND_STAGE_BRIDGE_AUDITED",
        original_data_doi=DOI,original_ScienceBase_item_id=SOURCE_ITEM,
        original_FGDC_SHA256=FGDC_SHA,
        original_original_file_SHA256=SOURCE_EXPECT,
        original_source_sample_rows=2221,source_sample_rows_without_sample_number=5,
        original_vocalization_rows=2222,
        original_larval_table_rows=1055,
        same_sample_ids_valid_for_both=1054,
        original_source_shared_taxa=list(TAXA),
        original_publication="Glorioso and Waddle (2025), USGS CC0",
        same_event=pairedstats,
        first_strictly_later_larval_observation=holdout,
        original_source_data_outcomes_are_stage_detection_not_survival=True,
        source_ABC_field_posterior_estimated=False,
        odonate_or_salamander_predation_causally_estimated=False,
        no_new_biological_simulations=True,
        original_G14_G15_field_two_background_gates_unchanged=True,
        future_year_predictive_stage_link_supported=(
          holdout["forward_2015_2016"]["brier_added_prior_call_gain"]>0 and
          holdout["forward_2015_2016"]["logloss_added_prior_call_gain"]>0),
    )
    files={
        "G18_13_exact_frog_species_within_sample_detection.csv":per_tax,
        "G18_lagged_original_site_year_species_heldout_predictions.csv":validated,
    }
    for name,frame in files.items():frame.to_csv(out/name,index=False)
    # Output only masked source site keys; no coordinates/personnel/raw source copy.
    result["outputs_SHA256"]={name:sha(out/name) for name in files}
    (out/"G18_USGS_INDEPENDENT_STAGE_OBSERVATION_RESULT.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("G18_USGS_SOURCE_AND_STAGE_RESULT "+json.dumps({
        "status":result["status"],"same_event":pairedstats,
        "later_site_heldout":holdout,
        "future_year_prediction_pass":result["future_year_predictive_stage_link_supported"],
    },ensure_ascii=False),flush=True)
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    q=p.parse_args()
    run(q.source,q.out)
