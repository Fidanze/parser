from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process
import os
from Window import Window


class CustomProcess(Process):
    def __init__(self):
        super().__init__()
        self._window = None

    def run(self):
        '''
        Method to be run in sub-process; can be overridden in sub-class
        '''
        self._window = Window() if not self._window else self._window
        if self._target:
            self._target(self._window, *self._args, **self._kwargs)

    def join(self):
        super().join()
        self._popen = None

    def set_task(self, target, args=(), kwargs={}):
        # self._window = Window()
        self._target = target
        self._args = tuple(args)
        # kwargs['window'] = self._window
        self._kwargs = dict(kwargs)


def func(window, x):
    window.open('https://www.google.com')
    x = x+5
    print(x**2)


def func1(x):
    x = x+5
    print(x**2)


def op(n):
    with open('asda.txt', 'a') as f:
        f.write(f'{os.getpid()} was here\n')
    print('hey')


if __name__ == '__main__':
    # # freeze_support()
    # c = CustomProcess()
    # c.set_task(func, args=(11,))
    # c.start()
    # c.join()
    # c.set_task(func, args=(12,))
    # c.start()
    # c.join()
    # print('asdasdasds')

    with ProcessPoolExecutor(5) as executor:
        gen_product_availabilities = executor.map(op, list(range(20)))



import time
import os
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from Window import Window
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

NUMBER_OF_PROCESSORS = int(os.environ['NUMBER_OF_PROCESSORS'])//2


def timing_val(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        print(t2-t1)
        return res
    return wrapper

def chunkify(lst,n):
    return [lst[i::n] for i in range(n)]

def get_number_of_pages(url: str) -> int:
    window = Window()
    window.open(url)
    last_page_elem = window.wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, 'pagination-widget__page-link_last')))
    number_of_pages = int(
        last_page_elem.get_attribute('href').split('?p=')[-1])
    return number_of_pages

def get_product_urls_from_page(window, page_url: str) -> List[str]:
    window.open(page_url)
    products = window.wait.until(EC.visibility_of_all_elements_located((
        By.CLASS_NAME, 'catalog-product__name')))
    result = [product.get_attribute('href') +
              'characteristics/' for product in products]
    return result

def get_product_options(window, product_url: str) -> dict[str, str]:
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
    return product_options

def get_availability(page_url: str)-> None:
    window = Window()
    window.open(page_url)
    results = []
    names = window.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.catalog-products.view-simple > div > a')))
    prices = window.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.catalog-products.view-simple > div > div.product-buy.product-buy_one-line.catalog-product__buy > div > div.product-buy__price')))
    buttons = window.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.product-buy.product-buy_one-line.catalog-product__buy > button.button-ui.button-ui_white.button-ui_icon.wishlist-btn + button')))
    for data in zip(names, prices, buttons):
        # button = buttons[1].text if len(buttons) == 2 else 'Аналоги'
        results.append({'name': data[0].get_attribute('href') + 'characteristics/', 'price': data[1].text.split('\n')[0],
                        'available': True if data[2].text == 'Купить' else False})
    #|----------------------------|
    #| not implement yet          |
    #| send_result_to_db(results) |
    #|----------------------------|
    window.close()

def get_availability1(pages: list[str])-> None:
    window = Window()
    for page_url in pages:
        window.open(page_url)
        results = []
        names = window.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.catalog-products.view-simple > div > a')))
        prices = window.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.catalog-products.view-simple > div > div.product-buy.product-buy_one-line.catalog-product__buy > div > div.product-buy__price')))
        buttons = window.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.product-buy.product-buy_one-line.catalog-product__buy > button.button-ui.button-ui_white.button-ui_icon.wishlist-btn + button')))
        for data in zip(names, prices, buttons):
            # button = buttons[1].text if len(buttons) == 2 else 'Аналоги'
            results.append({'name': data[0].get_attribute('href') + 'characteristics/', 'price': data[1].text.split('\n')[0],
                            'available': True if data[2].text == 'Купить' else False})
        #|----------------------------|
        #| not implement yet          |
        #| send_result_to_db(results) |
        #|----------------------------|
    window.close()

