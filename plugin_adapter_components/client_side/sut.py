import time
from splinter import Browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from xmldiff import main
from lxml import etree
from io import StringIO 

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
        self.browser.find_by_css(css_selector).is_visible()
        self.browser.find_by_css(css_selector).click()


    def click_link(self, css_selector):
        self.browser.find_by_css(css_selector).is_visible()
        self.browser.find_by_css(css_selector).click()
        self.generate_response()


    def visit(self, url):
        self.browser.visit(url)
        self.generate_response()


    def fill_in(self, css_selector, value):
        self.page_source = self.browser.html
        self.browser.find_by_css(css_selector).fill(value)


    # Create a new Browser instance
    def start(self, headless=True):
        self.browser = Browser('chrome', headless=headless)
        self.browser.wait_time = 10
        #WebDriverWait(self.browser.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body.loaded')))


    def generate_response(self):

        self.page_source = self.browser.html
        response = [
            "page_title",
            {"_title": "string", "_url": "string"},
            {"_title": self.browser.title, "_url": self.browser.url}
        ]
        self.handle_response(response)
        return


    def get_updates(self):

        if not self.page_source:
            return
        
        before = self.page_source
        after = self.browser.html

        parser = etree.HTMLParser()

        before = etree.parse(StringIO(before), parser)
        after = etree.parse(StringIO(after), parser)

        results = main.diff_trees(before, after)

        nodes = {}
        for result in results:
            attributes = {}
            fields = result._fields
            for field in fields:
                attributes[field] = str(getattr(result, field))

            # Check if the key exists in nodes
            if type(result).__name__ in nodes:
                nodes[type(result).__name__].append(attributes)
            else:
                nodes[type(result).__name__] = [attributes]

        if nodes:
            response = ["page_update", {'nodes': 'struct'},{'nodes': nodes}]
            self.handle_response(response)

        self.page_source = self.browser.html
