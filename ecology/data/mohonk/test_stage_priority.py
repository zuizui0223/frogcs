import unittest
from ecology.data.mohonk.analyze_egg_stage_priority import compute,pond_cluster_ci

def rec(day,taxon,stage,count):
    return {"eventDate":day,"decimalLatitude":"41.7","decimalLongitude":"-74.1",
            "scientificName":taxon,"lifeStage":stage,"individualCount":str(count)}
WOOD="Lithobates sylvaticus"
SPOT="Ambystoma maculatum"
JEFF="Ambystoma jeffersonianum"
class StagePrioritySafety(unittest.TestCase):
    def test_order_and_cooccurrence_same_pond_date(self):
        r=[rec("2019-03-01",WOOD,"egg",4),rec("2019-03-01",SPOT,"egg",0),
           rec("2019-03-01",WOOD,"tadpole",0),rec("2019-03-01",SPOT,"tadpole",0),
           rec("2019-03-08",WOOD,"egg",1),rec("2019-03-08",SPOT,"egg",3),
           rec("2019-03-08",WOOD,"tadpole",2),rec("2019-03-08",SPOT,"tadpole",0)]
        s,by,_y,_e=compute(r)
        self.assertEqual(s["pondyears"],1)
        self.assertEqual(s["wood_frog_egg_first"],1)
        self.assertEqual(s["median_gap_days_spotted_minus_wood"],7)
        self.assertEqual(s["pond_dates_frog_tadpole_and_spotted_egg_codetected"],1)
        self.assertEqual(s["pond_dates_spotted_salamander_larvae_recorded_positive"],0)
    def test_missing_stage_row_not_assumed_assessed(self):
        r=[rec("2020-04-01",WOOD,"egg",1),rec("2020-04-01",SPOT,"egg",1)]
        s,_,_,events=compute(r)
        self.assertEqual(s["pond_dates_both_four_target_stages_assessed"],0)
        self.assertFalse(events[0]["frog_tadpole_assessed"])
    def test_strict_first_positive_earlier_salamander(self):
        r=[rec("2018-03-01",WOOD,"egg",0),rec("2018-03-01",SPOT,"egg",4),
           rec("2018-03-10",WOOD,"egg",1),rec("2018-03-10",SPOT,"egg",2)]
        s,_,_,_=compute(r)
        self.assertEqual(s["spotted_salamander_egg_first"],1)
    def test_duplicate_stage_entries_collapse_not_sum(self):
        r=[rec("2019-03-01",WOOD,"egg",0),rec("2019-03-01",WOOD,"egg",1),
           rec("2019-03-01",SPOT,"egg",1)]
        s,_,_,_=compute(r)
        self.assertEqual(s["duplicate_target_stage_day_keys"],1)
        self.assertEqual(s["same_first_detection_date"],1)

if __name__=="__main__":unittest.main()
