from cis.plotting.genericplot import GenericPlot


class ComparativeScatter(GenericPlot):

    def plot(self):
        import numpy as np
        lims = [np.min([self.ax.get_xlim(), self.ax.get_ylim()]),  # min of both axes
                np.max([self.ax.get_xlim(), self.ax.get_ylim()])]  # max of both axes

        # now plot both limits against eachother
        self.ax.plot(lims, lims, color="black", linestyle="dashed")

        self.mplkwargs["marker"] = self.itemstyle

        self.mplkwargs["color"] = self.color

        self.ax.scatter(self.x, self.y,
                   s=self.itemwidth, edgecolors="none", *self.mplargs, **self.mplkwargs)

    def unpack_data_items(self, packed_data_items, x_wrap_start=None):
        self.x = packed_data_items[0].data
        self.y = packed_data_items[1].data

    @staticmethod
    def guess_axis_label(data, axisvar=None, axis=None):
        """
        Sets the default axis label for a comparative plot, e.g. a comparative scatter or a 3d histogram
        :param axis: The axis to set the default label for
        """
        from .APlot import format_units
        if axis.lower() == 'x':
            item_index = 0
        elif axis.lower() == 'y':
            item_index = 1

        units = data[item_index].units
        name = data[item_index].name()
        return name + " " + format_units(units)

    @staticmethod
    def valid_number_of_datagroups(number_of_datagroups):
        return number_of_datagroups == 2
