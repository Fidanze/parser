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
chrome_options.add_argument("--incognito")
# chrome_options.add_argument("headless") нужно ещё разобраться

driver = webdriver.Chrome(options=chrome_options)

wait = WebDriverWait(driver, 5)
actions = ActionChains(driver)

driver.get(url)
close_popups(wait)

button_show_more = wait.until(EC.presence_of_element_located((
    By.CSS_SELECTOR, '[data-role="show-more-btn"]')))
button_show_more = wait.until(EC.presence_of_element_located((
    By.CSS_SELECTOR, '[text="ещё"]')))
while button_show_more.is_displayed() and button_show_more.text:
    # actions.move_to_element(button_show_more).perform()
    # кликаем на кнопку, через click не срабатывает тк, меню снизу закреплено и мешает
    button_show_more.send_keys('\ue007')
    button_show_more = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, '[text="ещё"]')))
# elems = wait.until(EC.presence_of_all_elements_located(
#     (By.CSS_SELECTOR, '[data-id="product"]')))
# data_results = []
# for elem in elems:
#     elem_url = wait.until(EC.presence_of_element_located(
#         (By.CLASS_NAME, "catalog-product__name"))).get_attribute('href')
#     driver.get(elem_url)
#     data_from_elem = {'ulr': elem_url, 'price': wait.until(EC.presence_of_element_located((
#         By.CLASS_NAME, 'data_from_elem')))}
#     elem_options = driver.find_elements(
#         by=By.CLASS_NAME, value='product-characteristics__spec')
#     for elem_option in elem_options:
#         elem_option_name = elem_option.find_element(
#             by=By.CLASS_NAME, value='product-characteristics__spec-title').text
#         elem_option_value = elem_option.find_element(
#             by=By.CLASS_NAME, value='product-characteristics__spec-value').text
#         data_from_elem[elem_option_name] = elem_option_value
#     data_results.append(data_from_elem)
#     driver.back()
# print(data_results)
driver.close()
