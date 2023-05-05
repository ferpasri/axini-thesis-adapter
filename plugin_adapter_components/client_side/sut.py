import time
from splinter import Browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SeleniumSut:
    """
    Constructor
    """
    def __init__(self, logger, responses):
        self.logger = logger
        self.responses = responses
        self.browser = None

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
        self.responses.append(response)


    def click(self, css_selector):
        self.browser.find_by_css(css_selector).first.click()
        self.generate_page_update_response()


    def visit(self, url):
        self.browser.visit(url)
        self.generate_page_update_response()


    def fill_in(self, css_selector, value):
        self.browser.find_by_css(css_selector).fill(value)
        self.generate_page_update_response()


    def start(self):
        self.browser = Browser('chrome')
        self.browser.wait_time = 5
        #WebDriverWait(self.browser.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body.loaded')))


    def generate_page_update_response(self):
        response = ["page_update", {"_html": "string", "_url": "string"}, {"_html": self.browser.html, "_url": self.browser.url}]
        self.handle_response(response)