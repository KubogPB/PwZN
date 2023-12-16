import numba
import argparse
import random
import math
import numpy as np
from rich import progress
from PIL import Image, ImageDraw

from time import time

#--------------------------------------------------------------------------------------------------------------------------------------------------
#ZADANIE 2

random.seed()

class Symulacja:
    def __init__(self, size: int, wsp_J: float, wsp_beta: float, wsp_B: float, gest: float, job:progress.Progress = None, job_ID:progress.TaskID = None):
        if(job != None):
            task_init_ID = job.add_task('[cyan]Tworzenie siatki:', total=size*size*2 + 3)

        self.siatka = []
        self.J = wsp_J
        self.B = wsp_B
        self.beta = wsp_beta

        spiny = []

        for i in range(size*size): #tworzenie lsity spinów wg. gęstości
            if(i < gest*size*size):
                spiny.append(-1)
            else:
                spiny.append(1)
            
            if(job != None):
                job.update(task_init_ID, advance=1)
            if((job != None) & (job_ID != None)):
                        job.update(job_ID, advance=1)
        
        random.shuffle(spiny) #mieszanie spinów

        for i in range(size): #przypisanie spinów do siatki
            siatka_tmp = []
            for j in range(size):
                siatka_tmp.append(spiny[i*size+j])

                if(job != None):
                    job.update(task_init_ID, advance=1)
                if((job != None) & (job_ID != None)):
                    job.update(job_ID, advance=1)

            self.siatka.append(siatka_tmp)
        
        if(job != None):
            job.update(task_init_ID, advance=1)

        #liczenie hamiltonianu
        self.hamiltonian = self.calc_hamiltonian()
        if(job != None):
            job.update(task_init_ID, advance=1)

        #liczenie magnetyzacji
        self.magnetyzacja = self.calc_magnetyzacja()
        if(job != None):
            job.update(task_init_ID, advance=1)
            job.remove_task(task_init_ID)
        
    
    #funcja do liczenia hamiltonianu
    def calc_hamiltonian(self):
        sum1 = 0
        sum2 = 0
        size = len(self.siatka)

        for i in range(size):
            for j in range(size):
                if(j < size - 1):
                    sum1 += self.siatka[i][j] * self.siatka[i][j+1]
                else:
                    sum1 += self.siatka[i][j] * self.siatka[i][0]
                
                if(i < size - 1):
                    sum1 += self.siatka[i][j] * self.siatka[i+1][j]
                else:
                    sum1 += self.siatka[i][j] * self.siatka[0][j]

                sum2 += self.siatka[i][j]
        
        return -self.J*sum1-self.B*sum2
    
    #funkcja do obliczania magnetyzacji
    def calc_magnetyzacja(self):
        mag = 0
        a = len(self.siatka)

        for i in self.siatka:
            for j in i:
                mag += j
        
        return mag/(a*a)
    
    def symulate(self, steps:int, job:progress.Progress = None, job_ID:progress.TaskID = None):
        a = len(self.siatka)

        last_job_ID_makro = None
        # last_job_ID_mikro = None

        krok = 1
        while krok <= steps:

            #tworzenie progressbara dla makrokroku
            if(last_job_ID_makro != None):
                job.remove_task(last_job_ID_makro)

            if(job != None):
                makro_task_ID = job.add_task('[red]Makrokrok ' + str(krok) + ':', total=a*a)
                last_job_ID_makro = makro_task_ID
            

            #iterowanie po mikrokorkach
            for _ in range(a):
                for _ in range(a):
                    #losowanie spinu
                    i = random.randint(0, len(self.siatka)-1)
                    j = random.randint(0, len(self.siatka)-1)

                    #liczenie różnicy energii
                    e0 = 0
                    e1 = 0
                    if(i == 0):
                        e0 += self.siatka[i][j]*self.siatka[a-1][j]
                        e1 += -self.siatka[i][j]*self.siatka[a-1][j]
                    else:
                        e0 += self.siatka[i][j]*self.siatka[i-1][j]
                        e1 += -self.siatka[i][j]*self.siatka[i-1][j]
                    
                    if(i == a-1):
                        e0 += self.siatka[i][j]*self.siatka[0][j]
                        e1 += -self.siatka[i][j]*self.siatka[0][j]
                    else:
                        e0 += self.siatka[i][j]*self.siatka[i+1][j]
                        e1 += -self.siatka[i][j]*self.siatka[i+1][j]
                    
                    if(j == 0):
                        e0 += self.siatka[i][j]*self.siatka[i][a-1]
                        e1 += -self.siatka[i][j]*self.siatka[i][a-1]
                    else:
                        e0 += self.siatka[i][j]*self.siatka[i][j-1]
                        e1 += -self.siatka[i][j]*self.siatka[i][j-1]
                    
                    if(j == a-1):
                        e0 += self.siatka[i][j]*self.siatka[i][0]
                        e1 += -self.siatka[i][j]*self.siatka[i][0]
                    else:
                        e0 += self.siatka[i][j]*self.siatka[i][j+1]
                        e1 += -self.siatka[i][j]*self.siatka[i][j+1]

                    e0 *= -self.J
                    e1 *= -self.J

                    e0 -= self.B * self.siatka[i][j]
                    e1 -= -self.B * self.siatka[i][j]

                    del_e = e1 - e0
                    
                    if(del_e <= 0): #jezeli energia po zmiane jest mniejsza
                        self.siatka[i][j] = -self.siatka[i][j]

                        self.hamiltonian -= e0
                        self.hamiltonian += e1

                        self.magnetyzacja += self.siatka[i][j]*2/(a*a)
                    else: #jezeli energia wieksza
                        if(random.random() < math.exp(-self.beta*del_e)):
                            self.siatka[i][j] = -self.siatka[i][j]

                            self.hamiltonian -= e0
                            self.hamiltonian += e1

                            self.magnetyzacja += self.siatka[i][j]*2/(a*a)
                    
                    if(job != None):
                        job.update(makro_task_ID, advance=1)

                    if((job != None) & (job_ID != None)):
                        job.update(job_ID, advance=1)


            #ponowne liczenie hamiltonianu i magnetyzcji po każdym makrokorku ze względu na błąd zaokrąglenia
            self.hamiltonian = self.calc_hamiltonian()
            self.magnetyzacja = self.calc_magnetyzacja()

            yield (krok, self.siatka, self.hamiltonian, self.magnetyzacja)
            krok += 1


