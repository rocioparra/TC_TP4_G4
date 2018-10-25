import filter
import numpy as np
from scipy import signal
import appoximations
from filter_template import LowPassTemplate, GroupDelayTemplate, TemplateParameters


class LowPass(filter.Filter):
    def __init__(self, template, approx):
        super().__init__("Low-pass", approx)
        self.denormalized_template = template

    @staticmethod
    def get_available_approximations():
        return appoximations.get_attenuation_approximations()

    @staticmethod
    def get_parameter_list():
        return TemplateParameters(wa=True, wp=True, Aa=True, Ap=True)

    def normalize(self):
        self.normalized_template = self.denormalized_template
        self.normalized_template.wp = 1
        self.normalized_template.wa = self.denormalized_template.wa/self.denormalized_template.wp

    def denormalize_one_pole(self, pole):
        # cambio de variable: s-> s/wp

        # 1/(s-p) -> (wp) /(s - wp*p)
        # entonces por cada polo REAL en poles tengo:
        wp = self.denormalized_template.wp
        if pole.imag == 0:
            [denorm_zeroes, denorm_poles, gain_factor] = signal.tf2zpk([wp], [1, -wp*pole])

        # 1/( (s-p)*(s-conj(p))) =  1/(s^2 -2*real(p)*s + abs(p)^2) ->
        # (wp)^2 / (s^2 - 2*real(p)*wp *s + wp^2*abs(p)^2)
        # entonces por cada polo IMAGINARIO tengo:

        else:
            [denorm_zeroes, denorm_poles, gain_factor] = \
                signal.tf2zpk([wp**2], [1, - 2 * np.real(pole)*wp, wp**2 * abs(pole)**2])

        return [list(denorm_poles), list(denorm_zeroes), gain_factor]


class HighPass(filter.Filter):
    def __init__(self, template, approx):
        super().__init__("High-pass", approx)
        self.denormalized_template = template

    @staticmethod
    def get_available_approximations():
        return appoximations.get_attenuation_approximations()

    @staticmethod
    def get_parameter_list():
        return TemplateParameters(wa=True, wp=True, Aa=True, Ap=True)

    def normalize(self):
        self.normalized_template = \
            LowPassTemplate(param=[1, self.denormalized_template.wp / self.denormalized_template.wa,
                                   self.denormalized_template.alpha_p, self.denormalized_template.alpha_a],
                            n_min=self.denormalized_template.n_min, n_max=self.denormalized_template.n_max,
                            q_max=self.denormalized_template.q_max,
                            denorm_degree=self.denormalized_template.denorm_degree)

    def denormalize_one_pole(self, pole):
        # cambio de variable: s-> wp/s

        # 1/(s-p) -> 1/(wp/s -p) -> (-s)/(s*p - wp)
        # entonces por cada polo REAL en poles tengo:
        wp = self.denormalized_template.wp
        if pole.imag == 0:
            [denorm_zeroes, denorm_poles, gain_factor] = signal.tf2zpk([-1, 0], [pole, -wp])

        # 1/( (s-p)*(s-conj(p))) =  1/(s^2 -2*real(p)*s + abs(p)^2) ->
        # s^2/((p*conj(p))*s^2 + (- p*wp - wp*conj(p))*s + wp^2)

        # entonces por cada polo IMAGINARIO en poles tengo:

        else:
            [denorm_zeroes, denorm_poles, gain_factor] = \
                signal.tf2zpk([1, 0, 0], [abs(pole) ** 2, -wp * 2 * np.real(pole), wp ** 2])

        return [list(denorm_poles), list(denorm_zeroes), gain_factor]


class BandPass(filter.Filter):
    def __init__(self, template, approx):
        super().__init__("Band-pass", approx)
        self.denormalized_template = template
        self.q = self.denormalized_template.w0/self.denormalized_template.bw_p

    @staticmethod
    def get_available_approximations():
        return appoximations.get_attenuation_approximations()

    @staticmethod
    def get_parameter_list():
        return TemplateParameters(w0=True, BWp=True, BWa=True, Aa=True, Ap=True)

    def normalize(self):
        wa_norm = self.denormalized_template.bw_a/self.denormalized_template.bw_p
        self.normalized_template = \
            LowPassTemplate(param=[1, wa_norm, self.denormalized_template.alpha_p, self.denormalized_template.alpha_a],
                            n_min=self.denormalized_template.n_min, n_max=self.denormalized_template.n_max,
                            q_max=self.denormalized_template.q_max,
                            denorm_degree=self.denormalized_template.denorm_degree)

    def denormalize_one_pole(self, pole):
        # cambio de variable: s -> q*(s/wo+wo/s) = q*(s^2+wo^2)/(s*wo)

        # 1/(s-p) -> (wo*s)/(q*s^2 - p*s*wo + q*wo^2)

        # entonces por cada polo REAL tengo:

        if pole.imag == 0:
            [denorm_zeroes, denorm_poles, gain_factor] = \
                signal.tf2zpk([self.denormalized_template.w0, 0], [self.q, -pole * self.denormalized_template.w0,
                                                                   self.q * self.denormalized_template.w0**2])

        # 1/( (s-p)*(s-conj(p)) ) ->
        # ((-wo^2)*s^2)/((-q^2)*s^4 + q*wo*(conj(p) + p) *s^3 + (- 2*q^2*wo^2 - p*conj(p)*wo^2)*s^2 + (p*q*wo^3 + q*wo^3*conj(p))*s - q^2*wo^4)
        # ((-wo^2)*s^2)/(a*s^4 + b *s^3 + c *s^2 + d *s + e)

        # entonces por cada polo IMAGINARIO tengo:

        else:
            a = -self.q**2
            b = self.q * self.denormalized_template.w0 * 2 * np.real(pole)
            c = -(2*self.q**2 + abs(pole)**2)*self.denormalized_template.w0**2
            d = 2 * np.real(pole) * self.q * self.denormalized_template.w0**3
            e = - self.q**2 * self.denormalized_template.w0**4

            [denorm_zeroes, denorm_poles, gain_factor] = signal.tf2zpk([-self.denormalized_template.w0**2, 0, 0],
                                                                       [a, b, c, d, e])

        return [list(denorm_poles), list(denorm_zeroes), gain_factor]


