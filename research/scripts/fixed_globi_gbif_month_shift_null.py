#!/usr/bin/env python3
"""Cyclic-phenology control for pinned GloBI stage edges and GBIF 1° stage cells.

Requires TWO independently successful GitHub Actions artifacts:
 GloBI 2026-09-10 MD5-verified full-source, nonself stage edge candidates
 GBIF 2026-08 experimental Anura/Odonata 1° month/year cube.

The result is GBIF stage **co-reporting phase congruence**, NOT predation
rates, species interactions, frog calling, plant refuge or statistical proof.
Analysis protocol: research/GLOBAL_STAGE_PHENOLOGY_SHIFT_NULL_SPEC_V0_1.md
"""
import argparse
import collections
import csv
import json
import math
from pathlib import Path

SOURCE_GLOBI="https://doi.org/10.5281/zenodo.22691479"
SOURCE_GBIF="https://github.com/zuizui0223/frogcs/actions/runs/40190152042"
MASK=(1<<12)-1
SHIFTS=list(range(12))
THRESHOLDS=(1,5)
ELIGIBLE="GBIF_1DEG_REPORT_COMPATIBILITY_NOT_VERIFIED_ENCOUNTER"


def rotate(mask,n):
    if not 0<=n<=11:
        raise ValueError("Need phase shift in 0..11")
    if n==0:return mask
    return ((mask<<n)&MASK)|(mask>>(12-n))


def read_cell_cubes(path):
    """Store bitset of occupied observed months per species×stage×grid×year."""
    masks={t:collections.defaultdict(int) for t in THRESHOLDS}
    n=0
    nrecords=0
    with Path(path).open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f)
        wanted={"species","stage","latcell","loncell","year","month","n_records"}
        if not wanted.issubset(reader.fieldnames or []):
            raise ValueError("Missing exact expected GBIF stage grid columns")
        for row in reader:
            n+=1
            try:
                name=row["species"].strip()
                stage=row["stage"].strip()
                glat=int(row["latcell"])
                glon=int(row["loncell"])
                year=int(row["year"])
                month=int(row["month"])
                ct=int(row["n_records"])
            except (KeyError,ValueError):
                raise ValueError("Invalid GBIF aggregate cell schema row "+str(n))
            if ct<=0 or not 2010<=year<=2026 or not 1<=month<=12:
                raise ValueError("Invalid GBIF cell date/count "+str(n))
            if not -90<=glat<=90 or not -180<=glon<=180:
                raise ValueError("GBIF geographic cell outside earth "+str(n))
            if stage not in ("adult","aquatic_immature","juvenile","egg","unlabelled"):
                raise ValueError("Unexpected GBIF stage label "+stage)
            nrecords+=ct
            key=(name,stage)
            cy=(glat,glon,year)
            for threshold in THRESHOLDS:
                if ct>=threshold:
                    masks[threshold][key][cy]|=1<<(month-1)
    return masks,dict(rows=n,source_observations=nrecords,
                      stage_pairs_atleast1=len(masks[1]),
                      stage_pairs_atleast5=len(masks[5]))


