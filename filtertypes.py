import filter
import numpy as np
from scipy import signal
import appoximations
from filter_template import GroupDelayTemplate
from filter_template import LowPassTemplate


def get_filter_dict():
    filter_dict = {
        "Low-pass": LowPass,
        "High-pass": HighPass,
        "Band-pass": BandPass,
        "Band-reject": BandReject,
        "Group delay": GroupDelay
    }
    return filter_dict


class LowPass(filter.Filter):
    def __init__(self, approx, wp, wa, alpha_a, alpha_p, n):
        super().__init__("lp", approx, n)
        self.alpha_a = alpha_a
        self.alpha_p = alpha_p
        self.wp = wp
        self.wa = wa

    @staticmethod
    def get_available_approximations():
        return appoximations.get_attenuation_approximations()

    @staticmethod
    def get_parameter_list():
        return ["wp", "wa", "alpha p", "alpha a"]

    def normalize(self):
        self.normalized_template = LowPassTemplate(wp=1, wa=self.wa/self.wp, alpha_a=self.alpha_a, alpha_p=self.alpha_p)

    def denormalize_one_pole(self, pole):
        # cambio de variable: s-> s/wp

        # 1/(s-p) -> (wp) /(s - wp*p)
        # entonces por cada polo REAL en poles tengo:

        if pole.imag == 0:
            [denorm_zeroes, denorm_poles, gain_factor] = signal.tf2zpk([self.wp], [1, -self.wp*pole])

        # 1/( (s-p)*(s-conj(p))) =  1/(s^2 -2*real(p)*s + abs(p)^2) ->
        # (wp)^2 / (s^2 - 2*real(p)*wp *s + wp^2*abs(p)^2)
        # entonces por cada polo IMAGINARIO tengo:

        else:
            [denorm_zeroes, denorm_poles, gain_factor] = signal.tf2zpk([self.wp**2], [1, - 2 * np.real(pole)*self.wp, self.wp**2 * abs(pole)**2])

        return [denorm_poles, denorm_zeroes, gain_factor]


class HighPass(filter.Filter):
    def __init__(self, approx, wa, wp, alpha_a, alpha_p, n):
        super().__init__(filter_type="hp", approx=approx, n=n)
        self.alpha_a = alpha_a
        self.alpha_p = alpha_p
        self.wp = wp
        self.wa = wa

    @staticmethod
    def get_available_approximations():
        return appoximations.get_attenuation_approximations()

    @staticmethod
    def get_parameter_list():
        return ["wp", "wa", "alpha p", "alpha a"]

    def normalize(self):
        self.normalized_template = LowPassTemplate(wp=1, wa=self.wp / self.wa, alpha_p=self.alpha_p, alpha_a=self.alpha_a)

    def denormalize_one_pole(self, pole):
        # cambio de variable: s-> wp/s

        # 1/(s-p) -> 1/(wp/s -p) -> (-s)/(s*p - wp)
        # entonces por cada polo REAL en poles tengo:

        if pole.imag == 0:
            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([-1, 0], [pole, -self.wp])

        # 1/( (s-p)*(s-conj(p))) =  1/(s^2 -2*real(p)*s + abs(p)^2) ->
        # s^2/((p*conj(p))*s^2 + (- p*wp - wp*conj(p))*s + wp^2)

        # entonces por cada polo IMAGINARIO en poles tengo:

        else:
            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([1, 0, 0],
                                                                             [abs(pole) ** 2, -self.wp * 2 * np.real(pole),
                                                                              self.wp ** 2])

        return [denorm_poles, denorm_zeroes, gain_factor]


class BandPass(filter.Filter):
    def __init__(self, approx, wa_minus, wp_minus, wa_plus, wp_plus, alpha_p, alpha_a, n):
        super().__init__("bp", approx, n)
        self.alpha_a = alpha_a
        self.alpha_p = alpha_p
        self.wa_minus = wa_minus
        self.wp_minus = wp_minus
        self.wa_plus = wa_plus
        self.wp_plus = wp_plus
        self.wo = np.sqrt(self.wa_plus*self.wa_minus)
        self.q = self.wo / (self.wp_plus - self.wp_minus)

    @staticmethod
    def get_available_approximations():
        return appoximations.get_attenuation_approximations()

    @staticmethod
    def get_parameter_list():
        return ["w0", "Q", "alpha p", "alpha a"]

    def normalize(self):
        self.normalized_template = LowPassTemplate(wp=1, wa=(self.wa_plus - self.wa_minus) / (self.wp_plus - self.wp_minus), alpha_a=self.alpha_a, alpha_p=self.alpha_p)

    def denormalize_one_pole(self, pole):
        # cambio de variable: s -> q*(s/wo+wo/s) = q*(s^2+wo^2)/(s*wo)

        # 1/(s-p) -> (wo*s)/(q*s^2 - p*s*wo + q*wo^2)

        # entonces por cada polo REAL tengo:

        if pole.imag == 0:
            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([self.wo, 0], [self.q, -pole * self.wo, self.q * self.wo**2])

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

            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([-self.wo**2, 0, 0], [a, b, c, d, e])

        return [denorm_poles, denorm_zeroes, gain_factor]


class BandReject(filter.Filter):
    def __init__(self, approx, w0, q, alpha_a, alpha_p, n):
        super().__init__("br", approx, n)
        self.alpha_a = alpha_a
        self.alpha_p = alpha_p
        self.w0 = w0
        self.q = q

    @staticmethod
    def get_available_approximations():
        return appoximations.get_attenuation_approximations()

    @staticmethod
    def get_parameter_list():
        return ["w0", "Q", "alpha p", "alpha a"]

    def normalize(self):
        self.normalized_template = LowPassTemplate(wp=1, wa=(self.wp_plus - self.wp_minus) /(self.wa_plus - self.wa_minus),alpha_p=self.alpha_p, alpha_a=self.alpha_a)

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
            e = self.q**2 * self.wo**4
            # denominador

            f = abs(pole)**2 * self.q**2
            g = -self.q*self.wo*2*np.real(pole)
            h = (2*abs(pole)**2 * self.q**2 * self.wo**2 + self.wo**2)
            i = -self.wo**3*self.q*2*np.real(pole)
            j = abs(pole)**2 * self.q**2 * self.wo**4

            [denorm_zeroes, denorm_poles, gain_factor] = scipy.signal.tf2zpk([a, 0, c, 0, e], [f, g, h, i, j])

        return [denorm_poles, denorm_zeroes, gain_factor]


class GroupDelay(filter.Filter):
    # params = [w_rg, tau, tolerance]
    def __init__(self, approx, w_rg, tau, tolerance, n):
        super().__init__(filter_type="gd", approx=approx, n=n)
        self.w_rg = w_rg
        self.tau = tau
        self.tolerance = tolerance

    @staticmethod
    def get_available_approximations():
        return appoximations.get_group_delay_approximations()

    @staticmethod
    def get_parameter_list():
        return ["w rg", "tau", "alpha p", "alpha a"]

    def normalize(self):
        self.normalized_template = GroupDelayTemplate(w_rg=self.w_rg * self.tau, tau=1, tolerance=self.tolerance)

    def denormalize_one_pole(self, pole):
        self.denormalized_k /= self.tau
        self.denormalized_poles.append(pole/self.tau)
