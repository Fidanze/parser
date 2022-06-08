from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Pool, current_process
import threading
import time
import os
import json
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from WindowsPool import WindowsPool

PLACE_COUNT = 3046


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


def chunkify(lst, n):
    return [lst[i::n] for i in range(n)]


def parse_data(pool, places):
    window = pool.pop_window()
    local_places = len(places)
    while places:
        place = places.pop()
        window.set_place(place.split('___'))
        while True:
            try:
                elem = window.wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'body > div.container.category-child > div > div.products-page__title > span')))
                counter = elem.text.split()[0]
                break
            except StaleElementReferenceException:
                pass
        process = current_process().name[-1]
        thread = threading.current_thread().name[-1::]
        print(
            f'{process}_{thread}: {str((1 - (len(places)/local_places))*100)[:7]} %')
        yield [place, counter]

    pool.put_window(window)


def process_main(places: List[str]):
    pool = WindowsPool()
    gens = [parse_data(pool, places) for _ in range(2)]

    with ThreadPoolExecutor(2) as executor:
        res_generator = executor.map(gen_next, gens)

    res = list(res_generator)
    with open('res.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)

    del pool


def main():
    with open('cities.json', 'r', encoding='utf-8') as f:
        places = json.load(f)

    NUMBER_OF_PROCESSORS = int(os.environ['NUMBER_OF_PROCESSORS'])
    pool = Pool(NUMBER_OF_PROCESSORS)

    with ProcessPoolExecutor(NUMBER_OF_PROCESSORS) as executor:
        executor.map(
            process_main, chunkify(places, NUMBER_OF_PROCESSORS))
    del pool


def main1():
    pool = WindowsPool()
    window = pool.pop_window()
    data = []
    # window.open(URL)
    window.open_place_menu()
    time.sleep(2)
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
                data.append('___'.join(
                    [district.text, region.text, city.text]))

    with open('true_cities.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    t1 = time.time()
    main()
    t2 = time.time()
    print(t2-t1)
