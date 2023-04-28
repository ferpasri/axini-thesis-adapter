from selenium import webdriver
from selenium.webdriver.common.by import By

class SeleniumSut:
    """
    Constructor
    """
    def __init__(self, logger, response_received):
        self.logger = logger
        self.response_received = response_received
        self.driver = None

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


    def landing_page_button_click(self):
        response = ["c_landing_page_button_clicked", { "data": "string" }, {"data": "test"} ]
        add_to_cart_button = self.driver.find_element(By.CSS_SELECTOR,"#ec_add_to_cart_1")
        add_to_cart_button.click()
        return self.handle_response(response)
    

    def start(self):
        self.driver = webdriver.Chrome()
        # go to the page with items listing
        self.driver.get("https://academybugs.com/find-bugs/")
        return self.handle_response(["started", {}, {}])
        