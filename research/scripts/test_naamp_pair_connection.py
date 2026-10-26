import unittest
from naamp_pair_connection import accepted_key


class IdentityTests(unittest.TestCase):
    def test_accepted_and_synonym_same_key(self):
        self.assertEqual(accepted_key(dict(matchType='EXACT',rank='SPECIES',status='ACCEPTED',usageKey=10)),10)
        self.assertEqual(accepted_key(dict(matchType='EXACT',rank='SPECIES',status='SYNONYM',usageKey=20,acceptedUsageKey=10)),10)

    def test_higher_rank_not_silently_matched(self):
        with self.assertRaises(ValueError):
            accepted_key(dict(matchType='HIGHERRANK',rank='GENUS',status='ACCEPTED',usageKey=10))

    def test_synonym_without_accepted_key_rejected(self):
        with self.assertRaises(ValueError):
            accepted_key(dict(matchType='EXACT',rank='SPECIES',status='SYNONYM',usageKey=20))


if __name__ == '__main__': unittest.main()
