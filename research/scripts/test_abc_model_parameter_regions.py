"""Pure synthetic checks for genuine-ABC accepted-rate quartiles and pairing."""
import unittest
import numpy as np
import pandas as pd

from model_native_abc_rf import PRIOR_PARAMS
from abc_model_parameter_regions import (
    ORIGINAL_BASELINE, independent_prior_weights, quartile_prior_codes,
    all_parameter_regions,pair_refuge_original,N_PRIOR_DRAWS
)


def synthetic_prior_and_signs():
    n=N_PRIOR_DRAWS
    rng=np.random.default_rng(330)
    prior=pd.DataFrame({"draw":np.arange(n),
        "attack_scale":np.linspace(.25,1,n),
        "s_growth_multiplier":rng.permutation(np.linspace(.75,1.25,n)),
        "d_growth_multiplier":rng.permutation(np.linspace(.75,1.25,n)),
        "rho":rng.permutation(np.linspace(.55,.9,n)),
        "conversion":rng.permutation(np.linspace(2,6,n)),
        "f_juvenile_survival":rng.permutation(np.linspace(.6,.9,n)),
        "f_adult_survival":rng.permutation(np.linspace(.25,.6,n)),
        "f_delay":np.tile([2,3],n//2)})
    classes=[f"model_{i:02d}" for i in range(10)]+list(ORIGINAL_BASELINE)
    rows=[]
    for cls in classes:
        for i in range(n):
            if cls==ORIGINAL_BASELINE[0]:
                val=(i<64)
            elif cls==ORIGINAL_BASELINE[1]:
                val=(i<48)
            else:
                val=(i<32)
            for rev in (0,1):
                rows.append(dict(structure_id=cls,
                                 context="original",family="baseline",
                                 risk=bool(cls==ORIGINAL_BASELINE[1]),
                                 draw=i,reverse_on=rev,
                                 matches_log=bool(val),matches_raw=bool(val)))
    return pd.DataFrame(rows),prior


class TruePriorRegionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference,cls.prior=synthetic_prior_and_signs()

    def test_reverse_on_off_are_one_independent_prior_vector(self):
        weights=independent_prior_weights(self.reference,"log")
        self.assertEqual(len(weights),12*N_PRIOR_DRAWS)
        self.assertEqual(int(weights[
            weights.structure_id==ORIGINAL_BASELINE[0]].accepted_weight.sum()),64)
        self.assertTrue(weights.n_reverse.eq(2).all())
        self.assertTrue(weights.accepted_weight.isin([0,1]).all())

    def test_prior_bins_fixed_not_fitted_from_accepted_parameter_values(self):
        for param in PRIOR_PARAMS:
            bins=quartile_prior_codes(self.prior,param)
            vals=pd.Series(bins)
            if param=="f_delay":
                self.assertEqual(vals.value_counts().sort_index().to_dict(),{2:128,3:128})
            else:
                self.assertEqual(vals.value_counts().sort_index().to_dict(),
                                 {0:64,1:64,2:64,3:64})
        bad=self.prior.iloc[:-1]
        with self.assertRaises(ValueError):
            quartile_prior_codes(bad,"attack_scale")

    def test_original_accepted_lower_attack_quartile_enrichment(self):
        q,s,w=all_parameter_regions(self.reference,self.prior)
        self.assertEqual(len(s),12*len(PRIOR_PARAMS)*2)
        self.assertEqual(len(q),12*(len(PRIOR_PARAMS)-1)*4*2+12*2*2)
        k=q[(q.scale=="log") &
            (q.structure_id==ORIGINAL_BASELINE[0]) &
            (q.parameter=="attack_scale")].sort_values("prior_bin")
        self.assertEqual(k.n_accepted_effective.tolist(),[64.,0.,0.,0.])
        self.assertAlmostEqual(k.enrichment_vs_class_overall.iloc[0],4.)
        self.assertEqual(k.n_prior_draws.tolist(),[64]*4)

    def test_matched_refuge_bootstrap_preserves_shared_draws(self):
        weights=pd.concat([
            independent_prior_weights(self.reference,scale).assign(scale=scale)
            for scale in ("log","raw")
        ],ignore_index=True)
        r,t=pair_refuge_original(weights,n_boot=99)
        self.assertEqual(len(r),N_PRIOR_DRAWS*2)
        self.assertEqual(len(t),2)
        for row in t.itertuples():
            self.assertEqual(row.n_both,48)
            self.assertEqual(row.n_off_only,16)
            self.assertEqual(row.n_on_only,0)
            self.assertEqual(row.n_neither,192)
            self.assertAlmostEqual(row.mean_off_minus_on,16/N_PRIOR_DRAWS)
            self.assertGreater(row.paired_bootstrap_95_low,0.)

    def test_discordant_reversal_weight_is_not_double_counted(self):
        modified=self.reference.copy()
        selection=(modified.structure_id==ORIGINAL_BASELINE[0]) & (modified.draw==100) & (modified.reverse_on==1)
        modified.loc[selection,"matches_log"]=True
        weights=independent_prior_weights(modified,"log")
        w=weights[(weights.structure_id==ORIGINAL_BASELINE[0])&(weights.draw==100)]
        self.assertEqual(float(w.accepted_weight.iloc[0]),.5)
        self.assertEqual(int(w.reverse_acceptance_difference.iloc[0]),1)
        self.assertEqual(float(weights[weights.structure_id==ORIGINAL_BASELINE[0]].accepted_weight.sum()),64.5)


if __name__=="__main__":
    unittest.main()
