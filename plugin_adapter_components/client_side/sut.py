import time
from splinter import Browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import difflib

class SeleniumSut:
    """
    Constructor
    """
    def __init__(self, logger, responses, event_queue):
        self.logger = logger
        self.responses = responses
        self.event_queue = event_queue
        self.browser = None
        self.page_source = ''

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


    def click(self, css_selector):
        self.page_source = self.browser.html
        self.browser.find_by_css(css_selector).first.click()
        time.sleep(3)
        # properties = self.get_properties(expected_element)
        # self.generate_response(properties=properties)


    def visit(self, url):
        self.browser.visit(url)
        self.page_source = self.browser.html
        self.generate_response(title=True)


    def fill_in(self, css_selector, value):
        self.page_source = self.browser.html
        self.browser.find_by_css(css_selector).fill(value)


    # Create a new Browser instance
    def start(self, headless=True):
        self.browser = Browser('chrome', headless=headless)
        self.browser.wait_time = 5
        #WebDriverWait(self.browser.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body.loaded')))


    def generate_response(self, title=False, properties={}):

        if title:
            response = [
                "page_title",
                {"_title": "string", "_url": "string"},
                {"_title": self.browser.title, "_url": self.browser.url}
            ]
            self.handle_response(response)
            return

        response = [
            "page_update",
            {
                'style': 'string',
                'value': 'string', 
                'disabled': 'boolean', 
                'checked': 'boolean',
                'src': 'string',
                'href': 'string',
                'textContent': 'string',
            },
            properties
        ]

        self.handle_response(response)

    def parse_html(self, expected_element_selector):
        parsed_html = BeautifulSoup(self.browser.html, 'html.parser')
        return parsed_html.select(expected_element_selector)[0]


    # This method searches an element for the given properties and returns a list of all equal properties
    # AMP can then compare expected with actual based on the missing properties (those who were not equal)
    def get_properties(self, css_selector):

        element = self.browser.find_by_css(css_selector)
        for key  in self.properties:
            if element[key]:
                self.properties[key] = element[key]

        return self.properties


    def get_updates(self):

        if not self.page_source:
            return
        
        current_page_source = self.browser.html
        diff = difflib.unified_diff(self.page_source.splitlines(), current_page_source.splitlines())
        added_lines = []
        removed_lines = []

        for line in diff:
            if line.startswith('+'):
                added_lines.append(line[1:].rstrip('\n\t'))
            elif line.startswith('-'):
                removed_lines.append(line[1:].rstrip('\n\t'))

        if added_lines or removed_lines:
            print('Added lines:')
            print(added_lines)

            print('Removed lines:')
            print(removed_lines)

            response = ["page_update", {'ok': 'string'},{'ok':'ok'}]
            self.handle_response(response)
        self.page_source = current_page_source
