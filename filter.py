from abc import ABC, abstractmethod
import numpy as np
from scipy import signal
from appoximations import approximation_factory
import matplotlib.pyplot as plt


class Filter(ABC):

    def __init__(self, filter_type, approx):
        self.type = filter_type
        self.approx = approx
        self.normalized_poles = []
        self.denormalized_poles = []
        self.normalized_zeros = []
        self.denormalized_zeros = []
        self.normalized_k = None
        self.denormalized_k = None
        self.normalized_template = None
        self.denormalized_template = None
#        self.normalized_tf = None
#        self.denormalized_tf = None
        self.n = None

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

        self.add_only_one_complex(self.denormalized_poles)
        self.add_only_one_complex(self.denormalized_zeros)

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
    # calculate_poles

    # INPUT:
        # no input
    # OUTPUT:
        # void
    def calculate_pzkn(self):
        self.normalize()  # obtengo la plantilla normalizada

        # determino el grado con el que voy a hacer el filtro
        approximation = approximation_factory(self.approx)
        n = approximation.get_min_n(self.normalized_template)  # obtengo el minimo que me cumple plantilla
        if n > self.normalized_template.n_max:  # aplico las restricciones que me dijo el usuario
            n = self.normalized_template.n_max
        elif n < self.normalized_template.n_min:
            n = self.normalized_template.n_min

        # obtengo polos y ceros para este orden
        [self.normalized_poles, self.normalized_zeros, self.normalized_k] = \
            approximation.pzk(n, self.normalized_template)
        self.correct_norm_degree()
        self.denormalize()      # desnormalizo todos los polos
        q = self.get_max_q()

        while q > self.denormalized_template.q_max and n > 1:
            n -= 1  # bajo el grado hastas que cumpla q<q_max o no pueda bajar mas
            [self.normalized_poles, self.normalized_zeros, self.normalized_k] = \
                approximation.pzk(n, self.normalized_template)
            self.correct_norm_degree()
            self.denormalize()
            q = self.get_max_q()
        self.n = n


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

    @staticmethod
    def calculate_tf(positive_poles, positive_zeros, k):
        Filter.re_add_complex(positive_poles)
        Filter.re_add_complex(positive_zeros)
        sys = signal.ZerosPolesGain(positive_zeros, positive_poles, k)
        Filter.add_only_one_complex(positive_poles)
        Filter.add_only_one_complex(positive_zeros)
        return sys.to_tf()

    def correct_norm_degree(self):
        # obtengo la atenuacion en [wp, wa] (wp=1 porque estoy en normalizado)
        w = np.logspace(start=0, stop=np.log10(self.normalized_template.wa), endpoint=True, base=10)
        [w, attenuation, _] = signal.bode(system=self.calculate_tf(self.normalized_poles, self.normalized_zeros,
                                                                   self.normalized_k), w=w)
        attenuation *= (-1)

        # busco w_low: la menor frecuencia para la que A(w)<=alpha_p -> A(w_low) ~= alpha_p
        # quiero k_low: A(k_low * wp) = alpha_p -> k_low = w_l/wp = w_l >= 1
        k_low = 1
        for i in range(len(w)):
            if attenuation[i] > self.normalized_template.alpha_p:
                if i >= 1:
                    k_low = w[i - 1]
                break

        # busco w_high: la mayor frecuencia para la que A(w)>=alpha_a -> A(w_high) ~= alpha_a
        # quiero k_high: A(k_high * wa) = alpha_a -> k_high = w_high/wa <= 1
        w_high = self.normalized_template.wa
        for i in range(len(w) - 1, -1, -1):
            if attenuation[i] < self.normalized_template.alpha_a:
                if i < len(w) - 1:
                    w_high = w[i + 1]
                break
        k_high = w_high / self.normalized_template.wa

        # 0%    ->  k_norm = k_l
        # 100%  ->  k_norm = k_h <= k_l
        # x%    ->  k_norm = k_h + (k_l-k_h) *x/100
        k_norm = k_low - (k_low - k_high) * self.normalized_template.denorm_degree / 100

        self.normalized_poles = [pole / k_norm for pole in self.normalized_poles]
        self.normalized_zeros = [zero / k_norm for zero in self.normalized_zeros]
        self.normalized_k *= (k_norm ** (len(self.normalized_zeros) - len(self.normalized_poles)))

    def get_max_q(self):
        q = [np.absolute(pole)/(2*pole.real) for pole in self.denormalized_poles if pole.imag]
        q = q + [np.absolute(zero)/(2*zero.real) for zero in self.denormalized_zeros if zero.imag]
        if q:
            return max(q)
        else:
            return 0
