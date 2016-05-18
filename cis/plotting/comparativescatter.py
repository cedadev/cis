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

    def calculate_axis_limits(self, axis, min_val, max_val):
        if axis == "x":
            axis_index = 0
        elif axis == "y":
            axis_index = 1

        c_min, c_max = self.calc_min_and_max_vals_of_array_incl_log(axis, self.unpacked_data_items[axis_index]["data"])

        new_min = c_min if min_val is None else min_val
        new_max = c_max if max_val is None else max_val

        return new_min, new_max

    def set_default_axis_label(self, axis):
        """
        Sets the default axis label for a comparative plot, e.g. a comparative scatter or a 3d histogram
        :param axis: The axis to set the default label for
        """
        axis = axis.lower()
        axislabel = axis + "label"
        if axis == 'x':
            item_index = 0
        elif axis == 'y':
            item_index = 1

        if getattr(self, axislabel) is None:
            units = self.packed_data_items[item_index].units
            name = self.packed_data_items[item_index].name()
            setattr(self, axislabel, name + " " + self.format_units(units))
