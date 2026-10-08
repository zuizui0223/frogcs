"""Synthetic end-to-end receipt -> route/year -> NAAMP run climate history tests."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import pytest
import pandas as pd

DIR=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(DIR))
sp=importlib.util.spec_from_file_location('daymet_event',DIR/'build_daymet_survey_exposure_panel.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)


def fixture():
    sample={"routes":[{"route_id":"VA:1234","state":"VA",
               "coordinate_status":"route_median_geometry_pass_unverified"}],
            "selection":{"input_uses_count_data":False}}
    yearvals={str(y):{"prior5_tmean_anomaly_c":(y-2000)/10,
                     "prior5_precip_ratio_to_1981_2000":0.85} for y in range(2001,2016)}
    climate={"analysis":"daymet_route_level_pilot_v0_1", "status":"complete_source_screening",
             "n_requested":1,"reads_frog_calling_data":False,
             "routes":[{"route_id":"VA:1234","state":"VA",
                 "coordinate_geometry_status":"route_median_geometry_pass_unverified",
                 "daymet_daily_rows":35*365, "annual_observations":35,
                 "baseline_years":"1981-2000",
                 "retrospective_trend_is_not_an_early_year_predictor":True,
                 "descriptive_1981_2015_temp_slope_c_decade":1.23,
                 "climate_state_by_survey_year":yearvals}]}
    runs=[];stops=[]
    for y in (2001,2007,2015):
        for round in (1,2):
            runid=f'r{y}_{round}'
            runs.append({"RunID":runid,"SurveyDate":f'05/10/{y}',"SurveyYear":str(y),
                "State":"VA","RouteNumber":"1234","RouteType":"1",
                "RunNumber":str(round),"UnifiedProtocol":"1","DaysSinceRain":"2",
                "TempScale":"C","ObserverTrackingID":"obs1"})
            stops.extend({"RunID":runid,"StopNumber":str(k),"SkippedStop":"0",
                          "SiteID":str(k),"AirTemp":"18"} for k in range(1,11))
    return sample,climate,pd.DataFrame(runs),pd.DataFrame(stops)


def test_route_year_exposures_do_not_pseudo_replicate_climate():
    a,b,c,d=fixture()
    result,counts=m.combine(a,b,c,d)
    assert len(result)==6
    assert counts['selected_survey_runs']==6
    assert counts['distinct_climate_route_years']==3
    assert counts['input_surveyed_stop_visits']==60
    assert result.groupby('survey_year').prior5_tmean_anomaly_c.nunique().eq(1).all()
    assert result.climate_history_last_year.lt(result.survey_year).all()
    assert 'descriptive_1981_2015_temp_slope_c_decade' not in result.columns
    assert result.observer_id.eq('obs1').all()
    assert not any('frog' in s or 'CallingIndex' in s for s in result.columns)


def test_no_partial_receipt_is_allowed():
    a,b,c,d=fixture();b['status']='partial_source_screening'
    with pytest.raises(ValueError,match='incomplete'):
        m.combine(a,b,c,d)


def test_missing_focal_year_is_hard_error():
    a,b,c,d=fixture();del b['routes'][0]['climate_state_by_survey_year']['2009']
    with pytest.raises(ValueError,match='Incomplete strictly-prior'):
        m.combine(a,b,c,d)


def test_missing_route_or_changed_coordinate_identity_is_hard_error():
    a,b,c,d=fixture();b['routes'][0]['route_id']='VA:other'
    with pytest.raises(ValueError,match='identity'):
        m.combine(a,b,c,d)
    a,b,c,d=fixture();b['routes'][0]['coordinate_geometry_status']='verified_external'
    with pytest.raises(ValueError,match='coordinate'):
        m.combine(a,b,c,d)


def test_tampered_source_or_future_info_rejected():
    a,b,c,d=fixture();b['routes'][0]['retrospective_trend_is_not_an_early_year_predictor']=False
    with pytest.raises(ValueError,match='future-leakage'):
        m.combine(a,b,c,d)
    a,b,c,d=fixture();b['routes'][0]['climate_state_by_survey_year']['2012']['prior5_tmean_anomaly_c']=float('nan')
    with pytest.raises(ValueError,match='Invalid climate state'):
        m.combine(a,b,c,d)


def test_fail_if_unselected_site_or_no_run_matches():
    a,b,c,d=fixture();a['routes'][0]['route_id']='MD:6'
    b['routes'][0]['route_id']='MD:6'
    with pytest.raises(ValueError,match='No NAAMP runs'):
        m.combine(a,b,c,d)
