"""Unit tests for paired 80-y ABC importance-prior sensitivity, no new field claims."""
import unittest

import numpy as np
import pandas as pd

from abc_prior_density_stress import (
    N_DRAWS,SCENARIOS,importance_weights,matrix_of_independent_rate_draws,
    weighted_summary
)


def fake_prior():
    rng=np.random.default_rng(31415)
    n=N_DRAWS
    return pd.DataFrame(dict(
        draw=np.arange(n),
        attack_scale=np.exp(np.linspace(np.log(.2501),np.log(.9999),n)),
        s_growth_multiplier=rng.uniform(.75,1.25,n),
        d_growth_multiplier=rng.uniform(.75,1.25,n),
        rho=rng.uniform(.55,.9,n),
        conversion=rng.uniform(2.,6.,n),
        f_juvenile_survival=np.linspace(.6001,.8999,n),
        f_adult_survival=rng.uniform(.25,.60,n),
        f_delay=np.r_[np.full(n//2,2),np.full(n//2,3)]))


class ABCDensitySensitivityTests(unittest.TestCase):
    def test_9_declared_scenarios_nonnegative_normalized_and_no_leakage(self):
        table,w=importance_weights(fake_prior())
        self.assertEqual(set(w),set(SCENARIOS))
        self.assertEqual(len(table),len(SCENARIOS)*N_DRAWS)
        for k,a in w.items():
            self.assertEqual(len(a),N_DRAWS)
            self.assertTrue(np.isfinite(a).all())
            self.assertTrue((a>=0).all())
            self.assertAlmostEqual(a.sum(),N_DRAWS)
        np.testing.assert_array_equal(w["original"],np.ones(N_DRAWS))
        p=fake_prior()
        self.assertGreater(w["attack_uniform"][-1],
                           w["attack_uniform"][0])
        self.assertGreater(w["attack_favors_weak"][0],
                           w["attack_favors_weak"][-1])
        self.assertGreater(w["frog_juvenile_favors_high"][-1],
                           w["frog_juvenile_favors_high"][0])
        self.assertTrue(np.all(w["maturity_favors_2y"][:128]==1.5))
        self.assertTrue(np.all(w["maturity_favors_2y"][128:]==.5))

    def test_weighted_class_probs_are_paired_and_replay_baseline(self):
        n=N_DRAWS
        a=np.zeros((n,3))
        a[:65,0]=1.
        a[:48,1]=1.
        a[:6,2]=1.
        base=np.ones(n)
        idx=np.random.default_rng(177).integers(0,n,size=(99,n))
        rates,shares,ess_accepted,ess,b_rates,b_share=weighted_summary(a,base,idx)
        np.testing.assert_allclose(rates,[65/256,48/256,6/256])
        np.testing.assert_allclose(shares,[65/119,48/119,6/119])
        self.assertAlmostEqual(ess,256)
        np.testing.assert_allclose(ess_accepted,[65,48,6])
        self.assertEqual(b_rates.shape,(99,3))
        self.assertEqual(b_share.shape,(99,3))
        np.testing.assert_allclose(b_share.sum(axis=1),1.)

    def test_weighted_acceptance_correctly_uses_shared_full_draw_ids(self):
        n=N_DRAWS
        a=np.zeros((n,2))
        a[:n//2,0]=1.
        a[n//2:,1]=1.
        p=fake_prior()
        _,w=importance_weights(p)
        ra,sh,*_=weighted_summary(a,w["maturity_favors_2y"])
        np.testing.assert_allclose(ra,[.75,.25])
        np.testing.assert_allclose(sh,[.75,.25])
        rb,other,*_=weighted_summary(a,w["maturity_favors_3y"])
        np.testing.assert_allclose(rb,[.25,.75])
        self.assertTrue(np.allclose(other,[.25,.75]))

    def test_wrong_prior_support_is_rejected(self):
        p=fake_prior()
        for name,value in (("attack_scale",0.),("f_juvenile_survival",1.),
                           ("f_delay",4)):
            wrong=p.copy();wrong.loc[0,name]=value
            with self.assertRaises(ValueError):
                importance_weights(wrong)
        with self.assertRaises(ValueError):
            importance_weights(p.iloc[:-1])

    def test_source_reverse_edge_never_counted_as_independent_prior(self):
        rows=[]
        for i in range(12):
            for draw in range(N_DRAWS):
                for edge in (0,1):
                    rows.append(dict(structure_id=f"class_{i:02d}",
                                     context="original" if i<4 else "other",
                                     family="baseline" if i%2 else "shared_both",
                                     risk=bool(i%2),
                                     draw=draw,reverse_on=edge,
                                     matches_log=bool(draw<(i+1)*3),
                                     matches_raw=bool(draw<(i+1)*2)))
        source=pd.DataFrame(rows)
        ids,classes,A,grouped=matrix_of_independent_rate_draws(source,"log")
        self.assertEqual(len(classes),12)
        self.assertEqual(A.shape,(N_DRAWS,12))
        self.assertEqual(len(grouped),N_DRAWS*12)
        self.assertTrue(np.isin(A,[0,1]).all())
        self.assertEqual(int(A[:,0].sum()),3)
        broken=source[~((source.structure_id=="class_00")&
                        (source.draw==0)&(source.reverse_on==1))]
        with self.assertRaises((AssertionError,ValueError)):
            matrix_of_independent_rate_draws(broken,"log")


if __name__=="__main__":
    unittest.main()
