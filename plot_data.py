
class PlotData:
    def __init__(self, plot_type, title, x_label, y_label):
        self.plot_type = plot_type
        self.title = title
        self.x_label = x_label
        self.y_label = y_label


class ContinuousPlotData(PlotData):
    def __init__(self, title, x_label, y_label, x_data, y_data):
        super().__init__('c', title, x_label, y_label)
        self.x_data = x_data
        self.y_label = y_data


class ScatterPlotData(PlotData):
    def __init__(self, title, x_label, y_label, points):
        super().__init__('s', title, x_label, y_label)
        self.points = points


class TemplatePlotData(PlotData):
    def __init__(self, title, x_label, y_label, covered_areas):
        super().__init__('t', title, x_label, y_label)
        self.covered_areas = covered_areas
