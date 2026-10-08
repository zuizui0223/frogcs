"""Synthetic-only validation of route climate extraction without frog response data."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
from datetime import date, timedelta
import pandas as pd
import pytest

S=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(S))
sp=importlib.util.spec_from_file_location('route_daymet',S/'daymet_route_climate_pilot.py')
m=importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)


def synthetic_sources(states=('Virginia',)):
    r=[];s=[];c=[]
    for state in states:
        for year in (2001,2003,2005,2007,2009,2011,2013):
            rid=f'{state}_{year}'
            r.append({'RunID':rid,'SurveyDate':f'05/10/{year}',
               'SurveyYear':str(year),'UnifiedProtocol':'1',
               'State':state,'RouteNumber':'R001' if state=='Virginia' else 'R002',
               'RouteType':'1','RunNumber':'2','DaysSinceRain':'2',
               'TempScale':'C'})
            for i in range(10):
                site=f'{state}_S{i}'
                s.append({'RunID':rid,'StopNumber':str(i+1),'SkippedStop':'0',
                         'SiteID':site,'AirTemp':'15'})
        for i in range(10):
            c.append({'RouteNumber':'R001' if state=='Virginia' else 'R002',
                      'SiteID':f'{state}_S{i}', 'lat':40.0+0.001*i,
                      'lon':-100.0-0.001*i})
    return pd.DataFrame(r),pd.DataFrame(s),pd.DataFrame(c)


def synthetic_daymet(years=m.YEARS):
    body=['# synthetic daily Daymet-like source',
          'year,yday,prcp (mm/day),tmax (deg c),tmin (deg c)']
    for y in years:
        for d in range(1,366):
            body.append(f'{y},{d},2,20,10')
    return ('\n'.join(body)+'\n').encode()


def test_fixed_sampling_does_not_access_frog_counts_and_is_stable():
    runs,stops,coords=synthetic_sources(('Virginia','Maryland'))
    sample,receipt=m.select_routes(runs,stops,coords,max_routes=2)
    sample2,receipt2=m.select_routes(runs.sample(frac=1,random_state=4),
        stops.sample(frac=1,random_state=6),coords.sample(frac=1,random_state=7),max_routes=2)
    assert sample==sample2
    assert receipt['n_sampled_states']==2
    assert all(p['coordinate_status']=='route_median_geometry_pass_unverified' for p in sample)
    assert receipt['site_level_externally_verified'] is False
    assert receipt['input_uses_count_data'] is False


def test_daymet_csv_parses_365_days_per_year_and_leap_day():
    d=m.parse_daymet_csv(synthetic_daymet())
    assert len(d)==35*365
    assert d.query('year == 1984 and yday == 60').iloc[0].date=='1984-02-29'
    assert d.query('year == 1984 and yday == 365').iloc[0].date=='1984-12-30'
    assert d.query('year == 1985 and yday == 365').iloc[0].date=='1985-12-31'
    assert d.precip_mm.sum()==pytest.approx(35*365*2)


def test_daymet_complete_record_missing_row_hard_fails():
    raw=synthetic_daymet()
    txt=raw.decode().replace('1988,27,2,20,10\n','')
    with pytest.raises(ValueError,match='Incomplete'):
        m.parse_daymet_csv(txt.encode())


def test_daymet_unexpected_366_fails():
    text=synthetic_daymet().decode()+ '1984,366,2,20,10\n'
    with pytest.raises(ValueError,match='invalid'):
        m.parse_daymet_csv(text.encode())


def test_daymet_nonphysical_precip_hard_fails():
    txt=synthetic_daymet().decode().replace('1983,22,2,20,10','1983,22,-5,20,10')
    with pytest.raises(ValueError,match='Nonphysical'):
        m.parse_daymet_csv(txt.encode())


def test_climate_trends_and_strictly_prior_years():
    daily=m.parse_daymet_csv(synthetic_daymet())
    result=m.climate_summary(daily)
    assert result['annual_observations']==35
    assert result['baseline_mean_temp_c']==pytest.approx(15)
    assert result['baseline_precip_mm_year']==pytest.approx(730)
    assert result['descriptive_1981_2015_temp_slope_c_decade']==pytest.approx(0)
    assert result['climate_state_by_survey_year']['2001']['prior5_tmean_anomaly_c']==pytest.approx(0)
    assert result['climate_state_by_survey_year']['2015']['prior5_precip_ratio_to_1981_2000']==pytest.approx(1)
    # A warm survey year must not affect a strictly antecedent exposure.
    altered=daily.copy()
    altered.loc[altered.year==2015,'tmean_c'] += 10
    updated=m.climate_summary(altered)
    assert updated['climate_state_by_survey_year']['2015']==result['climate_state_by_survey_year']['2015']


def test_daymet_url_is_pinned_to_official_api():
    url=m.daymet_url(40,-100)
    assert url.startswith('https://daymet.ornl.gov/single-pixel/api/data?')
    assert '1981' in url and '2015' in url
    with pytest.raises(ValueError,match='outside|Outside'):
        m.daymet_url(61,-100)
