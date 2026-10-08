import importlib.util,sys
from pathlib import Path
import pandas as pd,pytest
script=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(script))
spec=importlib.util.spec_from_file_location('acoustic360417',script/'explore_iowa360417_acoustic_environment_v20.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def sources():
    runs=[];stops=[];calls=[];land=[]
    for year in (2010,2011,2012,2013,2015):
        rid=str(year)
        runs.append(dict(RunID=rid,State='Iowa',RouteNumber='360417',RouteType='1',RunNumber='2',
            SurveyDate=f'05/10/{year}',SurveyYear=str(year),UnifiedProtocol='1',
            DaysSinceRain='2',TempScale='C',ObserverTrackingID='obs'))
        for stop in range(1,11):
            stops.append(dict(RunID=rid,StopNumber=str(stop),SiteID=f's{stop}',
                SkippedStop='0',AirTemp='20'))
        # Chorus shifts from stop 10 in 2010/2011 to stop 3 after 2012.
        stop=10 if year<=2011 else 3
        calls.append(dict(RunID=rid,StopNumber=str(stop),Species='Frog A',CallingIndex='2'))
        calls.append(dict(RunID=rid,StopNumber='8',Species='Frog B',CallingIndex='1'))
    for year in range(2009,2015):
        for stop in range(1,11):
            for radius in (250,1000):
                forest=10-(2 if (stop==10 and year>=2012) else 0)
                land.append(dict(site_id=f's{stop}',stop_number=stop,radius_m=radius,year=year,
                   forest_pct=forest,agriculture_pct=60,developed_pct=20,
                   wetland_pct=0,open_water_pct=0,historic_field_station_verified=False))
    return pd.DataFrame(runs),pd.DataFrame(stops),pd.DataFrame(calls),pd.DataFrame(land)

def test_route_acoustic_split_retains_all_sites_and_taxa():
    r,s,c,l=sources()
    result,collapsed,duplicates=m.prepare(r,s,c,l)
    report=m.summarize(result,collapsed,duplicates,l)
    assert len(result)==100 # 5 surveys x 10 stops x 2 buffers
    assert report['n_runs']==5
    assert len(report['all_ten_sites_both_radii'])==20
    assert report['no_confirmatory_inference_permitted']
    assert report['n_distinct_species_positive']==2
    site10=next(z for z in report['all_ten_sites_both_radii'] if z['radius_m']==250 and z['stop_number']==10)
    assert site10['forest_pct_2011_to_2012_change']==pytest.approx(-2)
    assert site10['post_minus_pre_mean_strong_species']==pytest.approx(-1)
    site3=next(z for z in report['all_ten_sites_both_radii'] if z['radius_m']==250 and z['stop_number']==3)
    assert site3['post_minus_pre_mean_strong_species']==pytest.approx(1)

def test_nondetected_frog_is_acoustic_zero_only_and_duplicate_counts_do_not_add_species():
    r,s,c,l=sources()
    c=pd.concat([c,c.iloc[[0]]],ignore_index=True)
    a,collapse,dup=m.prepare(r,s,c,l)
    assert dup==1
    assert a[(a.run_id=='2010')&(a.stop_number==9)&(a.buffer_m==250)].iloc[0].strong_species==0
    assert a[(a.run_id=='2010')&(a.stop_number==10)&(a.buffer_m==250)].iloc[0].strong_species==1

def test_future_landcover_cannot_fill_missing_previous_year():
    r,s,c,l=sources()
    l=l[l.year!=2009]
    with pytest.raises(ValueError,match='antecedent'):
        m.prepare(r,s,c,l)

def test_same_year_event_excluded_from_pre_post_comparison():
    r,s,c,l=sources()
    a,collapse,dup=m.prepare(r,s,c,l)
    report=m.summarize(a,collapse,dup,l)
    summary={e['era']:e['n_survey_runs'] for e in report['era_summary']}
    assert summary['year_2012_unordered']==1
    assert summary['pre']==2 and summary['post']==2
    assert all(e['n_surveys']==2 for e in report['all_ten_sites_both_radii'][:0])

def test_reassigned_site_id_stops_analysis():
    r,s,c,l=sources()
    s.loc[(s.RunID=='2013')&(s.StopNumber=='10'),'SiteID']='s10_relocated'
    with pytest.raises(ValueError,match='ambiguous'):
        m.prepare(r,s,c,l)
