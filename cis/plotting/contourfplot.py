from cis.plotting.genericplot import Generic2DPlot


class ContourfPlot(Generic2DPlot):

    def plot(self):
        """
        Plots a filled contour plot
        """
        self.contour_plot(True)
