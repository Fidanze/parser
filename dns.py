

from cgi import print_exception
from doctest import DebugRunner
from typing_extensions import dataclass_transform
from unicodedata import name
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

url = "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?from_search=1&order=6&stock=now-today-tomorrow-later-out_of_stock"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
# chrome_options.add_argument("headless") нужно ещё разобраться

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
elems = driver.find_elements(by=By.CSS_SELECTOR, value='[data-id="product"]')
data_results = []
for elem in elems:
    elem_url = elem.find_element(
        by=By.CLASS_NAME, value="catalog-product__name").get_attribute('href')
    driver.get(elem_url)
    data_from_elem = {'ulr': elem_url, 'price': driver.find_element(
        by=By.CLASS_NAME, value='data_from_elem')}
    elem_options = driver.find_elements(
        by=By.CLASS_NAME, value='product-characteristics__spec')
    for elem_option in elem_options:
        elem_option_name = elem_option.find_element(
            by=By.CLASS_NAME, value='product-characteristics__spec-title').text
        elem_option_value = elem_option.find_element(
            by=By.CLASS_NAME, value='product-characteristics__spec-value').text
        data_from_elem[elem_option_name] = elem_option_value
    data_results.append(data_from_elem)
    driver.back()
print(data_results)
driver.close()1
