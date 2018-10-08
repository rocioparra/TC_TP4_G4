import math
import cmath
import numpy
from interface import implements, Interface, default


class Approximation(Interface):
    @staticmethod
    def get_min_n(self, wa_norm, alpha_a, alpha_p):
        pass

    @staticmethod
    def pzk(self, n, alpha_p):
    # devuelve los polos y ceros con im()>0. como las funciones que definen son a coefs ctes reales, agregar el conjugado
        pass

    @default
    def epsilon(self, alpha_p):
        return math.sqrt(10**(alpha_p/10)-1)


class Butterworth(implements(Approximation)):
    @staticmethod
    def get_min_n(self, wa_norm, alpha_a, alpha_p):
        epsilon = self.epsilon(alpha_p)
        return math.ceil(math.log10(math.sqrt((10**(alpha_a/10)-1))/epsilon)/math.log10(wa_norm))

    @staticmethod
    def pzk(self, n, alpha_p):
        epsilon = self.epsilon(alpha_p)
        poles = []
        r = epsilon**(-1/n)
        delta_theta = math.pi/n
        theta = math.pi/2 + delta_theta/2

        while len(poles) < n//2: # agrego los polos con im(p)>0
            poles.append(cmath.rect(r, theta))
            theta += delta_theta

        if len(poles) == n-1: # si me falta un polo esta en el eje real
            poles.append(-r)

        return [poles, [], 1]


class Chebyshev(implements(Approximation)):
    @staticmethod
    def get_min_n(self, wa_norm, alpha_a, alpha_p):
        epsilon = self.epsilon(alpha_p)
        n = math.acosh(math.sqrt(10**(alpha_a/10))/epsilon)/math.acosh(wa_norm)
        return n

    @staticmethod
    def pzk(self, n, alpha_p):
        epsilon = self.epsilon(alpha_p)
        beta = math.asinh(1/epsilon)/n

        poles = []
        for k in range(1, n//2+1):
            alpha = (2*k - 1) * math.pi / 2 / n
            re = math.sen(alpha) * math.sinh(beta)
            im = math.cos(alpha) * math.cosh(beta)
            poles.append(re + 1j*im)

        if len(poles) < math.ceil(n/2):
            poles.append(-abs(math.sinh(beta)))

        return [poles, [], 1]


class InvChebyshev(implements(Approximation)):
    @staticmethod
    def get_min_n(self, wa_norm, alpha_a, alpha_p):
    ## A ESTE PASARLE WP_NORM, WA_NORM = 1
        epsilon = 1/self.epsilon(alpha_a)
        return math.acosh(1/(epsilon * math.sqrt(10**(alpha_p/10)-1)))/math.acosh(1/wa_norm)
        pass

    @staticmethod
    def pzk(self, n, alpha_p):
        epsilon = 1/self.epsilon(alpha_a)
        beta = math.asinh(1/epsilon)/n

        poles = []
        zeros = []

        for k in range(1, n//2+1):
            alpha = (2 * k - 1) * math.pi / 2 / n
            rec1 = math.sen(alpha) * math.sinh(beta)
            imc1 = math.cos(alpha) * math.cosh(beta)

            poles.append(1/(rec1 - 1j * imc1))
            zeros.append(-1j / math.cos(alpha))

        if len(poles) < math.ceil(n/2):
            poles.append(-abs(1/math.sinh(beta)))
            zeros.append(1j)

        return [poles, zeros, 1]


class Bessel(implements(Approximation)):
    @staticmethod
    def get_min_n(self, wa_norm, alpha_a, alpha_p):
        pass

    @staticmethod
    def pzk(self, n, alpha_p):
        pass

    @staticmethod
    def get_coefficients(n):
        if n == 1:
            return [1, 1]
        elif n == 2:
            return [1, 3, 1]
        else:
            b_n_1 = (2*n-1) * Bessel.get_coeffients(n-1)
            b_n_2 = numpy.convolve(Bessel.get_coeffients(n-2), [1, 0 ,0])
            b_n_1 = numpy.pad(b_n_1, (len(b_n_2)-len(b_n_1), 0), 'constant', constant_values=0)
            return b_n_1 + b_n_2
