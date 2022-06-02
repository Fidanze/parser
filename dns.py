import time
import os
from concurrent.futures import ThreadPoolExecutor
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from queue import Queue


def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('log-level=3')

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    return driver


def city_closure(current_city: str):
    def set_city(wait):
        button = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "v-confirm-city__link")))
        button.click()
        city_search_input = wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "base-ui-input-search__input")))
        city_search_input.send_keys(current_city)
        city_list = wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "cities-search")))
        while True:
            try:
                finded_cities = city_list.find_elements(
                    By.CLASS_NAME, 'modal-row')
                for city in finded_cities:
                    f_span = city.find_element(By.TAG_NAME, 'span')
                    s_span = f_span.find_element(By.TAG_NAME, 'spam')
                    if s_span.text == current_city:
                        s_span.click()
                        break
                else:
                    raise NoSuchElementException
                break
            except NoSuchElementException:
                city_search_input.send_keys(' ')

    return set_city


def get_urls(main_url):
    nonlocal city_setter
    driver = get_driver()
    wait = WebDriverWait(driver, 10)
    driver.get(main_url)
    city_setter(wait)
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


def parse_data():
    driver = apps_queue.get()
    wait = WebDriverWait(driver, 7)
    driver.maximize_window()
    is_first_url = True
    while True:
        url = urls.pop() if len(urls) else None
        if url is None:
            driver.close()
            break
        driver.get(url)
        if is_first_url:
            city_setter(wait)
            is_first_url = False

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

        yield data_from_elem


def gen_next(gen):
    while True:
        try:
            next(gen)
        except StopIteration:
            break


def parse_by_city(current_city):
    city_setter = city_closure(current_city)
    THREAD_COUNT = int(os.environ['NUMBER_OF_PROCESSORS'])//2
    apps_queue: Queue = Queue(THREAD_COUNT)
    urls = get_urls(
        'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/')
    for _ in range(THREAD_COUNT):
        apps_queue.put(get_driver())
    gens = [parse_data() for _ in range(THREAD_COUNT)]
    with ThreadPoolExecutor(THREAD_COUNT) as executor:
        current_city_data = executor.map(gen_next, gens)
    with open(f'./cities/{current_city}.json', 'w', encoding='utf-8') as f:
        json.dump(current_city_data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    t1 = time.time()
    with open('cities.json', 'r', encoding='utf-8') as f:
        cities = json.load(f)
    for current_city in cities:
        parse_by_city(current_city)
    t2 = time.time()
    print(t2-t1)
