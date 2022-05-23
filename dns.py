from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import json

from concurrent.futures import ProcessPoolExecutor
import os
import time


def timing_val(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        print(t2-t1)
    return wrapper


def parse_elem_options(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    chrome_options.add_argument('log-level=3')

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 7)
    driver.maximize_window()
    driver.get(url)

    data_from_elem = {'ulr': url, 'price': wait.until(EC.visibility_of_all_elements_located((
        By.CLASS_NAME, 'product-buy__price')))[0].text}

    i = 1
    while True:
        try:
            wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'product-characteristics__expand'))).click()
            i += 1
            options = wait.until(EC.visibility_of_all_elements_located(
                (By.CLASS_NAME, 'product-characteristics__spec')))
            break
        except TimeoutException:
            print(f"Try {i} to click on expand button on url: {url}")

    for option in options:
        name = option.find_element(
            by=By.CLASS_NAME, value='product-characteristics__spec-title').text
        value = option.find_element(
            by=By.CLASS_NAME, value='product-characteristics__spec-value').text
        data_from_elem[name] = value

    driver.close()
    return data_from_elem


@timing_val
def get_all_data():
    url = "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    chrome_options.add_argument('log-level=3')

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 7)
    driver.maximize_window()
    driver.get(url)

    data_results = []

    while True:
        elems = wait.until(EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, "catalog-product__name")))
        elem_urls = [elem.get_attribute('href') for elem in elems]

        with ProcessPoolExecutor(max_workers=int(os.environ['NUMBER_OF_PROCESSORS'])-2) as executor:
            result = executor.map(parse_elem_options, elem_urls)
        data_results.extend(list(result))

        next_page = wait.until(EC.visibility_of_element_located((
            By.CLASS_NAME, 'pagination-widget__page-link_next')))
        if 'pagination-widget__page-link_disabled' in next_page.get_attribute("class"):
            break

        next_page.click()

    driver.close()

    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(data_results, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    get_all_data()
