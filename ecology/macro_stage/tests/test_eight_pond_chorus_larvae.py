import unittest
from ecology.macro_stage.scripts.reanalyse_eight_pond_chorus_larvae import (
    excel_date, STAGE_CODES, hypergeom, circular, enemy_reference
)
class OriginalEightPondEcology(unittest.TestCase):
    def test_original_dryad_taxon_codes_are_explicit(self):
        self.assertEqual(STAGE_CODES["R.cla"],"RCL")
        self.assertEqual(STAGE_CODES["H.ver"],"HV")
        self.assertEqual(STAGE_CODES["B.woo"],"BW")
        self.assertEqual(len(STAGE_CODES),11)
    def test_excel_original_epoch(self):
        self.assertEqual(str(excel_date(36892)),"2001-01-01")
    def test_conditional_week_stage_overlap_null(self):
        a=[True,False,False];b=[True,False,False]
        self.assertEqual(len(hypergeom(a,b)),2)
        self.assertAlmostEqual(hypergeom(a,b)[1],1/3)
        self.assertAlmostEqual(circular(a,b)[1],1/3)
    def test_both_guild_stages_no_assumed_predation(self):
        rows=[{"pond":1,"year":2002,"date":x,"frog_larvae":a,"Naiad":b}
              for x,a,b in ((1,2,0),(2,0,1),(3,1,1))]
        r,g=enemy_reference(rows,"Naiad")
        self.assertEqual(r["fixed"]["observed"],1)
        self.assertAlmostEqual(r["fixed"]["expected"],4/3,places=6)
        self.assertEqual(g[0]["partner"],"Naiad")
if __name__=="__main__":unittest.main()
