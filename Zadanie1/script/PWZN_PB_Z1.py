import argparse
from ascii_graph import Pyasciigraph
from ascii_graph import colors

import collections
from _collections_abc import Iterable 
collections.Iterable = Iterable

import tqdm


def string_cleaner(string: str): #do czyszczenia wyrazów z interpunkcji
    for i in range(0x7e):
        if ((ord(chr(i)) >= ord('a')) & (ord(chr(i)) <= ord('z')) | (chr(i) == '-') | (chr(i) == "'")):
            continue
        string = string.replace(chr(i), '')

    string = string.strip("'")
    string = string.strip('-')
    string = string.strip('"')

    return string


#ustawianie przyjmowanych parametrów
parser = argparse.ArgumentParser(description='Zadanie 1')
parser.add_argument('file_name', help='Nazwa pliku', nargs='+', type=str)
parser.add_argument('-wc','--word_count', default=10, help='Liczba wyrazów do wyświetlenia w histogramie', type=int)
parser.add_argument('-wml','--word_min_lenght', default=0, help='Minimalna długość słowa do wyświetlenia w histogramie', type=int)
parser.add_argument('-i', '--ignore', default=[], help='Wyrazy do pominięcia w analizie', nargs='+', type=str)
parser.add_argument('-is', '--ignore_string', default=[], help='Ignoruj wyrazy z danym ciągiem znaków', nargs="+", type=str)
parser.add_argument('-fs', '--find_string', default=[], help='Znajdź wyrazy z danym ciągiem znaków', nargs='+', type=str)

args = parser.parse_args()


#zczytywanie danych
word_set = set()
word_list = []

for file_name in args.file_name:
    file = open(file_name, 'r', encoding="UTF-8")

    for line in tqdm.tqdm(file.readlines(), desc=str.join(' ', ['Czytanie pliku', file_name])):
        for word in line.split():
            word_clean = string_cleaner(word.lower())

            if(len(word_clean) < args.word_min_lenght):
                continue

            if(len(args.find_string) > 0):
                for str_to_find in args.find_string:
                    if word_clean.find(str_to_find) != -1:
                        break
                else:
                    continue

            for ignore in args.ignore:
                if(word_clean == ignore):
                    break
            else:
                for ignore in args.ignore_string:
                    if(word_clean.find(ignore) != -1):
                        break
                else:
                    word_set.add(word_clean)
                    word_list.append(word_clean)
            
    file.close()



#przygotowanie danych (odsiew, sortowanie)
data_prep = []
for data in tqdm.tqdm(word_set, desc='Analizowanie danych'):
    data_prep.append((word_list.count(data), data))

data_prep.sort()


color_order = [colors.Gre, colors.Yel, colors.Red]


#przygotowanie danych do przekazania do histogramu
data_graph = []
if len(data_prep) > args.word_count:
    for i in range(args.word_count):
       data_graph.append((data_prep[len(data_prep)-1-i][1], data_prep[len(data_prep)-1-i][0], color_order[(len(color_order)*i)//args.word_count]))
else:
    for i in range(len(data_prep)):
       data_graph.append((data_prep[len(data_prep)-1-i][1], data_prep[len(data_prep)-1-i][0], color_order[(len(color_order)*i)//len(data_prep)]))


#wyświetlenie histogramu
graph = Pyasciigraph(line_length=250)

for line in graph.graph("Histogram wyrazów", data_graph):
    print(line)


