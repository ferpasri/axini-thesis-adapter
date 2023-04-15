import struct
from threading import Thread
# from .logger import Logger
from .tests.landing_page import LandingPage
# from unittest import main
import unittest

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
    def handle_response_status(self, function_name, response):
        if response[1] != '':
            self.logger.error("Sut", "Error in function {} failed due to: {}".format(function_name, response[1]))

        self.logger.debug("Sut", "Add response from {}: {}".format(function_name, self.parse_status_code(response[0])))
        self.responses.append(self.parse_status_code(response[0]))

    def landing_page_button_click(self):

        runner = unittest.TextTestRunner()
        result = runner.run(unittest.TestLoader().loadTestsFromTestCase(LandingPage.testButtonClick))
        print(result)
        # print("test")
        # test = main(module=LandingPage.testButtonClick, argv=testArgs)
        # print(test.result.wasSuccessful())