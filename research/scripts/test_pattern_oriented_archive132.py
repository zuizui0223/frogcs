"""Tests: include all 132 frozen source variants rather than favorable cases."""
import itertools
import unittest
import numpy as np
import pandas as pd

from pattern_oriented_archive132 import DESIGN, archived_full_catalog, N_CASES, LEVELS
from pattern_oriented_abc_pilot import group_exact_surfaces


def fabricated_archive():
    inventory=pd.read_csv(DESIGN)
    data=[]
    for z in inventory.itertuples(index=False):
        for v,s,o in itertools.product((0.,1.),np.linspace(.25,2.,LEVELS),np.linspace(.25,2.,LEVELS)):
            row=z._asdict()
            row.update(vegetation=v,S_source=s,D_source=o,
                       F_B=1.5+.004*z.case+.02*s-.03*o+.07*v)
            data.append(row)
    all_cells=pd.DataFrame(data)
    parts=[]
    for risk in (False,True):
        for mode in ("dynamic","frozen"):
            sel=all_cells[(all_cells.risk==risk)&
                          ((all_cells.edge=="frozen")== (mode=="frozen"))].copy()
            parts.append(sel)
    return parts,inventory


class CompleteCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames,cls.inventory=fabricated_archive()

    def test_all_archived_cases_present_without_sign_based_prefilter(self):
        grids,metadata=archived_full_catalog(self.frames,self.inventory)
        self.assertEqual(len(grids),N_CASES)
        self.assertEqual(len(metadata),N_CASES)
        self.assertEqual(sum(x.size for x in grids.values()),N_CASES*2*LEVELS*LEVELS)
        self.assertIn("case_000",grids)
        self.assertIn("case_131",grids)
        self.assertTrue(all(np.isfinite(x).all() for x in grids.values()))

    def test_fails_closed_when_source_excludes_one_case(self):
        bad=[x.copy() for x in self.frames]
        case=self.inventory.iloc[0]["case"]
        bad=[x[x.case!=case] for x in bad]
        with self.assertRaises(ValueError):
            archived_full_catalog(bad,self.inventory)
        with self.assertRaises(ValueError):
            archived_full_catalog(self.frames,self.inventory.iloc[:-1])
        with self.assertRaises(ValueError):
            archived_full_catalog(self.frames[:3],self.inventory)

    def test_corrupted_metadata_and_duplicate_cell_rejected(self):
        changed=[x.copy() for x in self.frames]
        nonempty=next(i for i,x in enumerate(changed) if len(x))
        changed[nonempty].loc[changed[nonempty].index[0],"family"]="unrecorded_type"
        with self.assertRaises(AssertionError):
            archived_full_catalog(changed,self.inventory)
        dup=[x.copy() for x in self.frames]
        dup[nonempty]=pd.concat([dup[nonempty],dup[nonempty].iloc[:1]],ignore_index=True)
        with self.assertRaises(ValueError):
            archived_full_catalog(dup,self.inventory)

    def test_duplicate_mechanistic_grids_must_share_group(self):
        grids,meta=archived_full_catalog(self.frames,self.inventory)
        aliases,groups=group_exact_surfaces(grids)
        self.assertEqual(len(aliases),N_CASES)
        self.assertEqual(sum(map(len,groups.values())),N_CASES)


if __name__=="__main__":
    unittest.main()
