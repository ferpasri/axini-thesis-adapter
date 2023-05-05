import time
from splinter import Browser
from selenium.webdriver.common.by import By
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
        time.sleep(2)


    def expect_page_to_have(self, css_selector, title=None):
        if title:
            element = self.browser.is_element_present_by_css(css_selector, text=title)
        else:
            element = self.browser.is_element_present_by_css(css_selector)

        response = ["expect_page_to_have", { "found": "string" }, {"found": element}]
        return self.handle_response(response)


    def expect_page_not_to_have(self, css_selector, title=None):
        if title:
            element = self.browser.is_element_present_by_css(css_selector, text=title)
        else:
            element = self.browser.is_element_present_by_css(css_selector)
        response = ["expect_page_not_to_have", { "not_found": "string"}, {"not_found": element}]
        return self.handle_response(response)


    def visit(self, url):
        self.browser.visit(url)
        time.sleep(2)


    def get_url(self):
        response = ["get_url", {"_url" : "string"}, {"_url": self.browser.url}]
        return self.handle_response(response)


    def get_value(self, css_selector):
        value = self.browser.find_by_css(css_selector).first.value
        response = ["get_value", { "css_selector": "string", "value": "string" }, {"css_selector": css_selector, "value": value}]
        return self.handle_response(response)


    def fill_in(self, css_selector, value):
        self.browser.find_by_css(css_selector).fill(value)
        time.sleep(2)


    def start(self):
        self.browser = Browser('chrome')
        self.browser.visit("https://academybugs.com/find-bugs/")
        WebDriverWait(self.browser.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body.loaded')))
