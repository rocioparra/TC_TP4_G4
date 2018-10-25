import math
import cmath
import numpy
from abc import ABC, abstractmethod
import numpy.polynomial.legendre as legpol
from numpy.polynomial import Polynomial
import numpy.polynomial.polynomial as poly
from group_delay import group_delay
from scipy.special import ellipk, ellipj
#from sortedcontainers import SortedDict
import copy


def get_attenuation_approximations():
    return ["Butterworth", "Chebyshev", "Inverse Chebyshev"]


def get_group_delay_approximations():
    return ["Bessel"]


def approximation_factory(s):
    switcher = {
        "Bessel":               Bessel,
        "Butterworth":          Butterworth,
        "Chebyshev":            Chebyshev,
        "Inverse Chebyshev":    InvChebyshev
    }

    return switcher.get(s)


class Approximation(ABC):
    @staticmethod
    @abstractmethod
    def get_min_n(template):
        pass

    @staticmethod
    @abstractmethod
    def pzk(n, template):
    # devuelve los polos y ceros con im()>0. como las funciones que definen son a coefs ctes reales, agregar el conjugado
        pass

    @staticmethod
    def epsilon(alpha):
        return math.sqrt(10**(alpha/10)-1)


class Butterworth(Approximation):
    @staticmethod
    def get_min_n(template):
        epsilon = Butterworth.epsilon(template.alpha_p)
        return math.ceil(math.log10(math.sqrt((10**(template.alpha_a/10)-1))/epsilon)/math.log10(template.wa))

    @staticmethod
    def pzk(n, template):
        epsilon = Butterworth.epsilon(template.alpha_p)
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


class Chebyshev(Approximation):
    @staticmethod
    def get_min_n(template):
        epsilon = Chebyshev.epsilon(template.alpha_p)
        n = math.acosh(math.sqrt(10**(template.alpha_a/10))/epsilon)/math.acosh(template.wa)
        return math.ceil(n)

    @staticmethod
    def pzk(n, template):
        epsilon = Chebyshev.epsilon(template.alpha_p)
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
            gain *= 10 ** (-template.alpha_p / 20)
        return [poles, [], gain]


