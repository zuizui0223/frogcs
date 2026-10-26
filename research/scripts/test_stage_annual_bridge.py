import unittest
from stage_annual_bridge_check import growth

class AnnualBridgeTest(unittest.TestCase):
    def test_one_year_closed_form(self):
        self.assertAlmostEqual(growth(.4,.25,1),.6)
    def test_no_retention(self):
        for m in (1,2,3): self.assertAlmostEqual(growth(.8,0,m),.5)
    def test_delayed_characteristic_equation(self):
        for m in (1,2,3):
            x=growth(.4,.25,m)
            self.assertAlmostEqual(x**m-.5*x**(m-1)-.1,0)
            self.assertGreater(growth(.8,.25,m),x)

if __name__=='__main__': unittest.main()
