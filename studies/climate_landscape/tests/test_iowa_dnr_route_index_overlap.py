import sys
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import audit_iowa_dnr_route_index_overlap as m


def test_index_parse_ignores_script_and_short_local_route_numbers():
    html=('<html><body>Official Frog and Toad Survey Maps '+
          ''.join(f'<div>County 360{n:03d} 10 No <a href="/media/{n}">Frog and Toad Survey Map, Route ID 360{n:03d}</a></div>'
                 for n in range(101,132))+
          '<div>Frog and Toad Survey Map, Route ID 99</div>'+
          '<script>Frog and Toad Survey Map, Route ID 360999</script></body></html>')
    a=m.parse_index(html.encode('utf-8'))
    assert len(a)==31
    assert a[0]=='360101' and '360999' not in a


def test_index_without_official_routes_fails_closed():
    with pytest.raises(ValueError,match='too small'):
        m.parse_index(b'<html><body>'+b'hello'*1000+b'</body></html>')


def metadata():
    runs=[];stops=[];coords=[]
    for route in ('360101','360102'):
        for year in (2008,2009):
            rid=f'{route}_{year}'
            runs.append(dict(RunID=rid,State='Iowa',RouteNumber=route,RouteType='1',RunNumber='1',
                 UnifiedProtocol='1',SurveyYear=str(year),SurveyDate=f'05/18/{year}',
                 DaysSinceRain='1',TempScale='C'))
            for i in range(1,11):
                stops.append(dict(RunID=rid,SiteID=f'{route}_s{i}',StopNumber=str(i),SkippedStop='0',AirTemp='18'))
        for i in range(1,11):
            coords.append(dict(RouteNumber=route,SiteID=f'{route}_s{i}',lat=42+i*.001,lon=-92-i*.001))
    return pd.DataFrame(runs),pd.DataFrame(stops),pd.DataFrame(coords)


def test_only_complete_original_iowa_routes_count():
    a,b,c=metadata()
    published={f'360{n:03d}' for n in range(102,132)}
    got=m.overlap(a,b,c,published)
    assert got['n_standardized_2001_2015_iowa_naamp_routes']==2
    assert got['n_dnr_routes_matching_standardized_naamp_iowa_cohort']==1
    assert got['n_dnr_routes_matching_all_usgs_coordinate_route_ids']==1
    assert got['first_metadata_only_eligible_match']=='360102'
    assert got['standardized_cohort_overlap_routes'][0]['n_years']==2
    assert got['n_historical_field_sites_independently_verified']==0


def test_short_routes_rejected():
    a,b,c=metadata()
    with pytest.raises(ValueError,match='Malformed'):
        m.overlap(a,b,c,{'123'}|{f'360{n:03d}' for n in range(102,132)})


def test_absent_current_route_is_not_rescued_by_outcome():
    a,b,c=metadata()
    published={f'360{n:03d}' for n in range(201,233)}
    got=m.overlap(a,b,c,published)
    assert got['n_dnr_routes_matching_standardized_naamp_iowa_cohort']==0
    assert got['first_metadata_only_eligible_match'] is None
    assert got['frog_counts_csv_read'] is False
