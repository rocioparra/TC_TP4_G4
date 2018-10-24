from abc import ABC, abstractmethod
import numpy as np
from scipy import signal
from appoximations import approximation_factory
import matplotlib.pyplot as plt
import filtertypes


class Filter(ABC):
    filter_dict = {}

    def __init__(self, filter_type, approx, n):
        super().__init__()
        self.type = filter_type
        self.approx = approx
        self.n = n  # # ver que onda cuando lo calculo yo vs cuando me lo imponen
        self.normalized_poles = []
        self.denormalized_poles = []
        self.normalized_zeros = []
        self.denormalized_zeros = []
        self.normalized_k = None
        self.denormalized_k = None
        self.normalized_template = None
        self.denormalized_template = None
        self.stages = None

# porcentaje de normalizacion ahre
# etapas

    @staticmethod
    def get_available_filters():
        if not Filter.filter_dict:
            Filter.filter_dict = filtertypes.get_filter_dict()

        return list(Filter.filter_dict.keys())

    @staticmethod
    def get_parameters_for(filter_str):
        return (Filter.filter_dict.get(filter_str)).get_parameter_list()

    @staticmethod
    def get_approximations_for(filter_str):
        return (Filter.filter_dict.get(filter_str)).get_available_approximations()

    @staticmethod
    @abstractmethod
    def get_available_approximations():
        pass

    @staticmethod
    @abstractmethod
    def get_parameter_list():
        pass

    @abstractmethod
    def normalize(self):
        pass

    # --------------------------
    # denormalize
    # -------------------------
    # desnormalize denormaliza todos los polos y ceros de la lista de polos y ceros normalizados
    # cambia denormalized_poles y denormalized_zeros, actualizandolos con los nuevos valores.

    # INPUT:
            #no input
    # OUTPUT:
            #void

    def denormalize(self):
        self.denormalized_k = self.normalized_k
        self.denormalized_poles = []    #vacio las listas por las dudas
        self.denormalized_zeros = []
        
        for p in self.normalized_poles:
            [denorm_poles, denorm_zeroes, gain_factor] = self.denormalize_one_pole(p)
            self.denormalized_poles.append(denorm_poles)
            self.denormalized_zeros.append(denorm_zeroes)
            self.denormalized_k = self.denormalized_k * gain_factor

        for z in self.normalized_zeros:
            # ESTA AL REVES A PROPOSITO!!! LOS CEROS TIENEN CONVERSION INVERSA A LOS POLOS!!
            [denorm_zeroes, denorm_poles, gain_factor] = self.denormalized_one_pole(z)
            self.denormalized_poles.append(denorm_poles)
            self.denormalized_zeros.append(denorm_zeroes)
            self.denormalized_k = self.denormalized_k * (1/gain_factor)

        self.denormalized_poles = self.add_only_one_complex(self.denormalized_poles)
        self.denormalized_zeros = self.add_only_one_complex(self.denormalized_zeros)

    # --------------------------
    # denormalize_one_pole
    # -------------------------
    # desnormalize_one_pole es un metodo abstracto, depende del tipo de filtro a utilizar
    # aplica el cambio de variable apropiado a un solo polo real o a un par conjugado
    # devuelve [denorm_poles, denorm_zeroes, gain_factor]

    # INPUT:
        # 1) pole: el polo a desnormalizar,  puede ser un complejo, en cuyo caso contara como tambien haber mandado su conjugado.
    # OUTPUT:
        # 1) denorm_poles: polos resultantes de desnormalizar. DEVUELVE DOS COMPLEJOS CONJUGADOS EN CASO DE ESTAR EN ESTA OPCION
                        # debera eliminarse el conjugado en caso de no necesitarlo!!!
        # 2) denorm_zeroes: ceros resultantes de desnormalizar. DEVUELVE DOS COMPLEJOS CONJUGADOS EN CASO DE ESTAR EN ESTA OPCION
                        # debera eliminarse el conjugado en caso de no necesitarlo!!!
        # 3) gain_factor: la ganancia resultante del cambio de variable para ese polo.

    @abstractmethod
    def denormalize_one_pole(self, pole):
        pass

    # --------------------------
    # calculate_poles
    # -------------------------
    # calculate_poles hace normalizacion del filtro, obtiene la funcion transferencia para la aproximacion pertinente

    # INPUT:
        # no input
    # OUTPUT:
        # void
    def calculate_poles(self):
        self.normalize()

        approximation = approximation_factory(self.approx)
        n = approximation.get_min_n(self.normalized_template)
        [self.normalized_poles, self.normalized_zeros, self.normalized_k] = approximation.pzk(n, self.normalized_template)
        self.adjust_denorm_degree()
        self.denormalize()      # desnormalizo todos los polos

        #antes de graficar, si necesito todos los polos:
        self.re_add_complex(self.denormalized_zeros)
        self.re_add_complex(self.denormalized_poles)

        sys = signal.ZerosPolesGain(self.denormalized_zeros, self.denormalized_poles, self.denormalized_k)
        hmia = sys.to_tf()
        [w, mag, pha] = signal.bode(hmia)
        plt.semilogx(w, -mag)
        plt.grid(b=True)
        plt.show()


    # --------------------------
    # add_only_one_complex
    # -------------------------
    # recorre la lista complex_nums, reconoce los numeros pertenecientes a C-R
    # (parte imaginaria distinta de cero)
    # de aqui elimina de la lista el complejo con parte imaginaria negativa y
    # deja su conjugado en la lista.

    # INPUT:
        # 1) complex_nums: lista con numeros a la cual se le eliminara cualquier complejo con parte imaginaria negativa
    # OUTPUT:
        # void.
    @staticmethod
    def add_only_one_complex(complex_nums):
        for comp in complex_nums:
            if comp.imag < 0:
                complex_nums.remove(comp)
            else:
                pass

        return complex_nums
    # --------------------------
    # re_add_complex
    # -------------------------
    # recorre la lista complex_nums, reconoce los numeros pertenecientes a C-R
    # con parte imaginaria positiva
    # de aqui agrega a la lista el complejo con parte imaginaria negativa y
    # deja su conjugado en la lista.

    # INPUT:
        # 1) complex_nums: lista con numeros a la cual se le eliminara cualquier complejo con parte imaginaria negativa
    # OUTPUT:
        # void.
    @staticmethod
    def re_add_complex(complex_nums):
        for comp in complex_nums:
            if comp.imag > 0:
                complex_nums.append(np.conj(comp))
            else:
                pass

    # --------------------------
    # auto_stage_decomposition
    # -------------------------
    # auto_stage_decomposition obtiene la cadena de etapas que intentan maximizar el rd total

    # INPUT:
        # 1) vout_min: minimo vout para el filtro para superar el piso de ruido
        # 2) vout_max: maximo vout para el filtro total para que no saturen los opamps en alguna de las etapas
    # OUTPUT:
        # void.
    def auto_stage_decomposition(self, vout_min, vout_max):

        self.stages.clear()
        zeros = self.denormalized_zeros
        poles = self.denormalized_poles
        for zero in zeros:
            st = Stage.find_best_partner(zero, poles, self.gain_factor, vout_min, vout_max)
            self.stages.append(st)
        for pole in poles:              #me quede sin ceros, procedo con los polos!
            self.stages.append(Stage(pole, [], self.gain_factor))

    # --------------------------
    # single_stage_decomposition
    # -------------------------
    # single_stage_decomposition obtiene una etapa para una cierta configuracion de polos y ceros, orden 1 o 2

    # INPUT:
        # 1) poles: polos para la construccion de la etapa
        # 2) zeros: ceros para la construccion de la etapa
        # 3) gain_factor: factor de ganancia para la construccion de la etapa
    # OUTPUT:
        # void.
    def single_stage_decomposition(self, poles, zeros, gain_factor,vout_min, vout_max):
        st = Stage(poles, zeros, gain_factor)  # ingresado por usuario, de una sola etapa x vez
        self.stages.append(st)
        Stage.update_dynamic_ranges(self.stages, vout_min, vout_max)

