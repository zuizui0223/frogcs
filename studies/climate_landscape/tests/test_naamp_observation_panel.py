import importlib.util
from pathlib import Path
import pandas as pd
import pytest
sp=importlib.util.spec_from_file_location('naamp_panel',Path(__file__).resolve().parents[1]/'scripts'/'build_naamp_observation_panel.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

def data():
    run=pd.DataFrame([dict(RunID='a',SurveyDate='05/10/2010',SurveyYear='2010',UnifiedProtocol='1',RouteNumber='0701',RouteType='1',State='VA',RunNumber='2',DaysSinceRain='2',TempScale='C')])
    stops=pd.DataFrame([dict(RunID='a',StopNumber=str(i),SiteID=f's{i}',AirTemp='15',SkippedStop='0') for i in range(1,11)])
    return run,stops

def test_no_count_columns_or_fake_nondetections():
    run,stops=data()
    out,rec=m.make(run,stops)
    assert len(out)==10
    assert out.route_id.iloc[0]=='VA:0701'
    assert out.survey_round.iloc[0]==2
    assert rec['counts_csv_opened']==False
    assert 'calling_index' not in out.columns

def test_nonconforming_survey_skipped():
    run,stops=data()
    stops.loc[0,'SkippedStop']='1'
    out,r=m.make(run,stops)
    assert len(out)==0 and r['n_runs_incomplete_number_of_stops']==1

def test_missing_or_relocated_sites_do_not_enter():
    run,stops=data()
    stops.loc[0,'SiteID']='s2'
    out,r=m.make(run,stops)
    assert out.empty and r['n_runs_with_missing_or_repeated_site_id']==1

def test_invalid_date_not_silently_fixed():
    run,stops=data()
    run.loc[0,'SurveyYear']='2011'
    out,r=m.make(run,stops)
    assert out.empty and r['n_invalid_date_rows']==1

def test_eligible_route_maintains_leading_zero_identifier():
    run,stops=data()
    x,_=m.make(run,stops)
    assert x.route_number.iloc[0]=='0701'


def test_pre_2001_is_out_of_scope_not_date_error():
    run,stops=data()
    run.loc[0,'SurveyYear']='1998'
    run.loc[0,'SurveyDate']='05/10/1998'
    out,rec=m.make(run,stops)
    assert out.empty and rec['n_invalid_date_rows']==0
