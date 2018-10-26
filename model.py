import filtertypes
import filter_template
import filter
from scipy import signal
import numpy
from plot_data import ContinuousPlotData, ScatterPlotData, TemplatePlotData, ScatterPoint
from group_delay import group_delay
import math


class Model:
    def __init__(self):
        self.filter_dict = {
            "Low-pass":     [filtertypes.LowPass, filter_template.LowPassTemplate],
            "High-pass":    [filtertypes.HighPass, filter_template.HighPassTemplate],
            "Band-pass":    [filtertypes.BandPass, filter_template.BandPassTemplate],
            "Band-reject":  [filtertypes.BandReject, filter_template.BandRejectTemplate],
            "Group delay":  [filtertypes.GroupDelay, filter_template.GroupDelayTemplate]
        }
        self.filters = {}
        self.filter_list = []
        self.stages = {}
        self.curr_id = 0
        self.stage_id = 0
# stage 2: diagrama de polos y ceros

    @staticmethod
    def get_available_plots():
        return (["Bode diagram - attenuation", "Bode diagram - phase", "Step response", "Impulse response",
                 "Group delay", "Q values", "Pole-zero map"])

    def get_plot(self, filter_id, plot_name, norm):
        if int(norm):
            plot_type = 2
        else:
            plot_type = 1

        return self.filters[filter_id][plot_type][plot_name]

    def get_available_filters(self):
        return list(self.filter_dict.keys())

    def get_parameters_for(self, filter_str):
        return (self.filter_dict.get(filter_str))[0].get_parameter_list()

    def get_approximations_for(self, filter_str):
        return (self.filter_dict.get(filter_str))[0].get_available_approximations()

    def add_filter(self, filter_type, approx, param, n_min, n_max, q_max, denorm_degree=None):
        template = (self.filter_dict.get(filter_type)[1])(param, n_min, n_max, q_max, denorm_degree)

        if template.is_ok():
            f = (self.filter_dict.get(filter_type)[0])(template, approx)

            f.calculate_pzkn()

            plots = {}
            norm_plots = {}
            self.get_filter_plots(f, plots, norm_plots)

            self.curr_id += 1
            self.filters[self.curr_id] = [f, plots, norm_plots]
            return f.type + " " + f.approx + " order " + str(f.n), self.curr_id
        else:
            return "Error: parametros no validos", -1

    @staticmethod
    def get_filter_plots(f, plots, norm_plots):
        f.re_add_complex(f.denormalized_poles)
        f.re_add_complex(f.denormalized_zeros)
        Model.get_plots_from_pzk(f.denormalized_poles, f.denormalized_zeros, f.denormalized_k, f.denormalized_template,
                                 plots)
        f.add_only_one_complex(f.denormalized_poles)
        f.add_only_one_complex(f.denormalized_zeros)

        f.re_add_complex(f.normalized_poles)
        f.re_add_complex(f.normalized_zeros)
        Model.get_plots_from_pzk(f.normalized_poles, f.normalized_zeros, f.normalized_k, f.normalized_template,
                                 norm_plots)
        f.add_only_one_complex(f.normalized_poles)
        f.add_only_one_complex(f.normalized_poles)


    @staticmethod
    def get_plots_from_pzk(p, z, k, template, plots):
        tf = signal.ZerosPolesGain(z, p, k)
        tf = tf.to_tf()

        [w, y, y2] = signal.bode(system=tf, n=1000)
        plots["Bode diagram - attenuation"] = [ContinuousPlotData(x_label="Frequency", x_units="rad/s",
                                        y_label="Attenuation", y_units="dB",  x_data=w, y_data=(-1)*y,
                                        logscale=True, dB=True)]
        plots["Bode diagram - phase"] = [ContinuousPlotData(x_label="Frequency", x_units="rad/s",
                                        y_label="Phase", y_units="(°)", x_data=w, y_data=y2, dB=False, logscale=True)]

        [x, y] = signal.step(tf, N=1000)
        plots["Step response"] = [ContinuousPlotData(x_label="Time", x_units="s",
                                        y_label="Amplitude", y_units="dimensionless", logscale=False, dB=False,
                                        x_data=x, y_data=y)]

        [x, y] = signal.impulse(tf, N=1000)
        plots["Impulse response"] = [ContinuousPlotData(x_label="Time", x_units="s",
                                        y_label="Amplitude", y_units="dimensionless", logscale=False, dB=False,
                                        x_data=x, y_data=y)]
        plots["Pole-zero map"] = [Model.get_pzplot(p, z)]

        [gd_points, gd_deltas] = group_delay(w, p, z)
        delta_points = []
        for delta in gd_deltas:
            d = ScatterPoint
            d.x = delta[0]
            d.y = gd_points[w.index(d.x)]
            d.mark = "arrow"
            d.legend = str(delta[1])
            delta_points.append(d)

        plots["Group delay"] = [ContinuousPlotData(x_label="Frequency", x_units="rad/s", y_label="Delay",
                                        y_units="s", logscale=True, dB=False, x_data=w, y_data=gd_points)]
        #plots["Group delay"].append(ScatterPlotData(x_label="Frequency", x_units="rad/s", y_label="Delay",
        #                             y_units="s", logscale=True, dB=False, points=delta_points))

        q = []
        Model.get_q_points(p, q)
        Model.get_q_points(z, q)
        plots["Q values"] = [ScatterPlotData(x_label="", x_units="", y_label="Q", y_units="dimensionless",
                                     logscale=False, dB=False, points=q)]

        template_plot = template.get_plot()
        if template.template_type == "Group delay":
            template_plot.covered_areas[0].bottom = min(plots["Group delay"][0].y_data)
            template_plot.covered_areas[0].left = w[0]
            plots["Group delay"].append(template_plot)
        else:
            template_plot.covered_areas[0].left = w[0]
            template_plot.covered_areas[-1].right = w[-1]
            min_y = min(plots["Bode diagram - attenuation"][0].y_data)
            max_y = max(plots["Bode diagram - attenuation"][0].y_data)
            for area in template_plot.covered_areas:
                if abs(area.top) == math.inf:
                    area.top = max_y
                elif abs(area.bottom) == math.inf:
                    area.bottom = min_y
        plots["Bode diagram - attenuation"].append(template_plot)

    def get_filter_pzplot(self, filter_id):
        return self.filters[filter_id][1]["Pole-zero map"]


    #stage_id
    def delete_stage(self, filter_id, stage_id):
        f = self.filters[filter_id][0]
        f.delete_stage(f.stages[int(stage_id)-1])

    def auto_stages(self, filter_id, vout_min, vout_max):
        f = self.filters[filter_id][0]
        f.auto_stage_decomposition(float(vout_min), float(vout_max))

    def get_auto_stages_plots(self, filter_id):
        stages = self.filters[filter_id][0].stages

        st_plots = []
        for stage in stages:
            tf = signal.ZerosPolesGain(stage.zeros, stage.poles, stage.gain_factor)
            tf = tf.to_tf()

            [w, y, y2] = signal.bode(system=tf, n=1000)
            st_plots.append(ContinuousPlotData(x_label="Frequency", x_units="rad/s",  y_label="Attenuation", y_units="dB", x_data=w,
                                                y_data=(-1) * y, logscale=True, dB=True))
        return st_plots

    # llamar a esta INMEDIATAMENTE despues de get_auto_stages_plots
    def get_auto_stage_p_strings(self, filter_id, stage_id):
        stages = self.filters[filter_id][0].stages
        poles = stages[int(stage_id)-1].poles
        filter.Filter.re_add_complex(poles)
        p_strings = []
        for pole in poles:
            p_strings.append(str(pole))
        filter.Filter.add_only_one_complex(poles)
        return p_strings

    def get_auto_stage_z_strings(self, filter_id, stage_id):
        stages = self.filters[filter_id][0].stages
        zeros = stages[int(stage_id)-1].zeros
        filter.Filter.re_add_complex(zeros)
        z_strings = []
        for zero in zeros:
            z_strings.append(str(zero))
        filter.Filter.add_only_one_complex(zeros)
        return z_strings

    def get_auto_stages_k(self, filter_id, stage_id):
        return str(self.filters[filter_id][0].stages[int(stage_id)-1].gain_factor)

    def single_stage(self, filter_id, poles, zeros, gain_factor, vout_min, vout_max):
        f = self.filters[filter_id][0]
        polos = []
        ceros = []
        ganancia = 0
        for pole in poles:
            polos.append(float(pole))
        for zero in zeros:
            ceros.append(float(zero))
        ganancia = float(gain_factor)
        vout_min = float(vout_min)
        vout_max = float(vout_max)

        f.single_stage_decomposition(poles, zeros, gain_factor, vout_min, vout_max)

    def single_stage_plots(self, filter_id):
        stages = self.filters[filter_id][0].stages
        st_plots = []
        for stage in stages:
            tf = signal.ZerosPolesGain(stage.zeros, stage.poles, stage.gain_factor)
            tf = tf.to_tf()

            [w, y, y2] = signal.bode(system=tf, n=1000)
            st_plots.append(ContinuousPlotData(x_label="Frequency", x_units="rad/s",  y_label="Attenuation", y_units="dB", x_data=w,
                                                y_data=(-1) * y, logscale=True, dB=True))
        return st_plots

    def single_stage_pzk_strings(self, filter_id, stage_id):
        stage = self.filters[filter_id][0].stages[int(stage_id)-1]
        polos = []
        ceros = []
        ganancia = 0
        for pole in stage.poles:
            polos.append(str(pole))
        for zero in stage.zeros:
            ceros.append(str(zero))
        ganancia = str(stage.gain_factor)

        return polos, ceros, ganancia

    def get_stage_info(self, filter_id, stage_id):
        stages = self.filters[filter_id][0].stages
        infos = []
        for info in stages[stage_id-1].get_display_info():
            infos.append(str(info))
        return infos
    def get_pzk_strings(self, filter_id):
        f = self.filters[filter_id][0]
        pole_str = []
        zero_str = []
        k = str(f.denormalized_k)

        for p in f.denormalized_poles:
            pole_str.append(str(p))

        for z in f.denormalized_zeros:
            zero_str.append(str(z))

        return pole_str, zero_str, k

    @staticmethod
    def get_pzplot(p, z):
        pole_points = Model.add_pz_points(p, "x")
        zero_points = Model.add_pz_points(z, "o")
        points = pole_points + zero_points
        return ScatterPlotData(x_label="Real", x_units="rad/s", y_label="Imaginary",
                               y_units="rad/s", logscale=False, dB=False, points=points)

    @staticmethod
    def add_pz_points(singularities, mark):
        points = []
        for s in singularities:
            point = ScatterPoint()
            point.x = s.real
            point.y = s.imag
            point.format = mark
            point.legend = None

            repeat = next((rp for rp in points if rp.x == point.x and rp.y == point.y), None)
            if repeat is not None:
                if repeat.legend is None:
                    repeat.legend = 1
                point.legend = int(repeat.legend) + 1
            else:
                points.append(point)

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
