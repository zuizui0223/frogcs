import importlib.util,sys
from pathlib import Path
import pandas as pd
import pytest
root=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(root))
spec=importlib.util.spec_from_file_location('iowa360417',root/'audit_iowa_360417_pdf_waypoints.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def sample():
    lines=["Route ID: 360417","Site Number Name County Latitude Longitude Directions"]
    for i in range(1,11):
        county='Warren' if i<=5 else 'Madison'
        lines.append(f"{i} {i*.7:.1f} {county} {41.5-i*.01:.7f} {-93.79-i*.005:.7f} road details")
    return lines

def test_parses_exact_ten_labeled_pdf_rows():
    x=mod.waypoint_table_from_pages(["\n".join(sample()[:7]),"\n".join(sample()[7:])])
    assert len(x)==10 and x.stop_no.tolist()==list(range(1,11))
    assert x.latitude.iloc[0]==pytest.approx(41.49)

def test_reject_missing_or_duplicate_dnr_stop():
    lines=sample()
    with pytest.raises(ValueError,match='No unambiguous'):
        mod.waypoint_table_from_pages(['\n'.join(lines[:-1])])
    lines[3]=lines[2]
    with pytest.raises(ValueError,match='No unambiguous'):
        mod.waypoint_table_from_pages(['\n'.join(lines)])

def make_naamp(x):
    runs=[];stops=[];coords=[]
    for y in (2009,2010):
        rid=f'r{y}'
        runs.append({'RunID':rid,'State':'Iowa','RouteNumber':'360417','RouteType':'1',
              'RunNumber':'2','UnifiedProtocol':'1','SurveyYear':str(y),
              'SurveyDate':f'05/10/{y}','DaysSinceRain':'1','TempScale':'C'})
        for row in x.itertuples(index=False):
            stops.append({'RunID':rid,'StopNumber':str(row.stop_no),'SkippedStop':'0',
                          'SiteID':f'id{row.stop_no}','AirTemp':'20'})
    for row in x.itertuples(index=False):
        coords.append({'RouteNumber':'360417','SiteID':f'id{row.stop_no}',
                       'lat':row.latitude,'lon':row.longitude})
    return pd.DataFrame(runs),pd.DataFrame(stops),pd.DataFrame(coords)

def test_coordinate_agreement_does_not_verify_field_history():
    x=mod.waypoint_table_from_pages(['\n'.join(sample())])
    r,s,c=make_naamp(x)
    a=mod.compare_original(r,s,c,x)
    assert a['n_comparable_coordinate_stops']==10
    assert a['n_within_100m']==10
    assert a['n_historical_field_sites_independently_verified']==0

def test_wrong_usgs_coordinate_kept_as_mismatch_not_repaired():
    x=mod.waypoint_table_from_pages(['\n'.join(sample())])
    r,s,c=make_naamp(x)
    c.loc[c.SiteID=='id1','lon']-=0.005
    a=mod.compare_original(r,s,c,x)
    assert a['n_within_100m']<=9
    assert a['n_historical_field_sites_independently_verified']==0
