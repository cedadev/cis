from cis.plotting.plot import multilayer_plot, basic_plot, drawbluemarble


def format_plot(ax, logx, logy, grid, fontsize, xlabel, ylabel, title):
    """
    Used by 2d subclasses to format the plot
    """
    import matplotlib
    import numpy as np

    if logx:
        ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")

    if grid:
        ax.grid(True, which="both")

    if fontsize is not None:
        matplotlib.rcParams.update({'font.size': fontsize})

    if xlabel is not None:
        ax.set_xlabel(xlabel)

    if ylabel is not None:
        ax.set_ylabel(ylabel)

    if title is not None:
        ax.set_title(title)


def apply_map_axis_limits(ax, xmin=None, xmax=None, xstep=None, ymin=None, ymax=None, ystep=None):
    """
    Applies the specified limits to the given axis
    """
    import cartopy.crs as ccrs
    from cis.plotting.plot import get_best_map_ticks
    import numpy as np

    transform = ccrs.PlateCarree(360)

    global_tolerance = 0.8

    # We can't optionally pass in certain bounds to set_extent so we need to pull out the existing ones and only
    #  change the ones we've been given.
    x1, x2, y1, y2 = ax.get_extent()
    # If the user hasn't specified any limits and the data spans most of the globe, just make it a global plot
    if all(lim is None for lim in (xmin, xmax, ymin, ymax)) and \
            ((y2 - y1 > (ax.projection.y_limits[1] - ax.projection.y_limits[0]) * global_tolerance) or
                 (x2 - x1 > (ax.projection.x_limits[1] - ax.projection.x_limits[0]) * global_tolerance)):
        ax.set_global()
    else:
        xmin = xmin if xmin is not None else x1
        xmax = xmax if xmax is not None else x2
        ymin = ymin if ymin is not None else y1
        ymax = ymax if ymax is not None else y2
        ax.set_extent([xmin, xmax, ymin, ymax], crs=transform)

    # Get the updated extent
    x1, x2, y1, y2 = ax.get_extent()

    # Get default ticks
    xticks, yticks = get_best_map_ticks(ax)

    # If we're given user steps then calculate our own ticks
    if xstep is not None:
        xticks = np.arange(x1, x2 + xstep, xstep)

    if ystep is not None:
        yticks = np.arange(y1, y2 + ystep, ystep)

    ax.set_xticks(xticks)
    ax.set_yticks(yticks)


def apply_axis_limits(ax, xmin=None, xmax=None, xstep=None, ymin=None, ymax=None, ystep=None):
    """
    Applies the specified limits to the given axis
    """
    import numpy as np

    ax.set_xlim(xmin=xmin, xmax=xmax)
    ax.set_ylim(ymin=ymin, ymax=ymax)

    if xstep is not None:
        min_val, max_val = ax.get_xlim()
        ticks = np.arange(min_val, max_val + xstep, xstep)

        ax.set_xticks(ticks)

    if ystep is not None:
        min_val, max_val = ax.get_ylim()
        ticks = np.arange(min_val, max_val + ystep, ystep)

        ax.set_yticks(ticks)


def get_x_wrap_start(data_list, user_xmin=None):
    from cis.utils import find_longitude_wrap_start as find_start

    # FIND THE WRAP START OF THE DATA
    all_starts = [find_start(data) for data in data_list if find_start(data) is not None]
    data_wrap_start = min(all_starts) if all_starts else None

    # NOW find the wrap start of the user specified range
    if user_xmin is not None:
        x_wrap_start = -180 if user_xmin < 0 else 0
    else:
        x_wrap_start = data_wrap_start

    return x_wrap_start


class Plotter(object):

    def __init__(self, data, type=None, output=None, height=None,
                 width=None, logx=False, logy=False, xmin=None,
                 xmax=None, xstep=None, ymin=None, ymax=None, ystep=None, nasabluemarble=False,
                 grid=False, xlabel=None, ylabel=None, title=None, fontsize=None, *args, **kwargs):
        """
        Constructor for the plotter. Note that this method also does the actual plotting.

        :param data: A list of packed (i.e. GriddedData or UngriddedData objects) data items to be plotted
        :param type: The plot type to be used, as a string
        :param out_filename: The filename of the file to save the plot to. Optional. Various file extensions can be
         used, with png being the default
        :param args: Any other arguments received from the parser
        :param kwargs: Any other keyword arguments received from the plotter
        """

        x_start = get_x_wrap_start(data, xmin)
        if x_start is not None and 'central_longitude' not in kwargs:
            kwargs['central_longitude'] = x_start - 180.0

        # Turn data into a single object if it is one - otherwise we end up with an overlay plot
        if isinstance(data, list) and len(data) == 1:
            data = data[0]

        # If it's still a list... We don't use the object methods because in the case of the command line API
        #  we allow mixed Gridded and Ungridded data sets - which we don't allow for CommonDataLists
        if isinstance(data, list):
            plot, self.ax = multilayer_plot(data, how=type, *args, **kwargs)
        else:
            if 'layer_opts' in kwargs:
                kwargs.update(kwargs.pop('layer_opts')[0])
            plot, self.ax = basic_plot(data, how=type, *args, **kwargs)

        self.fig = self.ax.get_figure()
        # TODO: All of the below functions should be static, take their own arguments and apply only to the plot.ax
        # instance

        self.set_width_and_height(width, height)

        format_plot(self.ax, logx, logy, grid, fontsize, xlabel, ylabel, title)

        if plot.is_map():
            apply_map_axis_limits(self.ax, xmin, xmax, xstep, ymin, ymax, ystep)
            # This has to come after applying the axis limits because otherwise the image can get cropped
            if nasabluemarble:
                drawbluemarble(self.ax)
        else:
            apply_axis_limits(self.ax, xmin, xmax, xstep, ymin, ymax, ystep)

            # Rescale the data after changing the limits and possibly making log scale
            self.ax.relim()
            self.ax.autoscale()

        self.output_to_file_or_screen(output)

    def output_to_file_or_screen(self, out_filename=None):
        """
        Outputs to screen unless a filename is given

        :param out_filename: The filename of the file to save the plot to. Various file extensions can be used, with
         png being the default
        """
        import logging
        import matplotlib.pyplot as plt

        if out_filename is None:
            plt.show()
        else:
            logging.info("saving plot to file: " + out_filename)
            width = self.fig.get_figwidth()
            self.fig.savefig(out_filename, bbox_inches='tight',
                             pad_inches=0.05 * width)  # Will overwrite if file already exists

    def set_width_and_height(self, width, height):
        """
        Sets the width and height of the plot
        Uses an aspect ratio of 4:3 if only one of width and height are specified
        If neither width or height are specified it defaults to 8 by 6 inches.
        """

        if height is not None:
            if width is None:
                width = height * (4.0 / 3.0)
        elif width is not None:
            height = width * (3.0 / 4.0)
        else:
            height = 6
            width = 8

        self.fig.set_figheight(height)
        self.fig.set_figwidth(width)