import random
import simpy
import numpy
import statistics
import matplotlib.pyplot as pyplot

wait_time = [] #deklaracja listy przechowującej czas postoju autobusu na przystanku
passenger = 6 #inicjalizacja liczby osób na przystanku na początku symulacji
time = 0 #inicjalizacja zmiennej określającej czas wsiadania ludzi do autobusu
new_passengers = [] #deklaracja listy przechowującej liczbę osób przychodzących na przystanek w czasie symulacji

def new_pass(env): #funkcja losująca liczbę osób przychodzących na przystanek
    global passenger
    yield env.timeout(numpy.random.exponential(2.0)) #przesunięcie czasu o losowy czas wyliczany funkcją logarytmiczną
    pass_count = int(numpy.random.normal(4, 2)) #losowanie liczby pasażerów przy użyciu funkcji normalnej rzutowanej na int
    print("Wylosowano " + pass_count.__str__())
    passenger += pass_count #dodanie wylosowanej liczby do liczby osób stojących na przystanku
    new_passengers.append(pass_count) #dodanie wylosowanej liczby do listy pasażerów

def get_in(): #funkcja losująca liczbę wsiadających osób i licząca czas wsiadania do autobusu
    global passenger
    global time
    pass_in = 100 #inicjalizacja liczby wsiadających osób (dużą wartością, aby przy pierwszym wywołaniu
                    # spełniało warunek if)
    if (passenger != 0):
        while pass_in > passenger:
            pass_in = int(numpy.random.normal(5, 2)) #losowanie liczby wsiadających osób z użyciem funkcji normalnej
    else:
        pass_in = 0
    print("Na przystanku " + passenger.__str__() + " Wsiadlo " + pass_in.__str__())
    time = pass_in * random.randrange(1,3) #obliczenie czasu wsiadania przy użyciu liczby wsiadających
                                            # osób i liczby z podanego przedziału
    passenger -= pass_in #zmniejszenie liczby osób na przystanku o ilość wsiadających osób

class BusStop(object): #klasa obsługująca autobus
    def __init__(self, env, lot, arr_time):
        self.env = env
        self.bus_lot = simpy.Resource(env, lot)
        self.arrtime = simpy.Resource(env, arr_time)

    def arrive(self, bus):
        get_in() #wywołanie funkcji losującej wsiadające osoby
        arr_time = self.env.now #zapisanie w zmiennej czasu, kiedy przyjechał autobus
        yield self.env.timeout(time) #przesunięcie czasu, o czas obliczony w funkcji get_in()
        wait_time.append(self.env.now - arr_time) #dodanie do listy czasu postoju obliczonego przez odjęcie
                                                    # od aktualnego czasu, czasu postoju
        print("Arrived at " + arr_time.__str__() + " Left at " + self.env.now .__str__() +
               " Stood " + (self.env.now - arr_time).__str__())

def statistic(wait_time, new_passengers): #funkcja licząca funkcje statystyczne i generujaca wykresy
    wait_mean = statistics.mean(wait_time)  #obliczenie i zapisanie do zmiennej średniego czasu postoju
    wait_var = statistics.variance(wait_time)   #obliczenie i zapisanie do zmiennej warjancji czasu postoju
    print("Mean bus on stop time: " + wait_mean.__str__() + " Variance: " + wait_var.__str__())
    pyplot.plot(wait_time) #wygenerowanie wykresu liniowego przedstawiającego dane z listy wait_time
    pyplot.xlabel("Ordinal number")
    pyplot.ylabel("Wait time")
    pyplot.show()   #wyświetlenie wykresu
    newcomer_mean = statistics.mean(new_passengers) #obliczenie i zapisanie do zmiennej średniej liczby nowych osób
    newcomer_median = statistics.median(new_passengers) #obliczenie i zapisanie do zmiennej mediany nowych osób
    print("Men new people on stop: " + newcomer_mean.__str__() + " Median: " + newcomer_median.__str__())
    pyplot.plot(new_passengers) #wygenerowanie wykresu liniowego przedstawiającego dane z listy new_passengers
    pyplot.xlabel("Ordinal number")
    pyplot.ylabel("Passenger count")
    pyplot.show()   #wyświetlenie wykresu

def bus_stop(env, bus, busstop):    #funkcja obsługująca podjeżdżanie autobusów
    with busstop.bus_lot.request() as request:  #wygenerowanie prośby o miejsce na przystanku
        yield request #oczekiwanie na miejsce
        yield env.process(busstop.arrive(bus))  #uruchomienie funkcji arrive

def stop_control(env, lot, arr_time):   #funkcja obsługująca symulację
    busstop = BusStop(env, lot, arr_time)   #utworzenie obiektu klasy

    for bus in range(2):    #utworzenie pierwszych autobusów w symulacji
        env.process(bus_stop(env, bus, busstop))    #wywołanie funkcji bus_stop dla pierwszych autobusów

    while True:
        yield env.timeout(random.randint(1, 10))    #przesunięcie czasu o liczbę naturalną z podanego przedziału
        env.process(new_pass(env)) #wywołanie funkcji generującej nowe osoby
        bus += 1    #dodanie nowego autobusu do symulacji
        env.process(bus_stop(env, bus, busstop))    #wywołanie funkcji bus_stop dla reszty symulacji


def main():
    random.seed(42) #ustalenie ziarnistości losowania
    lot = 3 #inicjalizacja liczby miejsc dla autobusów na przystanku
    arr_time = 1    #inicjalizacja zmiennej przechowującej czas przybycia autobusu na przystanek
    env = simpy.Environment()   #utworzenie środowiska
    env.process(stop_control(env, lot, arr_time))   #uruchomienie symulacji
    env.run(until=160)  #czas trwania symulacji

    statistic(wait_time, new_passengers)    #wyświetlenie wyników obliczeń i wykresów

if __name__ == '__main__':
    main()  #wywołanie funkcji main