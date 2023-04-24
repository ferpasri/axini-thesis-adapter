import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

class LandingPage(unittest.TestCase):
# class landing_page(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        # go to the page with items listing
        self.driver.get("https://academybugs.com/find-bugs/")

    def testButtonClick(self):
        add_to_cart_button = self.driver.find_element(By.CSS_SELECTOR,"#ec_add_to_cart_1")
        add_to_cart_button.click()

        self.assertEqual(True,True)

    def tearDown(self):
        self.driver.close()

# if __name__ == "__main__":
#     unittest.main(warnings='ignore')