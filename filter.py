from abc import ABC, abstractmethod
import math
import cmath
import numpy as np
from scipy import signal
from appoximations import Butterworth
from filter_template import AttenuationTemplate
import matplotlib.pyplot as plt


class Filter(ABC):

    def __init__(self, filter_type, approx, alphaP, alphaA, n):
        super().__init__()
        self.type = filter_type
        self.approx = approx
        self.n = n  # # ver que onda cuando lo calculo yo vs cuando me lo imponen
        self.alphaP = alphaP
        self.alphaA = alphaA
        self.poles = []
        self.zeros = []
        self.k = None

# porcentaje de normalizacion ahre
# etapas

    @abstractmethod
    def normalize(self):
        pass

    #me deja en self poles y en self.zeroes todos los ceros y polos resultantes de desnormalizar
    def denormalize(self):
        self.k = 1
        final_denorm_poles = []
        final_denorm_zeroes = []

        for p in self.poles:
            [denorm_poles, denorm_zeroes, gain_factor] = self.denormalize_one_pole(p)
            # si se puede apependear tod o junto mejor, no lo se hacer en sintaxis
            final_denorm_poles.append(denorm_poles)
            final_denorm_zeroes.append(denorm_zeroes)
            self.k = self.k * gain_factor

        self.poles = self.add_only_one_complex(final_denorm_poles)
        self.zeros = self.add_only_one_complex(final_denorm_zeroes)

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

    def calculate_poles(self):
        self.normalize()
        # asignar self.poles y self.zeroes y self.k a lo que me devuelva el switcher
        template = AttenuationTemplate(wa_norm=self.wan, alpha_p=self.alphaP, alpha_a=alpha_a)
        n = Butterworth.get_min_n(template)
        [self.poles, self.zeros, self.k] = Butterworth.pzk(template=template, n=n)
        self.denormalize()      # desnormalizo todos los polos

        def switch(self.type4):
            switcher = {
                1: "lp",
                2: "hp",
                3: "March",
                4: "April",
            }
        switcher.get(self.type)
        re_add_complex(self.zeros)
        re_add_complex(self.poles)
        sys = signal.ZerosPolesGain(self.zeros, self.poles, self.k)
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
    def add_only_one_complex(self, complex_nums):
        for comp in complex_nums:
            if comp.imag <0:
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
    def re_add_complex(self, complex_nums):
        for comp in complex_nums:
            if not comp.imag > 0:
                new_comp = conj(comp)
                complex_nums.append(new_comp)
            else:
                pass