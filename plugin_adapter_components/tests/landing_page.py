import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class LandingPage(unittest.TestCase):
# class landing_page(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.get("http://localhost:4200/")

    def testButtonClick(self):
        elem = self.driver.find_element(By.ID, "alert_btn")
        elem.click()
        alert = self.driver.switch_to.alert
        self.assertEqual(alert.text, "test")
        alert.dismiss()
        self.assertNotIn("No results found.", self.driver.page_source)

    def tearDown(self):
        self.driver.close()

# if __name__ == "__main__":
#     unittest.main(warnings='ignore')