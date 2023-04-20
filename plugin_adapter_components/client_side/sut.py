from .tests.landing_page import LandingPage
import unittest

class SeleniumSut:
    """
    Constructor
    """
    def __init__(self, logger,response_received):
        self.logger = logger
        self.response_received = response_received
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
        self.logger.info("Sut", "Selenium has stopped testing the SUT")

    """
    Parse the SUT's response and add it to the response stack from the
    Handler class.
    """
    def handle_response(self, response):
        self.logger.debug("Sut", "Add response: {}".format(response))
        self.response_received(response)

    """
    Run a specific test case 
    param tuple[] data
    """
    def run_test_case(self, test, data = {}):
        print(test)
        
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

    def landing_page_button_click(self):
        response = [ "c_landing_page_button_clicked", { "data":"string" }, {"data": "test"} ]
        result = self.run_test_case(LandingPage("testButtonClick"))
        return self.handle_response(response)
        