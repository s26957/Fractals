import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class Plotter:
    """przygotowanie figury na podstawie dostarczonej listy transformacji i ich prawdopodobienstw wystąpienia"""

    lastAsked = {}  #przetrzymyane są gotowe dane do wyswietlenia 5 ostatnich figur o ktore było zapytanie

    def __init__(self, transformations):
        """inicializuje plotter listą transformacji i normalizowanymi przypisanymi im prawdopodobienstwami"""
        sum_of_weights = 0
        self.weights = []
        self.transformations = []

        #pobieranie macierzy transformacji, pobieranie wag
        for line in transformations:
            self.transformations.append(line[:-1])
            self.weights.append(line[-1])
            sum_of_weights += line[-1]

        #normalizacjia wag
        for i in range(len(self.weights)):
            self.weights[i] = self.weights[i] / sum_of_weights

    def plot(self, name):
        """zwraca figure do wyswietlenia"""
        if name == None:
            fig = self.__prepere_new_plot()
        else:
            if name in self.lastAsked:
                fig = self.lastAsked[name]
            else:
                fig = self.__prepere_new_plot()
                self.lastAsked[name] = fig
                if len(self.lastAsked) > 5:
                    self.lastAsked.pop(next(iter(self.lastAsked)))
        return fig

    def __prepere_new_plot(self):
        """tworzy figurę do wyświetlenia w przypadku gdy nie jest przechowywana w slowniku figur o które były ostatnio odpytania"""
        n, x, y = 200000, 0, 0
        x_vec, y_vec = [], []

        for i in range(n):
            #losowanie transformacji:
            id = np.random.choice(len(self.transformations), p=self.weights)
            chosen_transform = self.transformations[id]

            #wyliczanie nowych wspolrzecnych:
            x, y = self.__transform(chosen_transform, x, y)
            x_vec.append(x)
            y_vec.append(y)

        fig = Figure(figsize=(5, 5), dpi=100)
        plot1 = fig.add_subplot(111)
        plot1.scatter(x_vec, y_vec, s=0.2)
        return fig

    def __transform(self, transformation, x, y):
        """transformowanie dostarczonych x i y zgodnie ze wspolczynnikami z listy wspolczynnikow"""
        return (transformation[0] * x + transformation[1] * y + transformation[2],
                transformation[3] * x + transformation[4] * y + transformation[5])

class fileHandler():
    """obsluga plikow, dostarczanie metod do wczytywania i zapisywania do pliku z obsluga wyjatkow"""
    def __init__(self, filename):
        self.filename = filename

    def read_file(self):
        predefined_transforms = {}
        try:
            datafile = open(self.filename, 'r')
        except FileNotFoundError:
            print("FILE NOT FOUND => impossible to load fractal examples ")
        except IOError:
            print("ERROR TRYING TO OPEN THE FILE => impossible to load fractal examples ")
        except Exception:
            print("UNEXPECTED ERROR OPENING THE FILE => impossible to load fractal examples ")
        else:
            with datafile:
                for line in datafile:
                    line = line.strip().split(";")
                    predefined_transforms[line[0]] = []
                    for transformation in line[1:]:
                        predefined_transforms[line[0]].append(
                            [float(z) for z in transformation.split(",") if not z == ''])
        return predefined_transforms

    def save_to_file(self, predefinedTransforms):
        try:
            datafile = open(self.filename, 'w')
        except FileNotFoundError:
            print("FILE NOT FOUND => impossible to load fractal examples ")
        except IOError:
            print("ERROR TRYING TO OPEN THE FILE => impossible to load fractal examples ")
        except Exception:
            print("UNEXPECTED ERROR OPENING THE FILE => impossible to load fractal examples ")
        else:
            with datafile:
                for fractalName in predefinedTransforms:
                    lineToWrite = fractalName
                    for transformation in predefinedTransforms[fractalName]:
                        lineToWrite = lineToWrite + ";" + str(transformation).strip("]")[1:]
                    lineToWrite = lineToWrite.replace(" ", "") + "\n"
                    datafile.write(lineToWrite)


