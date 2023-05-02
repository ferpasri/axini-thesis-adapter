from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import capybara

class SeleniumSut:
    """
    Constructor
    """
    def __init__(self, logger, responses):
        self.logger = logger
        self.responses = responses
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
        self.responses.append(response)


    """
    Run a specific test case 
    param tuple[] data
    """


    def landing_page_button_click(self):
        response = ["clicked", { "css": "string" }, {"data": "test"} ]
        add_to_cart_button = self.driver.find_element(By.CSS_SELECTOR,"#ec_add_to_cart_1")
        add_to_cart_button.click()
        return self.handle_response(response)
    
    def click_on(self, css_selector):
        add_to_cart_button = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        add_to_cart_button.click()
        time.sleep(2)


    def expect_element(self, css_selector):
        element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        title = ''
        if hasattr(element, 'title'):
            title = element.title

        response = ["get_element", { "css_selector": "string", "title": "string" }, {"css_selector": css_selector, "title": title}]
        return self.handle_response(response)
    

    def navigate(self, url):
        self.driver.get(url)
        time.sleep(2)

    def get_url(self):
        response = ["get_url", {"_url" : "string"}, {"_url": self.driver.current_url}]
        return self.handle_response(response)

    def get_value(self, css_selector):
        element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        value = element.get_attribute("value")
        response = ["get_value", { "css_selector": "string", "value": "string" }, {"css_selector": css_selector, "value": value}]
        return self.handle_response(response)   
    
    def fill_in(self, css_selector, value):
        element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        element.send_keys(value)
        time.sleep(2)


    

    def start(self):
        self.driver = webdriver.Chrome()
        # go to the page with items listing
        self.driver.get("https://academybugs.com/find-bugs/")
        #return self.handle_response(["started", {}, {}])
        