import filter
import numpy as np
import scipy
class LowPass(filter.Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        filter.Filter.__init__(self, "lp", approx, alphaP, alphaA, n)
        self.wp = template[0]
        self.wa = template[1]

    def normalize(self):
        pass

    def denormalize_one_pole(self,pole):
        # cambio de variable: s-> s/wp

        # 1/(s-p) -> (wp) *s/(s - wp*p)
        # entonces por cada polo REAL en poles tengo:

        if pole.imag == 0:
            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([self.wp, 0], [1, -self.wp*pole])

        # 1/( (s-p)*(s-conj(p))) =  1/(s^2 -2*real(p)*s + abs(p)^2) ->
        # (wp)^2 / (s^2 - 2*real(p)*wp *s + wp^2*abs(p)^2)
        # entonces por cada polo IMAGINARIO tengo:

        else:
            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([self.wp**2], [1, - 2 * np.real(pole)*self.wp, self.wp**2 * abs(pole)**2])

        return [denorm_poles, denorm_zeroes, gain_factor]


class HighPass(filter.Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        filter.Filter.__init__(self, "hp", approx, alphaP, alphaA, n)
        self.wp = template[0]
        self.wa = template[1]

    def normalize(self):
        pass

    def denormalize_one_pole(self, pole):
        # cambio de variable: s-> wp/s

        # 1/(s-p) -> (-1/p) *s/(s - wp/p)
        # entonces por cada polo REAL en poles tengo:

        if pole.imag == 0:
            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([-1],[pole, -self.wp])

        # 1/( (s-p)*(s-conj(p))) =  1/(s^2 -2*real(p)*s + abs(p)^2) ->
        # s^2/((p*conj(p))*s^2 + (- p*wp - wp*conj(p))*s + wp^2)

        # entonces por cada polo IMAGINARIO en poles tengo:

        else:
            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([1], [abs(pole)**2, -self.wp*2*np.real(pole), self.wp**2])

        return [denorm_poles, denorm_zeroes, gain_factor]

class BandPass(filter.Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        filter.Filter.__init__(self, "bp", approx, alphaP, alphaA, n)
        self.w0 = template[0]
        self.q = template[1]

    def normalize(self):
        pass

    def denormalize_one_pole(self, pole):
        # cambio de variable: s -> q*(s/wo+wo/s) = q*(s^2+wo^2)/(s*wo)

        # 1/(s-p) -> (wo*s)/(q*s^2 - p*s*wo + q*wo^2)

        # entonces por cada polo REAL tengo:

        if pole.imag == 0:
            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([self.wo], [self.q, -pole * self.wo, self.q * self.wo**2])

        # 1/( (s-p)*(s-conj(p)) ) ->
        # ((-wo^2)*s^2)/((-q^2)*s^4 + q*wo*(conj(p) + p) *s^3 + (- 2*q^2*wo^2 - p*conj(p)*wo^2)*s^2 + (p*q*wo^3 + q*wo^3*conj(p))*s - q^2*wo^4)
        # ((-wo^2)*s^2)/(a*s^4 + b *s^3 + c *s^2 + d *s + e)

        # entonces por cada polo IMAGINARIO tengo:

        else:
            a = -self.q**2
            b = self.q * self.wo * 2 * np.real(pole)
            c = -(2*self.q**2 + abs(pole)**2)*self.wo**2
            d = 2 * np.real(pole) * self.q * self.wo**3
            e = - self.q**2 * self.wo**4

            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([-self.wo**2], [a, b, c, d, e])


        return [denorm_poles, denorm_zeroes, gain_factor]


class BandReject(filter.Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        filter.Filter.__init__(self, "br", approx, alphaP, alphaA, n)
        self.w0 = None  # ver esto
        self.q = None

    def normalize(self):
        pass

    def denormalize_one_pole(self, pole):

        # cambio de variable: s -> 1/ ( q*(s/wo+wo/s) ) == s*wo / (q * (s^2 + wo^2) )

        # 1/(s-p) -> (- q*s^2 - q*wo^2)/(p*q*s^2 - s*wo + p*q*wo^2)
        # entonces por cada polo REAL tengo:

        if pole.imag == 0:
            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk(
                [-self.q, 0, -self.q*self.wo**2], [pole*self.q, - self.wo, pole*self.q*self.wo**2])

        # (q^2*s^4 + 2*q^2*s^2*wo^2 + q^2*wo^4) /
        # ((p*q^2*conj(p))*s^4 + (- q*wo*conj(p) - p*q*wo)*s^3 + (2*p*conj(p)*q^2*wo^2 + wo^2)*s^2 + (- p*q*wo^3 - q*wo^3*conj(p))*s + p*q^2*wo^4*conj(p))

        # que se puede escribir como
        # (a*s^4 + c*s^2 + e) /
        # (f*s^4 + g*s^3 + h *s^2 + i *s + j)
        # entonces por cada polo IMAGINARIO tengo:
        else:

            # numerador
            a = self.q**2
            c = 2 * self.q**2 * self.wo**2
            e = self.q**2 * self.wo**2
            # denominador

            f = abs(pole)**2 * self.q**2
            g = -self.q*self.wo*2*np.real(pole)
            h = (2*abs(pole)**2 * self.q**2 * self.wo**2 + self.wo**2)
            i = -self.wo**3*self.q*2*np.real(pole)
            j = abs(pole)**2 * self.q**2 * self.wo**4

            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([a, 0, c, 0, e], [f, g, h, i, j])

        return [denorm_poles, denorm_zeroes, gain_factor]
