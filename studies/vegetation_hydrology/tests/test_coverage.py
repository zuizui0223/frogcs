"""Tests: calendar counts never use frog-outcome data."""
import importlib.util
import unittest
from pathlib import Path

p=Path(__file__).resolve().parents[1]/"scripts"/"audit_calendar_coverage.py"
spec=importlib.util.spec_from_file_location("coverage",p)
coverage=importlib.util.module_from_spec(spec)
spec.loader.exec_module(coverage)
def row(site,run,date,state="VA",route="01"):
    return {"State":state,"RouteNumber":route,"SiteID":site,"RunID":run,
            "SurveyYear":date[:4],"SurveyDate":date}
class TestCoverage(unittest.TestCase):
    def test_visit_site_year_distinction(self):
        x=[row("A","one","2001-06-01"),row("A","two","2001-07-01"),
           row("A","three","2002-06-01"),row("B","four","2001-07-01")]
        sy,r=coverage.summarize(x)
        self.assertEqual((r["total_station_visits"],r["unique_physical_sites"],
                          r["unique_site_years"],r["sites_observed_ge_2_years"]),(4,2,3,1))
        self.assertEqual([v["unique_site_years"] for v in sy],[2,1])
        self.assertFalse(r["frog_outcomes_accessed"])
    def test_duplicate_event_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            coverage.summarize([row("A","one","2001-06-01")]*2)
    def test_cross_state_identity_rejected(self):
        with self.assertRaisesRegex(ValueError,"cross State"):
            coverage.summarize([row("A","one","2001-06-01"),
                                row("A","two","2002-06-01",state="MD")])
if __name__=="__main__": unittest.main()
