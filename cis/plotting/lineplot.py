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

        for i, unpacked_data_item in enumerate(self.unpacked_data_items):
            datafile = self.datagroups[i]
            if datafile["itemstyle"]:
                if datafile["itemstyle"] in LinePlot.line_styles:
                    self.mplkwargs["linestyle"] = datafile["itemstyle"]
                else:
                    from cis.exceptions import InvalidLineStyleError
                    raise InvalidLineStyleError(
                        "'" + datafile["itemstyle"] + "' is not a valid line style, please use one of: " + str(
                            self.line_styles))
            else:
                self.mplkwargs.pop("linestyle", None)

            if datafile["color"]:
                self.mplkwargs["color"] = datafile["color"]
            else:
                self.mplkwargs.pop("color", None)

            if unpacked_data_item["x"].shape[0] != unpacked_data_item["data"].shape[0]:
                raise InvalidDimensionError("The plot axes are incompatible, please check and specify at least one "
                                            "axis manually.")

            self.matplotlib.plot(unpacked_data_item["x"], unpacked_data_item["data"], *self.mplargs, **self.mplkwargs)

    def set_default_axis_label(self, axis):
        import cis.exceptions as cisex
        import iris.exceptions as irisex
        from .APlot import format_units
        axis = axis.lower()
        axislabel = axis + "label"

        if getattr(self, axislabel) is None:
            try:
                units = self.packed_data_items[0].coord(getattr(self, axis + "axis")).units
            except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                units = self.packed_data_items[0].units

            if len(self.packed_data_items) == 1:
                try:
                    name = self.packed_data_items[0].coord(getattr(self, axis + "axis")).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.packed_data_items[0].name()
                # only 1 data to plot, display
                setattr(self, axislabel, name + " " + format_units(units))
            else:
                # if more than 1 data, legend will tell us what the name is. so just displaying units
                setattr(self, axislabel, format_units(units))
