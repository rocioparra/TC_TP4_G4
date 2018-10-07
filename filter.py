from abc import ABC, abstractmethod
import math
import cmath
import numpy as np
from scipy import signal


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
#
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

    #INPUT:
        # 1) pole: el polo a desnormalizar,  puede ser un complejo, en cuyo caso contara como tambien haber mandado su conjugado.
    #OUTPUT:
        # 1) denorm_poles: polos resultantes de desnormalizar. DEVUELVE DOS COMPLEJOS CONJUGADOS EN CASO DE ESTAR EN ESTA OPCION
                        # debera eliminarse el conjugado en caso de no necesitarlo!!!
        # 2) denorm_zeroes: ceros resultantes de desnormalizar. DEVUELVE DOS COMPLEJOS CONJUGADOS EN CASO DE ESTAR EN ESTA OPCION
                        # debera eliminarse el conjugado en caso de no necesitarlo!!!
        # 3) gain_factor: la ganancia resultante del cambio de variable para ese polo.

    @abstractmethod
    def denormalize_one_pole(self, pole):
        pass


    def calculate_poles(self):
        self.normalize()     # obtengo polos para la normalizada
        self.add_only_one_complex(self.poles)  # elimino uno de los dos complejos conjugados
        self.add_only_one_complex(self.zeros)


        self.denormalize()      #desnormalizo todos los polos

    # --------------------------
    # add_only_one_complex
    # -------------------------
    #recorre la lista complex_nums, reconoce los numeros pertenecientes a C-R
    #(parte imaginaria distinta de cero)
    #de aqui elimina de la lista el complejo con parte imaginaria negativa y
    #deja su conjugado en la lista.

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

