from abc import ABC, abstractmethod
import math
from plot_data import TemplatePlotData


class TemplateParameters:
    def __init__(self, wa=False, wp=False, alpha_a=False, alpha_p=False, w0=False, bw_p=False, bw_a=False, tau=False, tol=False, w_rg=False):
        self.data = [wa, wp, alpha_a, alpha_p, w0, bw_p, bw_a, tau, tol, w_rg]
        [self.wa, self.wp, self.alpha_a, self.alpha_p, self.w0, self.bw_p, self.bw_a, self.tau, self.tol, self.w_rg] = \
            [wa, wp, alpha_a, alpha_p, w0, wp, bw_a, tau, tol, w_rg]


class FilterTemplate(ABC):
    def __init__(self, template_type, n_min, n_max, q_max, denorm_degree):
        self.template_type = template_type
        self.n_min = n_min
        self.n_max = n_max
        self.q_max = q_max
        self.denorm_degree = denorm_degree

    @abstractmethod
    def get_plot(self):
        pass

    @abstractmethod
    def get_pass_bands(self):
        pass


class LowPassTemplate(FilterTemplate):
    def __init__(self, param, n_min, n_max, q_max, denorm_degree):
        super().__init__("Low-pass", n_min, n_max, q_max, denorm_degree)
        [self.wp, self.wa, self.alpha_p, self.alpha_a] = [param.wp, param.wa, param.alpha_p, param.alpha_a]

    def get_plot(self):
        pass_band = RectangularArea(top=math.inf, bottom=self.alpha_p, left=0, right=self.wp)
        stop_band = RectangularArea(top=self.alpha_a, bottom=-math.inf, left=self.wa, right=math.inf)
        return TemplatePlotData(x_label="Frequency", x_units="rad/s",
                                y_label="Attenuation", y_units="dB", logscale=True, dB=True,
                                covered_areas=[pass_band, stop_band])

    def get_pass_bands(self):
        return [[0, self.wp]]


class HighPassTemplate(FilterTemplate):
    def __init__(self, param, n_min, n_max, q_max, denorm_degree):
        super().__init__("High-pass", n_min, n_max, q_max, denorm_degree)
        [self.wp, self.wa, self.alpha_p, self.alpha_a] = [param.wp, param.wa, param.alpha_p, param.alpha_a]

    def get_plot(self):
        pass_band = RectangularArea(top=math.inf, bottom=self.alpha_p, left=self.wp, right=math.inf)
        stop_band = RectangularArea(top=-math.inf, bottom=self.alpha_a, left=0, right=self.wa)
        return TemplatePlotData(x_label="Frequency", x_units="rad/s",
                                y_label="Attenuation", y_units="dB", logscale=True, dB=True,
                                covered_areas=[pass_band, stop_band])

    def get_pass_bands(self):
        return [[self.wp, math.inf]]



class BandPassTemplate(FilterTemplate):
    def __init__(self, param, n_min, n_max, q_max, denorm_degree):
        super().__init__("Band-pass", n_min, n_max, q_max, denorm_degree)
        [self.w0, self.bw_p, self.bw_a, self.alpha_p, self.alpha_a] = \
            [param.w0, param.bw_p, param.bw_a, param.alpha_p, param.alpha_a]

        w02 = self.w0 ** 2
        self.wp_plus = (self.bw_p + math.sqrt(self.bw_p ** 2 + 4 * w02)) / 2
        self.wp_minus = w02 / self.wp_plus
        self.wa_plus = (self.bw_a + math.sqrt(self.bw_a ** 2 + 4 * w02)) / 2
        self.wa_minus = w02 / self.wa_plus

    def get_plot(self):
        stop_low = RectangularArea(top=math.inf, bottom=self.alpha_a, left=0, right=self.wa_minus)
        pass_band = RectangularArea(top=self.alpha_p, bottom=-math.inf, left=self.wp_minus, right=self.wp_plus)
        stop_high = RectangularArea(top=math.inf, bottom=self.alpha_a, left=self.wa_plus, right=math.inf)

        return TemplatePlotData(x_label="Frequency", x_units="rad/s",
                                y_label="Attenuation", y_units="dB", logscale=True, dB=True,
                                covered_areas=[stop_low, pass_band, stop_high])

    def get_pass_bands(self):
        return [[self.wp_minus, self.wp_plus]]


class BandRejectTemplate(FilterTemplate):
    def __init__(self, param, n_min, n_max, q_max, denorm_degree):
        super().__init__("Band-reject", n_min, n_max, q_max, denorm_degree)
        [self.w0, self.bw_p, self.bw_a, self.alpha_p, self.alpha_a] = \
            [param.w0, param.bw_p, param.bw_a, param.alpha_p, param.alpha_a]

        w02 = self.w0 ** 2
        self.wp_plus = (self.bw_p + math.sqrt(self.bw_p ** 2 + 4 * w02)) / 2
        self.wp_minus = w02 / self.wp_plus
        self.wa_plus = (self.bw_a + math.sqrt(self.bw_a ** 2 + 4 * w02)) / 2
        self.wa_minus = w02 / self.wa_plus

    def get_plot(self):
        pass_low = RectangularArea(top=self.alpha_p, bottom=-math.inf, left=0, right=self.wp_minus)
        stop_band = RectangularArea(top=math.inf, bottom=self.alpha_a,  left=self.wa_minus, right=self.wa_plus)
        pass_high = RectangularArea(top=self.alpha_p, bottom=-math.inf, left=self.wp_plus, right=math.inf)

        return TemplatePlotData(x_label="Frequency", x_units="rad/s",
                                y_label="Attenuation", y_units="dB", logscale=True, dB=True,
                                covered_areas=[pass_low, stop_band, pass_high])

    def get_pass_bands(self):
        return [[0, self.wp_minus], [self.wp_plus, math.inf]]


class GroupDelayTemplate(FilterTemplate):
    def __init__(self, param, n_min, n_max, q_max):
        super().__init__("Group delay", n_min, n_max, q_max, denorm_degree=None)
        [self.w_rg, self.tau, self.tol] = [param.w_rg, param.tau, param.tol]

    def get_plot(self):
        min_tau = RectangularArea(top=self.tau*(1-self.tol), bottom=-math.inf, left=-math.inf, right=self.w_rg)
        return TemplatePlotData(x_label="Frequency", x_units="rad/s",
                                y_label="Attenuation", y_units="dB", logscale=True, dB=True,
                                covered_areas=[min_tau])

    def get_pass_bands(self):
        return [[0, self.w_rg]]


class RectangularArea:
    def __init__(self, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
