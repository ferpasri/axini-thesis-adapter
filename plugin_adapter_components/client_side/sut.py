import time
from splinter import Browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import difflib
from bs4 import BeautifulSoup

props = ['style']


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


    def click_link(self, css_selector):
        self.browser.find_by_css(css_selector).first.click()
        time.sleep(3)
        self.generate_response()


    def visit(self, url):
        self.browser.visit(url)
        time.sleep(3)
        self.generate_response()


    def fill_in(self, css_selector, value):
        self.page_source = self.browser.html
        self.browser.find_by_css(css_selector).fill(value)


    # Create a new Browser instance
    def start(self, headless=True):
        self.browser = Browser('chrome', headless=headless)
        self.browser.wait_time = 5
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
        
        current_page_source = self.browser.html
        diff = difflib.unified_diff(self.page_source.splitlines(), current_page_source.splitlines())
        added_lines = []
        removed_lines = []

        for line in diff:
            if line.startswith('+'):
                added_lines.append(line[1:].replace('\t','').replace('\n',''))
            elif line.startswith('-'):
                removed_lines.append(line[1:].replace('\t','').replace('\n',''))

        if added_lines or removed_lines:
            added_lines.pop(0)
            removed_lines.pop(0)

            tmp = {}
            for removed_line, added_line in zip(removed_lines, added_lines):
                vals = self.get_css_selector(removed_line, added_line)
                if vals:
                    tmp.update(vals)

            if tmp:
                response = ["page_update", {'elems': 'struct'},{'elems': tmp}]
                self.handle_response(response)

        self.page_source = current_page_source




    def get_css_selector(self, r_line, a_line):
        # Create a BeautifulSoup object
        removed_element = BeautifulSoup(r_line, 'html.parser').find(True)
        added_element = BeautifulSoup(a_line, 'html.parser').find(True)

        css_selector = ""
        before = ""
        after = ""
        tmp = {}

        if removed_element and added_element:
                    
            # Build the CSS selector string
            css_selector_parts = [removed_element.name]

            element_id = removed_element.get('id')
            if element_id:
                css_selector_parts.append("#" + element_id)

            element_classes = removed_element.get('class')
            if element_classes:
                css_classes = ".".join(element_classes)
                css_selector_parts.append("." + css_classes)

            css_selector = "".join(css_selector_parts)

            for prop in props:
#                before = removed_element.get(prop) if removed_element.get(prop) else ''
                after = added_element.get(prop) if added_element.get(prop) else ''
                tmp[css_selector] = {prop : after}

        return tmp