class FractalsCreator:
    """dostarczanie GUI i obsluga zapytan uzytkownika"""

    window = tk.Tk()
    filehandler = fileHandler('resources/FractalsMatrix.txt')

    predefined_transforms = {}  #wczytane z pliku transformacje potrzebne do otrzymania danych fraktali
    list_of_predefined_transforms = []  #combobox z fraktalami ktorych transformacje sa zapisane (i uzytkownik moze je wybrac)

    entries_of_transf_factors = []  #tkinter entries - podawanie wspolczynnikow do tranfsormacji
    curren_transformations_set = []

    columnNameLabels = ['a', 'b', 'c', 'd', 'e', 'f', "prawdop"]
    row_indexes_labels = []

    def __init__(self, window_h, window_w):
        """inicjalizacja szerokoscia i wysokoscia okna"""
        self.windowHeight = window_h
        self.windowWidth = window_w

    def start(self):
        self.__setWindow()

    def __setWindow(self, firstTime=True):
        """tworzenie okna glownego"""

        but_add = tk.Button(master=self.window, command=self.__add_transf_row, height=2, width=3, text="add")
        but_del = tk.Button(master=self.window, command=self.__del_transf_row, height=2, width=3, text="delete")
        but_save = tk.Button(master=self.window, command=self.__save_new_transf, height=2, width=3, text="save")
        but_set_automatic = tk.Button(master=self.window, command=self.__set_data, height=1, width=3, text="set")
        but_draw = tk.Button(master=self.window, command=self.__draw, height=2, width=3, text="draw")
        but_save_to_file = tk.Button(master=self.window, command=self.__save_to_file, height=2, width=3, text="to file")

        but_add.grid(column=0, row=0, pady=10)
        but_del.grid(column=1, row=0, pady=10)
        but_save.grid(column=2, row=0, pady=10)
        but_set_automatic.grid(column=len(self.columnNameLabels) - 1, row=0, pady=10)
        but_draw.grid(column=len(self.columnNameLabels), row=0, pady=10)
        but_save_to_file.grid(column=len(self.columnNameLabels) + 1, row=0, pady=10)

        #nazywanie kolumn wspolczynnikow:
        for i in range(len(self.columnNameLabels)):
            tk.Label(self.window, text=self.columnNameLabels[i]).grid(column=i + 1, row=1, padx=10)

        if firstTime:
            #wczytanie przygotowanych tranfosrmacji do uzyskania fraktali (z pliku)
            self.__set_prepared_fractals_transformations_from_file()
        self.__set_list_of_predefined_fractals()  #przygotowanie comoboxa z fraktalami do wyboru
        self.__add_transf_row()
        self.window.geometry('600x550')
        self.window.mainloop()

    def __add_transf_row(self):
        """dodawanie wiersza pozwalajacego wpisac wspolczynniki kolejnej transfromacji"""
        nOfRows = len(self.row_indexes_labels)
        l = tk.Label(self.window, text=str(nOfRows))
        l.grid(column=0, row=nOfRows + 2, padx=10)
        self.row_indexes_labels.append(l)

        entry = []
        for i in range(len(self.columnNameLabels)):
            e = tk.Entry(self.window, width=5)
            e.grid(column=i + 1, row=nOfRows + 2, padx=10)
            entry.append(e)
        self.entries_of_transf_factors.append(entry)

    def __del_transf_row(self):
        """usuniecie wiersza pozwalajacego wpisac na wspolczynniki kolejnej transformacji"""
        if len(self.entries_of_transf_factors) > 1:
            self.row_indexes_labels[-1].grid_remove()
            self.row_indexes_labels.remove(self.row_indexes_labels[-1])

            for element in self.entries_of_transf_factors[-1]:
                element.grid_remove()
            self.entries_of_transf_factors.remove(self.entries_of_transf_factors[-1])

    def __set_list_of_predefined_fractals(self):
        """tworzenie listy combobox zawierajacej nazwy fraktali do wyboru dla ktorych transformacje zostaly
        predefiniowane w pliku"""
        self.list_of_predefined_transforms = ttk.Combobox(state="readonly",
                                                          values=[nazwa for nazwa in self.predefined_transforms.keys()])
        self.list_of_predefined_transforms.place(x=200, y=23)

    def __set_prepared_fractals_transformations_from_file(self):
        """wczytywanie predefiniowanych fraktali wraz transformacjami pozwalajacymi je wyrysowac z pliku"""
        self.predefined_transforms = self.filehandler.read_file()

    def __save_to_file(self):
        """zapisywanie do pliku zapisanych przez uzytkownika transformacji dla danych figur"""
        self.filehandler.save_to_file(self.predefined_transforms)

    def __take_data(self):
        """pobranie z widoku wspolczynnikow transformacji, zwraca True w przypadku powodzenia"""

        self.curren_transformations_set = []

        #w przypadku 1 transformacji o zerowym prawdopodobienstwie żadna figura nie powstanie => nie wyświetlam
        if (len(self.entries_of_transf_factors) == 1 and
                self.entries_of_transf_factors[0][len(self.columnNameLabels) - 1] == 0):
            return False

        for transformRaw in self.entries_of_transf_factors:
            transform = []
            for i in range(len(transformRaw)):
                try:
                    factor = float(transformRaw[i].get())

                    #sprawdzanie czy prawdopodobienstwo jest wieksze od 0
                    if (factor < 0 and
                            i == (len(self.columnNameLabels) - 1)):
                        raise ValueError
                    transform.append(factor)
                except ValueError:
                    self.curren_transformations_set = []
                    return False
            self.curren_transformations_set.append(transform)
        return True

    def __draw(self):
        """wyrysowywanie figury z komunikowaniem w przypadku bledu parametrow"""
        if self.__take_data():

            fig = Plotter(self.curren_transformations_set).plot(self.list_of_predefined_transforms.get())
            self.__clear_window()
            canvas = FigureCanvasTkAgg(fig, master=self.window)
            canvas.draw()
            canvas.get_tk_widget().pack()

            button = tk.Button(master=self.window, text="go back", command=self.__reset)
            button.pack(side=tk.BOTTOM)
        else:
            error_communicat = tk.Label(master=self.window, text="!factors a-f have to be numeric, and probability > 0")
            error_communicat.place(x=0, y=self.windowHeight - 50)

    def __reset(self):
        self.__clear_window()

        self.entries_of_transf_factors = []
        self.row_indexes_labels = []

        self.curren_transformations_set = []
        self.list_of_predefined_transforms = []
        self.__setWindow(False)

    def __clear_window(self):
        for w in self.window.winfo_children():
            w.destroy()

    def __set_data(self):
        """uzupelnianie widoku wspolczynnikami wybranej gotowej transformacji"""
        if self.list_of_predefined_transforms.get() != "":
            new_transformations = self.predefined_transforms.get(self.list_of_predefined_transforms.get())

            how_much_too_much = len(self.entries_of_transf_factors) - len(new_transformations)
            for i in range(how_much_too_much):
                self.__del_transf_row()

            for i in range(len(self.entries_of_transf_factors), len(new_transformations)):
                self.__add_transf_row()

            self.curren_transformations_set = new_transformations
            for i in range(len(self.entries_of_transf_factors)):
                for j in range(len(self.columnNameLabels)):
                    self.entries_of_transf_factors[i][j].delete(0, tk.END)
                    self.entries_of_transf_factors[i][j].insert(0, str(new_transformations[i][j]))

    def __save_new_transf(self):
        """dodanie tranformacji stworzonej przez uzytkownika do zapisanych"""
        self.__take_data()
        key = "newTransf" + str(len(self.predefined_transforms))
        self.predefined_transforms[key] = self.curren_transformations_set
        self.__set_list_of_predefined_fractals()


fractalsCreator = FractalsCreator(550, 600)
fractalsCreator.start()
