"""Season-matched species comparisons and a leave-focal-species-out chorus sensitivity."""
from itertools import combinations
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from threadpoolctl import threadpool_limits
import sdm_flooded_omission as sdm
from naamp_species_strong_call_sensitivity import build_outcomes

OUT=sdm.ROOT/"species_predator_correlations_20261111"

def correlations(raw, traits):
    freq,counts,support,ranges=build_outcomes(raw,sdm.site,all_species_ranges=True)
    models=sdm.models.query("background=='uniform'")
    guilds={g:np.mean([sdm.refit(m,sdm.base) for m in rows.itertuples()],axis=0)
            for g,rows in models.groupby("guild")}
    rows=[]
    for species in traits.index:
        keep=np.isin(sdm.routes,list(ranges[species]))
        focal=freq[keep,counts.columns.get_loc("species|"+species)]
        # Counts strong visits after removing the focal taxon; includes silent visits in denominator.
        others=freq[keep,counts.columns.get_loc("leave_out|"+species)]
        for guild,score in guilds.items():
            a=pd.DataFrame({"suit":rankdata(score[keep]),"focal":rankdata(focal),"others":rankdata(others)})
            a-=a.groupby(sdm.routes[keep]).transform("mean")
            base=a.suit.corr(a.focal)
            z=a.others.to_numpy()
            vals=a[["suit","focal"]].to_numpy()
            if z@z>0:
                vals=vals-np.outer(z,z@vals/(z@z))
            adj=pd.DataFrame(vals).corr().iloc[0,1] if len(vals)>1 else np.nan
            rows.append([species,guild,base,adj])
    r=pd.DataFrame(rows,columns=["species","guild","raw","chorus_adjusted"])
    r.to_csv(OUT/"chorus_sensitivity.csv",index=False)
    return r

def main(raw):
    traits=pd.read_csv(OUT/"breeding_traits_44.csv").set_index("species")
    r=correlations(raw,traits)
    panel=traits[traits.strong_routes>=25].copy()
    panel["duration"]=np.sqrt(panel.days_low*panel.days_high).where(panel.duration_definition.eq("reported larval development"))
    panel["permanent"]=panel.hydroperiod.eq("Permanent").astype(int)
    # Explicit free-floating or surface films only. Near-surface attachment alone is a different strategy.
    panel["surface_spawn"]=panel.egg_position.str.contains("floating|surface film").astype(int)
    pairs=[]
    for sp,other in combinations(panel.index,2):
        a,b=panel.loc[sp],panel.loc[other]
        for guild in ("Odonata","Caudata"):
            idx=r[r.guild.eq(guild)].set_index("species")
            np.testing.assert_allclose(idx.at[sp,"raw"],a[guild],atol=1e-12)
            pairs.append([sp,other,guild,abs(a.doy-b.doy),abs(a.relative_day-b.relative_day),
                          a.permanent-b.permanent,a.surface_spawn-b.surface_spawn,np.sign(a.duration-b.duration),
                          int(a.days_low>b.days_high)-int(b.days_low>a.days_high) if pd.notna(a.duration*b.duration) else np.nan,
                          int("surface" in a.egg_position or "floating" in a.egg_position)-int("surface" in b.egg_position or "floating" in b.egg_position),
                          a[guild]-b[guild],idx.at[sp,"chorus_adjusted"]-idx.at[other,"chorus_adjusted"]])
    pairs=pd.DataFrame(pairs,columns=['a','b','guild','calendar_gap','relative_gap','permanent','surface_spawn','duration','nonoverlap_duration','surface_broad','delta','adjusted_delta'])
    pairs.to_csv(OUT/'timing_matched_pairs.csv',index=False)
    rows=[]
    for clock in ['calendar_gap','relative_gap']:
        for window in [7,14,21]:
            for guild in ['Odonata','Caudata']:
                for trait in ['permanent','surface_spawn','duration','nonoverlap_duration','surface_broad']:
                    z=pairs[(pairs[clock]<=window)&pairs.guild.eq(guild)&pairs[trait].abs().eq(1)]
                    for outcome in ['delta','adjusted_delta']:
                        diff=z[trait]*z[outcome]
                        species=set(z.a)|set(z.b)
                        loo=[diff[(z.a!=s)&(z.b!=s)].mean() for s in species]
                        rows.append([clock,window,guild,trait,outcome,len(z),len(species),diff.mean(),diff.gt(0).sum(),pd.Series(loo,dtype=float).min(),pd.Series(loo,dtype=float).max()])
    out=pd.DataFrame(rows,columns=['clock','window','guild','trait','outcome','pairs','species','mean_difference','positive_pairs','leave_one_species_min','leave_one_species_max'])
    out.to_csv(OUT/'timing_trait_contrasts.csv',index=False)
    print(out.query("clock=='calendar_gap' and window==7").round(4).to_string(index=False))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("raw",type=Path)
    with threadpool_limits(limits=1):
        main(parser.parse_args().raw)
