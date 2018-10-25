import numpy as np
import filter
import math
from scipy import signal
class Stage:
    def __init__(self, poles, zeros, gain_factor, vout_min, vout_max, pass_bands):
        self.poles = poles
        self.zeros = zeros
        self.gain_factor = gain_factor

        [self.vin_min, self.vin_max, self.k_min, self.k_max, self.dynamic_range] = self.calculate_rd(self.poles,
                                                                                                self.zeros, vout_min, vout_max,
                                                                                                self.gain_factor, pass_bands)
        self.q = None
        # etapas de primer o segundo orden solamente!!
        if poles[0].imag and poles[0].real:   # si es complejo
            self.q = np.absolute(poles[0]) / (2 * poles[0].real)  # calculo el q

    def get_display_info(self):
        return [self.vin_min, self.vin_max, self.q, self.dynamic_range]

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
        # 6) pass_bands: intervalos en los que buscar maximos y minimos de la transferencia para poder calcular el rango dinamico y asi maximizarlo
    # OUTPUT:
        # stage correspondiente al best partner del cero.
    @staticmethod
    def find_best_partner(zero, poles, gain_factor, vout_min, vout_max, pass_bands):
        zero = [zero]
        max_rd = -math.inf
        best_partner = None

        for pole in poles:          # recorro la lista de polos
            pole = [pole]
            [_, _, _, _, rd] = Stage.calculate_rd(zero, pole, vout_min, vout_max, gain_factor, pass_bands)

            if rd > max_rd and len(pole) >= 1:             # el que tiene mejor rd es la mejor pareja
                best_partner = [pole[0]]

        st = Stage(zero, best_partner, gain_factor, vout_min, vout_max, pass_bands)

        # elimino al polo que acabo de utilizar para que no se itere con el al buscar al companero del prox cero
        poles.remove(best_partner)
        return st

    @staticmethod
    def update_dynamic_ranges(stages, vout_min, vout_max, pass_bands):
        for k in range(len(stages)):
            stages[k] = Stage(poles=stages[k].poles, zeros=stages[k].zeros, gain_factor=stages[k].gain_factor,
                              vout_min=vout_min, vout_max=vout_max, pass_bands=pass_bands)

    @staticmethod
    def calculate_rd(zeros, poles, vout_min, vout_max, gain_factor, pass_bands):
        [min_at, max_at] = Stage.get_min_max_attenuation(zeros, poles, gain_factor, pass_bands)
        vin_max = abs(vout_max * min_at)
        vin_min = abs(vout_min * max_at)
        rd = vin_max / vin_min
        return [vin_min, vin_max, min_at, max_at, rd]

    @staticmethod
    def get_min_max_attenuation(poles, zeros, gain_factor, pass_bands):

        filter.Filter.re_add_complex(poles)
        filter.Filter.re_add_complex(zeros)

        sys = signal.ZerosPolesGain(zeros, poles, gain_factor)
        max_at = -math.inf
        min_at = math.inf

        for pass_band in pass_bands:
            w = np.logspace(start=math.log10(pass_band[0]), stop=math.log10(pass_band[1]), endpoint=True, base=10)
            [_, attenuation, _] = signal.bode(system=sys, w=w)
            if min(attenuation) < min_at:
                min_at = min(attenuation)
            if max(attenuation) > max_at:
                max_at = max(attenuation)

        filter.Filter.add_only_one_complex(poles)
        filter.Filter.add_only_one_complex(zeros)

        return [min_at, max_at]

