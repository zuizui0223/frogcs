"""No biological false positive: G5 constrained source score and 2×2 source geometry."""
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from g5_source_constrained_acoustic_holdout_20261106 import (
    constrained_train_predict,read_corner_source,features_by_background,
    CORNERS
)
from g4_field_model_alignment_8corner_audit_20261106 import predictor_basis


class MechanismConstrainedFieldBridgeTests(unittest.TestCase):
    def test_original_eight_corner_source_is_saturated_empirical_interaction(self):
        rng=np.random.default_rng(20261106)
        o=rng.random(500)
        s=rng.random(500)
        v=rng.integers(0,2,500)
        B=predictor_basis(o,s,v)
        coef=np.array([1.,.2,-.3,.4,-.5,.7,.21,.3])
        mechanism=B[:,4:]@coef[4:]
        self.assertEqual(np.linalg.matrix_rank(np.c_[B,mechanism]),8)
        self.assertLess(np.max(np.abs(B@np.linalg.lstsq(B,mechanism,rcond=None)[0]-mechanism)),1e-12)

    def test_original_source_corner_manifest_has_no_outcome_based_selection(self):
        rows=[]
        for arm in ("00","11"):
            for v,s,o in CORNERS:
                rows.append(dict(arm=arm,vegetation=v,caudata=s,odonata=o,
                    mean_log_F_B=float(v+s-o+(.5 if arm=="11" else -.5)*s*o)))
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"source.csv"
            pd.DataFrame(rows).to_csv(p,index=False)
            x=read_corner_source(p)
            self.assertEqual(set(x),{"00","11"})
            self.assertTrue(np.isfinite(x["11"]).all())

    def test_observation_slope_cannot_reversely_fit_model_predator_assumption(self):
        rng=np.random.default_rng(20261106)
        base=rng.normal(size=(400,3))
        proxy=rng.normal(size=400)
        x=np.c_[base,proxy]
        n=np.full(400,10)
        k=np.rint(10/(1+np.exp(proxy))).astype(int) # calls ANTI-correlate with model F
        p,coef=constrained_train_predict(x[:300],k[:300],n[:300],x[300:])
        self.assertGreaterEqual(coef,-1e-12)
        self.assertTrue(np.all(np.isfinite(p)))
        self.assertTrue(np.all((p>0)&(p<1)))


if __name__=="__main__":
    unittest.main()
