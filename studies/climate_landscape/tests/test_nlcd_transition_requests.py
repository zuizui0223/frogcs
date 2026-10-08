import importlib.util
from pathlib import Path
import pandas as pd
import pytest
S=Path(__file__).resolve().parents[1]/'scripts'/'build_nlcd_transition_requests.py'
sp=importlib.util.spec_from_file_location('nlcd_change_req',S)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)


def frame():
    return pd.DataFrame([{'run_id':'R1','route_id':'VA:1','site_id':'T1',
             'latitude':37.5,'longitude':-76.2,'survey_date':'2008-05-20',
             'coordinate_qc_status':'verified_external','verification_source_id':'SYNTH'}])


def test_prior_only_five_year_window_two_buffers():
    a=m.make(frame())
    assert len(a)==2
    assert a.year_earlier.unique().tolist()==[2002]
    assert a.year_later.unique().tolist()==[2007]
    assert set(a.buffer_m)=={250,1000}
    assert all(a.run_id=='R1')


def test_refuse_unverified_station():
    a=frame();a['coordinate_qc_status']='pass_unverified'
    with pytest.raises(ValueError,match='Independent'):
        m.make(a)


def test_refuse_outcome_leakage():
    a=frame();a['CallingIndex']=3
    with pytest.raises(ValueError,match='Outcome data'):
        m.make(a)


def test_refuse_post_naamp_survey():
    a=frame();a['survey_date']='2018-05-20'
    with pytest.raises(ValueError,match='2001–2015'):
        m.make(a)


def test_refuse_duplicate_event():
    a=frame();a=pd.concat([a,a],ignore_index=True)
    with pytest.raises(ValueError,match='Duplicate'):
        m.make(a)
