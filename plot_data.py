
class PlotData:
    def __init__(self, plot_type, title, x_label, y_label, x_units, y_units, logscale, dB):
        self.plot_type = plot_type
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.x_units = x_units
        self.logscale = logscale
        self.dB = dB


class ContinuousPlotData(PlotData):
    def __init__(self, title, x_label, y_label, x_units, y_units, logscale, dB, x_data, y_data,):
        super().__init__('c', title, x_label, y_label, x_units, y_units, logscale, dB)
        self.x_data = x_data
        self.y_data = y_data


class ScatterPlotData(PlotData):
    def __init__(self, title, x_label, y_label, x_units, y_units, logscale, dB, points):
        super().__init__('s', title, x_label, y_label, x_units, y_units, logscale, dB)
        self.points = points  # x, y, format, legend


class ScatterPoint:
    def __init__(self):
        self.x = None
        self.y = None
        self.format = None
        self.legend = None


class TemplatePlotData(PlotData):
    def __init__(self, title, x_label, y_label, x_units, y_units, logscale, dB, covered_areas):
        super().__init__('t', title, x_label, y_label, x_units, y_units, logscale, dB)
        self.covered_areas = covered_areas
