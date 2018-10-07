from .user import User
from .dir import Dir
import Filter

class LowPass(Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        Filter.__init__(self, "lp", approx, template, alphaP, alphaA, n)
        self.wp = template[0]
        self.wa = template[1]

    def normalize(self):
        pass

    def denormalize(self):
        self.poles = [p / self.wp for p in self.poles]
        self.zeros = []
        self.k = 1

class HighPass(Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        Filter.__init__(self, "hp", approx, template, alphaP, alphaA, n)
        self.wp = template[0]
        self.wa = template[1]

    def normalize(self):
        pass

    def denormalize(self)
        ## cambio de variable: s-> wp/s
        ## 1/(s/p+1) -> (p/wp) * s / (s/(wp/p) + 1)
        ## entonces por cada polo en p tengo:
        ## - un cero en el origen
        ## - un polo en wp/p
        ## - ganancia p/wp
        self.zeros = numpy.zeros(norm_poles.len())
        self.k = wp ** (-norm_poles.len())

        denorm_poles = []
        for p in self.poles:
            denorm.poles.append(poles.append(wp / p))
            self.k *= p

        self.poles = denorm_poles



class BandPass(Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        Filter.__init__(self, "bp", approx, template, alphaP, alphaA, n)
        self.w0 = None #ver esto
        self.q = None

    def normalize(self):
        pass

    def denormalize(self):
        pass


class BandReject(Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        Filter.__init__(self, "br", approx, template, alphaP, alphaA, n)
        self.w0 = None #ver esto
        self.q = None

    def normalize(self):
        pass

    def denormalize(self):
        pass
