from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

import time
import json
import argparse

parser = argparse.ArgumentParser(description='Zadanie 6')
parser.add_argument('file_name', help='Nazwa pliku do zapisu danych', type=str)
args = parser.parse_args()

options = Options()
#options.add_argument('--headless')

service = Service('webdriver/chromedriver.exe')

driver = webdriver.Chrome(service=service, options=options)
driver.get('https://refractiveindex.info/')

#akceptacja ciasteczek
button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'fc-button-background')))
action = ActionChains(driver)
action.move_to_element(button)
action.click()
action.perform()

wl = 0.633 #długość fali

#wpisanie długości fali
wavelength_field = driver.find_element(By.ID, 'wavelength')
for i in range(10):
    wavelength_field.send_keys(Keys.BACKSPACE)
wavelength_field.send_keys(str(wl))
wavelength_field.send_keys(Keys.ENTER)

#kliknięcie na OTHER - miscellaneous materials
print('Clicking "other"')
driver.find_element(By.CSS_SELECTOR, 'main > div > form').find_element(By.CSS_SELECTOR, 'select > option[value=other]').click()

#szukanie ile elementów znajduje się w Book w dziale Intermetallics
print('Finding "Intermetallics"')
books_range = driver.find_element(By.CSS_SELECTOR, 'main > div > form').find_elements(By.CSS_SELECTOR, 'select[id=book] > optgroup[label=Intermetallics] > option')


ri =[]
print()

for i in range(len(books_range)):
    books_form = driver.find_element(By.CSS_SELECTOR, 'main > div > form')
    books_form.find_element(By.CSS_SELECTOR, 'select[id=book]').click() #kliknięcie na Books
    option = books_form.find_elements(By.CSS_SELECTOR, 'select[id=book] > optgroup[label=Intermetallics] > option') #wybranie materiału
    option_name = option[i].text #zapisanie nazwy materiału
    option[i].click() #kliknięcie na wybrany materiał

    #czytanie wsp. n i k
    n_div_temp = driver.find_element(By.ID, 'container_n')
    n_div = n_div_temp.find_element(By.ID, 'n')
    k_div_temp = driver.find_element(By.ID, 'container_k')
    k_div = k_div_temp.find_element(By.ID, 'k')
    print(option_name)
    print('n=' + str(n_div.text)) #wypisanie n
    print('k=' + str(k_div.text)) #wypisanie k
    print()
    ri.append((option_name, n_div.text, k_div.text)) #zapis

driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)


content_list = (wl, ri)
json_file_name = args.file_name

if(not json_file_name.endswith('.json')):
   json_file_name += '.json'

with open(json_file_name, 'w') as f:
    json.dump(content_list, f, indent=4)


time.sleep(5)
print("END")
driver.close()
