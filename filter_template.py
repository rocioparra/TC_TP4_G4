from abc import ABC


class FilterTemplate(ABC):
    def __init__(self, template_type):
        self.template_type = template_type
        # self.n = 0


class AttenuationTemplate(FilterTemplate):
    def __init__(self, wa_norm, alpha_p, alpha_a):
        super().__init__('at')
        self.wa_norm = wa_norm
        self.alpha_p = alpha_p
        self.alpha_a = alpha_a


class GroupDelayTemplate(FilterTemplate):
    def __init__(self, w_rg, tolerance):
        super().__init__('gd')
        self.tol = tolerance
        self.w_rg = w_rg
