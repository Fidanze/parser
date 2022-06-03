import time
import os
from concurrent.futures import ThreadPoolExecutor
import json
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from WindowsPool import WindowsPool


def get_city_urls(window, url: str) -> List[str]:
    window.open(url)
    urls = []

    while True:
        elems = window.wait.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "catalog-product__name")))

        urls.extend([elem.get_attribute('href') +
                    'characteristics/' for elem in elems])

        next_page = window.wait.until(EC.visibility_of_element_located((
            By.CLASS_NAME, 'pagination-widget__page-link_next')))
        if 'pagination-widget__page-link_disabled' in next_page.get_attribute("class"):
            break
        else:
            window.driver.get(next_page.get_attribute('href'))

    return urls


def gen_next(gen):
    result = []
    while True:
        try:
            result.append(next(gen))
        except StopIteration:
            break
    return result


def parse_data(pool, urls: List[str]):
    window = pool.pop_window()
    while True:
        if len(urls):
            url = urls.pop()
            window.open(url)
        else:
            pool.put_window(window)
            break

        data_from_elem = {'ulr': url.removesuffix('characteristics/'), 'price': window.wait.until(EC.visibility_of_all_elements_located((
            By.CLASS_NAME, 'product-buy__price')))[0].text}

        options = window.wait.until(EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, 'product-characteristics__spec')))

        for option in options:
            name = option.find_element(
                by=By.CLASS_NAME, value='product-characteristics__spec-title').text
            value = option.find_element(
                by=By.CLASS_NAME, value='product-characteristics__spec-value').text
            data_from_elem[name] = value

        yield data_from_elem


def main():
    folder_path = os.path.dirname(__file__)
    url = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/'

    with open('cities.json', 'r', encoding='utf-8') as f:
        cities = json.load(f)

    pool = WindowsPool()
    for city in cities:
        t1 = time.time()
        pool.set_city(city)
        main_window = pool.pop_window()
        urls = get_city_urls(main_window, url)
        pool.put_window(main_window)

        THREAD_COUNT = int(os.environ['NUMBER_OF_PROCESSORS'])
        gens = [parse_data(pool, urls) for _ in range(THREAD_COUNT)]
        with ThreadPoolExecutor(THREAD_COUNT) as executor:
            city_data_generator = executor.map(gen_next, gens)
        city_data = []
        [city_data.extend(data) for data in city_data_generator]
        city_file_path = os.path.join(
            folder_path, f'cities\{city}.json')
        with open(city_file_path, 'w', encoding='utf-8') as f:
            json.dump(city_data, f, ensure_ascii=False, indent=4)
        t2 = time.time()
        print(f'{t2-t1} seconds for {city}')

    del pool


if __name__ == '__main__':
    t1 = time.time()
    main()
    t2 = time.time()
    print(t2-t1)