class InvChebyshev(Approximation):
    @staticmethod
    def get_min_n(template):
        return Chebyshev.get_min_n(template)

    @staticmethod
    def epsilon(alpha):
        return 1/math.sqrt(10**(alpha/10)-1)

    @staticmethod
    def pzk(n, template):
        epsilon = InvChebyshev.epsilon(template.alpha_a)
        beta = -math.asinh(1 / epsilon) / n
        gain = 1
        poles = []
        zeros = []

        for k in range(1, n // 2 + 1):
            alpha = (2 * k - 1) * math.pi / 2 / n
            re = math.sin(alpha) * math.sinh(beta)
            im = math.cos(alpha) * math.cosh(beta)
            p = template.wa/(re - 1j * im)
            poles.append(p)
            gain *= (numpy.absolute(p) ** 2)

            z = 1j * template.wa / math.cos(alpha)
            zeros.append(z)
            gain /= numpy.absolute(z)**2

        if n % 2 == 1:
            p = template.wa/math.sinh(beta)
            poles.append(p)
            gain *= (-p)

        return [poles, zeros, gain]


class Bessel(Approximation):
    polynomials = []
    # primeros dos polinomios de bessel. el resto los voy agregando a medida que los calculo

    @staticmethod
    def get_min_n(template):
        n = 1
        while not (Bessel.meets_template(template, n)):
            n += 1

        return n

    @staticmethod
    def meets_template(template, n):
        b = Bessel.get_poly(n)
        poles = poly.polyroots(c=b.coef)
        gd = group_delay(w=[template.w_rg], p=poles, z=[])
        if gd[0] >= 1-template.tol:
            return True
        else:
            return False

    @staticmethod
    def pzk(n, template):
        b_n = Bessel.get_poly(n)
        k = 1
        poles = []
        roots = b_n.roots()
        for i in range(len(roots)):
            if roots[i].imag > 0:
                poles.append(roots[i])
                k *= numpy.absolute(roots[i])**2
            elif roots[i].imag == 0:
                k *= numpy.absolute(roots[i])
                poles.append(roots[i])

        return poles, [], k

    @staticmethod
    def get_poly(n):
        if n > len(Bessel.polynomials):
            if n == 1:
                Bessel.polynomials.append(Polynomial(coef=[1, 1]))
            elif n == 2:
                Bessel.polynomials.append(Polynomial(coef=[3, 3, 1]))
            else:
                b_n_2 = poly.polymul(Polynomial(coef=[0, 0, 1]), Bessel.get_poly(n-2))
                b_n_1 = poly.polymul(Polynomial(coef=[2*n-1]), Bessel.get_poly(n-1))
                b_n = poly.polyadd(b_n_1, b_n_2)
                Bessel.polynomials.append(b_n[0])
        return Bessel.polynomials[n-1]



#peor caso n*k1 = 12.57! sorry not sorry, es imposible obtener ratios mayores con las funciones de scipy
# class Cauer(implements(Approximation)):
#     jacobi_imag_cos = None
#     elliptic_int_ratio = None
#
#     @staticmethod
#     def get_min_n(template):
#         k1 = Cauer.get_k1(template)
#         k = 1/template.wa  # selectividad (plantilla normalizada -> wp = 1 -> wp/wa = 1/wa_norm)
#         n = Cauer.ellipk_ratio(k)/Cauer.ellipk_ratio(k1)
#         return math.ceil(n)
#
#     @staticmethod
#     def pzk(n, template):
#         k1 = Cauer.get_k1(template)
#         k = Cauer.inverse_ellipk_ratio(n * Cauer.ellipk_ratio(k1))
#         gain = 10**(-template.alpha_p/20)
#         z = []
#         p = []
#
#         v0 = Cauer.inverse_jacobi(n, k1, Cauer.epsilon(template.alpha_p))/n
#         pole = 1j * Cauer.cd(1 - 1j*v0, k)
#         if pole.imag >= 0:
#             aux = 1j*pole.imag
#             if pole.real < 0:
#                 aux.real = pole.real
#             p.append(aux)
#             gain *= numpy.absolute(pole)
#             if pole.imag > 0:
#                 gain *= numpy.absolute(pole)
#
#         for i in range(1, n//2+1):
#             u = (2*i-1)/n
#             xi = Cauer.cd(u, k)  # ceros de la funcion racional eliptica
#             zero = 1j / (k*xi)
#             if zero.imag >= 0:
#                 z.append(zero)  # ceros de transferencia
#                 gain /= numpy.absolute(zero)
#                 if zero.imag > 0:
#                     gain /= numpy.absolute(zero)
#             z.append(zero)
#
#             pole = 1j * Cauer.cd(u - 1j*v0, k)
#
#             if pole.imag >= 0:
#                 gain *= numpy.absolute(pole)
#                 if pole.imag > 0:
#                     gain *= numpy.absolute(pole)
#                 aux = pole.imag * 1j
#                 if pole.real < 0:
#                     aux.real = pole.real
#                 p.append(aux)
#
#         return [p, z, gain]
#
#     @staticmethod
#     def ellipk_ratio(k):
#         return ellipk(k)/ellipk(math.sqrt(1-k**2))
#
#     @staticmethod
#     def inverse_ellipk_ratio(ratio):
#         if Cauer.elliptic_int_ratio is None:
#             Cauer.generate_tables()
#         i = Cauer.elliptic_int_ratio.bisect_left(ratio)  # indice del valor inmediatamente superior
#
#         high_ratio, ans = Cauer.elliptic_int_ratio.peekitem(i)
#         # interpolo linealmente si no lo pegue
#         if i > 0 and ratio is not high_ratio:
#             high = ans
#             [low_ratio, low] = Cauer.elliptic_int_ratio.peekitem(i-1)
#             ans = low + (ratio - low_ratio) * (high - low)/(high_ratio - low_ratio)
#
#         return ans
#
#     @staticmethod
#     def inverse_jacobi(n, k1, epsilon_p):
#         if Cauer.jacobi_imag_cos is None:
#             Cauer.generate_tables()
#
#         i = Cauer.jacobi_imag_cos.bisect_left(k1)
#         k_high, dict = Cauer.jacobi_imag_cos.peekitem(i)
#         if i>0 and k_high is not k1:
#             k_low, dict_low = Cauer.jacobi_imag_cos.peekitem(i-1)
#             if abs(k_low - k1) < abs(k_high - k1):
#                 dict = dict_low
#
#         i = dict.bisect_left(1/epsilon_p)
#         sn_high, w = dict.peekitem(i)
#         if i > 0 and sn_high is not 1/epsilon_p:
#             w_high = w
#             sn_low, w_low = dict.peekitem(i-1)
#             w = w_low + (1/epsilon_p-sn_low) * (w_high - w_low)/(sn_high - sn_low)
#
#         return w
#
#     @staticmethod
#     def generate_tables():
#         k = numpy.logspace(start=-16, stop=0, endpoint=False, num=1000)
#         k = 1-k
#         k = k[999:0:-1]  #obtengo puntos lo mas cerca del uno que puedo
#
#         ratio = [Cauer.ellipk_ratio(v) for v in k]
#         # genero un diccionario ordenado con keys=ellip(k), values=k
#         Cauer.elliptic_int_ratio = SortedDict(list(zip(ratio, k)))
#
#         # Sn(jw, k) = j * Sn(w, k')/Cn(w, k'), k' = sqrt(1-k**2)
#         # genero 1000 diccionarios de keys=Sn(jw,k), values=w, cada dict con k distinta
#         dict_list = []
#         for value in k:
#             # para una Sn(z, k), su dominio es [0,K]x[0,K'], K=ellip(k), K'=ellip(k')
#             # entonces si tengo dominio imaginario puro, tiene que estar entre 0 y K'
#             comp = math.sqrt(1 - value ** 2)
#             w = numpy.linspace(start=0, stop=ellipk(comp), num=1000)
#             [sn, cn, _, _] = ellipj(w, comp)
#             keys = sn/cn
#             kth_dict = SortedDict(list(zip(keys, w)))
#             dict_list.append((value, kth_dict))
#
#         Cauer.jacobi_imag_cos = SortedDict(dict_list)
#
#     @staticmethod
#     def cd(u, k):
#         if u.imag == 0:
#             _, cn, dn, _ = ellipj(u, k)
#             return cn/dn
#
#         v = u.imag
#         u = u.real
#         su, cu, du, _ = ellipj(u, k)
#         sv, cv, dv, _ = ellipj(v, math.sqrt(1-k**2))
#
#         num = cu*cv - 1j * su*du*sv*dv
#         den = du*cv*dv - 1j * (k**2)*su*cu*sv
#         return num/den
#
#     @staticmethod
#     def get_k1(template):
#         return Cauer.epsilon(template.alpha_p) / Cauer.epsilon(template.alpha_a)  # factor discriminante





# class Legendre(implements(Approximation)):
#     polynomials = []  # Ln(s) que voy calculando. FALTA INTEGRAR porque eso depende de wn
#
#     @staticmethod
#     def get_min_n(template):
#         epsilon = Approximation.epsilon(template)
#         n = 1
#         while not Legendre.ok(epsilon, Legendre.get_poly(n)):
#             n = n+1
#
#
#
#     @staticmethod
#     def pzk(n, template):
#         pass
#
#     @staticmethod
#     def ok(epsilon, pol):
#         pass
#
#     @staticmethod
#     def get_poly(n):
#         if n > len(Legendre.polynomials):
#             for i in range(len(Legendre.polynomials)+1, n+1):
#                 Legendre.calculate_nth_poly(i)
#         return Legendre.polynomials[n-1]
#
#     @staticmethod
#     def calculate_nth_poly(n):
#         k = (n - 1) // 2
#         new_pol = numpy.asarray([0])
#         leg_order = [1]  # para indicar que polinomio de legendre quiero
#
#         if n % 2 == 0:
#             for i in range(0, k + 1, 2):  # solo sumo los pares
#                 a = (2 * i + 1) / math.sqrt((k + 1) * (k + 2))
#                 leg_order[-1] = a  # pido que el polinomio este multiplicado por a
#                 ith_pol = legpol.leg2poly(leg_order)
#                 new_pol = poly.polyadd(new_pol, ith_pol)
#                 leg_order = [0] + leg_order  # la proxima iteracion pido un orden mas
#
#             new_pol = poly.polypow(new_pol, 2)
#             new_pol = poly.polymul(new_pol, numpy.asarray([1, 1]))
#         else:
#             for i in range(0, k+1):
#                 a = (2 * i + 1) / (math.sqrt(2)*(k + 1))
#                 leg_order[-1] = a  # pido que el polinomio este multiplicado por a
#                 ith_pol = legpol.leg2poly(leg_order)
#                 new_pol = poly.polyadd(new_pol, ith_pol)
#                 leg_order = [0] + leg_order  # la proxima iteracion pido un orden mas
#
#             new_pol = poly.polypow(new_pol, 2)
#
#         Legendre.polynomials.append(poly.polyint(c=new_pol, lbnd=-1))
