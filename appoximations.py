import math
import cmath
import numpy
from interface import implements, Interface, default


class Approximation(Interface):
    @staticmethod
    def get_min_n(wa_norm, alpha_a, alpha_p):
        pass

    @staticmethod
    def pzk(n, alpha_p, wa_norm):
    # devuelve los polos y ceros con im()>0. como las funciones que definen son a coefs ctes reales, agregar el conjugado
        pass

    @default
    @staticmethod
    def epsilon(alpha_p):
        return math.sqrt(10**(alpha_p/10)-1)


class Butterworth(implements(Approximation)):
    @staticmethod
    def get_min_n(wa_norm, alpha_a, alpha_p):
        epsilon = Butterworth.epsilon(alpha_p)
        return math.ceil(math.log10(math.sqrt((10**(alpha_a/10)-1))/epsilon)/math.log10(wa_norm))

    @staticmethod
    def pzk(n, alpha_p, wa_norm):
        epsilon = Butterworth.epsilon(alpha_p)
        poles = []
        r = epsilon**(-1/n)
        delta_theta = math.pi/n
        theta = math.pi/2 + delta_theta/2
        k = 1

        while len(poles) < n//2:# agrego los polos con im(p)>0
            p = cmath.rect(r, theta)
            poles.append(p)
            theta += delta_theta
            k *= numpy.absolute(p)**2

        if n % 2 == 1:  # si me falta un polo esta en el eje real
            poles.append(-r)
            k *= (-r)

        return [poles, [], k]


class Chebyshev(implements(Approximation)):
    @staticmethod
    def get_min_n(wa_norm, alpha_a, alpha_p):
        epsilon = Chebyshev.epsilon(alpha_p)
        n = math.acosh(math.sqrt(10**(alpha_a/10))/epsilon)/math.acosh(wa_norm)
        return math.ceil(n)

    @staticmethod
    def pzk(n, alpha_p, wa_norm):
        epsilon = Chebyshev.epsilon(alpha_p)
        beta = -math.asinh(1 / epsilon) / n
        gain = 1

        poles = []
        for k in range(1, n // 2 + 1):
            alpha = (2 * k - 1) * math.pi / 2 / n
            re = math.sin(alpha) * math.sinh(beta)
            im = math.cos(alpha) * math.cosh(beta)
            p = re + 1j * im
            poles.append(p)
            gain *= (numpy.absolute(p) ** 2)

        if n % 2 == 1:
            p = math.sinh(beta)
            poles.append(p)
            gain *= (-p)
        else:
            gain *= 10 ** (-alpha_p / 20)
        return [poles, [], gain]


class InvChebyshev(implements(Approximation)):
    @staticmethod
    def get_min_n(wa_norm, alpha_a, alpha_p):
        return Chebyshev.get_min_n(wa_norm=wa_norm, alpha_a=alpha_a, alpha_p=alpha_p)

    @staticmethod
    def epsilon(alpha_p): ##ESTE RECIBE ALPHA_A, NO P. PERO TIENE QUE TENER EL MISMO NOMBRE LA VARIABLE
        return 1/math.sqrt(10**(alpha_p/10)-1)

    @staticmethod
    def pzk(n, alpha_p, wa_norm): #PASARLE ALPHA_A, NO ALPHA_P
        epsilon = InvChebyshev.epsilon(alpha_p)
        beta = -math.asinh(1 / epsilon) / n
        gain = 1
        poles = []
        zeros = []

        for k in range(1, n // 2 + 1):
            alpha = (2 * k - 1) * math.pi / 2 / n
            re = math.sin(alpha) * math.sinh(beta)
            im = math.cos(alpha) * math.cosh(beta)
            p = wa_norm/(re - 1j * im)
            poles.append(p)
            gain *= (numpy.absolute(p) ** 2)

            z = 1j * wa_norm / math.cos(alpha)
            zeros.append(z)
            gain /= numpy.absolute(z)**2

        if n % 2 == 1:
            p = wa_norm/math.sinh(beta)
            poles.append(p)
            gain *= (-p)

        return [poles, zeros, gain]


class Bessel(implements(Approximation)):
    @staticmethod
    def get_min_n(wa_norm, alpha_a, alpha_p):
        pass

    @staticmethod
    def pzk(n, alpha_p, wa_norm):
        pass

    @staticmethod
    def get_coefficients(n):
        if n == 1:
            return [1, 1]
        elif n == 2:
            return [1, 3, 1]
        else:
            b_n_1 = (2*n-1) * Bessel.get_coeffients(n-1)
            b_n_2 = numpy.convolve(Bessel.get_coeffients(n-2), [1, 0,0])
            b_n_1 = numpy.pad(b_n_1, (len(b_n_2)-len(b_n_1), 0), 'constant', constant_values=0)
            return b_n_1 + b_n_2
