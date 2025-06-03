from splinter import Browser
from xmldiff import main
from lxml import etree
from io import StringIO 
import re
import time

# This class executes labels on the SUT and generates responses
class SeleniumSut:
    """
    Constructor
    """
    def __init__(self, logger, responses, event_queue, headless):
        self.logger = logger
        self.responses = responses
        self.event_queue = event_queue
        self.headless = headless
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
        self.browser.quit()


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
        self.browser.find_by_css(css_selector).is_visible()
        self.page_source = self.browser.html
        self.browser.find_by_css(css_selector).click()
    
    def accept_alert(self):
        self.browser.driver.switch_to.alert.accept()


    """
    Simulates a click on a link element specified by the 
    CSS selector and generates a response.
    param [String] css_selector
    """
    def click_link(self, css_selector):
        # Element is not clickable at point(x,y). Other element would receive the click
        #self.browser.find_by_css(css_selector).is_visible()
        #self.browser.find_by_css(css_selector).click()

        selectors = [css_selector, self.sanitize_selector(css_selector)]

        # Interact at JavaScript level
        for selector in selectors:
            print(f"click_link with selector: {selector}")
            if self.browser.is_element_present_by_css(selector, wait_time=5):
                element = self.browser.find_by_css(selector).first
                element.is_visible()
                old_url = self.browser.url
                self.browser.execute_script("arguments[0].scrollIntoView();", element._element)
                self.browser.execute_script("arguments[0].click();", element._element)

                # Wait for URL to change
                for _ in range(5):
                    time.sleep(1)
                    if self.browser.url != old_url:
                        break

                self.generate_response()
                return

        raise Exception(
            f"Element not found with original selector '{css_selector}' "
            f"or sanitized version '{selectors[1]}'."
        )

    """
    Loosens strict selectors: converts exact href matches to partial,
    removes IDs, and normalizes spacing.
    """
    def sanitize_selector(self, selector: str) -> str:
        selector = re.sub(r"\[href=['\"](.*?)['\"]\]", r"[href*='\1']", selector)
        selector = re.sub(r"#\w+", "", selector)
        selector = re.sub(r"\s+", " ", selector).strip()
        return selector

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
        selectors = [css_selector, self.sanitize_selector(css_selector)]

        # Interact at JavaScript level
        for selector in selectors:
            print(f"fill_in with selector: {selector}")
            if self.browser.is_element_present_by_css(selector, wait_time=5):
                element = self.browser.find_by_css(selector).first
                element.is_visible()
                self.browser.execute_script("arguments[0].scrollIntoView();", element._element)
                self.browser.execute_script(f"arguments[0].setAttribute('value', '{value}');", element._element)
                self.browser.execute_script("var event = new Event('input', { bubbles: true }); arguments[0].dispatchEvent(event);", element._element)
                self.generate_response()
                return

        raise Exception(
            f"Element not found with original selector '{css_selector}' "
            f"or sanitized version '{selectors[1]}'."
        )


    """
    Creates a new Selenium browser instance.
    """
    def start(self):
        self.browser = Browser('chrome', headless=self.headless)
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
