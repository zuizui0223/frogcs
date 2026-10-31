"""Structural identifiability test: external-immigration OFF collapses rho and
conversion into their PRODUCT in the original frogcs finite-N model.

This is a mathematical source property, NOT an inference from eight LHS
parameter simulation successes. With external immigration enabled rho also
enters the (1-rho) external supply term, so the same-product invariance
should fail when external arrivals are allowed.
"""
import unittest
import numpy as np

from finite_n_source_cohort_bridge import (
    annual_conditional_means, finite_annual_update,
    simulate_finite_group,
)
from rate_axis_synthetic_growth_rescue_80y import original_rate_factorial


class RhoConversionProductIdentifiability(unittest.TestCase):
    def fixture(self):
        n=np.ones((1,8,3),dtype=int)*5
        due=np.ones((1,8,3),dtype=int)*3
        survive=np.broadcast_to([.4,.5,0.],n.shape)
        juvenile=np.broadcast_to([.8,.8,.8],n.shape)
        delays=np.broadcast_to([2,2,1],n.shape)
        source=np.ones(n.shape,dtype=float)
        return n,due,survive,juvenile,delays,source

    def test_conditional_local_recruitment_has_product_symmetry(self):
        n,due,s,j,delay,source=self.fixture()
        shape=(1,8,1)
        rho_a=np.full(shape,.25); conv_a=np.ones(n.shape)*4.
        rho_b=np.full(shape,.5); conv_b=np.ones(n.shape)*2.
        a=annual_conditional_means(n/3,due/3,s,rho_a,conv_a,j,delay,source,immigrants=False)
        b=annual_conditional_means(n/3,due/3,s,rho_b,conv_b,j,delay,source,immigrants=False)
        for x,y in zip(a,b):
            np.testing.assert_array_equal(x,y)
        # External source destroys structural equivalence, as documented.
        aa=annual_conditional_means(n/3,due/3,s,rho_a,conv_a,j,delay,source,immigrants=True)
        bb=annual_conditional_means(n/3,due/3,s,rho_b,conv_b,j,delay,source,immigrants=True)
        np.testing.assert_array_equal(aa[1],bb[1])
        self.assertGreater(float(np.max(np.abs(aa[2]-bb[2]))),.1)

    def test_entire_stochastic_annual_population_draw_is_equal(self):
        n,due,s,j,delay,source=self.fixture()
        outputs=[]
        for rho,conversion in ((.25,4.),(.5,2.)):
            out=finite_annual_update(
                n,due,s,np.full((1,8,1),rho),np.ones(n.shape)*conversion,
                j,delay,source,np.random.default_rng(20261031),
                scale=3,movement="both",transfer=.15,immigration=False
            )
            outputs.append(out)
        np.testing.assert_array_equal(outputs[0][0],outputs[1][0])
        for k in outputs[0][1]:
            np.testing.assert_array_equal(outputs[0][1][k],outputs[1][1][k])

    def test_four_year_original_seasonal_source_invariance(self):
        original=original_rate_factorial(0)
        group=original[
            original.context.eq("original")&
            original.plant_model.eq("SF0_DF0_DS1_L0")&
            original.reverse_on.eq(0)
        ].reset_index(drop=True)
        self.assertEqual(len(group),8)
        replicates=[]
        for rho,conv in ((.25,4.),(.5,2.)):
            c=group.copy()
            c["rho"]=rho
            c["conversion"]=conv
            replicates.append(simulate_finite_group(
                c,scale=3,seed=101,mode="both",
                immigration=False,years=4,dt=.25,transfer=.15
            ))
        for key in replicates[0]:
            np.testing.assert_array_equal(
                replicates[0][key],replicates[1][key],
                err_msg="Same product but different original source run: "+key
            )


if __name__=="__main__":
    unittest.main()
