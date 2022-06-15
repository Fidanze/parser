import time
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from queue import Queue
from Window import Window


THREAD_COUNT = int(os.environ['NUMBER_OF_PROCESSORS'])


def timing_val(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        print(t2-t1)
        return res
    return wrapper


def init_funcs(pool: Queue):
    def get_number_of_pages(url: str) -> int:
        if pool.empty():
            window = Window()
        else:
            window = pool.get()
        window.open(url)
        last_page_elem = window.wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'pagination-widget__page-link_last')))
        number_of_pages = int(
            last_page_elem.get_attribute('href').split('?p=')[-1])
        pool.put(window)
        return number_of_pages

    def get_product_urls_from_page(page_url: str) -> List[str]:
        if pool.empty():
            window = Window()
        else:
            window = pool.get()
        window.open(page_url)

        products = window.wait.until(EC.visibility_of_all_elements_located((
            By.CLASS_NAME, 'catalog-product__name')))

        result = [product.get_attribute('href') +
                  'characteristics/' for product in products]
        pool.put(window)
        return result

    def get_availability(page_url: str) -> list[dict[str, str]]:
        if pool.empty():
            window = Window()
        else:
            window = pool.get()
        window.open(page_url)

        products = window.wait.until(EC.visibility_of_all_elements_located((
            By.CLASS_NAME, 'catalog-product')))
        results = []
        time.sleep(10)
        for product in products:
            name = product.find_element(
                By.CLASS_NAME, 'catalog-product__name').get_attribute('href') + 'characteristics/'
            price = product.find_element(
                By.CLASS_NAME, 'product-buy__price').text.split('\n')[0]
            buttons = product.find_elements(By.TAG_NAME, 'button')
            button = buttons[1].text if len(buttons) == 2 else 'Аналоги'
            results.append({'name':name,'price': price,
                             'available': True if button == 'Купить' else False})
        pool.put(window)
        return results

    def get_product_options(product_url: str) -> dict[str, str]:
        if pool.empty():
            window = Window()
        else:
            window = pool.get()
        window.open(product_url)

        options = window.wait.until(EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, 'product-characteristics__spec')))

        product_options = {}
        for option in options:
            name = option.find_element(
                by=By.CLASS_NAME, value='product-characteristics__spec-title').text
            value = option.find_element(
                by=By.CLASS_NAME, value='product-characteristics__spec-value').text
            product_options[name] = value
        pool.put(window)
        return product_options

    return get_number_of_pages, get_product_urls_from_page, get_product_options, get_availability


def parse_options(url: str) -> list[dict[str, str]]:

    pool: Queue = Queue(THREAD_COUNT)
    get_number_of_pages, get_products_urls_from_page, get_product_options, _ = init_funcs(
        pool)
    pages = [f'{url}?p={i+1}' for i in range(get_number_of_pages(url))]
    print('Got pages')

    with ThreadPoolExecutor(THREAD_COUNT) as executor:
        gen_product_urls = executor.map(get_products_urls_from_page, pages)

    products_url = []
    for product_url in gen_product_urls:
        products_url.extend(product_url)
    print('Got links from pages')

    with ThreadPoolExecutor(THREAD_COUNT) as executor:
        gen_products_options = executor.map(get_product_options, products_url)

    products = []
    for product_options in gen_products_options:
        products.append(product_options)
    print('Got product options')
    del pool
    return products


def parse_availability(url: str) -> list[dict[str, str]]:
    pool: Queue = Queue(THREAD_COUNT)
    get_number_of_pages, _, _, get_availability = init_funcs(
        pool)
    pages = [f'{url}?p={i+1}' for i in range(get_number_of_pages(url))]
    print('Got pages')
    t1 = time.time()
    with ThreadPoolExecutor(THREAD_COUNT) as executor:
        gen_product_availabilities = executor.map(get_availability, pages)
    t2 = time.time()
    print(t2-t1)
    product_availabilities = [product_availability for product_availabilities in gen_product_availabilities for product_availability in product_availabilities ]
    print('Got availabilities')

    del pool
    return product_availabilities


if __name__ == '__main__':
    url = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/'
    # url = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?stock=now-today-tomorrow-later-out_of_stock'
    # product_options = parse_options(url)
    product_availability = parse_availability(url)
