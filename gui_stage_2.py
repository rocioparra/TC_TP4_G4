#!/usr/apps/Python/bin/python
import matplotlib, sys
matplotlib.use('TkAgg')
from scipy import signal
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import*
import model


class GuiStage2:

    def show_credits(self):
        messagebox.showinfo("Credits", "La sororidad 2018")

    def populate_stages_data_frame(self, stages_data_frame):



        gain_frame = Frame(stages_data_frame)
        Q_frame = Frame(stages_data_frame)
        DR_frame = Frame(stages_data_frame)
        vmin_frame = Frame(stages_data_frame)
        vmax_frame = Frame(stages_data_frame)

        gain_frame.pack(side=TOP, fill = 'x')
        Q_frame.pack(side=TOP, fill = 'x')
        DR_frame.pack(side=TOP, fill = 'x')
        vmin_frame.pack(side=TOP, fill = 'x')
        vmax_frame.pack(side=TOP, fill = 'x')

        self.gain = Entry(gain_frame, state = NORMAL)
        self.gain.pack(side=RIGHT)
        self.Q = Entry(Q_frame, state=DISABLED)
        self.Q.pack(side=RIGHT)
        self.DR = Entry(DR_frame, state=DISABLED)
        self.DR.pack(side=RIGHT)
        self.vmin = Entry(vmin_frame, state=NORMAL)
        self.vmin.pack(side=RIGHT)
        self.vmax = Entry(vmax_frame, state=NORMAL)
        self.vmax.pack(side=RIGHT)

        Label(gain_frame, text="G").pack(side = RIGHT)
        Label(Q_frame, text="Q").pack(side = RIGHT)
        Label(DR_frame, text="DR").pack(side = RIGHT)
        Label(vmin_frame, text="V minimo").pack(side = RIGHT)
        Label(vmax_frame, text="V maximo").pack(side = RIGHT)

        self.set_data_button = Button(stages_data_frame, text = "Set data", command = self.set_data)
        self.set_data_button.pack()

    def populate_stages_plot_control_frame(self, stages_plot_control_frame):
        self.plot_mode_list = ["Individual", "Acumulative"]
        self.plot_mode = StringVar()
        self.plot_mode.set(self.plot_mode_list[0])

        #todo: los botones de agrandar achicar etc

        plot_mode_menu = OptionMenu(stages_plot_control_frame, self.plot_mode, *self.plot_mode_list)
        plot_mode_menu.pack(side = TOP, fill = 'x')

        stages_select_menu = Listbox(stages_plot_control_frame, xscrollcommand = True, selectmode = EXTENDED)
        stages_select_menu.pack(side = TOP, fill = 'x');

        #todo: debug, borrar

        debug_list =  ["gilada", "fsde", "dsfsd", "fofofo"]
        for item in debug_list:
            stages_select_menu.insert(END, item)

    def populate_stages_plot_frame(self, stages_plot_frame):
        graph = Canvas(stages_plot_frame)
        graph.pack(side = TOP,fill=BOTH,expand=True,padx=2,pady=4)
        f = Figure(figsize=(4,3))
        self.axis = f.add_subplot(111)

        self.dataPlot = FigureCanvasTkAgg(f, master=graph)  #Una Tk drawing area
        self.dataPlot.draw()
        self.dataPlot.get_tk_widget().pack(side = TOP)
        nav = NavigationToolbar2Tk(self.dataPlot, stages_plot_frame)    #la barra con toda la info
        nav.update()
        self.dataPlot._tkcanvas.pack(side = TOP, fill=X, expand=True)

    def populate_stages_overview_frame(self, stages_overview_frame):
        print("populate_stages_overview_frame")
        Button(stages_overview_frame, text="<", command=self.scroll_stages_overview_left).pack(side=LEFT, fill=Y)
        Button(stages_overview_frame, text=">", command=self.scroll_stages_overview_right).pack(side=RIGHT, fill=Y)
        # self.stages_overview_frame[1].frame.pack_forget()

    def populate_pole_zero_frame(self, pole_zero_frame):
        graph = Canvas(pole_zero_frame, width = 50, bg='red')
        graph.config(width=20, height=20)
        graph.pack(side = TOP, padx=2, pady=4)
        f = Figure(figsize=(3,3))
        self.axis = f.add_subplot(111)

        self.dataPlot = FigureCanvasTkAgg(f, master=graph)  #Una Tk drawing area
        self.dataPlot.draw()
        self.dataPlot.get_tk_widget().pack()
        self.dataPlot._tkcanvas.pack()

        auxFrame = Frame(pole_zero_frame)
        auxFrame.pack(side = TOP)

        self.pole_menu = Listbox(auxFrame, exportselection=False)
        self.pole_menu.pack(side = LEFT)
        self.zero_menu = Listbox(auxFrame, exportselection=False)
        self.zero_menu.pack(side = RIGHT)


        pole_debug_list =  ["polos 1", "polos 2", "polos 3", "polos 4"]
        for item in pole_debug_list:
            self.pole_menu.insert(END, item)

        zero_debug_list =  ["ceros 1", "ceros 2", "ceros 3", "ceros 4"]
        for item in zero_debug_list:
            self.zero_menu.insert(END, item)

        auxxFrame = Frame(pole_zero_frame)
        auxxFrame.pack(side = TOP)

        Button(auxxFrame, text = "Create stage with selected", command = self.create_stage_with_selected_cb).pack(side = TOP, fill = X)
        Button(auxxFrame, text = "Create all stages automatically", command = self.automatic_stages_cb).pack(side = TOP, fill = X)

    def scroll_stages_overview_left(self):
        if self.stages_overview_scroll_offset > 0:
            self.stages_overview_scroll_offset-=1
        self.draw_stages_overview()

    def scroll_stages_overview_right(self):
        if self.stages_overview_scroll_offset < (len(self.stages_overview_subframes)-3):
            self.stages_overview_scroll_offset += 1
        self.draw_stages_overview()

    def draw_stages_overview(self):
        for stage_overview in self.stages_overview_subframes:
            stage_overview.pack_forget()
        for i in range(3):
            if (self.stages_overview_scroll_offset + i) < len(self.stages_overview_subframes):
                self.stages_overview_subframes[self.stages_overview_scroll_offset + i].pack(side=LEFT)

    def add_stage(self, stage):

        f = Figure()
        new_stage_frame = Frame(self.stages_overview_frame)
        new_is_stage_selected = IntVar()
        Checkbutton(new_stage_frame, variable=new_is_stage_selected, state='normal', text='Stage' + str(i+1)).pack(side=BOTTOM, fill=X)   #todo: agregar nombre de la etapa
        graph = Canvas(new_stage_frame, bg='red', width=100)

        axis = FigureCanvasTkAgg(f, master=graph)
        # todo: dibujar en el canva s el filtro correspondiente
        self.stages_overview_dataPlots.append(axis)

        graph.pack(side=TOP, expand=True)
        self.stages_overview_subframes.append(new_stage_frame)
        self.stages_overview_is_selected.append(new_is_stage_selected)
        #self.draw_stages_overview() #: para ver que efectivamente se crean!

    def create_stage_with_selected_cb(self):
        print("create_stage_with_selected_cb")
        #add_stage

    def automatic_stages_cb(self):

        self.m.auto_stages(self.filter_id, float(self.vmin.get()), float(self.vmax.get()))
        self.stages_plots.clear()
        self.stages_plots = self.m.get_auto_stages_plots(self.filter_id)

        self.stages_p_strings.clear()
        self.stages_z_strings.clear()
        self.stages_k_strings.clear()

        for i in range(len(self.stages_plots)):
            self.stages_p_strings.append(self.m.get_auto_stage_p_strings(self.filter_id, i))
            self.stages_z_strings.append(self.m.get_auto_stage_z_strings(self.filter_id, i))
            self.stages_k_strings.append(self.m.get_auto_stages_k(self.filter_id, i))

    def set_data(self):
        print("G = ", int(self.gain.get()), ", Vmin = ", int(self.vmin.get()), ", Vmax = ", self.vmax.get())


    def __init__(self, filter_id, m):
        self.gain_input = None
        self.root = Tk()
        self.root.title("Tc Example")

        #set_filter

        self.gain = StringVar()
        self.Q = StringVar()
        self.DR = StringVar()
        self.vmin = StringVar()
        self.vmax = StringVar()

        # todo: obtener de Tomi:
        self.poles_list = []
        self.zeros_list = []


        self.stages_list = []
        self.stages_overview_subframes = []
        self.stages_overview_is_selected = []
        self.stages_overview_scroll_offset = 0
        self.stages_overview_list = []

        f = Figure()
        self.axis = f.add_subplot(111)

        self.filter_id = filter_id
        self.m = m
        self.stages_plots = []
        self.stages_p_strings = []
        self.stages_z_strings = []
        self.stages_k_strings = []

        #------------------------------------------------------------------------
        # menu de la ventana
        #------------------------------------------------------------------------
        menubar = Menu(self.root)
        menubar.add_command(label="About...", command=self.show_credits)
        menubar.add_command(label="Quit", command=self.root.quit)
        self.root.config(menu=menubar)

        #------------------------------------------------------------------------
        # todos los frames y subframes
        #------------------------------------------------------------------------


        self.pole_zero_frame = LabelFrame(self.root, text = "Pole-Zero", width = 50)
        self.pole_zero_frame.pack(side=LEFT, fill='y')
        self.populate_pole_zero_frame(self.pole_zero_frame)


        self.stages_frame = LabelFrame(self.root,text = "Stages",  width = 40)
        self.stages_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # divido en dos para poder poner cosas en las esquinas con side = TOP/BOTTOM
        self.stages_right_frame = LabelFrame(self.stages_frame, text="r")
        self.stages_right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        self.stages_left_frame = LabelFrame(self.stages_frame, text="l")
        self.stages_left_frame.pack(side=LEFT, fill=BOTH)


        #cuatro paneles dentro de stages:
        self.stages_data_frame = LabelFrame(self.stages_left_frame, text = "Stages data", width = 40)
        self.stages_data_frame.pack(anchor = 'nw', fill = X)
        self.populate_stages_data_frame(self.stages_data_frame)

        self.stages_plot_control_frame = LabelFrame(self.stages_left_frame, text="Plot control", width = 40)
        self.stages_plot_control_frame.pack(anchor='sw', fill=X)
        self.populate_stages_plot_control_frame(self.stages_plot_control_frame)

        self.stages_plot_frame = LabelFrame(self.stages_right_frame, text="Plot", width=1)
        self.stages_plot_frame.pack(anchor='ne', fill='x', expand=True)
        self.populate_stages_plot_frame(self.stages_plot_frame)

        self.stages_overview_dataPlots = []
        self.stages_overview_frame = LabelFrame(self.stages_right_frame, text="stages", width=40)
        self.stages_overview_frame.pack(anchor='se', fill='x', expand=True)
        self.populate_stages_overview_frame(self.stages_overview_frame)



