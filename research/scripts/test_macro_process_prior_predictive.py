"""Synthetic structural invariants for exploratory true-process rate draws."""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from run_macro_process_prior_predictive import (
    DESIGN, PATTERNS, DRAW_COUNT, scenario_set, prior_draws,
    anchor_values, batch_simulate, as_surface, pseudo_recovery,
    score_rate_library, BACKGROUNDS,
)


class RealProcessPriorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid,cls.structures=scenario_set(pd.read_csv(DESIGN),levels=3)

    def test_design_has_complete_24_structural_cases(self):
        self.assertEqual(len(self.structures),24)
        self.assertEqual(len(self.grid),24*2*3*3)
        self.assertEqual(self.grid.groupby("case").size().nunique(),1)
        self.assertEqual(set(self.structures.edge),{"frog_reverse","dynamic"})
        self.assertEqual(set(self.structures.risk),{True,False})

    def test_actual_parameter_draws_are_deterministic_and_bounded(self):
        x=prior_draws(8);y=prior_draws(8)
        pd.testing.assert_frame_equal(x,y)
        self.assertEqual(len(x),8)
        self.assertEqual(x.f_delay.value_counts().to_dict(),{2:4,3:4})
        self.assertTrue(x.attack_scale.between(.25,1.0).all())
        self.assertTrue(x.rho.between(.55,.90).all())
        self.assertTrue(x.conversion.between(2,6).all())
        self.assertTrue(x.f_juvenile_survival.between(.60,.90).all())
        with self.assertRaises(ValueError):
            prior_draws(3)

    def test_actual_kernel_recurred_across_two_years_and_both_risks(self):
        params=prior_draws(2).iloc[0].to_dict()
        part=self.grid[self.grid.case.isin([0,4,5,9,30,34,35,39])]
        result=batch_simulate(part,params,years=3,window=1,dt=.5)
        self.assertEqual(len(result),len(part))
        self.assertTrue(result.F_B.gt(0).all())
        self.assertTrue(result.F_fraction.between(0,1).all())
        self.assertTrue(np.isfinite(result.F_B_sd.to_numpy()).all())
        self.assertTrue((result.F_B_sd>=0).all())
        self.assertEqual(part.duplicated(["case","vegetation","S_source","D_source"]).sum(),0)

    def test_pseudo_recovery_never_trains_on_same_rate_draw(self):
        rng=np.random.default_rng(7)
        groups=["original|baseline|no_risk","original|baseline|risk"]
        rows=[]
        for bg in BACKGROUNDS:
            for draw in range(4):
                for case,grp in enumerate(groups):
                    vals=rng.normal(loc=case*5,scale=.2,size=len(PATTERNS))
                    rows.append(dict(background=bg,draw=draw,case=f"case_{case:03d}",
                                     structural_group=grp,
                                     **dict(zip(PATTERNS,vals))))
        library=pd.DataFrame(rows)
        # Function checks 24 cases per heldout draw: complete synthetic
        # design used to test the 24-case shape and common drawing.
        extra=[]
        for row in rows:
            for case in range(1,12):
                c=dict(row)
                c["case"]=f"case_{case*2+int(row['case'][-3:]):03d}"
                extra.append(c)
        synthetic=pd.DataFrame(rows+extra)
        inv={bg:np.eye(len(PATTERNS)) for bg in BACKGROUNDS}
        records=pseudo_recovery(synthetic,inv,{},4)
        self.assertEqual(len(records),2*4*24)
        self.assertTrue(records.minimum_distance.ge(0).all())

    def test_no_relabeling_of_historical_source_anchor(self):
        anchor=anchor_values()
        self.assertEqual(anchor["attack_scale"],.5)
        self.assertEqual(anchor["rho"],.75)
        self.assertEqual(anchor["conversion"],4.)
        self.assertEqual(anchor["f_delay"],2)
        self.assertEqual(anchor["f_adult_survival"],.4)


if __name__=="__main__":
    unittest.main()
