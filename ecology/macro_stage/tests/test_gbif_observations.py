import unittest
from ecology.macro_stage.scripts.harvest_gbif_observations import STAGE_CLASSES,REGIONS_SELECTED,reduced_record,COMMON_INAT_GBIF_DATASET

class TestOriginalSpeciesStageData(unittest.TestCase):
    def test_taxa_and_strata_fixed(self):
        self.assertEqual(len(REGIONS_SELECTED),5)
        self.assertEqual(len(STAGE_CLASSES),5)
        self.assertEqual(STAGE_CLASSES[2],("salamander_egg",953,"Egg"))
    def test_preserve_week_date_and_reduce_coordinates(self):
        row={"datasetKey":COMMON_INAT_GBIF_DATASET,"lifeStage":"Larva",
             "countryCode":"US","decimalLatitude":37.63,"decimalLongitude":-88.27,
             "year":2021,"month":3,"day":17,"gbifID":"42","speciesKey":123}
        out=reduced_record(row,"US35_40","frog_larva","Larva","US",35,40)
        self.assertEqual((out["grid_lat_05"],out["grid_lon_05"]),(37.5,-88.5))
        self.assertNotIn("decimalLatitude",out)
    def test_iso_country_filter_rejects_wrong_country(self):
        row={"datasetKey":COMMON_INAT_GBIF_DATASET,"lifeStage":"Larva",
             "countryCode":"CA","decimalLatitude":37.6,"decimalLongitude":-88.2,
             "year":2021,"month":3,"day":17,"gbifID":"44"}
        with self.assertRaisesRegex(ValueError,"countryCode"):
            reduced_record(row,"US35_40","frog_larva","Larva","US",35,40)
    def test_wrong_publisher_excluded(self):
        row={"datasetKey":"NOT-iNaturalist","lifeStage":"Larva",
             "countryCode":"US","decimalLatitude":37,"decimalLongitude":-88,"year":2021,"month":3,"gbifID":"42"}
        with self.assertRaisesRegex(ValueError,"publisher"):
            reduced_record(row,"US35_40","frog_larva","Larva","US",35,40)
if __name__=="__main__":unittest.main()