#
#         #------------------------------------------------------------------------
#         #create user input frame
#         #------------------------------------------------------------------------
#         user_input_frame = LabelFrame(self.root)
#         user_input_frame.pack(side=LEFT, fill="y")
#
#         #------------------------------------------------------------------------
#         #Frame filter_type-------------------------------------------------------
#         #------------------------------------------------------------------------
#         filter_type_frame = LabelFrame(user_input_frame, text = "Filter type", width = 20, height = 15)
#         filter_type_frame.pack(side = TOP, fill = "x")
#
#         # filter-type drop-down menu
#         self.filter_type_name = StringVar()
#         self.filter_type_name.set("Filter type")  # default value
#         filter_type_menu = OptionMenu(filter_type_frame, self.filter_type_name, *self.filter_type_list)
#         filter_type_menu.pack(side=TOP, fill = "x")
#
#         # filter_type confirm button
#         filter_type_set_button = Button(filter_type_frame, text = "Set filter type",command = self.set_filter_type)
#         filter_type_set_button.pack(side=TOP)
#
#
#         #------------------------------------------------------------------------
#         #Frame plantilla---------------------------------------------------------
#         #------------------------------------------------------------------------
#         template_parameters_frame = LabelFrame(user_input_frame, text = "Plantilla", width = 20, height = 15)
#         template_parameters_frame.pack(side = TOP, fill = "x")
#
#         approximation_type_name = StringVar()
#         approximation_type_name.set("Approximation type")  # default value
#         filter_type_menu = OptionMenu(template_parameters_frame, approximation_type_name, *self.approximation_type_list)
#         filter_type_menu.pack(side=TOP, fill="x")
#
#
#         #todos los parametros para el template
#         self.template_parameters_input = {
#             "wa": [],
#             "wp": [],
#             "Aa": [],
#             "Ap": [],
#             "BWp": [],
#             "BWa": [],
#             "tau": [],
#             "tol": [],
#             "wrg": []
#         }
#
#         #entries para los parametros del templates
#         for key in self.template_parameters_input:
#             self.template_parameters_input[key].append(StringVar())                           #template_parameters_input[key][0]
#             self.template_parameters_input[key].append(Frame(template_parameters_frame))      #template_parameters_input[key][1]
#             self.template_parameters_input[key].append(Entry(self.template_parameters_input[key][1], width = 30, textvariable=self.template_parameters_input[key][0], state='disabled'))
#             self.template_parameters_input[key][2].pack(side=RIGHT)
#             Label(self.template_parameters_input[key][1], text=key).pack(side=RIGHT)
#             self.template_parameters_input[key][1].pack(side=TOP, anchor = NE)
#
#
#         #desnormalizacion con sliders
#         desnorm_input = Frame(template_parameters_frame)
#         desnorm = StringVar()
#         desnorm_scale = Scale(desnorm_input, from_=0, to_=100, orient=HORIZONTAL)
#         desnorm_scale.pack(side = RIGHT)
#         desnormLabel = Label(desnorm_input, text="Desnormalizacion")
#         desnormLabel.pack(side=RIGHT, fill=X)
#         desnorm_input.pack(anchor = NW)
#
#
#         #Qmax
#         qmax_input_frame = Frame(template_parameters_frame)
#         self.qmax_value = StringVar()
#
#         qmax_label = Label(qmax_input_frame, text="Q max:")
#         qmax_input = Entry(qmax_input_frame, textvariable=self.qmax_value, width=5, state='disabled')
#
#         qmax_label.pack(side=LEFT)
#         qmax_input.pack(side=LEFT)
#
#         qmax_input_frame.pack(side=TOP, pady = 2)
#
#
#         #setemo modo de n
#         self.n_options_name = StringVar()
#         self.n_options_list = [ "N libre", "N min y max", "N fijo" ]
#         self.n_options_name.set(self.n_options_list[0])
#         n_options_menu = OptionMenu(template_parameters_frame,self.n_options_name, *self.n_options_list, command=self.n_mode_cb)
#         n_options_menu.pack(side=TOP)
#
#         #nmin y nmax
#         nmaxmin_input_frame = Frame(template_parameters_frame)
#
#         self.nmax_value = StringVar()
#         self.nmin_value = StringVar()
#
#         self.nmax_input = Entry(nmaxmin_input_frame, textvariable = self.nmax_value, width = 5, state = 'disabled')
#         self.nmin_input = Entry(nmaxmin_input_frame, textvariable = self.nmin_value, width = 5, state = 'disabled')
#
#         nmaxmin_label = Label(nmaxmin_input_frame, text="Rango N:")
#         nmaxmin_separator = Label(nmaxmin_input_frame, text=" - ")
#
#         nmaxmin_label.pack(side=LEFT)
#         self.nmin_input.pack(side=LEFT)
#         nmaxmin_separator.pack(side=LEFT)
#         self.nmax_input.pack(side=LEFT)
#
#         nmaxmin_input_frame.pack(side=TOP, pady = 2)
#
#
#
#         #n fijo
#         nfijo_input_frame = Frame(template_parameters_frame)
#         self.nfijo_value = StringVar()
#
#         nfijo_label = Label(nfijo_input_frame, text="N fijo:")
#         self.nfijo_input = Entry(nfijo_input_frame, textvariable = self.nfijo_value, width = 5, state = 'disabled')
#
#         nfijo_label.pack(side = LEFT)
#         self.nfijo_input.pack(side = LEFT)
#
#         nfijo_input_frame.pack(side=TOP, pady = 2)
#
#
#
#
#
#
#
#
#
#         template_parameters_set_button = Button(template_parameters_frame, text="Calculate new filter", command=self.calculate_new_filter_cb)
#         template_parameters_set_button.pack()
#
#
#
#
#
#         #------------------------------------------------------------------------
#         toolbar = Frame(self.root)
#
#         #todos los posibles graficos
#         self.filter_plots_info = {
#             "Mag": [],
#             "Ate": [],
#             "Pha": [],
#             "Pha ret": [],
#             "PZ": [],
#             "Step": [],
#             "Imp": []
#         }
#
#         #entries para los parametros del templates
#         for key in self.filter_plots_info:
# #            self.filter_plots_info[key].append(Button(toolbar, text=key, command=locals()[key]()))
# #            self.filter_plots_info[key][0].pack(side=LEFT,padx=2,pady=2)
#             print(key)
#
#             # self.template_parameters_input[key].append(StringVar())                           #template_parameters_input[key][0]
#             # self.template_parameters_input[key].append(Frame(template_parameters_frame))      #template_parameters_input[key][1]
#             # self.template_parameters_input[key].append(Entry(self.template_parameters_input[key][1], width = 30, textvariable=self.template_parameters_input[key][0], state='disabled'))
#             # self.template_parameters_input[key][2].pack(side=RIGHT)
#             # Label(self.template_parameters_input[key][1], text=key).pack(side=RIGHT)
#             # self.template_parameters_input[key][1].pack(side=TOP, anchor = NE)
#
#         #parametros de los graficos
#         self.normalizacion = StringVar()
#         self.unidades = StringVar()
#         self.db_veces = StringVar()
#         self.current_plot = StringVar()
#
#         #posibles valores para los parametros anteriores, el primero de la lista es el default
#         self.normalizacion_list = ["Desnormalizado", "Normalizado"]
#         self.unidades_list = ["Hz", "rad/s"]
#         self.db_veces_list = ["dB", "Veces"]
#         self.current_plot_list = ["Atenuacion", "Magnitud", "Fase", "Retardo de grupo", "Maximo Q", "Respuesta al impulso", "Respuesta al escalon", "Polos y ceros"]
#
#         #valores default
#         self.normalizacion.set(self.normalizacion_list[0])
#         self.unidades.set(self.unidades_list[0])
#         self.db_veces.set(self.db_veces_list[0])
#         self.current_plot.set(self.current_plot_list[0])
#
#         #creo los drop-down de los parametros
#         normalizacion_input = OptionMenu(toolbar, self.normalizacion, *self.normalizacion_list)
#         unidades_input = OptionMenu(toolbar, self.unidades, *self.unidades_list)
#         db_veces_input = OptionMenu(toolbar, self.db_veces, *self.db_veces_list)
#         current_plot_input = OptionMenu(toolbar, self.current_plot, *self.current_plot_list)
#
#         normalizacion_input.pack(side=TOP, pady=2, fill='x')
#         unidades_input.pack(side=TOP, pady=2, fill='x')
#         db_veces_input.pack(side=TOP, pady=2, fill='x')
#         current_plot_input.pack(side=TOP, pady=2, fill='x')
#
#         #-----------
#         #-----------
#         #-----------
#         self.existing_filters_frame = LabelFrame(toolbar, text = "Filtros existentes", width = 20)
#         self.existing_filters_frame.pack(side = TOP, fill = "x")
#
#         #obtener de rochi
#         self.filters = []
#         self.filters_input = []
#
#         stage_2_button = Button(toolbar, text="Seleccionados a etapa 2", command=self.stage_2_cb)
#         stage_2_button.pack(side=BOTTOM, fill='x')
#
#         delete_filters_button = Button(toolbar, text="Borrar deseleccionados", command=self.delete_unselected_cb)
#         delete_filters_button.pack(side=BOTTOM, fill='x')
#
#
#
#
#
#
#         toolbar.pack(side=RIGHT,fill=Y)
#         graph = Canvas(self.root)
#         graph.pack(side=TOP,fill=BOTH,expand=True,padx=2,pady=4)
#         #-------------------------------------------------------------------------------
#
#         f = Figure()
#         self.axis = f.add_subplot(111)
#         self.sys = signal.TransferFunction([1],[1,1])
#         self.w,self.mag,self.phase = signal.bode(self.sys)
#         self.stepT,self.stepMag = signal.step(self.sys)
#         self.impT,self.impMag = signal.impulse(self.sys)
#
#         self.dataPlot = FigureCanvasTkAgg(f, master=graph)
#         self.dataPlot.draw()
#         self.dataPlot.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
#         nav = NavigationToolbar2Tk(self.dataPlot, self.root)
#         nav.update()
#         self.dataPlot._tkcanvas.pack(side=TOP, fill=X, expand=True)
#         self.plotMag()
#         #-------------------------------------------------------------------------------
        self.root.mainloop()

#if __name__ == "__main__":
#    ex = GuiStage2()
