from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


class Window():

    def __init__(self) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors-spki-list')
        self.options.add_argument("--incognito")
        self.options.add_argument('log-level=3')

        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()

        self.wait = WebDriverWait(self.driver, 20)
        self.is_city_choosed = False

    def open(self, url: str):
        self.driver.get(url)
        if not self.is_city_choosed:
            self.choose_city()
            self.is_city_choosed = True

    def choose_city(self):
        button = self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "city-select__text")))
        button.click()
        city_search_input = self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "base-ui-input-search__input")))
        [city_search_input.send_keys(letter) for letter in self.city]
        city_list = self.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "cities-search")))
        while True:
            try:
                finded_cities = city_list.find_elements(
                    By.CLASS_NAME, 'modal-row')
                for city in finded_cities:
                    tag_a = city.find_element(By.TAG_NAME, 'a')
                    f_span = tag_a.find_element(By.TAG_NAME, 'span')
                    s_span = f_span.find_element(By.TAG_NAME, 'span')
                    if s_span.text == self.city:
                        s_span.click()
                        break
                else:
                    raise NoSuchElementException
                break
            except NoSuchElementException:
                city_search_input.clear()
                city_search_input.send_keys(self.city)

    def set_city(self, city: str):
        self.city = city
        self.is_city_choosed = False

    def close(self) -> None:
        self.driver.close()
