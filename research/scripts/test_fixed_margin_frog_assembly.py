#!/usr/bin/env python3
"""Synthetic tests for prespecified degree-conditioned frog co-occurrence."""
import copy
import itertools
import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import fixed_margin_frog_assembly as target

def margins(bits, nsites=10):
    return [int(x).bit_count() for x in bits], [
        sum((x>>j)&1 for x in bits) for j in range(nsites)]

class CurveballTests(unittest.TestCase):
    def test_row_col_margins_preserved_after_many_trades(self):
        before=[0b0000001111,0b0011100100,0b0011011000,0b0110000111]
        a=before.copy();r=random.Random(31)
        r0,c0=margins(before)
        effective=0
        for i in range(600):
            effective+=target.curveball_trade(a,r)
            self.assertEqual(margins(a),(r0,c0))
        self.assertGreater(effective,0)
    def test_total_pairwise_overlap_is_fixed(self):
        b=[0b1111,0b1100,0b1010,0b0101]
        expected=target.total_pairwise_overlap(b)
        r=random.Random(50)
        for _ in range(200):
            target.curveball_trade(b,r)
            self.assertEqual(target.total_pairwise_overlap(b),expected)
            self.assertEqual(expected,sum(n*(n-1)//2 for n in margins(b)[1]))
    def test_checkerboard_cscore_can_change_despite_fixed_margins(self):
        start=[0b0011,0b0101,0b0110,0b1100]
        r0,c0=margins(start)
        values=set()
        a=start.copy();r=random.Random(51)
        for _ in range(500):
            target.curveball_trade(a,r)
            values.add(target.cscore(a))
            self.assertEqual(margins(a),(r0,c0))
        self.assertGreater(len(values),1)
    def test_cscore_empty_or_one_species_is_nonestimable(self):
        self.assertIsNone(target.cscore([]))
        self.assertIsNone(target.cscore([0b1]))
    def test_deterministic_chains(self):
        a=[0b0011,0b0101,0b0110,0b1100]
        x=target.null_score(a,"PSEUDO_RUN")
        y=target.null_score(a,"PSEUDO_RUN")
        self.assertEqual(x,y)
        self.assertEqual(x["n_draws"],2*target.DRAWS_PER_CHAIN)
    def test_null_structural_invariance_flagged(self):
        b=[0b1,0b1,0b1]
        x=target.null_score(b,"STATIC")
        self.assertFalse(x["informative"])
        self.assertEqual(x["null_sd"],0)
    def test_wet_minus_dry_sign_is_explicit(self):
        self.assertAlmostEqual(target.wet_minus_dry(3,1),2)
        self.assertAlmostEqual(target.wet_minus_dry(1,3),-2)
    def test_route_equal_weight(self):
        route_rows=[("a",3.0),("b",-1.0),("b",-1.0),("b",-1.0)]
        self.assertAlmostEqual(target.route_equal_mean(route_rows),1.0)
    def test_gate_not_relaxed_to_save_null_result(self):
        self.assertFalse(target.coverage_gate(199,80))
        self.assertFalse(target.coverage_gate(200,79))
        self.assertTrue(target.coverage_gate(200,80))
    def test_zeros_not_implicitly_species_detections(self):
        raw={str(i):set() for i in range(1,11)}
        raw["1"]={"Hyla cinerea"}
        raw["3"]={"Acris crepitans","Hyla cinerea"}
        out=target.incidence_masks([str(i) for i in range(1,11)],raw)
        self.assertEqual(out,{"Acris crepitans":0b100,"Hyla cinerea":0b101})
    def test_observed_margins_have_ten_stops(self):
        with self.assertRaisesRegex(ValueError,"ten"):
            target.incidence_masks(["1"],{"1":{"Hyla cinerea"}})
    def test_complex_taxon_names_are_not_split(self):
        raw={str(i):set() for i in range(1,11)}
        raw["1"]={"Hyla chrysoscelis/versicolor complex"}
        out=target.incidence_masks(sorted(raw,key=int),raw)
        self.assertIn("Hyla chrysoscelis/versicolor complex",out)
    def test_one_sampled_run_sensitivities_are_not_fake_pair(self):
        self.assertEqual(target.PRIMARY_METRIC,"degree_conditioned_checkerboard_C")
    def test_constant_columns_do_not_make_finite_association(self):
        self.assertIsNone(target.cscore([0,0,0]))
    def test_seeds_differ_by_run_and_chain(self):
        seeds={target.seed_for(str(i),chain) for i in range(5) for chain in (0,1)}
        self.assertEqual(len(seeds),10)
    def test_survey_order_does_not_change_pair_null_margins(self):
        a=[0b001011,0b011101,0b101100,0b110001]
        b=list(reversed(a))
        self.assertAlmostEqual(target.cscore(a),target.cscore(b))

if __name__=="__main__":
    unittest.main()
