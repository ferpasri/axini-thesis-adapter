import struct
from threading import Thread
# from .logger import Logger
from .tests.landing_page import LandingPage
# from unittest import main
import unittest
import os

class Sut:
    """
    Constructor
    """
    def __init__(self, responses, logger):
        self.responses = responses
        self.logger = logger
        self.landingPage = LandingPage()

    """
    Special function: class name
    """
    def __name__(self):
        return "Sut"


    """
    Perform any cleanup if the selenium has stopped
    """
    def stop(self):
        self.logger.info("Sut", "Selenium has finished testing the SUT")


    """
    Parse the SUT's response and add it to the response stack from the
    Handler class.
    """
    def handle_response(self, response):
        # if response[1] != '':
            # self.logger.error("Sut", "Error in function {} failed due to: {}".format(response[0], response[1]))

        self.logger.debug("Sut", "Add response: {}".format(response))
        self.responses.append(response)

    """
    Run a specific test case 
    """
    def run_test_case(self, test):
        try:
            suite = unittest.TestSuite()
            suite.addTest(test)
            # TODO: print to file instead as logs
            runner = unittest.TextTestRunner(verbosity=0)
            result = runner.run(suite)

            # Only return the result if it succeeded
            if len(result.errors) > 0:
                for error in result.errors:
                    # error is a tuple of testCase and str, but the str is too long
                    self.logger.error("Sut", "Error in selenium test due to: {}".format(error[0]))

                raise Exception("a selenium test failed")
            return result
        
        # Catch any exceptions that occur during the selenium test
        except Exception as e:
            self.logger.error("Sut", "Error running selenium test: {}".format(str(e)))

    def landing_page_button_click(self):
        response = [ "landing_page_button_clicked", { "data":"string" }, {"data": "test"} ]

        result = self.run_test_case(LandingPage("testButtonClick"))
        return self.handle_response(response)
        