import filtertypes
import filter_template
import filter
from scipy import signal
from plot_data import ContinuousPlotData, ScatterPlotData, TemplatePlotData

class Model:
    def __init__(self):
        self.filter_dict = {
            "Low-pass":     [filtertypes.LowPass, filter_template.LowPassTemplate],
            "High-pass":    [filtertypes.HighPass, filter_template.HighPassTemplate],
            "Band-pass":    [filtertypes.BandPass, filter_template.BandPassTemplate],
            "Band-reject":  [filtertypes.BandReject, filter_template.BandRejectTemplate],
            "Group delay":  [filtertypes.GroupDelay, filter_template.GroupDelayTemplate]
        }
        self.filters = []
        self.plots = []

    def get_available_filters(self):
        return list(self.filter_dict.keys())

    def get_parameters_for(self, filter_str):
        return (self.filter_dict.get(filter_str))[0].get_parameter_list()

    def get_approximations_for(self, filter_str):
        return (self.filter_dict.get(filter_str))[0].get_available_approximations()

    def add_filter(self, filter_type, approx, param, n_min, n_max, q_max, denorm_degree):
        # devuelve el filter id! con eso llamo a get_plots
        template = (self.filter_dict.get(filter_type)[1])(param, n_min, n_max, q_max, denorm_degree)
        f = (self.filter_dict.get(filter_type)[0])(template, approx)
        f.calculate_pzkn()
        self.filters.append(f)
        return len(self.filters)-1

    def get_filter_plots(self, filter_id):
        f = self.filters[filter_id]

    @staticmethod
    def get_plots_from_pzk(p, z, k):
        tf = filter.Filter.calculate_tf(p, z, k)
        plots = []

        [x, y, y2] = signal.bode(system=tf, n=1000)
        plots.append(ContinuousPlotData(title="Bode diagram - magnitude", x_label="Frequency (rad/s)",
                                        y_label="Magnitude (dB)", x_data=x, y_data=y))
        plots.append(ContinuousPlotData(title="Bode diagram - phase", x_label="Frequency (rad/s)", y_label="Phase (°)",
                                        x_data=x, y_data=y2))

        [x, y] = signal.step(tf)
        plots.append(ContinuousPlotData(title="Step response", x_label="Time (s)", y_label="Amplitude (dimensionless)",
                                        x_data=x, y_data=y))

        [x, y] = signal.impulse(tf)
        plots.append(ContinuousPlotData(title="Step response", x_label="Time (s)", y_label="Amplitude (dimensionless)",
                                        x_data=x, y_data=y))

    @staticmethod
    def get_pzplot(p, z):
        filter.Filter.re_add_complex(p)
        filter.Filter.re_add_complex(z)

