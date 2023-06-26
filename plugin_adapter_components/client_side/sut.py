from splinter import Browser
from xmldiff import main
from lxml import etree
from io import StringIO 


# This class executes labels on the SUT and generates responses
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
    Add the response  to the response stack from the
    Handler class.
    param [[String, {String : String}, {String: String}]] css_selector
    """
    def handle_response(self, response):
        self.logger.debug("Sut", "Add response: {}".format(response))
        self.responses.append(response)


    """
    Simulates a click on an element specified by the 
    CSS selector
    param [String] css_selector
    """
    def click(self, css_selector):
        self.page_source = self.browser.html
        self.browser.find_by_css(css_selector).is_visible()
        self.browser.find_by_css(css_selector).click()


    """
    Simulates a click on a link element specified by the 
    CSS selector and generates a response.
    param [String] css_selector
    """
    def click_link(self, css_selector):
        self.browser.find_by_css(css_selector).is_visible()
        self.browser.find_by_css(css_selector).click()
        self.generate_response()


    """
    Navigates to the specified URL and generates a response.
    param [String] url
    """
    def visit(self, url):
        self.browser.visit(url)
        self.generate_response()


    """
    Enters the provided value into an input field
    specified by the CSS selector.
    param [String] css_selector
    param [String] value
    """
    def fill_in(self, css_selector, value):
        self.page_source = self.browser.html
        self.browser.find_by_css(css_selector).fill(value)


    """
    Creates a new Selenium browser instance.
    param [Boolean] headless
    """
    def start(self, headless=True):
        self.browser = Browser('chrome', headless=headless)
        self.browser.wait_time = 10


    """
    Generates a response containing the current page's title and URL.
    """
    def generate_response(self):
        self.page_source = self.browser.html
        response = [
            "page_title",
            {"_title": "string", "_url": "string"},
            {"_title": self.browser.title, "_url": self.browser.url}
        ]
        self.handle_response(response)


    """
    Compares the page source before and after an action, 
    detects updates, and generates a response.
    """
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

            if type(result).__name__ not in ['MoveNode', 'RenameNode']:
                if type(result).__name__ in nodes:
                    nodes[type(result).__name__].append(attributes)
                else:
                    nodes[type(result).__name__] = [attributes]

        if nodes:
            response = ["page_update", {'nodes': 'struct'},{'nodes': nodes}]
            self.handle_response(response)

        self.page_source = self.browser.html
