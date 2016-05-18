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

    def auto_set_ticks(self):
        """
        Use the matplotlib.ticker class to automatically set nice values for the major and minor ticks.
        Log axes generally come out nicely spaced without needing manual intervention. For particularly narrow latitude
        vs longitude plots the ticks can come out overlapped, so an exception is included to deal with this.
        """
        from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

        y_variable = self.yaxis.lower()
        x_variable = self.yaxis.lower()

        ymin, ymax = self.matplotlib.get_ylim()

        # Matplotlib xlim doesn't work with cartopy plots
        xmin, xmax = self.xmin, self.xmax
        # xmin, xmax = self.matplotlib.xlim()

        max_x_bins = 9
        max_y_bins = 9

        xsteps = self.xstep
        ysteps = self.ystep

        lon_steps = [1, 3, 6, 9, 10]
        lat_steps = [1, 3, 6, 9, 10]
        variable_step = [1, 2, 4, 5, 10]

        if (xmax - xmin) < 5:
            lon_steps = variable_step
        if (ymax - ymin) < 5:
            lat_steps = variable_step

        # We need to make a special exception for particularly narrow and wide plots, which will be lat vs lon
        # preserving the aspect ratio. This gives more options for the spacing to try and find something that can use
        # the maximum number of bins.
        if x_variable.startswith('lon') and y_variable.startswith('lat'):
            max_y_bins = 7  # as plots are wider rather than taller
            if (ymax - ymin) > 2.2 * (xmax - xmin):
                max_x_bins = 4
                max_y_bins = 11
            elif (xmax - xmin) > 2.2 * (ymax - ymin):
                max_x_bins = 14
                max_y_bins = 4

        lat_or_lon = 'lat', 'lon'

        if xsteps is None and not self.logx:
            if self.xaxis.lower().startswith(lat_or_lon):
                lon_locator = MaxNLocator(nbins=max_x_bins, steps=lon_steps)
                if self.is_map():
                    self.cartopy_axis.set_xticks(lon_locator.tick_values(xmin, xmax), crs=self.transform)
                    self.cartopy_axis.xaxis.set_major_formatter(LongitudeFormatter())
                else:
                    self.matplotlib.axes().xaxis.set_major_locator(lon_locator)
            else:
                self.matplotlib.axes().xaxis.set_major_locator(MaxNLocator(nbins=max_x_bins, steps=variable_step))

            if not self.is_map():
                self.matplotlib.axes().xaxis.set_minor_locator(AutoMinorLocator())
                self.matplotlib.axes().xaxis.grid(False, which='minor')

        if ysteps is None and not self.logy:
            if y_variable.startswith(lat_or_lon):
                lat_locator = MaxNLocator(nbins=max_y_bins, steps=lat_steps)
                if self.is_map():
                    self.cartopy_axis.set_yticks(lat_locator.tick_values(ymin, ymax), crs=self.transform)
                    self.cartopy_axis.yaxis.set_major_formatter(LatitudeFormatter())
                else:
                    self.matplotlib.axes().yaxis.set_major_locator(lat_locator)
            else:
                self.matplotlib.axes().yaxis.set_major_locator(MaxNLocator(nbins=max_y_bins, steps=variable_step))

            if not self.is_map():
                self.matplotlib.axes().yaxis.set_minor_locator(AutoMinorLocator())
                self.matplotlib.axes().yaxis.grid(False, which='minor')

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

    def format_time_axis(self):
        from cis.time_util import cis_standard_time_unit

        coords = self.packed_data_items[0].coords(standard_name=self.xaxis)
        if len(coords) == 0:
            coords = self.packed_data_items[0].coords(name_or_coord=self.xaxis)
        if len(coords) == 0:
            coords = self.packed_data_items[0].coords(long_name=self.xaxis)

        if len(coords) == 1:
            if coords[0].units == str(cis_standard_time_unit):
                self.ax.xaxis_date()
                # self.set_x_axis_as_time()

    def set_x_axis_as_time(self):
        from matplotlib import ticker
        from cis.time_util import convert_std_time_to_datetime

        ax = self.matplotlib.gca()

        def format_date(x, pos=None):
            return convert_std_time_to_datetime(x).strftime('%Y-%m-%d')

        def format_datetime(x, pos=None):
            # use iosformat rather than strftime as strftime can't handle dates before 1900 - the output is the same
            date_time = convert_std_time_to_datetime(x)
            day_range = self.matplotlib.gcf().axes[0].viewLim.x1 - self.matplotlib.gcf().axes[0].viewLim.x0
            if day_range < 1 and date_time.second == 0:
                return "%02d" % date_time.hour + ':' + "%02d" % date_time.minute
            elif day_range < 1:
                return "%02d" % date_time.hour + ':' + "%02d" % date_time.minute + ':' + "%02d" % date_time.second
            elif day_range > 5:
                return str(date_time.date())
            else:
                return date_time.isoformat(' ')

        def format_time(x, pos=None):
            return convert_std_time_to_datetime(x).strftime('%H:%M:%S')

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_datetime))
        tick_angle = self.xtickangle
        if tick_angle is None:
            self.xtickangle = 45
        self.matplotlib.xticks(rotation=self.xtickangle, ha="right")
        # Give extra spacing at bottom of plot due to rotated labels
        self.matplotlib.gcf().subplots_adjust(bottom=0.3)

        # ax.xaxis.set_minor_formatter(ticker.FuncFormatter(format_time))

    def set_font_size(self):
        """
        Converts the fontsize argument (if specified) from a float into a dictionary that matplotlib can recognise.
        Could be further extended to allow specifying bold, and other font formatting
        """


