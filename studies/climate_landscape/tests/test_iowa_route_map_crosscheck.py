import sys,importlib.util
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
path=Path(__file__).resolve().parents[1]/'scripts'/'audit_iowa_route_map_crosscheck.py'
sp=importlib.util.spec_from_file_location('iowa',path)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
reference_path=Path(__file__).resolve().parents[1]/'reference_routes'/'iowa_dnr_360411_2020_route_waypoints.csv'

def source():
    ref=pd.read_csv(reference_path,dtype={'route_number':str})
    runs,stops,coords=[],[],[]
    for year in (2010,2011):
        rid=f'run{year}'
        runs.append(dict(RunID=rid,State='Iowa',RouteNumber='360411',RouteType='1',RunNumber='2',
                         UnifiedProtocol='1',SurveyYear=str(year),SurveyDate=f'05/10/{year}',
                         DaysSinceRain='1',TempScale='C'))
        for no in range(1,11):
            stops.append(dict(RunID=rid,StopNumber=str(no),SkippedStop='0',
                              SiteID=f's{no:02d}',AirTemp='20'))
    for r in ref.itertuples(index=False):
        coords.append(dict(RouteNumber='360411',SiteID=f's{r.stop_no:02d}',lat=r.latitude,lon=r.longitude))
    return pd.DataFrame(runs),pd.DataFrame(stops),pd.DataFrame(coords),ref

def test_matching_external_coordinates_not_historical_verified():
    runs,stops,coords,ref=source()
    q=m.audit(runs,stops,coords,ref)
    assert q['status']=='METADATA_COORDINATE_CROSSCHECK_ONLY'
    assert q['n_map_reference_stops']==10
    assert q['n_stops_within_100m']==10
    assert q['max_documented_to_naamp_distance_m']<0.01
    assert q['n_field_verification_of_2001_2015_station_history']==0

def test_mismatch_not_repaired():
    r,s,c,ref=source()
    c.loc[c.SiteID=='s01','lon']-=.01
    q=m.audit(r,s,c,ref)
    assert q['n_stops_within_100m']==9
    assert q['max_documented_to_naamp_distance_m']>500

def test_historical_siteid_change_is_ambiguous():
    r,s,c,ref=source()
    s.loc[(s.RunID=='run2011') & s.StopNumber.eq('1'),'SiteID']='new'
    q=m.audit(r,s,c,ref)
    assert q['n_stop_numbers_with_ambiguous_historical_siteid']==1
    assert q['n_map_stops_unresolved']==1

def test_foreign_reference_date_rejected():
    r,s,c,ref=source()
    ref.loc[0,'reference_date']='2010-01-01'
    with pytest.raises(ValueError,match='reference date'):
        m.audit(r,s,c,ref)

def test_other_state_route_absence_reported():
    r,s,c,ref=source()
    r['State']='Delaware'
    q=m.audit(r,s,c,ref)
    assert q['status']=='ROUTE_NOT_IN_STANDARDIZED_NAAMP_COHORT'
