import filter
import numpy as np
class LowPass(filter.Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        filter.Filter.__init__(self, "lp", approx, alphaP, alphaA, n)
        self.wp = template[0]
        self.wa = template[1]

    def normalize(self):
        pass

    def denormalize(self):
        self.poles = [p / self.wp for p in self.poles]
        self.zeros = []
        self.k = 1


class HighPass(filter.Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        filter.Filter.__init__(self, "hp", approx, alphaP, alphaA, n)
        self.wp = template[0]
        self.wa = template[1]

    def normalize(self):
        pass

    def denormalize(self, pole):
        ## cambio de variable: s-> wp/s
        ## 1/(s-p) ->
        ## entonces por cada polo REAL en poles tengo:
        ## - un cero en el origen
        ## - un polo en
        ## - ganancia

        denorm_poles = []
        denorm_zeroes = []

        if pole.imag == 0:
            denorm_poles = []
            denorm_zeroes = []
            gain_factor = 1
            pass
        else:
            denorm_poles = []
            denorm_zeroes = []
            gain_factor = 1
            pass




        return [denorm_poles,denorm_zeroes, gain_factor]

class BandPass(filter.Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        filter.Filter.__init__(self, "bp", approx, alphaP, alphaA, n)
        self.w0 = template[0]
        self.q = template[1]

    def normalize(self):
        pass

    def denormalize_one_pole(self, pole):
        ## cambio de variable: s -> q*(s/wo+wo/s) = q*(s^2+wo^2)/(s*wo)

        ## 1/(s-p) -> (wo/p)*s / (s^2 - p*wo/q*s +wo^2)
        ## entonces por cada polo REAL tengo:
        ## - un cero en el origen
        ## - los dos polos que son raices de (s^2 - p*wo/q*s +wo^2)
        ## - ganancia wo/p

        denorm_poles = []
        denorm_zeroes = []

        if pole.imag == 0:
            denorm_poles = np.roots([1, -pole * self.wo /self.q, self.wo ** 2])
            denorm_zeroes = 0
            gain_factor = self.wo/self.p

        ## 1/( (s-p)*(s-conj(p)) ) -> (wo^2/q)*s^2 / ( s^4 - 2*wo*Re(p)/q *s^3 + (2*q^2+mod(p)^2/q^2)*wo^2 *s^2 - 2*wo^3*Re(p)/q *s + wo^4 )
        ## entonces por cada polo IMAGINARIO tengo:
        ## - dos ceros en el origen
        ## - los polos que son raices de s^4 - 2*wo*Re(p)/q *s^3 + (2*q^2+mod(p)^2/q^2)*wo^2 *s^2 - 2*wo^3*Re(p)/q *s + wo^4
        ## esto puede ser escrito como s^4 + a *s^3 + b *s^2 + c *s + d
        ## - ganancia wo^2/q

        else:
            a = - 2 * self.wo *np.real(pole) /self.q
            b = (2 * self.**2 + abs(pole)^2 / self.q**2 ) *self.wo**2
            c = - 2 * self.wo**3 * np.real(pole) / self.q
            d = self.w0 ** 4

            denorm_poles = np.roots([1, a, b, c, d])
            denorm_zeroes = [0, 0]
            gain_factor = self.wo**2 /self.q

        return [denorm_poles, denorm_zeroes, gain_factor]


class BandReject(filter.Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        filter.Filter.__init__(self, "br", approx, alphaP, alphaA, n)
        self.w0 = None #ver esto
        self.q = None

    def normalize(self):
        pass

    def denormalize_one_pole(self, pole):
        pass
