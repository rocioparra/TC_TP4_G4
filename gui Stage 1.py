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


class TCExample:

    def show_credits(self):
        messagebox.showinfo("Credits", "La sororidad 2018")



    def plot(self):
        result = {
            'Mag': lambda: self.plotMag(),
            'Ate': lambda: self.plotAte(),
            'Pha': lambda: self.plotPha(),
            'Pha ret': lambda:self.plotPhaRet(),
            'PZ': lambda: self.plotPZ(),
            'Step': lambda: self.plotStep(),
            'Imp': lambda: self.plotImp()
        }[self.current_plot]

    def plotPha(self):
        print("plot pha")
        for current_filter_info in self.filters_input:
            if current_filter_info[0]:  #si esta seleccionada
                print("imprimo fase del filtro ", current_filter_info[1].cget("text"))
                #todo: dibujar
                self.axis.clear()
                self.axis.semilogx(self.w,self.phase)
                self.axis.grid(color='grey',linestyle='-',linewidth=0.1)
                self.axis.set_xlabel("$f (Hz)$")
                self.axis.set_ylabel("$Phase (deg)$")
                self.dataPlot.draw()

    def plotPhaRet(self):
        print("plot pha ret")
        for current_filter_info in self.filters_input:
            if current_filter_info[0]:  #si esta seleccionada
                print("imprimo retardo de fase del filtro ", current_filter_info[1].cget("text"))
                #todo: dibujar
                self.axis.clear()
                self.axis.semilogx(self.w,self.phase)
                self.axis.grid(color='grey',linestyle='-',linewidth=0.1)
                self.axis.set_xlabel("$f (Hz)$")
                self.axis.set_ylabel("$Phase (deg)$")
                self.dataPlot.draw()

    def plotMag(self):
        print("plot mag")
        for current_filter_info in self.filters_input:
            if current_filter_info[0]:  #si esta seleccionada
                print("imprimo mag del filtro ", current_filter_info[1].cget("text"))
                #todo: dibujar
                self.axis.clear()
                self.axis.semilogx(self.w,self.mag)
                self.axis.grid(color='grey',linestyle='-',linewidth=0.1)
                self.axis.set_xlabel("$f (Hz)$")
                self.axis.set_ylabel("$V_{out}/V_{in} (dB)$")
                self.dataPlot.draw()

    def plotAte(self):
        print("plot ate")
        for current_filter_info in self.filters_input:
            if current_filter_info[0]:  #si esta seleccionada
                print("imprimo atenuacion del filtro ", current_filter_info[1].cget("text"))
                #todo: dibujar
                self.axis.clear()
                self.axis.semilogx(self.w,self.mag)
                self.axis.grid(color='grey',linestyle='-',linewidth=0.1)
                self.axis.set_xlabel("$f (Hz)$")
                self.axis.set_ylabel("$V_{out}/V_{in} (dB)$")
                self.dataPlot.draw()

    def plotStep(self):
        print("plot step")
        for current_filter_info in self.filters_input:
            if current_filter_info[0]:  #si esta seleccionada
                print("imprimo step del filtro ", current_filter_info[1].cget("text"))
                #todo: dibujar
                self.axis.clear()
                self.axis.plot(self.stepT,self.stepMag)
                self.axis.grid(color='grey',linestyle='-',linewidth=0.1)
                self.axis.set_xlabel("$t (s)$")
                self.axis.set_ylabel("$V_{out} (Volts)$")
                self.dataPlot.draw()

    def plotImp(self):
        print("plot imp")
        for current_filter_info in self.filters_input:
            if current_filter_info[0]:  #si esta seleccionada
                print("imprimo impulsiva del filtro ", current_filter_info[1].cget("text"))
                #todo: dibujar
                self.axis.clear()
                self.axis.plot(self.impT,self.impMag)
                self.axis.grid(color='grey',linestyle='-',linewidth=0.1)
                self.axis.set_xlabel("$t (s)$")
                self.axis.set_ylabel("$V_{out} (Volts)$")
                self.dataPlot.draw()

    def set_filter_type(self):
        print(self.filter_type_name.get())
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
        #todo
        #mandar a perrochi y obtener el nuevo filtro
        #guardar el nombre y los plot para plotear en filters_list
        #guardar el checkbox (state=normal) en filter_input_list
        #plot t-odo de nuevo

        #todo: calcular nmax y nmin para mandar


        template_parameters_list = []
        for key in self.template_parameters_input:
            if self.template_parameters_input[key][0].get():
                template_parameters_list.append(int(self.template_parameters_input[key][0].get()))
            else:
                template_parameters_list.append(None)
            print(self.template_parameters_input[key][0].get())

        template_parameters_list_to_send = TemplateParameters(*template_parameters_list)



        self.m.add_filter(self.filter_type_name.get(), self.approximation_type_name.get(), \
                          template_parameters_list_to_send, 0, 25, 4, 10 )
        new_filter_input = []               #checkbutton y variable para ver si esta seleccionado o no
        new_filter_input.append(IntVar())    #guarda si esta seleccionado o no
        new_filter_input.append(Checkbutton(self.existing_filters_frame, variable=new_filter_input[0], text="nuevo filtro re piola", state='normal'))
        new_filter_input[1].pack(side = TOP, fill='x')
#        new_filter_input.append() LA LISTA DE TODOS LOS GRAFICOS y el nombre grafico quizas
        self.filters_input.append(new_filter_input)

    # def set_template_parmeters(self):
    #     #todo: mandar a chiparra
    #     for key, value in self.template_parameters_input:
    #         print(key, value)

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
            if current_filter_info[0]:
                print("mando a la etapa 2 a los filtros ", current_filter_info[1].cget("text"))

    def delete_unselected_cb(self):
        for i in range(len(self.filters_input)-1, -1, -1):  #recorro de atras para adelante para no modificar el indice cuando elimino
            if not self.filters_input[i][0].get():
                self.filters_input[i][1].destroy()          #delete el checkbox y el elemento de la lista si no esta seleccionado
                del self.filters_input[i]

    def __init__(self):
        self.root = Tk()
        self.root.title("Tc Example")

        self.m = Model()

        self.filter_type_list = self.m.get_available_filters()
        self.approximation_type_list = ["Approximation type"]

        self.existing_filters = []

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
        desnorm = StringVar()
        desnorm_scale = Scale(desnorm_input, from_=0, to_=100, orient=HORIZONTAL)
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






        toolbar.pack(side=RIGHT,fill=Y)
        graph = Canvas(self.root)
        graph.pack(side=TOP,fill=BOTH,expand=True,padx=2,pady=4)
        #-------------------------------------------------------------------------------

        f = Figure()
        self.axis = f.add_subplot(111)
        self.sys = signal.TransferFunction([1],[1,1])
        self.w,self.mag,self.phase = signal.bode(self.sys)
        self.stepT,self.stepMag = signal.step(self.sys)
        self.impT,self.impMag = signal.impulse(self.sys)

        self.dataPlot = FigureCanvasTkAgg(f, master=graph)
        self.dataPlot.draw()
        self.dataPlot.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        nav = NavigationToolbar2Tk(self.dataPlot, self.root)
        nav.update()
        self.dataPlot._tkcanvas.pack(side=TOP, fill=X, expand=True)
        self.plotMag()
        #-------------------------------------------------------------------------------
        self.root.mainloop()

if __name__ == "__main__":
    ex = TCExample()
