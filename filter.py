from abc import ABC, abstractmethod
import math
import cmath
import numpy
from scipy import signal


class Filter(ABC):

    def __init__(self, filter_type, approx, template, alphaP, alphaA, n):
        super().__init__()
        self.type = filter_type
        self.approx = approx
        self.n = n # ver que onda cuando lo calculo yo vs cuando me lo imponen
        self.wp = wp
        self.wa = wa
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

    @abstractmethod
    def denormalize(self):
        pass

    def calculate_poles(self):
        self.calculate_norm_poles() ## reemplazar por switcher para approx
#        self.poles = [p/self.wp for p in self.poles]

        denorm = switcher.get(self.type)
        [self.poles, self.zeros, self.k] = denorm(self.poles)




