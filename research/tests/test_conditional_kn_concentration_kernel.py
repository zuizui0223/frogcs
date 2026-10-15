#!/usr/bin/env python3
"""Synthetic-only exact (total K, route-new N) conditional concentration tests."""
import sys
import unittest
from pathlib import Path
import math

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import conditional_kn_concentration_kernel_v0_1 as model

def toy(s=2,k_by_species=(4,2),qvalue=0.25,linked=False):
    q=np.full((s,10),qvalue,float)
    for i in range(s):
        q[i]+=np.linspace(-0.015,0.015,10)
    wet=np.zeros((s,10),int)
    for i,n in enumerate(k_by_species):
        wet[i,:n]=1
    dry=np.zeros_like(wet)
    link=np.ones((10,10),float)-np.eye(10) if linked else np.zeros((10,10),float)
    return {
        "q":q,"wet":wet,"dry":dry,
        "forest":np.linspace(0.15,0.75,10),
        "prior_strong":(np.arange(s*10).reshape(s,10)%3==0).astype(int),
        "forest_link":link,
        "guild":np.array([i%2 for i in range(s)],float),
        "soil_change_z":0.6,
        "q_response_state":"CI_ge_1","response_state":"CI_ge_1",
        "forest_link_source":"synthetic"
    }

class JointConcentrationTests(unittest.TestCase):
    def test_concentration_not_fixed_by_total_K_or_route_new_N(self):
        data=toy()
        generator=model.build(data)
        rng=np.random.default_rng(1234)
        draws=[generator.draw(rng) for _ in range(350)]
        Cs={model.concentration(y,data["dry"]) for y in draws}
        self.assertGreater(len(Cs),1,
          "Fixing individual species k would incorrectly freeze concentration")
        for y in draws:
            self.assertEqual(int(y.sum()),6)
            self.assertEqual(int((y.sum(axis=1)>0).sum()),2)

    def test_analytical_normalizer_two_route_new_taxa_each_one_stop(self):
        data=toy(k_by_species=(1,1))
        g=model.build(data)
        # N=2 and K=2 forces exactly one site in each of the two taxa.
        a=np.log(data["q"])-np.log1p(-data["q"])
        from scipy.special import logsumexp
        z=float(logsumexp(a[0])+logsumexp(a[1]))
        self.assertAlmostEqual(g.logZ,z,places=11)

    def test_network_pair_energy_changes_concentration_at_constant_K_N(self):
        data=toy(linked=True)
        base=model.build(data,{})
        treated=model.build(data,{"forest_link":1.3})
        rng0=np.random.default_rng(345)
        rng1=np.random.default_rng(345)
        b=np.array([model.concentration(base.draw(rng0),base.dry)
                    for _ in range(380)])
        t=np.array([model.concentration(treated.draw(rng1),treated.dry)
                    for _ in range(380)])
        self.assertGreater(t.mean(),b.mean()+0.6)
        self.assertEqual(base.total_K,treated.total_K)
        self.assertEqual(base.route_new_N,treated.route_new_N)

    def test_zero_forest_links_implies_zero_link_effect(self):
        data=toy(linked=False)
        base=model.build(data,{})
        changed=model.build(data,{"forest_link":20})
        self.assertAlmostEqual(base.logZ,changed.logZ,places=10)
        self.assertAlmostEqual(base.observed_logprob(),changed.observed_logprob(),places=10)

    def test_positive_score_and_posterior_predictive_are_finite(self):
        data=toy(linked=True)
        score=model.heldout_gain(data,{"forest_link":1.0,"site_forest":0.5})
        self.assertTrue(math.isfinite(score["heldout_gain"]))
        self.assertFalse(score["each_species_k_fixed"])
        self.assertTrue(score["not_identical_to_frozen_JAE_conditional_beta"])
        pp=model.posterior_predictive(data,{},draws=70,seed=233)
        self.assertTrue(pp["C_simulation_has_variance"])
        self.assertEqual(pp["K"],6)
        self.assertEqual(pp["N"],2)

    def test_phenology_and_forest_provenance_gates(self):
        data=toy()
        data["q_response_state"]="CI_ge_2"
        with self.assertRaisesRegex(ValueError,"mismatch"):
            model.build(data)
        data["q_response_state"]="CI_ge_1"
        data["forest_link_source"]="geometric_buffer_overlap"
        with self.assertRaisesRegex(ValueError,"not permitted"):
            model.build(data)
        data["forest_link_source"]="synthetic"
        data["q"][0,2]=0.
        with self.assertRaisesRegex(ValueError,"invalid Bernoulli"):
            model.build(data)

    def test_new_route_taxon_constraint_differs_from_total_taxa(self):
        data=toy(s=3,k_by_species=(2,2,0))
        data["dry"][0,0]=1  # taxon 0 was not a route-new taxon
        x=model.build(data)
        self.assertEqual(x.total_K,4)
        self.assertEqual(x.route_new_N,1)
        for y in (x.draw(np.random.default_rng(i)) for i in range(50)):
            self.assertEqual(int(y.sum()),4)
            self.assertEqual(int(((~data["dry"].any(axis=1)) &
                                   y.any(axis=1)).sum()),1)

    def test_conditional_normalizer_is_not_species_fixed_k(self):
        data=toy()
        x=model.build(data)
        self.assertEqual(x.DP.shape[0],3)
        self.assertAlmostEqual(x.observed_logprob(),
             model.heldout_gain(data,{})["baseline_logscore"],places=12)

if __name__=="__main__":unittest.main()
