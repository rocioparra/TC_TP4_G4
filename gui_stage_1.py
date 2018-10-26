#!/usr/apps/Python/bin/python
import matplotlib, sys
matplotlib.use('TkAgg')
from scipy import signal
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import *
from model import Model
from filter_template import TemplateParameters
import math
import matplotlib.pyplot
import matplotlib.markers
import gui_stage_2

class TCExample:

    def show_credits(self):
        messagebox.showinfo("Credits", "La sororidad 2018")

    def plot(self):
        self.axis.clear()
        self.axis.grid(color='grey', linestyle='-')
        for filter in self.filters_input:
            if filter[0].get():  #si esta seleccionada
                plots = self.m.get_plot(filter[2], self.current_plot.get(), self.normalizacion.get() != "Desnormalizado")
                for plot in plots:
                    self.axis.set_xlabel(plot.x_label + " (" + plot.x_units + ")")
                    self.axis.set_ylabel(plot.y_label + " (" + plot.y_units + ")")
                    if plot.plot_type == 'c':
                        if plot.logscale:
                            self.axis.semilogx(plot.x_data, plot.y_data)
                        else:
                            self.axis.plot(plot.x_data, plot.y_data)
                    if plot.plot_type == 's':
                        for point in plot.points:
                            # voy graficando punto por punto

                            if point.format == 'x':
                                self.axis.plot(point.x, point.y, color='green', marker=point.format)
                            if point.format == 'o':
                                self.axis.plot(point.x, point.y, color='blue', marker=point.format)

                    if plot.plot_type == 't':
                        areas = plot.covered_areas
                        for area in areas:
                            print("top: ", area.top, " bottom: ", area.bottom, " left : ", area.left, " right: ", area.right)
                            rect = matplotlib.patches.Rectangle((area.left, area.bottom), area.right - area.left, area.top - area.bottom, fill = True)
                            self.axis.add_patch(rect)
        self.dataPlot.draw()


    def set_filter_type(self):
        self.is_filter_type_set = True
        self.approximation_type_list =  self.m.get_approximations_for(self.filter_type_name.get())
        self.approximation_type_menu.destroy()
        self.approximation_type_menu = OptionMenu(self.template_parameters_frame, self.approximation_type_name, *self.approximation_type_list)
        self.approximation_type_menu.pack(side=TOP, fill="x")

        self.qmax_input.config(state='normal')

        self.template_parameters_needed = self.m.get_parameters_for(self.filter_type_name.get()).data
        for i in range(len(self.template_parameters_input)):
            if self.template_parameters_needed[i]:
                list(self.template_parameters_input.values())[i][2].config(state='normal')
            else:
                list(self.template_parameters_input.values())[i][2].config(state='disabled')

    def calculate_new_filter_cb(self):
        if (not self.is_filter_type_set) or self.approximation_type_name == "Approximation type":
            return
        nmin = 0
        nmax = 25
        if self.n_options_name == "N min y max":
            nmin = int(self.nmin_value.get())
            nmax = int(self.nmin_value.get())
        elif self.n_options_name == "N fijo":
            nmin = int(self.nfijo_value.get())
            nmax = int(self.nfijo_value.get())

        Qmax = 200
        if len(self.qmax_value.get()):
            Qmax = float(self.qmax_value.get())

        template_parameters_list = []
        for key in self.template_parameters_input:
            if self.template_parameters_input[key][0].get():
                template_parameters_list.append(float(self.template_parameters_input[key][0].get()))
            else:
                template_parameters_list.append(None)
            print(self.template_parameters_input[key][0].get())

        template_parameters_list_to_send = TemplateParameters(*template_parameters_list)


        normal = 1
        dn = self.normalizacion.get()
        if(dn == "Desnormalizado"):
            normal = 0

        auxTup = self.m.add_filter(self.filter_type_name.get(), self.approximation_type_name.get(), \
                          template_parameters_list_to_send, nmin, nmax, Qmax, normal)

        if auxTup[1] == -1:         #si hubo error
            messagebox.showinfo("Error", auxTup[0])
        else:
            new_filter_input = []
            new_filter_input.append(IntVar())   # guarda si esta seleccionado o no
            new_filter_input.append(auxTup[0])  # nombre
            new_filter_input.append(auxTup[1])  # filter index
            new_filter_input.append(Checkbutton(self.existing_filters_frame, variable=new_filter_input[0], text=new_filter_input[1], state='normal'))
            new_filter_input[3].pack(side = TOP, fill='x')
            self.filters_input.append(new_filter_input)


    def n_mode_cb(self, mode):
        if mode ==  "N libre":
            self.nmax_input.config(state="disabled")
            self.nmin_input.config(state="disabled")
            self.nfijo_input.config(state="disabled")
        elif mode ==  "N min y max":
            self.nmax_input.config(state="normal")
            self.nmin_input.config(state="normal")
            self.nfijo_input.config(state="disabled")
        elif mode == "N fijo":
            self.nmax_input.config(state="disabled")
            self.nmin_input.config(state="disabled")
            self.nfijo_input.config(state="normal")

    def stage_2_cb(self):
        for current_filter_info in self.filters_input:
            if current_filter_info[0].get():
                gui_stage_2.GuiStage2(current_filter_info[2], self.m)

    def delete_unselected_cb(self):
        for i in range(len(self.filters_input)-1, -1, -1):  #recorro de atras para adelante para no modificar el indice cuando elimino
            if not self.filters_input[i][0].get():
                self.filters_input[i][3].destroy()          #delete el checkbox y el elemento de la lista si no esta seleccionado
                del self.filters_input[i]

    def __init__(self):
        self.root = Tk()
        self.root.title("Tc Example")

        self.m = Model()

        self.is_filter_type_set = False

        self.filter_type_list = self.m.get_available_filters()
        self.approximation_type_list = ["Approximation type"]

        self.existing_filters = []  #contiene tuples de filter_ID y nombre

        #------------------------------------------------------------------------
        # create a toplevel menu
        #------------------------------------------------------------------------
        menubar = Menu(self.root)
        menubar.add_command(label="About...", command=self.show_credits)
        menubar.add_command(label="Quit", command=self.root.quit)
        self.root.config(menu=menubar)


        #------------------------------------------------------------------------
        #create user input frame
        #------------------------------------------------------------------------
        user_input_frame = LabelFrame(self.root)
        user_input_frame.pack(side=LEFT, fill="y")

        #------------------------------------------------------------------------
        #Frame filter_type-------------------------------------------------------
        #------------------------------------------------------------------------
        filter_type_frame = LabelFrame(user_input_frame, text = "Filter type", width = 20, height = 15)
        filter_type_frame.pack(side = TOP, fill = "x")

        # filter-type drop-down menu
        self.filter_type_name = StringVar()
        self.filter_type_name.set("Filter type")  # default value
        filter_type_menu = OptionMenu(filter_type_frame, self.filter_type_name, *self.filter_type_list)
        filter_type_menu.pack(side=TOP, fill = "x")

        # filter_type confirm button
        filter_type_set_button = Button(filter_type_frame, text = "Set filter type",command = self.set_filter_type)
        filter_type_set_button.pack(side=TOP)


        #------------------------------------------------------------------------
        #Frame plantilla---------------------------------------------------------
        #------------------------------------------------------------------------
        self.template_parameters_frame = LabelFrame(user_input_frame, text = "Plantilla", width = 20, height = 15)
        self.template_parameters_frame.pack(side = TOP, fill = "x")



        #todos los parametros para el template
        self.template_parameters_input = {
            "wa": [],
            "wp": [],
            "Aa": [],
            "Ap": [],
            "w0": [],
            "BWp": [],
            "BWa": [],
            "tau": [],
            "tol": [],
            "wrg": []
        }

        #entries para los parametros del templates
        for key in self.template_parameters_input:
            self.template_parameters_input[key].append(StringVar())                                 #template_parameters_input[key][0]
            self.template_parameters_input[key].append(Frame(self.template_parameters_frame))       #template_parameters_input[key][1]
            self.template_parameters_input[key].append(Entry(self.template_parameters_input[key][1], width = 30, textvariable=self.template_parameters_input[key][0], state='disabled'))
            self.template_parameters_input[key][2].pack(side=RIGHT)
            Label(self.template_parameters_input[key][1], text=key).pack(side=RIGHT)
            self.template_parameters_input[key][1].pack(side=TOP, anchor = NE)


        #desnormalizacion con sliders
        desnorm_input = Frame(self.template_parameters_frame)
        self.desnorm = StringVar()
        desnorm_scale = Scale(desnorm_input, from_=0, to_=100, orient=HORIZONTAL, variable = self.desnorm)
        desnorm_scale.pack(side = RIGHT)
        desnormLabel = Label(desnorm_input, text="Desnormalizacion")
        desnormLabel.pack(side=RIGHT, fill=X)
        desnorm_input.pack(anchor = NW)


        #Qmax
        qmax_input_frame = Frame(self.template_parameters_frame)
        self.qmax_value = StringVar()

        qmax_label = Label(qmax_input_frame, text="Q max:")
        self.qmax_input = Entry(qmax_input_frame, textvariable=self.qmax_value, width=5, state='disabled')

        qmax_label.pack(side=LEFT)
        self.qmax_input.pack(side=LEFT)

        qmax_input_frame.pack(side=TOP, pady = 2)


        #setemo modo de n
        self.n_options_name = StringVar()
        self.n_options_list = [ "N libre", "N min y max", "N fijo" ]
        self.n_options_name.set(self.n_options_list[0])
        n_options_menu = OptionMenu(self.template_parameters_frame,self.n_options_name, *self.n_options_list, command=self.n_mode_cb)
        n_options_menu.pack(side=TOP)

        #nmin y nmax
        nmaxmin_input_frame = Frame(self.template_parameters_frame)

        self.nmax_value = StringVar()
        self.nmin_value = StringVar()

        self.nmax_input = Entry(nmaxmin_input_frame, textvariable = self.nmax_value, width = 5, state = 'disabled')
        self.nmin_input = Entry(nmaxmin_input_frame, textvariable = self.nmin_value, width = 5, state = 'disabled')

        nmaxmin_label = Label(nmaxmin_input_frame, text="Rango N:")
        nmaxmin_separator = Label(nmaxmin_input_frame, text=" - ")

        nmaxmin_label.pack(side=LEFT)
        self.nmin_input.pack(side=LEFT)
        nmaxmin_separator.pack(side=LEFT)
        self.nmax_input.pack(side=LEFT)

        nmaxmin_input_frame.pack(side=TOP, pady = 2)



        #n fijo
        nfijo_input_frame = Frame(self.template_parameters_frame)
        self.nfijo_value = StringVar()

        nfijo_label = Label(nfijo_input_frame, text="N fijo:")
        self.nfijo_input = Entry(nfijo_input_frame, textvariable = self.nfijo_value, width = 5, state = 'disabled')

        nfijo_label.pack(side = LEFT)
        self.nfijo_input.pack(side = LEFT)

        nfijo_input_frame.pack(side=TOP, pady = 2)







        self.approximation_type_name = StringVar()
        self.approximation_type_name.set("Approximation type")  # default value
        self.approximation_type_menu = OptionMenu(self.template_parameters_frame, self.approximation_type_name, *self.approximation_type_list)
        self.approximation_type_menu.pack(side=TOP, fill="x")


        self.template_parameters_set_button = Button(user_input_frame, text="Calculate new filter", command=self.calculate_new_filter_cb)
        self.template_parameters_set_button.pack()





        #------------------------------------------------------------------------
        toolbar = Frame(self.root)

        #todos los posibles graficos
        self.filter_plots_info = {
            "Mag": [],
            "Ate": [],
            "Pha": [],
            "Pha ret": [],
            "PZ": [],
            "Step": [],
            "Imp": []
        }

        #entries para los parametros del templates
        for key in self.filter_plots_info:
