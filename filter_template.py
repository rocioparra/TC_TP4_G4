from abc import ABC


class FilterTemplate(ABC):
    def __init__(self, template_type, n_min, n_max, q_max, denorm_degree):
        self.template_type = template_type
        self.n_min = n_min
        self.n_max = n_max
        self.q_max = q_max
        self.denorm_degree = denorm_degree


class LowPassTemplate(FilterTemplate):
    def __init__(self, param, n_min, n_max, q_max, denorm_degree):
        super().__init__("Low-pass", n_min, n_max, q_max, denorm_degree)
        [self.wa, self.wp, self.alpha_p, self.alpha_p] = param


class HighPassTemplate(FilterTemplate):
    def __init__(self, param, n_min, n_max, q_max, denorm_degree):
        super().__init__("High-pass", n_min, n_max, q_max, denorm_degree)
        [self.wa, self.wp, self.alpha_p, self.alpha_p] = param


class BandPassTemplate(FilterTemplate):
    def __init__(self, w0, bw_p, bw_a, alpha_p, alpha_a, n_min, n_max, q_max, denorm_degree):
        super().__init__("Band-pass", n_min, n_max, q_max, denorm_degree)
        self.w0 = w0
        self.bw_p = bw_p
        self.bw_a = bw_a
        self.alpha_p = alpha_p
        self.alpha_a = alpha_a


class BandRejectTemplate(FilterTemplate):
    def __init__(self, param, n_min, n_max, q_max, denorm_degree):
        super().__init__("Band-reject", n_min, n_max, q_max, denorm_degree)
        [self.w0, self.bw_p, self.bw_a, self.alpha_p, self.alpha_a] = param


class GroupDelayTemplate(FilterTemplate):
    def __init__(self, param, n_min, n_max, q_max):
        super().__init__("Group delay", n_min, n_max, q_max, denorm_degree=None)
        [self.w_rg, self.tau, self.tol] = param