def read_edges(path):
    d=[]
    discarded=collections.Counter()
    seen=set()
    with Path(path).open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f)
        required={"predator","prey","predator_stage","prey_stage",
                  "predator_guild","prey_guild","source_rows","source_tiers",
                  "distinct_reference_citations","eligibility"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Unexpected pinned GloBI source fields")
        for row in reader:
            key=(row["predator"],row["predator_stage"],
                 row["prey"],row["prey_stage"])
            if row["predator"]==row["prey"]:
                discarded["conspecific"]+=1
                continue
            if row["eligibility"]!=ELIGIBLE:
                discarded["missing_one_or_both_stage_in_gbif"]+=1
                continue
            if key in seen:
                discarded["duplicate_species_stage_edge"]+=1
                continue
            seen.add(key)
            d.append(row)
    return d,dict(discarded)


def compare_one(pred,prey):
    """Counts of spatial-year-month GBIF co-reports for twelve calendar phases."""
    eligible=set(pred)&set(prey)
    n_phase=[0]*12
    strictyear=len(eligible)
    spatial_pred={(c[0],c[1]) for c in pred}
    spatial_prey={(c[0],c[1]) for c in prey}
    for cell in eligible:
        a=pred[cell];b=prey[cell]
        for shift in SHIFTS:
            n_phase[shift]+=(a&rotate(b,shift)).bit_count()
    obs=n_phase[0]
    others=n_phase[1:]
    null_mean=sum(others)/len(others)
    rank=(1+sum(x>=obs for x in others))/12
    return dict(
        compatible_grid_years=strictyear,
        compatible_spatial_cells=len(spatial_pred&spatial_prey),
        month_counts_all_phases=n_phase,
        observed_exact_grid_year_month=obs,
        month_shift_null_mean=null_mean,
        month_shift_null_median=sorted(others)[len(others)//2],
        month_shift_null_min=min(others),
        month_shift_null_max=max(others),
        observed_minus_shifted_mean=obs-null_mean,
        observed_over_shift_mean_plus1=(obs+1)/(null_mean+1),
        halfyear_shift_n=n_phase[6],
        one_sided_12_phase_rank_not_independent_p=rank,
    )


def run(gbif,globi,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    masks,mc=read_cell_cubes(gbif)
    edges,ex=read_edges(globi)
    if len(edges)<5:
        raise RuntimeError("Fewer than five source eligible stage pairs")
    rows=[]
    for edge in edges:
        pred=(edge["predator"],edge["predator_stage"])
        prey=(edge["prey"],edge["prey_stage"])
        for threshold in THRESHOLDS:
            x=compare_one(masks[threshold].get(pred,{}),
                          masks[threshold].get(prey,{}))
            row={key:edge.get(key,"") for key in [
                "predator","prey","predator_guild","prey_guild",
                "predator_stage","prey_stage","source_tiers",
                "source_dois","distinct_reference_citations",
                "source_rows","original_stages"]}
            row.update(dict(threshold_per_taxon_stage_cell=threshold))
            row.update(x)
            row["month_counts_all_phases"]=";".join(map(str,x["month_counts_all_phases"]))
            row["biology"]="COMPATIBLE_OBSERVED_STAGE_REPORTS_NOT_PREDATION"
            rows.append(row)
    filename=out/"stage_phenology_shift_pair_results.csv"
    with filename.open("w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction="ignore")
        w.writeheader();w.writerows(rows)
    summaries=[]
    for threshold in THRESHOLDS:
        d=[x for x in rows if x["threshold_per_taxon_stage_cell"]==threshold]
        testable=[x for x in d if x["compatible_grid_years"]>0]
        observed_zero=[x for x in testable if x["observed_exact_grid_year_month"]==0]
        sources=collections.Counter(
            ("Quick_Pond" if "QUICK_POND" in row["source_tiers"]
             else "iNaturalist" if "INAT" in row["source_tiers"]
             else "other_indexed")
            for row in testable)
        grouped=collections.Counter(
            (x["predator_guild"],x["prey_guild"],x["predator_stage"],
             x["prey_stage"]) for x in testable)
        summaries.append(dict(
            threshold_records_per_species_stage_grid_month=threshold,
            all_eligible_gloBI_species_stage_pairs=len(d),
            pairs_with_shared_grid_year=testable.__len__(),
            pairs_no_shared_grid_year=len(d)-len(testable),
            pairs_with_shared_year_but_no_same_month=len(observed_zero),
            pairs_with_same_grid_year_month=sum(
                x["observed_exact_grid_year_month"]>0 for x in testable),
            pairs_observed_above_11_shift_mean=sum(
                x["observed_exact_grid_year_month"] >
                x["month_shift_null_mean"] for x in testable),
            pairs_observed_below_shift_mean=sum(
                x["observed_exact_grid_year_month"] <
                x["month_shift_null_mean"] for x in testable),
            pooled_exact_reports_observed=sum(x["observed_exact_grid_year_month"]
                                              for x in testable),
            pooled_11_shift_mean_sum=sum(x["month_shift_null_mean"]
                                         for x in testable),
            source_category_counts=dict(sources),
            independent_strata_count=len(grouped),
            strata=[dict(predator_guild=k[0],prey_guild=k[1],
                         predator_stage=k[2],prey_stage=k[3],
                         candidate_pairs=n)
                    for k,n in sorted(grouped.items())],
            top_congruence_pairs=sorted([
                {key:x[key] for key in (
                    "predator","prey","predator_stage","prey_stage",
                    "observed_exact_grid_year_month",
                    "month_shift_null_mean","observed_minus_shifted_mean",
                    "one_sided_12_phase_rank_not_independent_p","source_tiers")}
                for x in testable
            ],key=lambda x:(-x["observed_minus_shifted_mean"],
                            x["predator"],x["prey"]))[:12],
        ))
    result=dict(
        status="REAL_GLOBI_GBIF_STAGE_MONTH_SHIFT_NULL_EXPLORATORY",
        analysis_date="2026-10-25",
        source_frozen_globi=SOURCE_GLOBI,
        source_gbif_1deg=SOURCE_GBIF,
        temporal_null="11 cyclic prey-month shifts within original grid×year",
        source_population="nonself GloBI stage links with both partners represented by positive GBIF Anura/Odonata stage observations",
        input_gbif_1deg_aggregate=mc,
        source_edges_read=len(edges),
        source_edge_discard_counts=ex,
        per_threshold=summaries,
        boundaries=[
            "Months shifted represent expected recording concordance under arbitrary relative phase, not a causal predator-prey or climatic null model.",
            "Same 1deg grid-year-month GBIF stage observations are not contemporaneous encounters at any pond, and source sightings may include introduced populations.",
            "GBIF experimental August 2026 source is NOT the official DOI citable full October release; true global extrapolation is unauthorized.",
            "Many edges share literature/web datasets. Aggregated shifted expected counts and 12-phase ranks have correlated error and are NOT independent P-values.",
            "A paired stage GloBI link is an index record, possibly inferred, not verified predation; no demonstrated demographic role reversal.",
            "GBIF stage underreporting, citizen science effort, rainy-season access, phenological survey bias and taxonomic inconsistencies are not corrected.",
            "No actual emergent reed-cover, wetland morphology, rainfall time series, chorus or eDNA measurement was used in this null.",
            "Multiple trophic candidate pairs are exploratory; do not claim confirmed worldwide seasonal predation synchronization."
        ]
    )
    (out/"observed_results.json").write_text(json.dumps(result,indent=2,
                                            ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_MONTH_SHIFT_FULL_GLOBI_GBIF_RESULTS")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("END_MONTH_SHIFT_FULL_GLOBI_GBIF_RESULTS")
    return result


def synthetic():
    assert rotate(1,0)==1
    assert rotate(1,1)==2 and rotate(1,11)==2048
    assert rotate(1<<11,1)==1
    p={(30,40,2021):1<<3,(30,40,2022):1<<5}
    q={(30,40,2021):1<<3,(30,40,2022):1<<7}
    r=compare_one(p,q)
    assert r["compatible_grid_years"]==2
    assert r["observed_exact_grid_year_month"]==1
    assert r["month_counts_all_phases"][10]==1
    assert r["one_sided_12_phase_rank_not_independent_p"]>=1/12
    assert compare_one({},q)["observed_exact_grid_year_month"]==0
    print("MONTH_SHIFT_FULL_STAGE_SENSITIVITY_SYNTHETIC_QA_PASS")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--gbif",default="research/data/gbif_open_artifact/focal_stage_1deg_month_year.csv")
    p.add_argument("--globi",default="research/data/full_globi_artifact/nonself_stage_pair_grid_results.csv")
    p.add_argument("--out",default="research/results/month_shift_globi_gbif")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:synthetic()
    else:run(a.gbif,a.globi,a.out)
