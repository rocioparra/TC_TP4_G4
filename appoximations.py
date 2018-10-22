import math
import cmath
import numpy
from interface import implements, Interface, default
import numpy.polynomial.legendre as legpol
from numpy.polynomial import Polynomial
import numpy.polynomial.polynomial as poly
from group_delay import group_delay


def approximation_factory(s):
    switcher = {
        "be": Bessel,
        "bw": Butterworth,
        "c1": Chebyshev,
        "c2": InvChebyshev
    }

    return switcher.get(s)


class Approximation(Interface):
    @staticmethod
    def get_min_n(template):
        pass

    @staticmethod
    def pzk(n, template):
    # devuelve los polos y ceros con im()>0. como las funciones que definen son a coefs ctes reales, agregar el conjugado
        pass

    @default
    @staticmethod
    def epsilon(alpha):
        return math.sqrt(10**(alpha/10)-1)


class Butterworth(implements(Approximation)):
    @staticmethod
    def get_min_n(template):
        epsilon = Butterworth.epsilon(template.alpha_p)
        return math.ceil(math.log10(math.sqrt((10**(template.alpha_a/10)-1))/epsilon)/math.log10(template.wa_norm))

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


class Chebyshev(implements(Approximation)):
    @staticmethod
    def get_min_n(template):
        epsilon = Chebyshev.epsilon(template.alpha_p)
        n = math.acosh(math.sqrt(10**(template.alpha_a/10))/epsilon)/math.acosh(template.wa_norm)
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


class InvChebyshev(implements(Approximation)):
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
            p = template.wa_norm/(re - 1j * im)
            poles.append(p)
            gain *= (numpy.absolute(p) ** 2)

            z = 1j * template.wa_norm / math.cos(alpha)
            zeros.append(z)
            gain /= numpy.absolute(z)**2

        if n % 2 == 1:
            p = template.wa_norm/math.sinh(beta)
            poles.append(p)
            gain *= (-p)

        return [poles, zeros, gain]


class Bessel(implements(Approximation)):
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



class Legendre(implements(Approximation)):
    polynomials = []  # Ln(s) que voy calculando. FALTA INTEGRAR porque eso depende de wn

    @staticmethod
    def get_min_n(template):
        epsilon = Approximation.epsilon(template)
        n = 1
        while not Legendre.ok(epsilon, Legendre.get_poly(n)):
            n = n+1



    @staticmethod
    def pzk(n, template):
        pass

    @staticmethod
    def ok(epsilon, pol):
        pass

    @staticmethod
    def get_poly(n):
        if n > len(Legendre.polynomials):
            for i in range(len(Legendre.polynomials), n+1):
                Legendre.calculate_nth_poly(i)
        return Legendre.polynomials[n]

    @staticmethod
    def calculate_nth_poly(n):
        k = (n - 1) // 2
        new_pol = Polynomial(coef=[0])
        leg_order = [1]  # para indicar que polinomio de legendre quiero

        if n % 2 == 0:
            for i in range(0, k + 1, 2):  # solo sumo los pares
                a = (2 * i + 1) / math.sqrt((k + 1) * (k + 2))
                leg_order[-1] = a  # pido que el polinomio este multiplicado por a
                ith_pol = legpol.leg2poly(legpol.Legendre(leg_order))
                new_pol = poly.polyadd(new_pol, ith_pol)
                leg_order = [0] + leg_order  # la proxima iteracion pido un orden mas

            new_pol = poly.polypow(new_pol, 2)
            new_pol = poly.polymul(new_pol, Polynomial(coef=[1, 1]))
        else:
            for i in range(0, k+1):
                a = (2 * i + 1) / (math.sqrt(2)*(k + 1))
                leg_order[-1] = a  # pido que el polinomio este multiplicado por a
                ith_pol = legpol.leg2poly(legpol.Legendre(leg_order))
                new_pol = poly.polyadd(new_pol, ith_pol)
                leg_order = [0] + leg_order  # la proxima iteracion pido un orden mas

            new_pol = poly.polypow(new_pol, 2)

        Legendre.polynomials.append(new_pol.integ(lbnd=-1))

