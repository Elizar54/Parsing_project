import requests

def indexing(repeats):
    start = 0
    list_of_indexes = []
    for i in range(repeats):
        index = html_text.find('<div class="x-product-card__card"', start + 1)
        list_of_indexes.append(index)
        start = index
    return list_of_indexes

text = input('Введите интересующий вас товар:\n')
url_search = 'https://www.lamoda.ru/catalogsearch/result/'
params_to_get = {'q' : text}
response = requests.get(url_search, params=params_to_get)
html_text = response.text
print(response.url)

print(len(html_text))   # 617962 символов

grid_catalog_index = html_text.find('<div class="grid__catalog">')
html_text = html_text[grid_catalog_index:]  # урежем html-страницу, отбросив все до начала каталога товаров
grid_catalog_count = html_text.count('<div class="x-product-card__card"')   # количество товаров в каталоге на странице
list_of_indexes = indexing(grid_catalog_count)
print(html_text.find('"/p/rtlacv440501/shoes-reebok-kedy/"'))
print(list_of_indexes)

list_of_items_codeds = []
for k in range(len(list_of_indexes) - 1):
    list_of_items_codeds.append(html_text[list_of_indexes[k] : list_of_indexes[k+1]])
list_of_items_codeds.append(html_text[list_of_indexes[-1]:])

print(len(list_of_items_codeds))

list_of_links = []
for part_of_code in list_of_items_codeds:
    link = ''
    a_href = part_of_code.find('<a href="')
    for symbol in part_of_code[a_href + 9:]:
        if symbol != '"':
            link += symbol
        else:
            list_of_links.append(link)
            break

print(list_of_links)