from typing import List
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Window():

    def __init__(self) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors-spki-list')
        self.options.add_argument('--incognito')
        self.options.add_argument('log-level=3')
        self.options.add_argument('--head-less')

        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()

        self.wait = WebDriverWait(self.driver, 60)
        self.place: List[str] | None = None

    def open(self, url: str):
        self.driver.get(url)

    def set_place(self, place: List[str]):
        button = self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "city-select__text")))
        button.click()

        columns = ('districts', 'regions', 'cities')
        for key, column in enumerate(columns):
            if self.place and self.place[key] == place[key]:
                continue
            column_elems = self.wait.until(EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, f'#select-city > div.lists-column > ul.{column} > li.modal-row')))
            for column_elem in column_elems:
                if place[key] == column_elem.text:
                    column_elem.click()
                    break
        self.place = place

    def close(self) -> None:
        self.driver.close()
