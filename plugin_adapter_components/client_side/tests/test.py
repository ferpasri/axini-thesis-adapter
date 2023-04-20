# A simple test file to test selenium directly
import unittest
from landing_page import LandingPage 

suite = unittest.TestSuite()
suite.addTest(LandingPage("testButtonClick"))
runner = unittest.TextTestRunner()
runner.run(suite)