class BandReject(filter.Filter):
    def __init__(self, template, approx):
        super().__init__("Band-reject", approx)
        self.denormalized_template = template
        self.q = self.denormalized_template.w0/self.denormalized_template.bw_p

    @staticmethod
    def get_available_approximations():
        return appoximations.get_attenuation_approximations()

    @staticmethod
    def get_parameter_list():
        return TemplateParameters(w0=True, BWp=True, BWa=True, Aa=True, Ap=True)

    def normalize(self):
        wa_norm = self.denormalized_template.bw_p / self.denormalized_template.bw_a
        self.normalized_template = \
            LowPassTemplate(param=[1, wa_norm, self.denormalized_template.alpha_p, self.denormalized_template.alpha_a],
                            n_min=self.denormalized_template.n_min, n_max=self.denormalized_template.n_max,
                            q_max=self.denormalized_template.q_max,
                            denorm_degree=self.denormalized_template.denorm_degree)

    def denormalize_one_pole(self, pole):

        # cambio de variable: s -> 1/ ( q*(s/wo+wo/s) ) == s*wo / (q * (s^2 + wo^2) )

        # 1/(s-p) -> (- q*s^2 - q*wo^2)/(p*q*s^2 - s*wo + p*q*wo^2)
        # entonces por cada polo REAL tengo:

        if pole.imag == 0:
            [denorm_zeroes, denorm_poles, gain_factor] = signal.tf2zpk(
                [-self.q, 0, -self.q*self.denormalized_template.w0**2],
                [pole*self.q, - self.denormalized_template.w0, pole*self.q*self.denormalized_template.w0**2])

        # (q^2*s^4 + 2*q^2*s^2*wo^2 + q^2*wo^4) /
        # ((p*q^2*conj(p))*s^4 + (- q*wo*conj(p) - p*q*wo)*s^3 + (2*p*conj(p)*q^2*wo^2 + wo^2)*s^2 + (- p*q*wo^3 - q*wo^3*conj(p))*s + p*q^2*wo^4*conj(p))

        # que se puede escribir como
        # (a*s^4 + c*s^2 + e) /
        # (f*s^4 + g*s^3 + h *s^2 + i *s + j)
        # entonces por cada polo IMAGINARIO tengo:
        else:

            # numerador
            a = self.q**2
            c = 2 * self.q**2 * self.denormalized_template.w0**2
            e = self.q**2 * self.denormalized_template.w0**4
            # denominador

            f = np.absolute(pole)**2 * self.q**2
            g = -self.q*self.denormalized_template.w0*2*pole.real
            h = (2*np.absolute(pole)**2 * self.q**2 * self.denormalized_template.w0**2 + self.denormalized_template.w0**2)
            i = -self.denormalized_template.w0**3*self.q*2*pole.real
            j = np.absolute(pole)**2 * self.q**2 * self.denormalized_template.w0**4

            [denorm_zeroes, denorm_poles, gain_factor] = signal.tf2zpk([a, 0, c, 0, e], [f, g, h, i, j])

        return [list(denorm_poles), list(denorm_zeroes), gain_factor]


class GroupDelay(filter.Filter):
    # params = [wrg, tau, tolerance]
    def __init__(self, template, approx):
        super().__init__(filter_type="Group delay", approx=approx)
        self.denormalized_template = template

    @staticmethod
    def get_available_approximations():
        return appoximations.get_group_delay_approximations()

    @staticmethod
    def get_parameter_list():
        return TemplateParameters(wrg=True, tau=True, tol=True)

    def normalize(self):
        wrgn = self.denormalized_template.wrg * self.denormalized_template.tau
        self.normalized_template = \
            GroupDelayTemplate(param=[wrgn, 1, self.denormalized_template.tolerance],
                               n_min=self.denormalized_template.n_min, n_max=self.denormalized_template.n_max,
                               q_max=self.denormalized_template.q_max)

    def denormalize_one_pole(self, pole):
        self.denormalized_k /= self.denormalized_template.tau
        self.denormalized_poles.append(pole/self.denormalized_template.tau)

    def correct_norm_degree(self):
        pass
