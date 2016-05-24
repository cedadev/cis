from cis.plotting.genericplot import GenericPlot, Generic2DPlot
from cis.plotting.APlot import APlot


# TODO: The generic scatter shouldn't have any of the if 2D stuff in...
class GenericScatter(APlot):
    def plot(self):
        """
        Plots one or many scatter plots
        Stores the plot in a list to be used for when adding the legend
        """
        from cis.plotting.plot import colors

        self.mplkwargs["s"] = self.itemwidth

        for i, unpacked_data_item in enumerate(self.unpacked_data_items):
            local_kwargs = self.mplkwargs.copy()
            datafile = self.datagroups[i]

            if "itemstyle" in datafile:
                local_kwargs["marker"] = datafile["itemstyle"]

            if 'cmap' in datafile:
                local_kwargs["cmap"] = datafile["cmap"]

            # Default to no edgecolour
            if "edgecolor" in datafile:
                local_kwargs["edgecolors"] = datafile["edgecolor"]
            elif 'marker' not in local_kwargs or local_kwargs['marker'] == 'o':
                local_kwargs["edgecolors"] = 'None'

            if "c" not in local_kwargs:
                if datafile.get("color", None):
                    local_kwargs["c"] = datafile["color"]
                elif unpacked_data_item.get("y", None) is not None:  # i.e. the scatter plot is 3D
                    local_kwargs["c"] = unpacked_data_item["data"]
                else:
                    local_kwargs["c"] = colors[i % len(colors)]

            x_coords = unpacked_data_item["x"]

            if unpacked_data_item.get("y", None) is not None:
                # 3D
                self.scatter_type = "3D"
                y_coords = unpacked_data_item["y"]
            else:
                # 2D
                self.scatter_type = "2D"
                y_coords = unpacked_data_item["data"]

            self.color_axis.append(
                self.matplotlib.scatter(x_coords, y_coords, *self.mplargs, **local_kwargs))

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


class ScatterPlot(GenericScatter, GenericPlot):
    pass


class ScatterPlot2D(GenericScatter, Generic2DPlot):
    pass