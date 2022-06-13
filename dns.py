import time
import os
from concurrent.futures import ThreadPoolExecutor
import json
from typing import List
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from WindowsPool import WindowsPool
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

def init_funcs(pool:WindowsPool):
    def get_number_of_pages(url: str) -> int:
        window = pool.pop_window()
        window.open(url)
        last_page_elem = window.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'pagination-widget__page-link_last')))
        number_of_pages = int(last_page_elem.get_attribute('href').split('?p=')[-1])
        pool.put_window(window)
        return number_of_pages

    def get_products_urls_from_page(page_url: str) -> List[str]:
        window = pool.pop_window()
        window.open(page_url)
        
        products = window.wait.until(EC.visibility_of_all_elements_located((
                    By.CLASS_NAME, 'catalog-product__name')))

        result = [product.get_attribute('href')+
                                'characteristics/' for product in products]
        pool.put_window(window)
        return result

    def get_product_options(product_url: str) -> dict[str,str]:
        window = pool.pop_window()
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
        pool.put_window(window)
        return product_options

    return get_number_of_pages, get_products_urls_from_page, get_product_options

def parse_options(url:str)->list[dict[str,str]]:
    
    pool = WindowsPool()
    get_number_of_pages, get_products_urls_from_page, get_product_options = init_funcs(pool)
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

if __name__ == '__main__':
    url = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?stock=now-today-tomorrow-later-out_of_stock'
    products = parse_options(url)
    print('')