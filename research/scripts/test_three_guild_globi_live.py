import unittest
from three_guild_globi_live import qualify,directed_identity

class GuildRows(unittest.TestCase):
    def row(self):
        return dict(source_taxon_name='Lithobates clamitans',target_taxon_name='Anax junius',
                    source_taxon_path='Animalia | Anura | Lithobates clamitans',
                    target_taxon_path='Animalia | Odonata | Anax junius',interaction_type='interactsWith',
                    source_specimen_life_stage=None,target_specimen_life_stage=None,study_citation=None)
    def test_unknown_stage_and_citation_not_excluded(self):
        self.assertEqual(qualify(self.row(),'Anura','Odonata'),'eligible_named_edge')
    def test_substring_is_not_guild(self):
        r=self.row();r['source_taxon_path']='NonAnura'
        self.assertEqual(qualify(r,'Anura','Odonata'),'source_guild_unverified')
    def test_order_level_endpoint_not_species(self):
        r=self.row();r['target_taxon_name']='Odonata'
        self.assertEqual(qualify(r,'Anura','Odonata'),'not_two_binomial_form_names')
    def test_no_forced_direction(self):
        self.assertEqual(qualify(self.row(),'Odonata','Anura'),'source_guild_unverified')
    def test_inverse_relation_not_reciprocal_predation(self):
        self.assertEqual(directed_identity('frog','newt','eatenBy'),('newt','frog','eats'))
    def test_symmetric_relation_once(self):
        self.assertEqual(directed_identity('newt','frog','coOccursWith'),('frog','newt','coOccursWith'))

if __name__=='__main__':unittest.main()
