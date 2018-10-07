import math
import cmath
from interface import implements, Interface, default


class Approximation(Interface):
    @staticmethod
    def get_min_n(self, wp, wa, alpha_a, alpha_p):
        pass

    @staticmethod
    def pzk(self, n, alpha_p):
        pass

    @default
    def epsilon(self, alpha_p):
        return math.sqrt(10**(alpha_p/10)-1)


class Butterworth(implements(Approximation)):
    @staticmethod
    def get_min_n(self, wp, wa, alpha_a, alpha_p):
        wa_norm = wa/wp
        epsilon = self.epsilon(alpha_p)
        return math.ceil(math.log10(math.sqrt((10**(alpha_a/10)-1))/epsilon)/math.log10(wa_norm))

    @staticmethod
    def pzk(self, n, alpha_p):
        epsilon = self.epsilon(alpha_p)
        poles = []
        r = epsilon**(-1/n)
        delta_theta = math.pi/n
        theta = math.pi/2 + delta_theta/2

        while len(poles) < n-1:
            poles.append(cmath.rect(r, theta))
            poles.append(cmath.rect(r, -theta))
            theta += delta_theta

        if len(poles) == n-1:
            poles.append(-r)

        return [poles, [], 1]


class Chebyshev(implements(Approximation)):
    @staticmethod
    def get_min_n(self, wp, wa, alpha_a, alpha_p):
        epsilon = self.epsilon(alpha_p)
        wa_norm = wa/wp
        n = math.acosh(math.sqrt(10**(alpha_a/10))/epsilon)/math.acosh(wa_norm)
        [p, z, k] = self.pzk(self, n, wp, wa, alpha_a, alpha_p)
        return [n, p, z, k]

    @staticmethod
    def pzk(self, n, alpha_p):
        pass


class InvChebyshev(implements(Approximation)):
    @staticmethod
    def get_min_n(self, wp, wa, alpha_a, alpha_p):
        pass

    @staticmethod
    def pzk(self, n, alpha_p):
        pass


class Bessel(implements(Approximation)):
    @staticmethod
    def get_min_n(self, wp, wa, alpha_a, alpha_p):
        pass

    @staticmethod
    def pzk(self, n, alpha_p):
        pass
