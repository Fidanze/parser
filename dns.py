import time
import os
from concurrent.futures import ThreadPoolExecutor
import json
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from Window import Window
from WindowsPool import WindowsPool

URL = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/'


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


def parse_data(pool, places: List[List[str]]):
    window = pool.pop_window()
    while True:
        window.open(URL)
        if len(places):
            place = places.pop()
            window.set_place(place)
            res = 0
        else:
            pool.put_window(window)
            break
        elem = window.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'body > div.container.category-child > div > div.products-page__title > span')))
        res += int(elem.text.split()[0])
        # while True:
        #     elems = window.wait.until(EC.presence_of_all_elements_located(
        #         (By.CLASS_NAME, "catalog-product__name")))

        #     res += len(elems)
        #     next_page = window.wait.until(EC.visibility_of_element_located((
        #         By.CLASS_NAME, 'pagination-widget__page-link_next')))
        #     if 'pagination-widget__page-link_disabled' in next_page.get_attribute("class"):
        #         break
        #     else:
        #         window.driver.get(next_page.get_attribute('href'))

        yield [place, res]


def main():

    with open('cities.json', 'r', encoding='utf-8') as f:
        places = json.load(f)

    pool = WindowsPool()

    THREAD_COUNT = int(os.environ['NUMBER_OF_PROCESSORS'])
    gens = [parse_data(pool, places) for _ in range(THREAD_COUNT)]

    with ThreadPoolExecutor(THREAD_COUNT) as executor:
        city_data_generator = executor.map(gen_next, gens)

    res = []
    [res.extend(data) for data in city_data_generator]

    # city_file_path = os.path.join(
    #     os.getcwd(), f'cities\{city}.json')
    with open('res.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)
    del pool


def main1():

    pool = WindowsPool()
    window = pool.pop_window()
    data = []
    window.open(URL)
    window.open_place_menu()
    districts_zone = window.wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'districts')))
    districts = districts_zone.find_elements(By.CLASS_NAME, 'modal-row')
    for district in districts:
        district.click()
        regions_zone = window.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'regions')))
        regions = regions_zone.find_elements(By.CLASS_NAME, 'modal-row')
        for region in regions:
            region.click()
            cities_zone = window.wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'cities')))
            cities = cities_zone.find_elements(By.CLASS_NAME, 'modal-row')
            for city in cities:
                data.append([district.text, region.text, city.text])

    with open('true_cities.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    t1 = time.time()
    main()
    t2 = time.time()
    print(t2-t1)