#funkcja do zapisywania obrazów
def save_img(symulacja:Symulacja, krok:int, name:str = None, job:progress.Progress = None, job_ID:progress.TaskID = None):
    if(job != None):
        job_img_ID = job.add_task('[yellow]Generowanie obrazu:', total=len(symulacja.siatka)*len(symulacja.siatka)+1)

    image = Image.new('1', (len(symulacja.siatka), len(symulacja.siatka)))
    for i in range(len(symulacja.siatka)):
        for j in range(len(symulacja.siatka)):
            draw = ImageDraw.Draw(image)
            if(symulacja.siatka[i][j] == -1):
                draw.point((i,j), fill=0)
            else:
                draw.point((i,j), fill=1)
            
            if(job != None):
                job.update(job_img_ID, advance=1)

            if((job != None) & (job_ID != None)):
                job.update(job_ID, advance=1)

    if(name != None):
        path=name+'_'+str(krok)+'.png'
        image.save(path)
    
    if(job != None):
        job.update(job_img_ID, advance=1)
                
    if((job != None) & (job_ID != None)):
        job.update(job_ID, advance=1)
    
    if(job != None):
        job.remove_task(job_img_ID)

    return image



# #Koniec definicji
# #Zaczyna się "main"



#Przyjmowanie parametrów początkowych
parser = argparse.ArgumentParser(description='Zadanie 2 - model Isinga')
parser.add_argument('size', help='Rozmiar siatki', type=int)
parser.add_argument('wsp_J', help='Wartość J', type=float)
parser.add_argument('wsp_beta', help='Wartość parametru beta', type=float)
parser.add_argument('wsp_B', help='Wartość pola B', type=float)
parser.add_argument('l_krok', help='Liczba kroków symulacji', type=int)
parser.add_argument('-g', '--gestosc', help='Początkowa gęstość spinów', type=float, default=0.5)
parser.add_argument('-fi', '--file_img', help='Nazwa plików z obrazkami', type=str, default=None)
parser.add_argument('-fa', '--file_anim', help='Nazwa pliku z animacją', type=str, default=None)
parser.add_argument('-fm', '--file_mag', help='Nazwa pliku z magnetyzacją', type=str, default=None)

