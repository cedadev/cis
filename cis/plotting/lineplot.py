from cis.plotting.genericplot import GenericPlot


class LinePlot(GenericPlot):
    line_styles = ["solid", "dashed", "dashdot", "dotted"]

    def plot(self):
        """
        Plots one or many line graphs
        """
        from cis.exceptions import InvalidDimensionError
        self.mplkwargs["linewidth"] = self.itemwidth

        self.mplkwargs.pop("vmax", None)
        self.mplkwargs.pop("vmin", None)

        if self.itemstyle:
            if self.itemstyle in LinePlot.line_styles:
                self.mplkwargs["linestyle"] = self.itemstyle
            else:
                from cis.exceptions import InvalidLineStyleError
                raise InvalidLineStyleError(
                    "'" + self.itemstyle + "' is not a valid line style, please use one of: " + str(
                        self.line_styles))
        else:
            self.mplkwargs.pop("linestyle", None)

        if self.color:
            self.mplkwargs["color"] = self.color
        else:
            self.mplkwargs.pop("color", None)

        if self.x.shape[0] != self.data.shape[0]:
            raise InvalidDimensionError("The plot axes are incompatible, please check and specify at least one "
                                        "axis manually.")

        self.ax.plot(self.x, self.data, *self.mplargs, **self.mplkwargs)


    @staticmethod
    def guess_axis_label(data, axisvar=None, axis=None):
        import cis.exceptions as cisex
        import iris.exceptions as irisex
        from .APlot import format_units

        try:
            units = data[0].coord(axisvar).units
        except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
            units = data[0].units

        if len(data) == 1:
            try:
                name = data[0].coord(axisvar).name()
            except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                name = data[0].name()
            # only 1 data to plot, display
            label = name + " " + format_units(units)
        else:
            # if more than 1 data, legend will tell us what the name is. so just displaying units
            label = format_units(units)
        return label
