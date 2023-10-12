'''
Leonov Kirill - 80
Elizarev Yaroslav - 50
'''

import requests
import json
import pandas as pd


def indexing(repeats):
    start = 0
    list_to_return = []
    for i in range(repeats):
        index = html_text.find('<div class="x-product-card__card"', start + 1)
        list_to_return.append(index)
        start = index
    return list_to_return


text = input('Введите интересующий вас товар:\n')
url_search = 'https://www.lamoda.ru/catalogsearch/result/'
number_of_page = 0
list_of_links = []

while True:
    number_of_page += 1
    params_to_get = {'q': text, 'page': number_of_page}
    response = requests.get(url_search, params=params_to_get)
    html_text = response.text

    grid_catalog_index = html_text.find('<div class="grid__catalog">')
    if grid_catalog_index == -1:
        break
    html_text = html_text[grid_catalog_index:]  # урежем html-страницу, отбросив все до начала каталога товаров
    grid_catalog_count = html_text.count('<div class="x-product-card__card"')   # количество товаров в каталоге на стр.
    list_of_indexes = indexing(grid_catalog_count)

    list_of_items_coded = []
    for index in range(len(list_of_indexes) - 1):
        list_of_items_coded.append(html_text[list_of_indexes[index]: list_of_indexes[index+1]])
    list_of_items_coded.append(html_text[list_of_indexes[-1]:])
    
    for part_of_code in list_of_items_coded:
        link = ''
        a_href = part_of_code.find('<a href="')

        for symbol in part_of_code[a_href + 9:]:
            if symbol != '"':
                link += symbol
            else:
                list_of_links.append(link)
                break
print('Ссылки на карточки товаров нафармлены, теперь ожидайте появления файла lamoda.xlsx в папке с проектом')

# здесь начну код по парсингу теперь уже карточек товаров
url_general = 'https://www.lamoda.ru'
df_python = []

for link in list_of_links:
    url_item = url_general + link
    response = requests.get(url_item)

# основные данные: бренд, наименование, цена, артикул
    item_html = response.text
    data_index = item_html.rfind('<script type="application/ld+json">')
    item_html = item_html[data_index:]
    index_of_left_bracket = item_html.find('{')
    index_of_right_bracket = item_html.rfind('}')
    item_html = item_html[index_of_left_bracket: index_of_right_bracket + 1]

    try:
        dict_data = json.loads(item_html)

        name_crude = dict_data['name']
        name_crude = name_crude.replace('&quot;', '', 1)
        brand = name_crude[0: name_crude.find('&')]

        name_crude = name_crude[name_crude.find('&'):]
        name_crude = name_crude.replace('&quot;', '')
        name = name_crude.strip()

        price = int(float(dict_data['offers']['price']))

        vendor_code = dict_data['offers']['sku']

        discount = 'Строка, которую мы никогда не увидим'
        
    except json.JSONDecodeError:
        brand = None
        name = None
        price = -1
        vendor_code = None
        discount = None

# парсим страну производства - для этой части кода не выявлено товаров, заставивших бы код упасть с ошибкой
    item_html_country = response.text
    item_html_country = item_html_country[item_html_country.find('<div id="modals">'):]
    item_html_country = item_html_country[item_html_country.find('<script>'):]
    item_html_country = item_html_country[0: item_html_country.find('</script>')]
    item_html_country = item_html_country[item_html_country.find('{'): item_html_country.rfind('}') + 1]
    item_html_country = item_html_country[item_html_country.find('Страна производства'):]
    item_html_country = item_html_country[item_html_country.find(':') + 1:]
    item_html_country = item_html_country[0: item_html_country.find('}')]
    country = item_html_country.strip('"')

# парсим цену без скидки (для товаров без акций получится обычная цена) и определяем саму скидку
    try:
        item_html_discount = response.text
        span_class_index = item_html_discount.find('span class="x-premium-product-prices__price "')
        item_html_discount = item_html_discount[span_class_index:]
        item_html_discount = item_html_discount[item_html_discount.find('content'):]
        item_html_discount = item_html_discount[item_html_discount.find('"') + 1:]
        item_html_discount = item_html_discount[0: item_html_discount.find('"')]

        price_without_discount = int(float(item_html_discount))
        if discount is not None:
            discount = '{:.0%}'.format(1 - price / price_without_discount)
    except ValueError:
        discount = 'Нет в наличии'
        price = 'Нет в наличии'

    df_python.append([vendor_code, brand, name, price, discount, country, url_item])

df = pd.DataFrame(data=df_python, columns=['vendor_code', 'brand', 'model', 'price', 'discount', 'country', 'link'])
df_available = df[df['price'] != 'Нет в наличии']
df_available = df_available.sort_values(by='price', ascending=True)
df_not_available = df[df['price'] == 'Нет в наличии']
df = pd.concat([df_available, df_not_available]).reset_index(drop=True)
df_complete = df[df['price'] != -1]
df_complete = df_complete[['vendor_code', 'brand', 'model', 'price', 'discount', 'country']]
df_incomplete = df[df['price'] == -1]

with pd.ExcelWriter('lamoda.xlsx') as writer:
    df_complete.to_excel(writer, sheet_name='Полные данные', index=False)
    df_incomplete.to_excel(writer, sheet_name='Неполные данные', index=False)
