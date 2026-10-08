import importlib.util
import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
p=Path(__file__).resolve().parents[1]/'scripts'/'audit_naamp_survey_attrition.py'
s=importlib.util.spec_from_file_location('attrition',p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)


def fixture():
    runs, stops=[],[]
    for year in (2008,2009,2010):
        rid=f'run{year}'
        runs.append(dict(RunID=rid,State='VA',RouteNumber='1020',RouteType='1',RunNumber='2',
              UnifiedProtocol='1',SurveyYear=str(year),SurveyDate=f'05/10/{year}',
              DaysSinceRain='1',TempScale='C'))
        for k in range(1,11):
            stops.append(dict(RunID=rid,StopNumber=str(k),SkippedStop='0',
                              SiteID=f's{k}',AirTemp='19'))
    return pd.DataFrame(runs),pd.DataFrame(stops)


def test_complete_field_runs_yield_two_full_pairs():
    r,st=fixture()
    q=m.audit(r,st)
    assert q['n_pre_stop_qc_candidate_runs']==3
    assert q['n_complete_standardized_runs_after_all_qc']==3
    assert q['n_adjacent_year_same_season_route_round_pairs']==2
    assert q['n_pair_both_full_field_opportunity']==2
    assert q['n_pair_both_in_final_analysis_panel']==2
    assert q['n_same_id_sampled_to_skipped_stop_transitions']==0


def test_skip_not_equated_with_absence_or_extinction():
    r,st=fixture()
    st.loc[(st.RunID=='run2009') & st.SiteID.eq('s3'),'SkippedStop']='1'
    q=m.audit(r,st)
    assert q['n_pre_stop_qc_candidate_runs']==3
    assert q['n_complete_standardized_runs_after_all_qc']==2
    assert q['n_candidate_runs_with_one_or_more_skipped_stops']==1
    assert q['n_pair_before_full_after_partial']==1
    assert q['n_pair_before_partial_after_full']==1
    assert q['n_same_id_sampled_to_skipped_stop_transitions']==1
    assert q['n_same_id_skipped_to_sampled_stop_transitions']==1
    assert q['no_automatic_retirement_or_extinction_classification'] is True


def test_same_stop_order_different_site_id_is_replacement_not_skipped():
    r,st=fixture()
    st.loc[(st.RunID=='run2009') & st.SiteID.eq('s3'),'SiteID']='different_s3'
    q=m.audit(r,st)
    assert q['n_same_order_siteid_replacement_transitions']==2
    assert q['n_same_id_sampled_to_skipped_stop_transitions']==0


def test_unknown_skip_not_imputed_zero():
    r,st=fixture()
    st.loc[(st.RunID=='run2009') & st.SiteID.eq('s3'),'SkippedStop']=''
    q=m.audit(r,st)
    assert q['n_candidate_stop_records_unknown_skip_code']==1
    assert q['n_candidate_runs_with_unknown_stop_state_or_missing_stop_rows']==1
    assert q['n_pair_both_in_final_analysis_panel']==0


def test_different_season_does_not_pair():
    r,st=fixture()
    r.loc[r.SurveyYear=='2009','SurveyDate']='08/10/2009'
    q=m.audit(r,st)
    assert q['n_adjacent_year_same_season_route_round_pairs']==0


def test_duplicate_stop_order_hard_fail():
    r,st=fixture()
    st.loc[(st.RunID=='run2009') & st.SiteID.eq('s4'),'StopNumber']='3'
    with pytest.raises(ValueError,match='Duplicate stop order'):
        m.audit(r,st)
