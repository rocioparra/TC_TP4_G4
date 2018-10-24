import numpy as np


class Stage:
    def __init__(self, poles, zeros, gain_factor, vout_min, vout_max):
        self.poles = poles
        self.zeros = zeros
        self.gain_factor = gain_factor
        self.f0 = -inf
        self.finf = inf

        # FALTA CALCULAR WP Y WA Y DEMAS!!
        # FIJARSE FUNCIONES CON TEMPLATE!!

        [self.vin_min, self.vin_max, self.dynamic_range] = self.calculate_rd(self.poles, self.zeros, vout_min, vout_max)

        self.q = None
        # etapas de primer o segundo orden solamente!!
        if len(poles) == 1:         # chequeo que sea un solo polo, que puede ser real o complejo:
            if not poles[0].imag:   # si es complejo
                self.q = np.abssolute(poles[0]) / (2 * poles.real)  # calculo el q



    def get_display_info(self):
        return [self.f0, self.finf, self.q, self.rd]
        pass

    # --------------------------
    # find_best_partner
    # -------------------------
    # find_best_partner encuentra a la mejor pareja para un cierto cero que intenta maximizar el rd de una sola etapa.
    # una vez hallado el polo que hace la mejor pareja, elimina al polo de la lista de polos asi ya no
    # se podra encontrar esa pareja para otro cero.

    # INPUT:
        # 1) zero: cero al que se le busca la pareja
        # 2) poles: lista de polos de la cual elegir la mejor pareja para cierto cero
        # 3) gain_factor: factor de ganancia para la etapa
        # 4) vout_min: vout_min: minimo vout para el filtro para superar el piso de ruido
        # 5) vout_max: maximo vout para el filtro total para que no saturen los opamps en alguna de las etapas
    # OUTPUT:
        # void.
    @staticmethod
    def find_best_partner(zero, poles, gain_factor, vout_min, vout_max):

        max_rd = -inf
        best_partner = None

        for pole in poles:          # recorro la lista de polos

            [_, _, rd] = calculate_rd(zero, poles, vout_min, vout_max)

            if rd > max_rd:             # el que tiene mejor rd es la mejor pareja
                best_partner = pole

        Filter.re_add_complex(best_partner)
        st = Stage(zero, [best_partner], gain_factor, vout_min, vout_max)

        # elimino al polo que acabo de utilizar para que no se itere con el al buscar al companero del prox cero
        poles.remove(best_partner)

        return st

    @staticmethod
    def update_dynamic_ranges(stages, vout_min, vout_max):
        for k in range(len(stages)):
            stages[k] = Stage(poles=stage.poles, zeros=stage.zeros, gain_factor=stage.gain_factor, vout_min=vout_min, vout_max=vout_max)

    @staticmethod
    def calculate_rd(zeros, poles, vout_min, vout_max):
        [min_at, max_at] = get_min_max_attenuation(zeros, poles, gain_factor)
        vin_max = vout_max / max_at
        vin_min = vout_min / min_at
        rd = vin_max / vin_min
        return [vin_min, vin_max, rd]

    @staticmethod
    def get_min_max_attenuation(poles, zeros, gain_factor):
        Filter.re_add_complex(poles)
        Filter.re_add_complex(zeros)

        sys = signal.ZeroesPolesGain(zeros, poles, gain_factor)
        w = np.logspace(start=log10(self.template.wp), stop=log10(self.template.wa), endpoint=True, base=10)
        [w, attenuation, _] = signal.bode(system=sys, w=w)

        Filter.add_only_one_complex(poles)
        Filter.add_only_one_complex(zeros)

        return [min(attenuation), max(attenuation)]
