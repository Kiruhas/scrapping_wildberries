import requests
from bs4 import BeautifulSoup
import json
import time
import os
import csv

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en,ru;q=0.9",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Mobile Safari/537.36"
}

############# Забираем все конечные ссылки ##############

# url = "https://wbxmenu-ru.wildberries.ru/v6/api?_app-type=sitemobile&locale=ru&lang=ru"
# req = requests.get(url=url, headers=headers)

# with open("categories.json", "w", encoding="utf=8") as file:
#     json.dump(req.json(), file, indent=4, ensure_ascii=False)

# with open("categories.json", encoding="utf=8") as file:
#     categories = json.load(file)

# categories = list(categories["data"].items())[0][1]
# data = {}
# count = 0
# catalog_name = "data"


# def checkChilds(categories):
#     global count, catalog_name
#     for cat in categories:
#         last_catalog_name = catalog_name
#         cat_id = cat["id"]
#         cat_name = cat["name"].replace("/", " & ").strip()
#         cat_key = "none"
#         cat_query = "none"
#         catalog_name += f"/{cat_name}"

#         if os.path.isdir(catalog_name):
#             pass
#         else:
#             os.mkdir(catalog_name)

#         if "shardKey" in cat:
#             cat_key = cat["shardKey"]

#         if "childNodes" in cat:
#             checkChilds(cat["childNodes"])

#         if "query" in cat:
#             cat_query = cat["query"]

#         cat_url = f"https://www.wildberries.ru{cat['pageUrl']}"

#         if "childNodes" in cat:
#             catalog_name = catalog_name.rsplit('/', 1)[0]
#             continue

#         data[count] = {
#             "id": cat_id,
#             "catalog_name": catalog_name,
#             "name": cat_name,
#             "shardKey": cat_key,
#             "query": cat_query,
#             "url": cat_url,
#         }
#         count += 1
#         catalog_name = last_catalog_name
#     return data


# cat_json = checkChilds(categories)

# with open("categories_end.json", "w", encoding="utf=8") as file:
#     json.dump(cat_json, file, indent=4, ensure_ascii=False)

############# ------------------------------------- ##############

############# Заходим на каждую страницу ##############

with open("categories_end.json", encoding="utf=8") as file:
    categories = json.load(file)

count = 0
for cat in categories.items():
    if count < 10:
        cat = cat[1]
        url = f"https://wbxcatalog-ru.wildberries.ru/{cat['shardKey']}/filters?{cat['query']}&locale=ru"
        req = requests.get(url=url, headers=headers)
        res = req.json()
        total = res['data']['total']
        total_pages = int(round((total / 99)))
        if total_pages > 100:
            total_pages = 100
        page = 0
        while page < total_pages:
            page += 1
            if page == 1:
                url = f"https://wbxcatalog-ru.wildberries.ru/{cat['shardKey']}/catalog?{cat['query']}&locale=ru"
            else:
                url = f"https://wbxcatalog-ru.wildberries.ru/{cat['shardKey']}/catalog?{cat['query']}&page={page}&locale=ru"

            print(url)
            req = requests.get(url=url, headers=headers)
            res = req.json()

            with open(f"{cat['catalog_name']}/{page}_page.csv", "w") as file:
                writer = csv.writer(file, delimiter=';', lineterminator='\n')
                write_data = (
                    "ID",
                    "Наименование",
                    "Бренд",
                    "Цена без скидки",
                    "Цена со скидкой",
                    "Процент скидки",
                    "Рейтинг товара",
                    "Количество отзывов"
                )
                writer.writerow(write_data)

            products = list(res["data"].items())[0][1]
            for product in products:
                product_id = product["id"]
                product_name = product["name"]
                product_brand = product["brand"]
                product_price = int(product["priceU"] / 100)
                product_sale_price = int(product["salePriceU"] / 100)
                product_sale_percent = product["sale"]
                product_rating = product["rating"]
                product_feedbacks = product["feedbacks"]

                write_data = (
                    product_id,
                    product_name,
                    product_brand,
                    product_price,
                    product_sale_price,
                    product_sale_percent,
                    product_rating,
                    product_feedbacks
                )

                with open(f"{cat['catalog_name']}/{page}_page.csv", "a") as file:
                    writer = csv.writer(file, delimiter=';',
                                        lineterminator='\n')
                    writer.writerow(write_data)

            count += 1
            print(f"Завершено {count}/{total_pages} страниц")
            time.sleep(1)

print(f"Работа выполнена успешно!")