args = parser.parse_args()

st_z2 = time()

with progress.Progress() as job_progress:
    total_it = args.size*args.size*args.l_krok+args.l_krok+args.size*args.size*2+2
    if((args.file_img != None) | (args.file_anim != None)):
        total_it += (args.size*args.size+1)*(args.l_krok+1)
    taskID = job_progress.add_task('[green]Progress całości:', total=total_it)

    sym = Symulacja(args.size, args.wsp_J, args.wsp_beta, args.wsp_B, args.gestosc, job_progress, taskID)

    # print('Krok:\t0')
    # print('Hamiltonian:',end='\t')
    # print(sym.hamiltonian)
    # print('Magnetyzacja:', end='\t')
    # print(sym.magnetyzacja)
    # print()

    if((args.file_img != None) | (args.file_anim != None)):
        img_sequence_first = (save_img(sym, 0, args.file_img, job_progress, taskID))
    if(args.file_mag != None):
        file = open(args.file_mag, mode='xt')
        file.write('Krok:\tMagnetyzacja:\n')
        file.write('0\t' + str(sym.magnetyzacja) + '\n')

    job_progress.update(taskID, advance=1)


    img_sequence = []

    for i in sym.symulate(args.l_krok, job_progress, taskID):
        # print('Krok:', end='\t')
        # print(i[0])
        # print('Hamiltonian:',end='\t')
        # print(i[2])
        # print('Magnetyzacja:', end='\t')
        # print(i[3])
        # print()

        if((args.file_img != None) | (args.file_anim != None)):
            img_sequence.append(save_img(sym, i[0], args.file_img, job_progress, taskID))
        if(args.file_mag != None):
            file.write(str(i[0]) + '\t' + str(i[3]) + '\n')
        
        job_progress.update(taskID, advance=1)

    if(args.file_mag != None):
        file.close()

    if(args.file_anim != None):
        img_sequence_first.save(args.file_anim+'.gif', save_all=True, append_images=img_sequence, duration=100, loop=0)
    
    job_progress.update(taskID, advance=1)

et_z2 = time()

time_z2 = et_z2 - st_z2

print('Time (w/o numba):', end=' ')
print(time_z2, end=' ')
print('s')



#--------------------------------------------------------------------------------------------------------------------------------------------------
#Zadanie 4

np.random.seed()

