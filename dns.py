import requests
from bs4 import BeautifulSoup as bs

response = requests.get(
    "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?from_search=1&order=6&stock=now-today-tomorrow-later-out_of_stock")
while True:
    soup = bs(response.content, 'html.parser')
    print(response)
