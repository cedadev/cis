from cis.plotting.genericplot import GenericPlot


class ContourfPlot(GenericPlot):
    def plot(self):
        """
        Plots a filled contour plot
        """
        self.contour_plot(True)

    def set_default_axis_label(self, axis):
        return self.set_3daxis_label(axis)

    def format_plot(self):
        self.format_time_axis()
        self.format_3d_plot()
