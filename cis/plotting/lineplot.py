"""
A basic line plot
"""
from cis.plotting.genericplot import GenericPlot


class LinePlot(GenericPlot):
    line_styles = ["solid", "dashed", "dashdot", "dotted"]

    def __call__(self, ax):
        """
        Plots one line
        """
        from cis.exceptions import InvalidDimensionError
        # Translate our argument names to mpl line kwargs
        self.mplkwargs["linewidth"] = self.itemwidth

        if self.itemstyle:
            if self.itemstyle in LinePlot.line_styles:
                self.mplkwargs["linestyle"] = self.itemstyle
            else:
                from cis.exceptions import InvalidLineStyleError
                raise InvalidLineStyleError(
                    "'" + self.itemstyle + "' is not a valid line style, please use one of: " + str(
                        self.line_styles))

        if self.color:
            self.mplkwargs["color"] = self.color

        if self.x.shape[0] != self.data.shape[0]:
            raise InvalidDimensionError("The plot axes are incompatible, please check and specify at least one "
                                        "axis manually.")

        ax.plot(self.x, self.data, *self.mplargs, **self.mplkwargs)

        super(LinePlot, self).__call__(ax)
