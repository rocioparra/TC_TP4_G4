import filtertypes
import filter_template
import filter
from scipy import signal
import numpy
from plot_data import ContinuousPlotData, ScatterPlotData, TemplatePlotData, ScatterPoint
from group_delay import group_delay


class Model:
    def __init__(self):
        self.filter_dict = {
            "Low-pass":     [filtertypes.LowPass, filter_template.LowPassTemplate],
            "High-pass":    [filtertypes.HighPass, filter_template.HighPassTemplate],
            "Band-pass":    [filtertypes.BandPass, filter_template.BandPassTemplate],
            "Band-reject":  [filtertypes.BandReject, filter_template.BandRejectTemplate],
            "Group delay":  [filtertypes.GroupDelay, filter_template.GroupDelayTemplate]
        }
        self.f = None
        self.norm_plots = []
        self.plots = []

    def get_available_filters(self):
        return list(self.filter_dict.keys())

    def get_parameters_for(self, filter_str):
        return (self.filter_dict.get(filter_str))[0].get_parameter_list()

    def get_approximations_for(self, filter_str):
        return (self.filter_dict.get(filter_str))[0].get_available_approximations()

    def add_filter(self, filter_type, approx, param, n_min, n_max, q_max, denorm_degree):
        template = (self.filter_dict.get(filter_type)[1])(param, n_min, n_max, q_max, denorm_degree)
        self.f = (self.filter_dict.get(filter_type)[0])(template, approx)
        self.f.calculate_pzkn()
        self.get_filter_plots(f, self.plots, self.norm_plots)

    @staticmethod
    def get_filter_plots(f, plots, norm_plots):
        f.re_add_complex(f.denormalized_poles)
        f.re_add_complex(f.denormalized_zeros)
        Model.get_plots_from_pzk(f.denormalized_poles, f.denormalized_zeros, f.denormalized_k, f.denormalized_template,
                                 plots)

        f.re_add_complex(f.normalized_poles)
        f.re_add_complex(f.normalized_zeros)
        Model.get_plots_from_pzk(f.normalized_poles, f.normalized_zeros, f.normalized_k, f.normalized_template,
                                 norm_plots)

    @staticmethod
    def get_plots_from_pzk(p, z, k, template, plots):
        tf = signal.ZerosPolesGain(z, p, k)
        tf = tf.to_tf()

        [w, y, y2] = signal.bode(system=tf, n=1000)
        plots.append(ContinuousPlotData(title="Bode diagram - magnitude", x_label="Frequency", x_units="rad/s",
                                        y_label="Attenuation", y_units="dB",  x_data=w, y_data=(-1)*y,
                                        logscale=True, dB=True))
        plots.append(ContinuousPlotData(title="Bode diagram - phase", x_label="Frequency", x_units="rad/s",
                                        y_label="Phase", y_units="(°)", x_data=w, y_data=y2, dB=False, logscale=True))

        [x, y] = signal.step(tf, N=1000)
        plots.append(ContinuousPlotData(title="Step response", x_label="Time", x_units="s",
                                        y_label="Amplitude", y_units="dimensionless", logscale=False, dB=False,
                                        x_data=x, y_data=y))

        [x, y] = signal.impulse(tf, N=1000)
        plots.append(ContinuousPlotData(title="Impulse response", x_label="Time", x_units="s",
                                        y_label="Amplitude", y_units="dimensionless", logscale=False, dB=False,
                                        x_data=x, y_data=y))
        plots.append(Model.get_pzplot(p, z))

        [gd_points, gd_deltas] = group_delay(w, p, z)
        delta_points = []
        for delta in gd_deltas:
            d = ScatterPoint
            d.x = delta[0]
            d.y = gd_points[w.index(d.x)]
            d.mark = "arrow"
            d.legend = str(delta[1])
            delta_points.append(d)

        plots.append(ContinuousPlotData(title="Group delay", x_label="Frequency", x_units="rad/s", y_label="Delay",
                                        y_units="s", logscale=True, dB=False, x_data=w, y_data=gd_points))
        plots.append(ScatterPlotData(title="Group delay",  x_label="Frequency", x_units="rad/s", y_label="Delay",
                                     y_units="s", logscale=True, dB=False, points=delta_points))

        q = []
        Model.get_q_points(p, q)
        Model.get_q_points(z, q)
        plots.append(ScatterPlotData(title="Q values", x_label="", x_units="", y_label="Q", y_units="dimensionless",
                                     logscale=False, dB=False, points=q))

        plots.append(template.get_plot())

    @staticmethod
    def get_pzplot(p, z):
        pole_points = Model.add_pz_points(p, "x")
        zero_points = Model.add_pz_points(z, "o")

        filter.Filter.re_add_complex(p)
        filter.Filter.re_add_complex(z)

        points = pole_points + zero_points
        return ScatterPlotData(title="Pole-zero map", x_label="Real", x_units="rad/s", y_label="Imaginary",
                               y_units="rad/s", logscale=False, dB=False, points=points)

    @staticmethod
    def add_pz_points(singularities, mark):
        points = []
        for s in singularities:
            point = ScatterPoint()
            point.x = s.real
            point.y = s.imag
            point.mark = mark
            point.legend = None

            repeat = next((rp for rp in points if rp.x == point.x and rp.y == point.y), None)
            if repeat is not None:
                if repeat.legend is None:
                    repeat.legend = 1
                point.legend = int(repeat.legend) + 1

        for p in points:
            if p.legend is not None:
                p.legend = str(p.legend)

        return points

    @staticmethod
    def get_q_points(comp, q):
        q_point = ScatterPoint()
        q_point.mark = "line"
        k = 1

        for c in comp:
            if c.imag and c.real:
                q_point.y = numpy.absolute(c) / (2 * abs(c.real))
                if next((repeat for repeat in q if repeat.y == q_point.y), None) is None:
                    q_point.x = str(k)
                    q.append(q_point)


