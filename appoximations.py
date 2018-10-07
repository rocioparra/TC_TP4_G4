import math
import cmath
from interface import implements, Interface


class Approximation(Interface):
    @staticmethod
    def pzk(self, wp, wa, alpha_a, alpha_p):
        pass


class Butterworth(implements(Approximation)):
    def butterworth(self, wp, wa, alphaP, alphaA):
        wa_norm = wa/wp
        epsilon = math.sqrt(10**(alphaP/10-1))
        n = math.ceil(math.log10((10**(alphaA/10)-1)/epsilon)/2/math.log10(wa_norm))
        poles = []

        for i in range(1, n+1):
            poles.append(wp*cmath.exp(1j*(2*i+n-1)*math.pi/2/n)/epsilon**(1/n))
        return [n, poles, [], 1]