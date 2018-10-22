from abc import ABC


class FilterTemplate(ABC):
    def __init__(self, template_type):
        self.template_type = template_type
        # self.n = 0


class LowPassTemplate(FilterTemplate):
    def __init__(self, wp, wa, alpha_p, alpha_a):
        super().__init__('lp')
        self.wa = wa
        self.wp = wp
        self.alpha_p = alpha_p
        self.alpha_a = alpha_a


class GroupDelayTemplate(FilterTemplate):
    def __init__(self, w_rg, tau, tolerance):
        super().__init__('gd')
        self.tol = tolerance
        self.w_rg = w_rg
        self.tau = tau


def template_factory(filter_type):
    if filter_type == "lp" or filter_type == "hp" or filter_type == "bp" or filter_type == "br":
        return LowPassTemplate()
    elif filter_type == 'gd':
        return GroupDelayTemplate()
    else:
        pass
