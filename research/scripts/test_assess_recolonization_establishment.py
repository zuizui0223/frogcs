"""Source-grounded recolonization vs reproduction tests (synthetic fixtures only)."""
import unittest
import numpy as np
import pandas as pd

from assess_recolonization_establishment import (
    natal_parent_births,attach_validated_births,event_table,
    patch_occupancy_transitions
)


class PersistenceAndParentOriginTests(unittest.TestCase):
    def patch_fixture(self):
        # S patch0 disappeared after year0; S patch1 colonized in year1,
        # produced offspring in year2 and persisted through years2-3.
        # S patch2 first returned at year4 and must be right-censored.
        rows=[]
        occupancy={0:[2,0,0,0,0],1:[0,1,2,1,0],2:[0,0,0,0,1]}
        for patch,alive in occupancy.items():
            for year,n in enumerate(alive):
                prev=alive[year-1] if year>0 else None
                rows.append(dict(mobility="original",reverse=False,seed=101,
                    guild="S",patch=patch,year=year,alive=n,
                    recolonized=bool(year>0 and prev==0 and n>0),
                    locally_extinct=bool(year>0 and prev>0 and n==0),
                    n_newborn=2 if (patch,year)==(1,2) else 0,
                    known_surviving_immigrant_arrivals=(
                        1 if (patch,year) in ((1,1),(2,4)) else 0),
                    births_with_exogenous_natal_parent=(
                        1 if (patch,year)==(1,2) else 0),
                    births_with_exogenous_founder=(
                        2 if (patch,year)==(1,2) else 0)))
        return pd.DataFrame(rows)

    def test_annual_return_has_two_followups_and_confirmed_local_birth(self):
        x=self.patch_fixture()
        events=event_table(x)
        self.assertEqual(len(events),2)
        a=events.set_index("patch")
        self.assertEqual(int(a.loc[1,"year_of_recolonization"]),1)
        self.assertTrue(a.loc[1,"retained_at_one_followup"])
        self.assertTrue(a.loc[1,"retained_at_two_followups"])
        self.assertEqual(int(a.loc[1,"locally_born_in_first_postreturn_year"]),2)
        self.assertEqual(int(a.loc[1,"births_with_external_natal_parent_in_postreturn_year"]),1)
        self.assertTrue(a.loc[1,"two_census_persistence_and_postreturn_births"])
        self.assertFalse(a.loc[1,"occupied_spell_right_censored"])
        self.assertEqual(int(a.loc[1,"consecutive_observed_occupied_censuses"]),3)

    def test_last_year_return_is_right_censored_not_called_failed_establishment(self):
        a=event_table(self.patch_fixture()).set_index("patch").loc[2]
        self.assertEqual(int(a.year_of_recolonization),4)
        self.assertFalse(a.one_census_followup_observed)
        self.assertFalse(a.two_census_followups_observed)
        self.assertTrue(pd.isna(a.retained_at_two_followups))
        self.assertTrue(pd.isna(a.two_census_persistence_and_postreturn_births))
        self.assertTrue(a.occupied_spell_right_censored)

    def test_missing_or_incorrect_annual_extirpation_label_fails_closed(self):
        q=self.patch_fixture()
        q.loc[(q.patch==1)&(q.year==1),"recolonized"]=False
        with self.assertRaises(AssertionError):
            event_table(q)
        q=self.patch_fixture()
        q.loc[(q.patch==0)&(q.year==1),"locally_extinct"]=False
        with self.assertRaises(AssertionError):
            event_table(q)

    def test_parent_natal_patch_and_founder_origin_are_distinct(self):
        parents=pd.DataFrame([
            dict(mobility="original",reverse=False,seed=101,guild="S",
                 uid=0,parent_uid=-1,generation=0,natal_patch=0,
                 founder_patch=0,birth_time=0.),
            dict(mobility="original",reverse=False,seed=101,guild="S",
                 uid=1,parent_uid=0,generation=1,natal_patch=1,
                 founder_patch=0,birth_time=1.5),
            dict(mobility="original",reverse=False,seed=101,guild="S",
                 uid=2,parent_uid=1,generation=2,natal_patch=1,
                 founder_patch=0,birth_time=2.5)])
        tab=natal_parent_births(parents).sort_values("year")
        self.assertEqual(tab.year.to_list(),[2,3])
        self.assertEqual(tab.births_with_exogenous_natal_parent.to_list(),[1,0])
        self.assertEqual(tab.births_with_exogenous_founder.to_list(),[1,1])
        # A birth year is the interval (year-1,year].
        self.assertEqual(tab.births_from_registry.sum(),2)

    def test_births_must_reconcile_with_all_ever_lived_children(self):
        r=pd.DataFrame([
            dict(mobility="off",reverse=False,seed=3,guild="F",
                 uid=0,parent_uid=-1,generation=0,natal_patch=0,
                 founder_patch=0,birth_time=0.),
            dict(mobility="off",reverse=False,seed=3,guild="F",
                 uid=1,parent_uid=0,generation=1,natal_patch=0,
                 founder_patch=0,birth_time=.95)])
        p=pd.DataFrame([
            dict(mobility="off",reverse=False,seed=3,guild="F",
                 patch=0,year=0,n_newborn=0),
            dict(mobility="off",reverse=False,seed=3,guild="F",
                 patch=0,year=1,n_newborn=1)])
        linked=attach_validated_births(p,r)
        self.assertEqual(linked.births_from_registry.to_list(),[0,1])
        incorrect=p.copy()
        incorrect.loc[incorrect.year==1,"n_newborn"]=0
        with self.assertRaises(AssertionError):
            attach_validated_births(incorrect,r)


if __name__=="__main__":
    unittest.main()
