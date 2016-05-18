from cis.plotting.genericplot import Generic2DPlot


class ContourPlot(Generic2DPlot):
    # 'contour' : PlotType(1, 2, plot_contour),
    def plot(self):
        """
        Plots a contour plot
        Stores the plot in a list to be used for when adding the legend
        """
        self.contour_plot(False)

    def set_default_axis_label(self, axis):
        return self.set_3daxis_label(axis)