@numba.njit(numba.int64[:, :](numba.int64[:, :], numba.float64, numba.float64, numba.float64))
def symulate(siatka, J, beta, B):
        a = len(siatka)

    # last_job_ID_makro = None
    # last_job_ID_mikro = None

    # krok = 1
    # while krok <= steps:

        #tworzenie progressbara dla makrokroku
        # if(last_job_ID_makro != None):
        #     job.remove_task(last_job_ID_makro)

        # if(job != None):
        #     makro_task_ID = job.add_task('[red]Makrokrok ' + str(krok) + ':', total=a*a)
        #     last_job_ID_makro = makro_task_ID
        

        #iterowanie po mikrokorkach
        for _ in range(a):
            for _2 in range(a):
                #losowanie spinu
                i = np.random.randint(0, len(siatka))
                j = np.random.randint(0, len(siatka))

                #liczenie różnicy energii
                e0 = 0
                e1 = 0
                if(i == 0):
                    e0 += siatka[i][j]*siatka[a-1][j]
                    e1 += -siatka[i][j]*siatka[a-1][j]
                else:
                    e0 += siatka[i][j]*siatka[i-1][j]
                    e1 += -siatka[i][j]*siatka[i-1][j]
                
                if(i == a-1):
                    e0 += siatka[i][j]*siatka[0][j]
                    e1 += -siatka[i][j]*siatka[0][j]
                else:
                    e0 += siatka[i][j]*siatka[i+1][j]
                    e1 += -siatka[i][j]*siatka[i+1][j]
                
                if(j == 0):
                    e0 += siatka[i][j]*siatka[i][a-1]
                    e1 += -siatka[i][j]*siatka[i][a-1]
                else:
                    e0 += siatka[i][j]*siatka[i][j-1]
                    e1 += -siatka[i][j]*siatka[i][j-1]
                
                if(j == a-1):
                    e0 += siatka[i][j]*siatka[i][0]
                    e1 += -siatka[i][j]*siatka[i][0]
                else:
                    e0 += siatka[i][j]*siatka[i][j+1]
                    e1 += -siatka[i][j]*siatka[i][j+1]

                e0 *= -J
                e1 *= -J

                e0 -= B * siatka[i][j]
                e1 -= -B * siatka[i][j]

                del_e = e1 - e0
                
                if(del_e <= 0): #jezeli energia po zmiane jest mniejsza
                    siatka[i][j] = -siatka[i][j]

                else: #jezeli energia wieksza
                    if(np.random.random() < math.exp(-beta*del_e)):
                        siatka[i][j] = -siatka[i][j]

                # if(job != None):
                #     job.update(makro_task_ID, advance=1)

                # if((job != None) & (job_ID != None)):
                #     job.update(job_ID, advance=1)


        #ponowne liczenie hamiltonianu i magnetyzcji po każdym makrokorku ze względu na błąd zaokrąglenia
        # hamil = calc_hamiltonian(siatka, J, B)
        # magnet = calc_magnetyzacja(siatka)

        # yield (krok, siatka)
        # krok += 1
        return(siatka)

@numba.njit(numba.float64(numba.int64[:,:], numba.float64, numba.float64))
def calc_hamiltonian(siatka, J, B):
    sum1 = 0
    sum2 = 0
    size = len(siatka)

    for i in range(size):
        for j in range(size):
            if(j < size - 1):
                sum1 += siatka[i][j] * siatka[i][j+1]
            else:
                sum1 += siatka[i][j] * siatka[i][0]
            
            if(i < size - 1):
                sum1 += siatka[i][j] * siatka[i+1][j]
            else:
                sum1 += siatka[i][j] * siatka[0][j]

            sum2 += siatka[i][j]
    
    return -J*sum1-B*sum2

@numba.njit(numba.float64(numba.int64[:,:]))
def calc_magnetyzacja(siatka):
    mag = 0
    a = len(siatka)

    for i in siatka:
        for j in i:
            mag += j
    
    return mag/(a*a)

def save_img(siatka, krok:int, name:str = None, job:progress.Progress = None, job_ID:progress.TaskID = None):
    if(job != None):
        job_img_ID = job.add_task('[yellow]Generowanie obrazu:', total=len(siatka)*len(siatka)+1)

    image = Image.new('1', (len(siatka), len(siatka)))
    for i in range(len(siatka)):
        for j in range(len(siatka)):
            draw = ImageDraw.Draw(image)
            if(siatka[i][j] == -1):
                draw.point((i,j), fill=0)
            else:
                draw.point((i,j), fill=1)
            
            if(job != None):
                job.update(job_img_ID, advance=1)

            if((job != None) & (job_ID != None)):
                job.update(job_ID, advance=1)

    if(name != None):
        path=name+'_'+str(krok)+'.png'
        image.save(path)
    
    if(job != None):
        job.update(job_img_ID, advance=1)
                
    if((job != None) & (job_ID != None)):
        job.update(job_ID, advance=1)
    
    if(job != None):
        job.remove_task(job_img_ID)

    return image

