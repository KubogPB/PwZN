import requests
import json
import argparse
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Zadanie 5')
parser.add_argument('file_name', help='Nazwa pliku do zapisu danych', type=str)
args = parser.parse_args()

# res = requests.get('https://www.fizyka.pw.edu.pl/Pracownicy/Lista-pracownikow/Pracownicy-badawczo-dydaktyczni')
res = requests.get('https://kwejk.pl/')
print('Status code: ' + str(res.status_code))
assert res.status_code == 200


soup = BeautifulSoup(res.text, 'html.parser')
main_div = soup.find_all('div', class_='media-element')

content_list = []

for data in main_div:
    name = data.find('span', class_='name')
    print('Username: ' + name.text.strip())

    title = data.find('h2')
    print('Title: ' + title.text.strip())

    tags = data.find('div', class_='tag-list')
    tag_list = []
    print('Tags: ', end='')
    for tag in tags:
        tag = tag.text.strip()
        if tag != '':    
            print(tag, end=' ')
            tag_list.append(tag)
    
    content_list.append((name.text.strip(), title.text.strip(), tag_list))

    print('\n--------------------------')


json_file_name = args.file_name

if(not json_file_name.endswith('.json')):
   json_file_name += '.json'

with open(json_file_name, 'w') as f:
    json.dump(content_list, f, indent=4)