def parse_options(url: str):

    pages = [f'{url}?p={i+1}' for i in range(get_number_of_pages(url))]
    print('Got pages')

    with ThreadPoolExecutor(NUMBER_OF_PROCESSORS) as executor:
        gen_product_urls = executor.map(get_product_urls_from_page, pages)

    products_url = []
    for product_url in gen_product_urls:
        products_url.extend(product_url)
    print('Got links from pages')

    with ThreadPoolExecutor(NUMBER_OF_PROCESSORS) as executor:
        gen_products_options = executor.map(get_product_options, products_url)

    products = []
    for product_options in gen_products_options:
        products.append(product_options)
    print('Got product options')

def parse_availability_thread(pages: list[str]):
    print('start parse_availability_thread')
    t1 = time.time()

    with ThreadPoolExecutor(NUMBER_OF_PROCESSORS) as executor:
        executor.map(get_availability, pages)
    
    t2 = time.time()
    print('end parse_availability_thread')
    return t2-t1

def parse_availability_process(pages: list[str]):
    print('start parse_availability_process')
    t1 = time.time()

    with ProcessPoolExecutor(NUMBER_OF_PROCESSORS) as executor:        
        executor.map(get_availability, pages)
    
    t2 = time.time()
    print('end parse_availability_process')
    return t2-t1

def parse_availability_thread1(pages: list[str]):
    print('start parse_availability_thread1')
    t1 = time.time()

    with ThreadPoolExecutor(NUMBER_OF_PROCESSORS) as executor:
        executor.map(get_availability1, chunkify(pages, NUMBER_OF_PROCESSORS))
    
    t2 = time.time()
    print('end parse_availability_thread1')
    return t2-t1

def parse_availability_process1(pages: list[str]):
    print('start parse_availability_process1')
    t1 = time.time()

    with ProcessPoolExecutor(NUMBER_OF_PROCESSORS) as executor:        
        executor.map(get_availability1, chunkify(pages, NUMBER_OF_PROCESSORS))
    
    t2 = time.time()
    print('end parse_availability_process1')
    return t2-t1

