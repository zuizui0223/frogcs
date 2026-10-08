import importlib.util
from pathlib import Path
import pandas as pd
import pytest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
SCRIPT=Path(__file__).resolve().parents[1]/'scripts'/'audit_naamp_historical_site_stability.py'
sp=importlib.util.spec_from_file_location('site_stability',SCRIPT)
mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)

def fixture():
    runs=[];stops=[];coords=[]
    for year in (2008,2009,2010):
        rid=f'r{year}'
        runs.append({'RunID':rid,'State':'VA','RouteNumber':'100001','RouteType':'1','RunNumber':'2',
          'UnifiedProtocol':'1','SurveyYear':str(year),'SurveyDate':f'05/10/{year}',
          'DaysSinceRain':'2','TempScale':'C'})
        for k in range(1,11):
            stops.append({'RunID':rid,'StopNumber':str(k),'SkippedStop':'0',
                          'SiteID':f'{k:03d}','AirTemp':'19'})
    for k in range(1,11):
        coords.append({'RouteNumber':'100001','SiteID':f'{k:03d}',
                       'lat':38+.001*k,'lon':-77-.001*k})
    return pd.DataFrame(runs),pd.DataFrame(stops),pd.DataFrame(coords)

def test_repeated_stable_sites_still_unverified():
    r,s,c=fixture();a=mod.audit_metadata(r,s,c)
    assert a['n_runs']==3
    assert a['n_route_site_keys']==10
    assert a['n_sites_surveyed_two_or_more_years']==10
    assert a['n_route_site_keys_stop_number_changed']==0
    assert a['n_adjacent_year_same_season_stop_pairs']==20
    assert a['n_adjacent_year_pairs_consistent_and_geometry_pass_unverified']==20
    assert a['sites_externally_verified']==0
    assert not a['counts_csv_read']

def test_reassigned_stop_number_is_flagged():
    r,s,c=fixture()
    mask=s.RunID=='r2010';idx1=s.index[mask & s.SiteID.eq('001')][0];idx2=s.index[mask & s.SiteID.eq('002')][0]
    s.loc[idx1,'StopNumber']='2';s.loc[idx2,'StopNumber']='1'
    a=mod.audit_metadata(r,s,c)
    assert a['n_route_site_keys_stop_number_changed']==2
    assert a['n_repeated_year_sites_stop_number_changed']==2
    assert a['n_adjacent_year_pairs_consistent_stop_number']==16
    assert a['n_adjacent_year_pairs_consistent_and_geometry_pass_unverified']==16

def test_duplicate_numeric_stop_rejected():
    r,s,c=fixture()
    s.loc[(s.RunID=='r2010') & s.SiteID.eq('002'),'StopNumber']='01'
    with pytest.raises(ValueError,match='Duplicated StopNumber'):
        mod.audit_metadata(r,s,c)

def test_geom_bad_does_not_count_as_provisional():
    r,s,c=fixture();c.loc[c.SiteID=='001','lon']=+77
    a=mod.audit_metadata(r,s,c)
    assert a['n_adjacent_year_pairs_consistent_and_geometry_pass_unverified']<20
    assert a['sites_externally_verified']==0
