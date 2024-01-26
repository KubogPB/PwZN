from time import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

import requests
from bs4 import BeautifulSoup
import re
from os.path import basename

from PIL import Image, ImageFilter


def img_saver(img_url, url, save_folder):
    link = img_url.get('href')

    print('Downloading ' + link)

    if(not link.startswith('http', 0, 3)):
        link:str = url + link
    
    img_file_name = save_folder + basename(link)
    with open(img_file_name, 'wb') as file:
        file.write(requests.get(link).content)
    
    img = Image.open(img_file_name)
    img = img.convert('L')
    img = img.filter(ImageFilter.GaussianBlur(10))

    img.save(img_file_name)


if __name__ == '__main__':
    adres = 'https://www.if.pw.edu.pl/~mrow/dyd/wdprir/'

    st = time()

    res = requests.get(adres)
    print('Status code: ' + str(res.status_code))
    assert res.status_code == 200

    soup = BeautifulSoup(res.text, 'html.parser')
    web_images = soup.find_all(href=re.compile('.png'))

    for w_img in web_images:
        img_saver(w_img, adres, '.\\Images1\\')

    et = time()
    print('Czas bez multiprocessingu: ' + str(et - st) + ' s')





    st = time()

    res = requests.get(adres)
    print('Status code: ' + str(res.status_code))
    assert res.status_code == 200

    soup = BeautifulSoup(res.text, 'html.parser')
    web_images = soup.find_all(href=re.compile('.png'))

    with ProcessPoolExecutor(multiprocessing.cpu_count()) as ex:
        futures = [ex.submit(img_saver, w_img, adres, '.\\Images2\\') for w_img in web_images]
        for future in as_completed(futures):
            print('End process')
    
    et = time()
    print('Czas z multiprocessingiem: ' + str(et - st) + ' s')