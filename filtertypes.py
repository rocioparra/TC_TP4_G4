import filter

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
            denorm_poles.append(wp / p)
            self.k *= p

        self.poles = denorm_poles



class BandPass(filter.Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        filter.Filter.__init__(self, "bp", approx, alphaP, alphaA, n)
        self.w0 = template[0]
        self.q = template[1]

    def normalize(self):
        pass

    def denormalize(self):
        pass


class BandReject(filter.Filter):
    def __init__(self, approx, template, alphaP, alphaA, n):
        filter.Filter.__init__(self, "br", approx, alphaP, alphaA, n)
        self.w0 = None #ver esto
        self.q = None

    def normalize(self):
        pass

    def denormalize(self):
        pass
