import importlib.util
import sys
from pathlib import Path
import pandas as pd

scripts=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(scripts))
spec=importlib.util.spec_from_file_location("feasibility",scripts/"run_public_naamp_feasibility.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sources():
    runs=[];stops=[];coords=[]
    for year,day in [(2010,"05/10/2010"),(2011,"05/11/2011"),(2012,"07/30/2012")]:
        rid=f"run{year}"
        runs.append(dict(RunID=rid,SurveyDate=day,SurveyYear=str(year),
                         UnifiedProtocol="1",RouteNumber="0701",RouteType="1",
                         State="VA",RunNumber="2",DaysSinceRain="2",TempScale="C"))
        for i in range(10):
            stops.append(dict(RunID=rid,StopNumber=str(i+1),SiteID=f"s{i+1}",
                              AirTemp="15",SkippedStop="0"))
    for i in range(10):
        coords.append(dict(RouteNumber="0701",SiteID=f"s{i+1}",
                           lat=40+i*.001,lon=-100-i*.001))
    return pd.DataFrame(runs),pd.DataFrame(stops),pd.DataFrame(coords)


def test_geometry_is_not_external_verification():
    a,b,c=sources()
    r=mod.summarize(a,b,c)
    assert r["n_candidate_ten_stop_runs"]==3
    assert r["n_surveyed_stop_opportunities"]==30
    assert r["n_stop_visits_matching_source_coordinates"]==30
    assert r["n_stop_visits_geometry_pass_but_unverified"]==30
    assert r["n_externally_verified_sites"]==0
    assert r["n_potential_same_site_consecutive_year_same_season_pairs"]==10
    assert r["n_potential_pairs_geometry_pass_but_unverified"]==10
    assert not r["frog_positive_count_file_opened"]


def test_route_numbers_in_two_states_are_ambiguous():
    a,b,c=sources()
    d=a.iloc[[0]].copy();d["State"]="NC";d["RunID"]="other"
    a=pd.concat([a,d],ignore_index=True)
    bb=b[b.RunID=="run2010"].copy();bb["RunID"]="other"
    b=pd.concat([b,bb],ignore_index=True)
    r=mod.summarize(a,b,c)
    assert r["n_route_numbers_reused_between_states"]==1
    assert r["n_stop_visits_geometry_pass_but_unverified"]==0


def test_out_of_season_survey_does_not_create_year_pair():
    a,b,c=sources()
    a.loc[a.SurveyYear=="2011","SurveyDate"]="09/25/2011"
    r=mod.summarize(a,b,c)
    assert r["n_potential_same_site_consecutive_year_same_season_pairs"]==0
