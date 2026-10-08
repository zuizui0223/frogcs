import sys,importlib.util
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
sp=importlib.util.spec_from_file_location('roadside',Path(__file__).resolve().parents[1]/'scripts'/'audit_naamp_roadside_detection_history.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

def data():
    runs=[];stops=[]
    for year in (2008,2009):
        runs.append({'RunID':f'r{year}','State':'VA','RouteNumber':'100001','RouteType':'1',
                     'RunNumber':'2','UnifiedProtocol':'1','SurveyYear':str(year),
                     'SurveyDate':f'05/10/{year}','DaysSinceRain':'3','TempScale':'C','ObserverTrackingID':'abc'})
        for k in range(1,11):
            stops.append({'RunID':f'r{year}','StopNumber':str(k),'SkippedStop':'0',
              'SiteID':f'{k:03d}','AirTemp':'20',
              'CarCount':str(k+(year-2008)), 'MassNoiseIndex':'1', 'Noise':'0','TimeOut':'0'})
    return pd.DataFrame(runs),pd.DataFrame(stops)

def test_expected_comparable_metadata_counts():
    a,b=data();r=m.audit(a,b)
    assert r['n_adjacent_year_same_season_site_pairs']==10
    assert r['n_complete_car_count_pairs']==10
    assert r['n_complete_acoustic_impairment_pairs']==10
    assert r['n_same_observer_pairs']==10
    assert r['n_increasing_car_count_pairs']==10
    assert r['median_car_count_change_in_comparable_pairs']==1
    assert r['frog_outcome_read'] is False

def test_unrecorded_noise_and_cars_not_assumed_zero():
    a,b=data()
    b.loc[b.RunID=='r2009',['CarCount','MassNoiseIndex','Noise','TimeOut']]=''
    r=m.audit(a,b)
    assert r['n_complete_car_count_pairs']==0
    assert r['n_complete_acoustic_impairment_pairs']==0
    assert r['median_car_count_change_in_comparable_pairs'] is None

def test_mass_noise_fallback_to_valid_binary_noise():
    a,b=data()
    b.loc[b.RunID=='r2009','MassNoiseIndex']='-99'
    b.loc[b.RunID=='r2009','Noise']='1'
    r=m.audit(a,b)
    assert r['n_complete_acoustic_impairment_pairs']==10

def test_missing_required_field_fails():
    a,b=data()
    with pytest.raises(ValueError,match='missing stop fields'):
        m.audit(a,b.drop(columns='CarCount'))
