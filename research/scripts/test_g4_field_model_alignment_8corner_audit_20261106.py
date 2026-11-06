"""Small pure regression tests: model-surface cannot add independent saturated predictors."""
import unittest

import numpy as np
from g4_field_model_alignment_8corner_audit_20261106 import (
    CORNERS, predictor_basis, surface_interpolation, original_rank01,
)


class OriginalFieldModelAlignmentTests(unittest.TestCase):
    def test_all_eight_original_corners_and_bilinear_source_reconstruction(self):
        rng=np.random.default_rng(20261106)
        values={c:float(rng.normal()) for c in CORNERS}
        # Explicit corner values are preserved verbatim.
        for v,s,o in CORNERS:
            a=surface_interpolation(values,[o],[s],[v])
            np.testing.assert_allclose(a,[values[(v,s,o)]],atol=1e-13,rtol=0)
        o=rng.random(1000);s=rng.random(1000);v=rng.integers(0,2,1000)
        observed=surface_interpolation(values,o,s,v)
        x=predictor_basis(o,s,v)
        b,*_=np.linalg.lstsq(x,observed,rcond=None)
        self.assertEqual(np.linalg.matrix_rank(x),8)
        self.assertLessEqual(float(np.max(np.abs(x@b-observed))),1e-12)
        # A simulated feature does not add an independent O/S/V column.
        self.assertEqual(np.linalg.matrix_rank(np.c_[x,observed]),8)

    def test_source_ranks_not_adult_breeding_dates(self):
        a=original_rank01([10,20,30,40,50])
        np.testing.assert_allclose(a,[0,.25,.5,.75,1],atol=1e-12)
        self.assertEqual(len(CORNERS),8)

    def test_reject_nonbinary_or_missing_original_source_grid(self):
        v={c:1. for c in CORNERS}
        with self.assertRaises(AssertionError):
            surface_interpolation(v,{0:1.},[.1],[0])
        with self.assertRaises(AssertionError):
            surface_interpolation({(0,0,0):1.},[.1],[.1],[0])
        with self.assertRaises(AssertionError):
            surface_interpolation(v,[.1],[.1],[2])


if __name__=="__main__":
    unittest.main()
