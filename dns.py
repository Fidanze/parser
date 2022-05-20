from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import json

url = "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?f[mx]=2fi-2fh-dbbc"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors-spki-list')
chrome_options.add_argument('log-level=3')

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)
actions = ActionChains(driver)
driver.maximize_window()
driver.get(url)

data_results = []
original_window = driver.current_window_handle


while True:
    elems = wait.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "catalog-product__name")))
    for elem in elems:
        elem_url = elem.get_attribute('href')

        # elem.send_keys(Keys.CONTROL + Keys.ENTER)
        driver.switch_to.new_window('tab')
        driver.get(elem_url)

        wait.until(EC.number_of_windows_to_be(2))

        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break

        data_from_elem = {'ulr': elem_url, 'price': wait.until(EC.presence_of_element_located((
            By.CLASS_NAME, 'product-buy__price'))).text}

        button_options_expand = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'product-characteristics__expand')))
        button_options_expand.click()

        options = wait.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 'product-characteristics__spec')))

        for option in options:
            name = option.find_element(
                by=By.CLASS_NAME, value='product-characteristics__spec-title').text
            value = option.find_element(
                by=By.CLASS_NAME, value='product-characteristics__spec-value').text
            data_from_elem[name] = value
        data_results.append(data_from_elem)

        driver.close()
        driver.switch_to.window(original_window)

    next_page = driver.find_element(
        By.CLASS_NAME, 'pagination-widget__page-link_next')
    if 'pagination-widget__page-link_disabled' in next_page.get_attribute("class"):
        break

    driver.get(next_page.get_attribute('href'))

with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(data_results, f, ensure_ascii=False, indent=4)
driver.close()
