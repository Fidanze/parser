from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

url = "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?from_search=1&order=6&stock=now-today-tomorrow-later-out_of_stock"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors-spki-list')
chrome_options.add_argument('log-level=3')
# chrome_options.add_argument("headless") нужно ещё разобраться

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)
driver.get(url)
data_results = []
# get urls of products
elems_urls = [elem.get_attribute('href') for elem in driver.find_elements(
    by=By.CLASS_NAME, value="catalog-product__name")]
elem_data = {}
for elem_url in elems_urls:
    driver.get(elem_url)
    # add url to product and price to data
    elem_data['ulr'] = elem_url
    elem_data['price'] = driver.find_element(
        by=By.CLASS_NAME, value='product-buy__price').text
    button_options_expand = driver.find_element(
        by=By.CLASS_NAME, value='product-characteristics__expand')
    button_options_expand.click()
    options = driver.find_elements(
        by=By.CLASS_NAME, value='product-characteristics__spec')
    for option in options:
        name = option.find_element(
            by=By.CLASS_NAME, value='product-characteristics__spec-title').text
        value = option.find_element(
            by=By.CLASS_NAME, value='product-characteristics__spec-value').text
        elem_data[name] = value
    data_results.append(elem_data)
    elem_data = {}
print(data_results)
driver.close()
