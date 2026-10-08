import importlib.util
from pathlib import Path
import pandas as pd
import pytest
sp=importlib.util.spec_from_file_location("coordinate_audit",Path(__file__).resolve().parents[1]/"scripts"/"audit_coordinates.py")
mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)


def example():
    return pd.DataFrame([
        ("270107","4501",37.2,-83.3),
        ("270107","4502",37.21,-83.31),
        ("270107","4507",37.22,83.302),
        ("880113","1",37.31,-77.1),
        ("880113","2",37.32,-77.11),
        ("880113","3",39.12925,-77.11),
        ("880113","4",37.33,-77.12),
        ("123","a",34.5,-80.0),
        ("123","a",34.5,-80.0),
        ("123","b",34.51,-80.01),
    ],columns=["RouteNumber","SiteID","lat","lon"])


def test_catches_known_wrong_sign_and_isolated_site():
    table, receipt=mod.audit(example())
    assert table.set_index("site_id").loc["4507","geometry_qc_status"]=="failed_domain"
    assert table.set_index("site_id").loc["3","geometry_qc_status"]=="review_geometry"
    assert receipt["coordinates_independently_verified"]==0
    assert set(table.coordinate_qc_status)=={"UNVERIFIED_DO_NOT_EXTRACT"}


def test_identical_duplicates_not_conflict():
    table,_=mod.audit(example())
    a=table.query("route_id=='123' and site_id=='a'").iloc[0]
    assert a.source_rows==2 and a.distinct_locations==1


def test_conflicting_duplicates_fail():
    d=example()
    d.loc[len(d)]=["123","a",38.0,-81.0]
    table,_=mod.audit(d)
    assert table.query("route_id=='123' and site_id=='a'").iloc[0].geometry_qc_status=="conflicting_site_coordinates"


def test_geometry_pass_not_independent_verification():
    table,_=mod.audit(example())
    assert table.query("route_id=='123' and site_id=='b'").iloc[0].geometry_qc_status=="pass_unverified"
    assert (table.coordinate_qc_status != "verified_external").all()