if __name__ == '__main__':
    short_url = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/'
    long_url = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?stock=now-today-tomorrow-later-out_of_stock'
    
    # short_pages = [f'{short_url}?p={i+1}' for i in range(get_number_of_pages(short_url))]
    long_pages = [f'{long_url}?p={i+1}' for i in range(get_number_of_pages(long_url))]
    results:list[float] = []
    
    # results.append(parse_availability_thread(short_pages))
    # results.append(parse_availability_process(short_pages))
    # results.append(parse_availability_thread1(short_pages))
    # results.append(parse_availability_process1(short_pages))
    # results.append(parse_availability_thread(long_pages))
    # results.append(parse_availability_process(long_pages))
    results.append(parse_availability_thread1(long_pages))
    results.append(parse_availability_process1(long_pages))
    results.append('')
    NUMBER_OF_PROCESSORS = int(os.environ['NUMBER_OF_PROCESSORS'])
    # results.append(parse_availability_thread(short_pages))
    # results.append(parse_availability_process(short_pages))
    # results.append(parse_availability_thread1(short_pages))
    # results.append(parse_availability_process1(short_pages))
    # results.append(parse_availability_thread(long_pages))
    # results.append(parse_availability_process(long_pages))
    results.append(parse_availability_thread1(long_pages))
    results.append(parse_availability_process1(long_pages))
    results.append('')
    NUMBER_OF_PROCESSORS = int(os.environ['NUMBER_OF_PROCESSORS'])*2
    # results.append(parse_availability_thread(short_pages))
    # results.append(parse_availability_process(short_pages))
    # results.append(parse_availability_thread1(short_pages))
    # results.append(parse_availability_process1(short_pages))
    # results.append(parse_availability_thread(long_pages))
    # results.append(parse_availability_process(long_pages))
    results.append(parse_availability_thread1(long_pages))
    results.append(parse_availability_process1(long_pages))
    print(*results, sep='\n')
    # <-------------------------------------------------------->
    # short url
    # 65.34538650512695 threads   with reopenning browsers
    # 73.6933228969574 processes  with reopenning browsers
    # 57.03972387313843 threads   without reopenning browsers
    # 58.94383430480957 processes without reopenning browsers
    # ---------------------------------------------------------
    # long url
    # 540.5564613342285 threads   with reopenning browsers
    # 469.43031334877014 processes  with reopenning browsers
    # 268.3258693218231 threads   without reopenning browsers
    # 267.7682032585144 processes without reopenning browsers
    # <-------------------------------------------------------->
    # увеличим кол-во потоков/процессов в 2 раза
    # <-------------------------------------------------------->
    # short url
    # 56.79016900062561 threads   with reopenning browsers
    # 57.2951557636261 processes  with reopenning browsers
    # 53.06681799888611 threads   without reopenning browsers 
    # 54.66286253929138 processes without reopenning browsers
    # ---------------------------------------------------------
    # long url
    # 348.397253036499 threads   with reopenning browsers 
    # 379.429696559906  processes  with reopenning browsers
    # 212.1985104084015 threads   without reopenning browsers 
    # 196.88433694839478 processes without reopenning browsers
    # <-------------------------------------------------------->
    # выводы:
    # 1) без переоткрывания быстрее
    # 2) перезапуск процесса происходит дольше перезапуска потока
    # 3) большой прирост скорости может дать изменение алгоритма сбора цены и наличия и отказ от time.sleep(10)
    #        последнее может занимать до 10*(130/number_of_proceessors) секунд + (разница в запуске и окончании между процессами)
    # <-------------------------------------------------------->
    # увеличим кол-во потоков/процессов в 3 раза
    # <-------------------------------------------------------->
    # short url
    # 65.36422348022461  threads   without reopenning browsers 
    # 62.728652477264404 processes without reopenning browsers
    # ---------------------------------------------------------
    # long url
    # 207.76291418075562 threads   without reopenning browsers !
    # 202.87267780303955 processes without reopenning browsers
    # <-------------------------------------------------------->
    # выводы:
    # 1) нельзя сказать точно что излишнее увеличение максимального числа потоков/процессов замедляет процесс
    # 2) используя этот компьютер ускорить процесс лишь за счёт увеличения максимального числа потоков/процессов невозможно 
    # 3) на данный момент необходимое время ~ 200 секунд


    # 58.53822064399719
    # 59.16045784950256
    # 46.70982623100281
    # 46.249165058135986
    # 422.93809032440186
    # 423.917049407959
    # 232.94992184638977
    # 239.93709182739258
    # 36.67730784416199
    # 37.39177870750427
    # 38.160741090774536
    # 38.867026567459106
    # 271.21772599220276
    # 267.339852809906
    # 152.58481550216675
    # 163.76456713676453
    # 43.06020259857178
    # 41.570491313934326
    # 43.069931983947754
    # 42.554829120635986
    # 284.01519322395325
    # 252.9826889038086
    # 147.96495747566223
    # 150.05299353599548
    # выводы:
    # нет смысла сильно увеличивать количество потоков/процессов более чем на 2
    # 8 => 10
    # 16 => 18
    # только short urls и без переоткрытия
    # 8 
    # 26.278136730194092
    # 27.682558059692383
    # 16
    # 30.844932079315186
    # 30.094597816467285
    # 18
    # 31.233699321746826
    # 34.372382402420044  
    # выводы:
    # нет смысла увеличивать кол-во потоков/процессов больше чем os.environ['NUMBER_OF_PROCESSORS']
    # изменения алгоритма ожидания цены, названия и наличия ускорили в short urls почти на 50%
    # проверим long_urls
    # 8 
    # 92.71243643760681
    # 97.38141512870789
    # 16
    # 105.71908354759216
    # 106.78847479820251
    # 18
    # 119.3249032497406
    # 112.92402195930481
    # выводы:
    # гипотеза о том что максимум потоков/процессов равен os.environ['NUMBER_OF_PROCESSORS'] подтвердилась
    # однако необычно то что в этот раз 8 потоков быстрее всех
    # 8
    # 97.25979804992676
    # 92.09092903137207
    # 16
    # 114.98018836975098
    # 108.26393914222717     