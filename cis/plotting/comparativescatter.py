from cis.plotting.genericplot import GenericPlot


class ComparativeScatter(GenericPlot):

    def plot(self):
        from cis.exceptions import InvalidNumberOfDatagroupsSpecifiedError
        if len(self.packed_data_items) == 2:
            # Add y=x line
            ax = self.matplotlib.gca()
            if self.logx and self.logy:
                import numpy.ma as ma
                positive_item0 = ma.array(self.unpacked_data_items[0]["data"],
                                          mask=self.unpacked_data_items[0]["data"] <= 0)
                positive_item1 = ma.array(self.unpacked_data_items[1]["data"],
                                          mask=self.unpacked_data_items[1]["data"] <= 0)
                min_val = min(positive_item0.min(), positive_item1.min())
                max_val = max(positive_item0.max(), positive_item1.max())
            else:
                min_val = min(self.unpacked_data_items[0]["data"].min(), self.unpacked_data_items[1]["data"].min())
                max_val = max(self.unpacked_data_items[0]["data"].max(), self.unpacked_data_items[1]["data"].max())
            y_equals_x_array = [min_val, max_val]
            ax.plot(y_equals_x_array, y_equals_x_array, color="black", linestyle="dashed")

            datagroup = self.datagroups[0]
            if datagroup["itemstyle"]:
                self.mplkwargs["marker"] = datagroup["itemstyle"]
            else:
                self.mplkwargs.pop("marker", None)

            if datagroup["color"]:
                self.mplkwargs["color"] = datagroup["color"]
            else:
                self.mplkwargs.pop("color", None)

            ax.scatter(self.unpacked_data_items[0]["data"], self.unpacked_data_items[1]["data"],
                       s=self.itemwidth, edgecolors="none", *self.mplargs, **self.mplkwargs)
        else:
            raise InvalidNumberOfDatagroupsSpecifiedError("Comparative scatter requires two datagroups")

    def unpack_data_items(self):
        return self.unpack_comparative_data()

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