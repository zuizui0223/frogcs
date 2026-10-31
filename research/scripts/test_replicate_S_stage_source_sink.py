"""Verify per-patch births–deaths–migration accounting and source replication.

Synthetic fixtures only; the real source run must separately confirm all
twenty annual censuses, complete UID generations and 64 genuine ABM paths.
"""
import unittest
import numpy as np
import pandas as pd

from replicate_S_stage_source_sink import (
    annual_group_counts,NEW_SEEDS,PARENT_SEEDS,
    YEARS,PATCHES,GUILDS
)
from run_equal_rate_S_stage_dispersal import NEW_MODES,equal_rate_modes


def synthetic_closed_ledger():
    rows=[]
    for guild in GUILDS:
        for patch in range(PATCHES):
            for year in range(YEARS+1):
                alive=0
                if guild=="F" and patch==(0 if year==0 else 1):alive=1
                if guild=="S" and patch==0:alive=1 if year==0 else 2
                if guild=="D" and patch==0 and year==0:alive=1
                rows.append(dict(guild=guild,patch=patch,year=year,alive=alive,
                                 n_newborn=int(guild=="S" and patch==0 and year==1)))
    reg=pd.DataFrame([
        dict(uid=0,parent_uid=-1,guild="F",natal_patch=0,last_known_patch=1,
             birth_time=0.,death_time=np.nan,alive=True),
        dict(uid=1,parent_uid=-1,guild="S",natal_patch=0,last_known_patch=0,
             birth_time=0.,death_time=np.nan,alive=True),
        dict(uid=2,parent_uid=-1,guild="D",natal_patch=0,last_known_patch=0,
             birth_time=0.,death_time=.5,alive=False),
        dict(uid=3,parent_uid=1,guild="S",natal_patch=0,last_known_patch=0,
             birth_time=.5,death_time=np.nan,alive=True),
    ])
    movement=pd.DataFrame([
        dict(uid=0,guild="F",time_year=.5,
             source_patch=0,destination_patch=1)])
    return pd.DataFrame(rows),reg,movement


class ExactSourceSinkAccounting(unittest.TestCase):
    def test_known_lifetime_movement_death_and_newborn_conserve_each_patch(self):
        p,r,m=synthetic_closed_ledger()
        x=annual_group_counts(p,r,m)
        self.assertEqual(len(x),YEARS*PATCHES*3)
        self.assertTrue(x.identity_residual.eq(0).all())
        first=x[x.year.eq(1)].set_index(["guild","patch"])
        self.assertEqual(first.loc[("F",0),"delta_alive"],-1)
        self.assertEqual(first.loc[("F",1),"inbound"],1)
        self.assertEqual(first.loc[("F",0),"outbound"],1)
        self.assertEqual(first.loc[("S",0),"births"],1)
        self.assertEqual(first.loc[("D",0),"deaths"],1)
        self.assertEqual(first.net_surviving_migration.sum(),0)

    def test_no_movement_is_not_a_source_of_fake_reoccupation(self):
        p,r,m=synthetic_closed_ledger()
        # Remove the F migration altogether, keep the founder in patch0.
        p.loc[(p.guild=="F")&(p.year>0)&p.patch.eq(0),"alive"]=1
        p.loc[(p.guild=="F")&(p.year>0)&p.patch.eq(1),"alive"]=0
        q=annual_group_counts(p,r,m.iloc[0:0].copy())
        self.assertTrue(q.inbound.eq(0).all())
        self.assertTrue(q.outbound.eq(0).all())
        self.assertTrue(q.identity_residual.eq(0).all())

    def test_missing_child_birth_or_falsified_death_is_rejected(self):
        p,r,m=synthetic_closed_ledger()
        modified=r[r.uid.ne(3)]
        with self.assertRaises(AssertionError):
            annual_group_counts(p,modified,m)
        modified=r.copy()
        modified.loc[modified.uid.eq(2),"last_known_patch"]=1
        with self.assertRaises(AssertionError):
            annual_group_counts(p,modified,m)
        modified=p.copy()
        modified.loc[(modified.guild=="S")&(modified.year.eq(1))&
                     modified.patch.eq(0),"n_newborn"]=0
        with self.assertRaises(AssertionError):
            annual_group_counts(modified,r,m)

    def test_rate_match_all_eight_conditions_and_strict_new_seeds(self):
        self.assertEqual(len(NEW_MODES),4)
        self.assertEqual(tuple(NEW_SEEDS),tuple(range(105,113)))
        self.assertTrue(set(PARENT_SEEDS).isdisjoint(NEW_SEEDS))
        for mode in NEW_MODES:
            p=equal_rate_modes(mode)
            x=np.asarray(p.diffusion)
            self.assertEqual(np.count_nonzero(x),1)
            self.assertTrue(set(x).issubset({0,.05,.22}))

    def test_zero_or_negative_census_declined(self):
        p,r,m=synthetic_closed_ledger()
        broken=p[p.year.ne(1)]
        with self.assertRaises(AssertionError):
            annual_group_counts(broken,r,m)
        broken=p.copy()
        broken.loc[0,"alive"]=-1
        with self.assertRaises(AssertionError):
            annual_group_counts(broken,r,m)


if __name__=="__main__":
    unittest.main()