@numba.njit(numba.int64[:, :](numba.int64, numba.float64, numba.float64, numba.float64, numba.float64))
def create_siatka(size: int, wsp_J: float, wsp_beta: float, wsp_B: float, gest: float):
    siatka = np.empty((size, size), dtype=numba.int64)
    spiny = np.empty((size*size), dtype=numba.int64)

    for i in range(size*size): #tworzenie lsity spinów wg. gęstości
        if(i < gest*size*size):
            # spiny.append(-1)
            spiny[i] = -1
        else:
            # spiny.append(1)
            spiny[i] = 1
    
    np.random.shuffle(spiny) #mieszanie spinów

    for i in range(size): #przypisanie spinów do siatki
        # siatka_tmp = []
        for j in range(size):
            # siatka_tmp.append(spiny[i*size+j])
            siatka[i][j] = spiny[i*size+j]

        # siatka.append(siatka_tmp)
    
    return siatka


#mian Zadanie 4

st_z4 = time()

with progress.Progress() as job_progress:
    total_it = args.l_krok
    if((args.file_img != None) | (args.file_anim != None)):
        total_it += (args.size*args.size+1)*(args.l_krok+1)
    taskID = job_progress.add_task('[green]Progress całości:', total=total_it)

    siatka = create_siatka(args.size, args.wsp_J, args.wsp_beta, args.wsp_B, args.gestosc)
    hamiltonian = calc_hamiltonian(siatka, args.wsp_J,  args.wsp_B)
    magnetyzacja = calc_magnetyzacja(siatka)

    # print('Krok:\t0')
    # print('Hamiltonian:',end='\t')
    # print(hamiltonian)
    # print('Magnetyzacja:', end='\t')
    # print(magnetyzacja)
    # print()

    if((args.file_img != None) | (args.file_anim != None)):
        img_sequence_first = (save_img(siatka, 0, args.file_img, job_progress, taskID))
    if(args.file_mag != None):
        file = open(args.file_mag, mode='xt')
        file.write('Krok:\tMagnetyzacja:\n')
        file.write('0\t' + str(magnetyzacja) + '\n')

    job_progress.update(taskID, advance=1)


    img_sequence = []

    for i in range(args.l_krok):
        siatka = symulate(siatka, args.wsp_J, args.wsp_beta, args.wsp_B)
        # print('Krok:', end='\t')
        # print(i)
        # print('Hamiltonian:',end='\t')
        # print(calc_hamiltonian(siatka, args.wsp_J, args.wsp_B))
        # print('Magnetyzacja:', end='\t')
        magnet = calc_magnetyzacja(siatka)
        # print(magnet)
        # print()

        if((args.file_img != None) | (args.file_anim != None)):
            img_sequence.append(save_img(siatka, i, args.file_img, job_progress, taskID))
        if(args.file_mag != None):
            file.write(str(i) + '\t' + str(magnet) + '\n')
        
        job_progress.update(taskID, advance=1)

    if(args.file_mag != None):
        file.close()

    if(args.file_anim != None):
        img_sequence_first.save(args.file_anim+'.gif', save_all=True, append_images=img_sequence, duration=100, loop=0)
    
    job_progress.update(taskID, advance=1)

et_z4 = time()

print('Time (numba):', end='\t')
time_z4 = et_z4 - st_z4
print(time_z4, end=' ')
print('s')

file_time = open('times.txt', 'w')
file_time.write('Time (w/o numba): ')
file_time.write(str(time_z2))
file_time.write(' s\n')
file_time.write('Time (numba): ')
file_time.write(str(time_z4))
file_time.write(' s\n')
file_time.close()
