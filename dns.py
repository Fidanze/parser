import time
import os
from concurrent.futures import ThreadPoolExecutor
import json
from typing import List
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from WindowsPool import WindowsPool

URL = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/'


def timing_val(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        print(t2-t1)
        return res
    return wrapper


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


@timing_val
def gen_next(gen):
    result = []
    while True:
        try:
            result.append(next(gen))
        except StopIteration:
            break
    return result


def parse_data(pool, place: str):
    window = pool.pop_window()
    window.open(URL)
    window.set_place(place.split('___'))
    results = []
    while True:
        try:
            show_more_button = window.driver.find_element(
                By.CSS_SELECTOR, '#products-list-pagination > button')
            show_more_button.click()
        except NoSuchElementException:
            break
        except:
            pass

    elems = window.driver.find_elements(
        By.CLASS_NAME, "catalog-product__name")

    results.extend([elem.get_attribute('href') +
                    'characteristics/' for elem in elems])
    pool.put_window(window)
    yield results


@timing_val
def main():

    with open('cities.json', 'r', encoding='utf-8') as f:
        places = json.load(f)

    pool = WindowsPool()
    THREAD_COUNT = int(os.environ['NUMBER_OF_PROCESSORS'])
    gens = [parse_data(pool, place) for place in places]

    with ThreadPoolExecutor(THREAD_COUNT) as executor:
        city_data_generator = executor.map(gen_next, gens)

    res = []
    [res.extend(data) for data in city_data_generator]

    # city_file_path = os.path.join(
    #     os.getcwd(), f'cities\{city}.json')
    with open('res.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)
    del pool


if __name__ == '__main__':
    main()
