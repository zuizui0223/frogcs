import unittest
from ecology.macro_stage.scripts.analyze_gbif_observations import do_analysis,MIN_STAGE_YEAR

class RecordLevelStageMacro(unittest.TestCase):
    def test_group_presence_does_not_imply_pond(self):
        row={"region":"US35_40","year":2020,"month":3,"guild_stage":"frog_larva",
             "grid_lat_05":37.0,"grid_lon_05":-87.5,"speciesKey":"123"}
        _,_,_,_,report=do_analysis([row])
        self.assertTrue(report["cannot_claim_pond_level_encounters"])
        self.assertEqual(report["n_stage_annotated_original_observations"],1)
    def test_no_larval_comparison_without_minimum_records(self):
        data=[{"region":"US35_40","year":2020,"month":3,"guild_stage":"frog_larva",
             "grid_lat_05":37.,"grid_lon_05":-87.5,"speciesKey":"123"} for _ in range(10)]
        _,_,fair,_,report=do_analysis(data)
        self.assertEqual(len(fair),0)
        self.assertEqual(MIN_STAGE_YEAR,15)
    def test_same_grid_month_not_same_pond(self):
        a={"region":"US35_40","year":2020,"month":3,"guild_stage":"frog_larva",
            "grid_lat_05":37.,"grid_lon_05":-87.5,"speciesKey":"123"}
        b={**a,"guild_stage":"salamander_egg"}
        _,_,_,grids,report=do_analysis([a,b])
        self.assertEqual(len(grids),1)
        found=next(q for q in report["n_half_degree_grid_year_month_frog_and_partner_observation"] if q["region"]=="US35_40" and q["partner_life_stage"]=="salamander_egg")
        self.assertEqual(found["both_positive_grid_year_month"],1)
if __name__=="__main__":unittest.main()
