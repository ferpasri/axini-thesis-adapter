import time
from splinter import Browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

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
        self.responses = []

    """
    Parse the SUT's response and add it to the response stack from the
    Handler class.
    """
    def handle_response(self, response):
        self.logger.debug("Sut", "Add response: {}".format(response))
        self.responses.append(response)


    def click(self, css_selector, expected_element_selector, properties):
        self.browser.find_by_css(css_selector).first.click()
        time.sleep(3)
        props = self.element_has_properties(expected_element_selector, properties)
        self.generate_page_update_response(expected_element_selector,props)


    def visit(self, url):
        self.browser.visit(url)
        self.generate_title_update_response()


    def fill_in(self, css_selector, value):
        self.browser.find_by_css(css_selector).fill(value)
        self.generate_page_update_response(css_selector)


    # Create a new Browser instance
    def start(self, headless=True):
        self.browser = Browser('chrome', headless=headless)
        self.browser.wait_time = 5
        #WebDriverWait(self.browser.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body.loaded')))


    def generate_page_update_response(self, css_selector=None, properties={}):

        response = [
            "page_update",
            {"_properties": {"style": "string"}},
            {"_properties": {"style": properties['style']}}
        ]

        self.handle_response(response)

    def parse_html(self, expected_element_selector):
        parsed_html = BeautifulSoup(self.browser.html, 'html.parser')
        return parsed_html.select(expected_element_selector)[0]


    def generate_title_update_response(self):

        response = [
            "page_title",
            {"_title": "string", "_url": "string"},
            {"_title": self.browser.title, "_url": self.browser.url}
        ]

        self.handle_response(response)


    # This method searches an element for the given properties and returns a list of all equal properties
    # AMP can then compare expected with actual based on the missing properties (those who were not equal)
    def element_has_properties(self, css_selector, property_values={}):
        element = self.browser.find_by_css(css_selector)
        actual_property_values = {}
        for property_name, expected_value in property_values.items():
            actual_value = element[property_name]

            # If the element does not have the required properties, return an empty dict
            if actual_value == expected_value:
                actual_property_values[property_name] = actual_value


        return actual_property_values
