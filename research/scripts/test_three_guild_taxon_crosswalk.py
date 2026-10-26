import unittest
from three_guild_taxon_crosswalk import validate_match,validate_accepted

class TaxonIdentity(unittest.TestCase):
    def row(self):
        return dict(matchType='EXACT',rank='SPECIES',status='SYNONYM',acceptedUsageKey=12,
                    usageKey=15,order='Anura',**{'class':'Amphibia'})
    def test_exact_synonym(self):self.assertEqual(validate_match(self.row(),'Anura'),12)
    def test_fuzzy_rejected(self):
        d=self.row();d['matchType']='FUZZY'
        with self.assertRaises(ValueError):validate_match(d,'Anura')
    def test_wrong_guild_rejected(self):
        with self.assertRaises(ValueError):validate_match(self.row(),'Caudata')
    def test_accepted_endpoint_must_be_same_species(self):
        d=dict(key=12,rank='GENUS',taxonomicStatus='ACCEPTED',order='Anura',canonicalName='Rana',**{'class':'Amphibia'})
        with self.assertRaises(ValueError):validate_accepted(d,12,'Anura')

if __name__=='__main__':unittest.main()
