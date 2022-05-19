from doctest import OPTIONFLAGS_BY_NAME
from filecmp import clear_cache
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def close_popups(wait):
    city_popup = wait.until(EC.presence_of_element_located((
        By.CLASS_NAME, 'confirm-city-mobile__accept')))
    city_popup.click()
    build_mode_popup = wait.until(EC.presence_of_element_located((
        By.CLASS_NAME, 'catalog-rsu-switch__new-tip-close')))
    build_mode_popup.click()



url = "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?from_search=1&order=6&stock=now-today-tomorrow-later-out_of_stock"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors-spki-list')
chrome_options.add_argument('log-level=3')
# chrome_options.add_argument("headless") нужно ещё разобраться

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 3)
actions = ActionChains(driver)

driver.get(url)

page = driver
data_results = []

bottom_navbar_offset = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'bottom-navbar-mobile__btn'))).rect['height']

while True:
    elems = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, '[data-id="product"]')))
    for elem in elems:
        elem_data = {}
        elem_url = elem.find_element(By.CLASS_NAME, "catalog-product__name").get_attribute('href')
        driver.get(elem_url)
        data_from_elem = {'ulr': elem_url, 'price': wait.until(EC.presence_of_element_located((
            By.CLASS_NAME, 'product-buy__price'))).text}

        button_options_expand = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'product-characteristics__expand')))
        actions.move_to_element_with_offset(button_options_expand, 0, bottom_navbar_offset)
        actions.click()

        options = wait.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 'product-characteristics__spec')))

        for option in options:
            name = option.find_element(
                by=By.CLASS_NAME, value='product-characteristics__spec-title').text
            value = option.find_element(
                by=By.CLASS_NAME, value='product-characteristics__spec-value').text
            elem_data[name] = value
        data_results.append(elem_data)

        driver.back()

    next_page = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'pagination-widget__page-link_next')))
    if 'pagination-widget__page-link_disabled' in next_page.get_attribute("class"):
        break
    
with open('result.txt', 'w') as f:
    f.write(data_results)
driver.close()
