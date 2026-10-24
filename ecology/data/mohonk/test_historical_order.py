import unittest
from ecology.data.mohonk.egg_order_historical_sensitivity import calculate
def egg(day,taxon,count,pond="44"):
    return {"eventDate":day,"decimalLatitude":pond,"decimalLongitude":"-73.0",
            "scientificName":taxon,"lifeStage":"egg","individualCount":str(count)}
WOOD="Lithobates sylvaticus";SPOT="Ambystoma maculatum"
class ArchiveStagePriority(unittest.TestCase):
    def test_positive_only_older_years_not_dry_absences(self):
        rows=[egg("2001-04-01",WOOD,1),egg("2001-04-08",SPOT,2),
              egg("2001-04-15",WOOD,1)]
        out,report=calculate(rows)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]["spotted_minus_wood_first_detection_days"],7)
        self.assertEqual(out[0]["reporting_era"],"positive_only_inconsistent")
        self.assertFalse(out[0]["original_absence_assumed"])
    def test_no_egg_stage_without_both_species(self):
        out,report=calculate([egg("1999-03-01",WOOD,1)])
        self.assertEqual(len(out),0)
    def test_report_eras_and_visit_thresholds_predeclared(self):
        _,report=calculate([egg("2020-03-01",WOOD,1),egg("2020-03-08",SPOT,1)])
        self.assertEqual(len(report["summary_by_era_and_visit_threshold"]),12)
        self.assertTrue(report["no_phenological_climate_trend_test"])

if __name__=="__main__":unittest.main()
