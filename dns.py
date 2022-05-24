from itertools import cycle
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import json

from concurrent.futures import ThreadPoolExecutor
import os
import time


def timing_val(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        func(*arg, **kw)
        t2 = time.time()
        print(t2-t1)
    return wrapper


def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('log-level=3')

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    return driver


def get_urls(main_url):
    driver = get_driver()
    wait = WebDriverWait(driver, 10)
    driver.get(main_url)

    urls = []

    while True:
        elems = wait.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "catalog-product__name")))

        urls.extend([elem.get_attribute('href') +
                    'characteristics/' for elem in elems])

        next_page = wait.until(EC.visibility_of_element_located((
            By.CLASS_NAME, 'pagination-widget__page-link_next')))
        if 'pagination-widget__page-link_disabled' in next_page.get_attribute("class"):
            break
        else:
            driver.get(next_page.get_attribute('href'))

    driver.close()
    return urls


def parse_data(driver, url):
    wait = WebDriverWait(driver, 7)
    driver.maximize_window()
    driver.get(url)

    data_from_elem = {'ulr': url.removesuffix('characteristics/'), 'price': wait.until(EC.visibility_of_all_elements_located((
        By.CLASS_NAME, 'product-buy__price')))[0].text}

    options = wait.until(EC.visibility_of_all_elements_located(
        (By.CLASS_NAME, 'product-characteristics__spec')))

    for option in options:
        name = option.find_element(
            by=By.CLASS_NAME, value='product-characteristics__spec-title').text
        value = option.find_element(
            by=By.CLASS_NAME, value='product-characteristics__spec-value').text
        data_from_elem[name] = value

    with open('result.json', 'a', encoding='utf-8') as f:
        json.dump(data_from_elem, f, ensure_ascii=False, indent=4)


@timing_val
def main():
    urls = get_urls(
        "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/")

    thread_count = 12  # int(os.environ['NUMBER_OF_PROCESSORS'])
    apps = [get_driver() for _ in range(thread_count)]
    print(len(urls))
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        executor.map(parse_data, cycle(apps), urls)
    [app.close() for app in apps]


if __name__ == '__main__':
    main()