#            self.filter_plots_info[key].append(Button(toolbar, text=key, command=locals()[key]()))
#            self.filter_plots_info[key][0].pack(side=LEFT,padx=2,pady=2)
            print(key)

            # self.template_parameters_input[key].append(StringVar())                           #template_parameters_input[key][0]
            # self.template_parameters_input[key].append(Frame(template_parameters_frame))      #template_parameters_input[key][1]
            # self.template_parameters_input[key].append(Entry(self.template_parameters_input[key][1], width = 30, textvariable=self.template_parameters_input[key][0], state='disabled'))
            # self.template_parameters_input[key][2].pack(side=RIGHT)
            # Label(self.template_parameters_input[key][1], text=key).pack(side=RIGHT)
            # self.template_parameters_input[key][1].pack(side=TOP, anchor = NE)

        #parametros de los graficos
        self.normalizacion = StringVar()
        self.unidades = StringVar()
        self.db_veces = StringVar()
        self.current_plot = StringVar()

        #posibles valores para los parametros anteriores, el primero de la lista es el default
        self.normalizacion_list = ["Desnormalizado", "Normalizado"]
        self.unidades_list = ["Hz", "rad/s"]
        self.db_veces_list = ["dB", "Veces"]
        self.current_plot_list = self.m.get_available_plots()

        #valores default
        self.normalizacion.set(self.normalizacion_list[0])
        self.unidades.set(self.unidades_list[0])
        self.db_veces.set(self.db_veces_list[0])
        self.current_plot.set(self.current_plot_list[0])

        #creo los drop-down de los parametros
        normalizacion_input = OptionMenu(toolbar, self.normalizacion, *self.normalizacion_list)
        unidades_input = OptionMenu(toolbar, self.unidades, *self.unidades_list)
        db_veces_input = OptionMenu(toolbar, self.db_veces, *self.db_veces_list)
        current_plot_input = OptionMenu(toolbar, self.current_plot, *self.current_plot_list)

        normalizacion_input.pack(side=TOP, pady=2, fill='x')
        unidades_input.pack(side=TOP, pady=2, fill='x')
        db_veces_input.pack(side=TOP, pady=2, fill='x')
        current_plot_input.pack(side=TOP, pady=2, fill='x')

        #-----------
        #-----------
        #-----------
        self.existing_filters_frame = LabelFrame(toolbar, text = "Filtros existentes", width = 20)
        self.existing_filters_frame.pack(side = TOP, fill = "x")

        #obtener de rochi
        self.filters = []
        self.filters_input = []

        stage_2_button = Button(toolbar, text="Seleccionados a etapa 2", command=self.stage_2_cb)
        stage_2_button.pack(side=BOTTOM, fill='x')

        delete_filters_button = Button(toolbar, text="Borrar deseleccionados", command=self.delete_unselected_cb)
        delete_filters_button.pack(side=BOTTOM, fill='x')

        Button(toolbar, text = "Plot", command = self.plot).pack()




        toolbar.pack(side=RIGHT,fill=Y)
        graph = Canvas(self.root)
        graph.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=4)
        #-------------------------------------------------------------------------------

        f = Figure()
        self.axis = f.add_subplot(111)
        self.sys = signal.TransferFunction([1], [1, 1])
        self.w, self.mag, self.phase = signal.bode(self.sys)
        self.stepT, self.stepMag = signal.step(self.sys)
        self.impT, self.impMag = signal.impulse(self.sys)

        self.dataPlot = FigureCanvasTkAgg(f, master=graph)
        self.dataPlot.draw()
        self.dataPlot.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        nav = NavigationToolbar2Tk(self.dataPlot, self.root)
        nav.update()
        self.dataPlot._tkcanvas.pack(side=TOP, fill=X, expand=True)
        # self.plotMag()
        #-------------------------------------------------------------------------------
        self.root.mainloop()

if __name__ == "__main__":
    ex = TCExample()
