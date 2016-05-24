import logging
from abc import abstractmethod, ABCMeta

from matplotlib.ticker import MaxNLocator, AutoMinorLocator


def format_units(units):
    """
    :param units: The units of a variable, as a string
    :return: The units surrounding brackets, or the empty string if no units given
    """
    if "since" in str(units):
        # Assume we are on a time if the units contain since.
        return ""
    elif units:
        return "(" + str(units) + ")"
    else:
        return ""


def calc_min_and_max_vals_of_array_incl_log(array, log=False):
    """
    Calculates the min and max values of a given array.
    If a log scale is being used only positive values are taken into account
    :param array: The array to calculate the min and max values of
    :param log: Is a log scale being used?
    :return: The min and max values of the array
    """

    if log:
        import numpy.ma as ma
        positive_array = ma.array(array, mask=array <= 0)
        min_val = positive_array.min()
        max_val = positive_array.max()
    else:
        min_val = array.min()
        max_val = array.max()
    return min_val, max_val


class APlot(object):

    __metaclass__ = ABCMeta

    # TODO: Reorder these into roughly the order they are most commonly used
    # @initializer
    def __init__(self, packed_data_items, ax, xaxis, yaxis, color=None,
                 edgecolor=None, itemstyle=None, label=None, *mplargs, **mplkwargs):
        """
        Constructor for Generic_Plot.
        Note: This also calls the plot method

        :param ax: The matplotlib axis on which to plot
        :param datagroup: The data group number in an overlay plot, 0 is the 'base' plot
        :param packed_data_items: A list of packed (i.e. Iris cubes or Ungridded data objects) data items
        :param plot_args: A dictionary of plot args that was created by plot.py
        :param mplargs: Any arguments to be passed directly into matplotlib
        :param mplkwargs: Any keyword arguments to be passed directly into matplotlib
        """
        import matplotlib.pyplot as plt

        self.packed_data_items = packed_data_items

        self.ax = ax

        self.xaxis = xaxis
        self.yaxis = yaxis
        self.color = color
        self.label = label
        self.edgecolor = edgecolor
        self.itemstyle = itemstyle

        self.mplargs = mplargs
        self.mplkwargs = mplkwargs

        self.color_axis = []

    @abstractmethod
    def plot(self):
        """
        The method that will do the plotting. To be implemented by each subclass of Generic_Plot.
        """
        pass

    @staticmethod
    def guess_axis_label(data, axisvar=None, axis=None):
        """
        :param data: The data to inspect for names and units
        :param axisvar: An axis name to look in coords for
        :param axis: An axis label (x or y)
        """
        import cis.exceptions as cisex
        import iris.exceptions as irisex
        try:
            coord = data.coord(axisvar)
        except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
            name = data.name()
            units = data.units
        else:
            name = coord.name()
            units = coord.units

        # in general, display both name and units in brackets
        return name + " " + format_units(units)

    def unpack_data_items(self):
        def __get_data(axis):
            variable = getattr(self, axis + 'axis')
            if variable == "default" or variable == self.packed_data_items[0].name() \
                    or variable == self.packed_data_items[0].standard_name \
                    or variable == self.packed_data_items[0].long_name:
                return self.packed_data_items[0].data
            else:
                if variable.startswith("search"):
                    number_of_points = float(variable.split(":")[1])
                    for coord in self.packed_data_items[0].coords():
                        if coord.shape[0] == number_of_points:
                            break
                else:
                    coord = self.packed_data_items[0].coord(variable)
                return coord.points if isinstance(self.packed_data_items[0], Cube) else coord.data

        def __set_variable_as_data(axis):
            old_variable = getattr(self, axis + 'axis')
            setattr(self, axis + 'axis', self.packed_data_items[0].name())
            logging.info("Plotting " + getattr(self,
                                               axis + 'axis') + " on the " + axis + " axis as " + old_variable + " has length 1")

        def __swap_x_and_y_variables():
            temp = self.xaxis
            self.xaxis = self.yaxis
            self.yaxis = temp

        from cis.utils import unpack_data_object
        from iris.cube import Cube
        import logging
        if len(self.packed_data_items[0].shape) == 1:
            x_data = __get_data("x")
            y_data = __get_data("y")

            if len(x_data) == 1 and len(y_data) == len(self.packed_data_items[0].data):
                __set_variable_as_data("x")
            elif len(y_data) == 1 and len(x_data) == len(self.packed_data_items[0].data):
                __set_variable_as_data("y")
            else:
                try:
                    if (x_data == y_data).all():
                        __swap_x_and_y_variables()
                except AttributeError:
                    if x_data == y_data:
                        __swap_x_and_y_variables()

        return [unpack_data_object(packed_data_item, self.xaxis, self.yaxis,
                                   self.x_wrap_start) for packed_data_item in self.packed_data_items]

    def unpack_comparative_data(self):
        return [{"data": packed_data_item.data} for packed_data_item in self.packed_data_items]