import unittest
from three_guild_delay_toy import simulate

class Toy(unittest.TestCase):
    def test_absent_third_cue_irrelevant(self):
        self.assertEqual(simulate(delay=20,third=False,cue=0)['completion'],simulate(delay=20,third=False,cue=30)['completion'])
    def test_drying_prevents_completion(self):
        self.assertEqual(simulate(delay=40,water=60)['completion'],0)
    def test_step_halving(self):
        a=simulate(delay=20,dt=.1)['completion'];b=simulate(delay=20,dt=.05)['completion']
        self.assertLess(abs(a-b),.005)

if __name__=='__main__':unittest.main()
