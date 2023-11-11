from time import time
import numpy as np


class Dekorator_Z3:
    def __init__(self, func):
        self.func = func
        self.min = 0
        self.max = 0
        self.srednia = 0
        self.sdev = 0
        self.runtime = []

    def __call__(self, *args, **kwargs):
        time_tmp = time()
        self.func(*args, **kwargs)
        self.runtime.append(time() - time_tmp)
        self.calc_stats()

    def wrapper(self, func):
        pass
    
    def calc_stats(self):
        self.min = np.min(self.runtime)
        self.max = np.max(self.runtime)
        self.srednia = np.mean(self.runtime)
        self.sdev = np.std(self.runtime)
    
    def show_stats(self):
        print('Liczba wywołań:', end=' ')
        print(len(self.runtime))

        print('Min:', end=' ')
        print(self.min, end=' ')
        print('s')

        print('Max:', end=' ')
        print(self.max, end=' ')
        print('s')
        
        print('Średnia:', end=' ')
        print(self.srednia, end=' ')
        print('s')
        
        print('Odchylenie standardowe:', end=' ')
        print(self.sdev, end=' ')
        print('s')    
    
    def get_stats(self):
        return (len(self.runtime),self.min, self.max, self.srednia, self.sdev)


@Dekorator_Z3
def my_func():
    matrix1 = np.random.random_integers(-5,5,(1000,1000))
    matrix2 = np.random.random_integers(-5,5,(1000,1000))
    print(matrix1)
    print(matrix2)
    matrix3 = matrix1 @ matrix2
    print(matrix3)
        
my_func()
print('\n\n--------------------------------------------\n\n')
my_func()
print('\n\n--------------------------------------------\n\n')
my_func()
print('\n\n--------------------------------------------\n\n')
my_func()
print('\n\n--------------------------------------------\n\n')
my_func()

my_func.show_stats()

my_func()
print('\n\n--------------------------------------------\n\n')
my_func()
print('\n\n--------------------------------------------\n\n')
my_func()
print('\n\n--------------------------------------------\n\n')
my_func()
print('\n\n--------------------------------------------\n\n')
my_func()

my_func.show_stats()