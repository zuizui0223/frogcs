"""Describe cross-species life history contrasts using existing within-route correlations."""
from pathlib import Path
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]/"results"
def main(traits_file):
    traits=pd.read_csv(ROOT/"forest_use_wetland_species_20261111/forest_traits_44.csv").set_index("species")
    stages=pd.read_excel(traits_file,sheet_name="data").set_index("Species")
    endings={"cinerea":"cinereus","squirella":"squirellus","gratiosa":"gratiosus"}
    for sp in traits.index:
        genus,ep=sp.split()
        name=("Dryophytes "+endings.get(ep,ep)) if genus=="Hyla" else sp
        if name in stages.index:
            traits.loc[sp,["source_species","mode","inferred"]]=[name,stages.at[name,"Life History Mode"],stages.at[name,"Inferred?"]]
    sites=pd.read_csv(ROOT/"naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz")
    v=pd.read_csv(ROOT/"naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz")
    v=v[v.site.isin(sites.site)&v.timeout.eq(0)].copy()
    assert len(v)==63180
    v["relative_day"]=v.doy-v.groupby(["site","year"]).doy.transform("median")
    v["species"]=v.source_taxa.str.split("|",regex=False)
    v=v.explode("species")
    v=v[v.species.isin(traits.index)]
    timing=v.groupby(["species","route","site","year"])[["doy","relative_day"]].median()
    for levels in [["species","route","site"],["species","route"],["species"]]:
        timing=timing.groupby(levels).median()
    a=pd.read_csv(ROOT/"species_predator_correlations_20261111/within_route.csv")
    a=a[a.domain=="detected_routes"].pivot(index=["species","strong_routes"],columns="guild",values="r").reset_index().set_index("species")
    out=ROOT/"species_predator_correlations_20261111"
    data=traits.join(timing).join(a)
    data.to_csv(out/"life_history.csv")
    print(data.groupby(["mode","inferred"],dropna=False).size())
    panel=data[data.strong_routes>=25]
    print(panel[["forest_score","doy","relative_day","Caudata","Odonata"]].corr(method="spearman").round(3))
    print(panel.groupby("forest_score")[["Caudata","Odonata"]].agg(["size","median"]).round(3))
    print(panel.loc[["Hyla versicolor","Hyla gratiosa","Gastrophryne carolinensis","Lithobates palustris","Lithobates clamitans","Lithobates catesbeianus"],["relative_day","doy","forest_score","mode"]])
    print(data[data["mode"].isna()].index.tolist())
if __name__=="__main__":
    main(Path(sys.argv[1]))
