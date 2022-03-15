"""
High-level plotting routines
Also contains a dictionary for the valid plot types.
All plot types need to be imported and added to the plot_types dictionary in order to be used.
"""
import logging

from cis.plotting.comparativescatter import ComparativeScatter
from cis.plotting.contourplot import ContourPlot, ContourfPlot
from cis.plotting.heatmap import Heatmap
from cis.plotting.histogram import Histogram
from cis.plotting.histogram2d import Histogram2D
from cis.plotting.lineplot import LinePlot
from cis.plotting.scatterplot import ScatterPlot, ScatterPlot2D
from cis.plotting.taylor import Taylor
from cis.plugin import get_all_subclasses
import cartopy.crs
import six

colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']


plot_types = {"contour": ContourPlot,
              "contourf": ContourfPlot,
              "heatmap": Heatmap,
              "line": LinePlot,
              "scatter": ScatterPlot,
              "scatter2d": ScatterPlot2D,
              "comparativescatter": ComparativeScatter,
              "histogram": Histogram,
              "histogram2d": Histogram2D,
              "taylor": Taylor}


# Available projections from Cartopy
projections = {cls.__name__: cls for cls in get_all_subclasses(cartopy.crs.Projection, "cartopy.crs")}


def format_units(units):
    """
    Optionally put brackets around a units string
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


def get_label(common_data, units=True):
    """
    Get a nicely formatted label from a CommonData object
    :param CommonData common_data:
    :param bool units: Include units in label? Default True
    :return string: A label
    """
    name = common_data.name() or ""
    if units:
        if name:
            name += " "
        name += format_units(common_data.units)
    return name


def _try_coord(data, coord_dict):
    """
    Try and find a single (extended) coord in a CommonData object using the dictionary provided
    :param CommonData data:
    :param dict coord_dict: Kwargs to look for coord
    :return: A single Coord or None if none can be found
    """
    import cis.exceptions as cis_ex
    import iris.exceptions as iris_ex
    try:
        coord = data.coord(**coord_dict)
    except (iris_ex.CoordinateNotFoundError, cis_ex.CoordinateNotFoundError):
        coord = None
    else:
        if not len(coord.points) > 1:
            # Don't guess a scalar coord
            coord = None
    return coord


def get_axis(d, axis, name=None):
    """
    Guess the best Coord to use for the axis
    :param CommonData d:
    :param string axis:
    :param string name:
    :return Coord: A single Coord
    """
    coord = _try_coord(d, dict(name_or_coord=name)) or _try_coord(d, dict(standard_name=name)) \
            or _try_coord(d, dict(axis=axis))

    # This is primarily for gridded data, but for Ungridded Data should just pick out the first Coord in the list.
    if coord is None:
        for c in d.coords():
            if axis == 'X' or len(d.shape) == 1:
                if c.shape[0] == d.shape[0]:
                    coord = c
                    break
            elif axis == 'Y' and len(d.shape) > 1:
                if c.shape[1] == d.shape[1]:
                    coord = c
                    break

    logging.info("Plotting " + coord.name() + " on the {} axis".format(axis))

    return coord


def set_x_axis_as_time(ax):
    """
    Nicely format a time axis
    """
    from matplotlib import ticker
    from matplotlib.dates import num2date

    def format_datetime(x, pos=None):
        # use iosformat rather than strftime as strftime can't handle dates before 1900 - the output is the same
        date_time = num2date(x)
        day_min, day_max = ax.get_xlim()
        day_range = day_max - day_min
        if day_range < 1 and date_time.second == 0:
            return "%02d" % date_time.hour + ':' + "%02d" % date_time.minute
        elif day_range < 1:
            return "%02d" % date_time.hour + ':' + "%02d" % date_time.minute + ':' + "%02d" % date_time.second
        elif day_range > 5:
            return str(date_time.date())
        else:
            return date_time.isoformat(' ')

    # Setup conversion of our standard time
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_datetime))
    # Then just let matplotlib format it nicely...
    ax.get_figure().autofmt_xdate()


def _get_extent(ax):
    """
     Calculates the diagonal extent of plot area in Km
    :return: The diagonal size of the plot in Km
    """
    from cis.utils import haversine
    x0, x1, y0, y1 = ax.get_extent()
    return haversine(y0, x0, y1, x1)


def _test_natural_earth_available():
    """
    Test whether we can download the natural earth cartographies.
    :return: Can we access natural earth?
    """
    from cartopy.io.shapereader import natural_earth
    from six.moves.urllib.error import HTTPError
    try:
        natural_earth_available = natural_earth()
    except HTTPError:
        natural_earth_available = False
    return natural_earth_available


def drawcoastlines(ax, coastlinescolour):
    """
    Adds coastlines to a plot.
    There are three levels of resolution used based on the spatial scale of the plot. These are determined using
    values determined by eye for bluemarble and the coastlines independently.
    """
    coastline_scales = [(0, '110m'), (500, '50m'), (100, '10m')]

    ext = _get_extent(ax)

    if _test_natural_earth_available():
        coastline_res = coastline_scales[0][1]
        for scale, res in coastline_scales[1:]:
            if scale > ext:
                coastline_res = res

        ax.coastlines(color=coastlinescolour, resolution=coastline_res)
    else:
        logging.warning('Unable to access the natural earth topographies required for plotting coastlines. '
                        'Check internet connectivity and try again')


def drawbluemarble(ax):
    """
    Adds nasa blue marble back ground to a plot
    There are three levels of resolution used based on the spatial scale of the plot. These are determined using
    values determined by eye for bluemarble and the coastlines independently.
    """
    from matplotlib.image import imread
    import cartopy.crs as ccrs
    import os.path as path
    from cis.utils import no_autoscale

    source_proj = ccrs.PlateCarree()

    bluemarble_scales = [(0, 'raster/world.topo.bathy.200407.3x1350x675.png'),
                         (5000, 'raster/world.topo.bathy.200407.3x2700x1350.png'),
                         (2500, 'raster/world.topo.bathy.200407.3x5400x2700.png')]

    ext = _get_extent(ax)

    # Search for the right resolution
    bluemarble_res = bluemarble_scales[0][1]
    for scale, res in bluemarble_scales[1:]:
        if scale > ext:
            bluemarble_res = res

    img = imread(path.join(path.dirname(path.realpath(__file__)), bluemarble_res))
    # Don't change the scale of the plot
    with no_autoscale(ax):
        ax.imshow(img, origin='upper', transform=source_proj, extent=[-180, 180, -90, 90])


def get_best_map_ticks(ax, transform=None):
    """
    Use the matplotlib.ticker class to automatically set nice values for the major and minor ticks.
    Log axes generally come out nicely spaced without needing manual intervention. For particularly narrow latitude
    vs longitude plots the ticks can come out overlapped, so an exception is included to deal with this.
    """
    from matplotlib.ticker import MaxNLocator

    max_x_bins = 9
    max_y_bins = 7  # as plots are wider rather than taller

    lon_steps = [1, 3, 6, 9, 10]
    lat_steps = [1, 3, 6, 9, 10]
    variable_step = [1, 2, 4, 5, 10]

    xmin, xmax, ymin, ymax = ax.get_extent(crs=transform)
    # ymin, ymax = ax.get_ylim()

    if (xmax - xmin) < 5:
        lon_steps = variable_step
    if (ymax - ymin) < 5:
        lat_steps = variable_step

    # We need to make a special exception for particularly narrow and wide plots, which will be lat vs lon
    # preserving the aspect ratio. This gives more options for the spacing to try and find something that can use
    # the maximum number of bins.
    if (ymax - ymin) > 2.2 * (xmax - xmin):
        max_x_bins = 4
        max_y_bins = 11
    elif (xmax - xmin) > 2.2 * (ymax - ymin):
        max_x_bins = 14
        max_y_bins = 4

    lon_locator = MaxNLocator(nbins=max_x_bins, steps=lon_steps)
    lat_locator = MaxNLocator(nbins=max_y_bins, steps=lat_steps)
    lon_ticks = lon_locator.tick_values(xmin, xmax)
    # Prune any large longitude ticks
    lon_ticks = [t for t in lon_ticks if abs(t) <= 360.0]
    lat_ticks = lat_locator.tick_values(ymin, ymax)
    # Prune any large latitude ticks
    lat_ticks = [t for t in lat_ticks if abs(t) <= 90.0]
    return lon_ticks, lat_ticks


def set_map_ticks(ax, xticks, yticks, transform=None):
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
    import cartopy.crs as ccrs

    if isinstance(ax.projection, ccrs._RectangularProjection):
        ax.set_xticks(xticks, crs=transform)
        ax.xaxis.set_major_formatter(LongitudeFormatter())

        ax.set_yticks(yticks, crs=transform)
        ax.yaxis.set_major_formatter(LatitudeFormatter())
    else:
        logging.debug("Not setting map ticks for non-rectangular projection. Setting gridlines instead.")
        ax.gridlines()


def add_color_bar(ax, mappable, vstep, logv, cbarscale, cbarorient, cbarlabel):
    """
    Adds a colour bar to a plot
    Allows specifying of tick spacing and orientation
    """
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator, LogFormatterMathtext

    cbar_kwargs = {}

    if vstep is not None:
        cbar_kwargs['ticks'] = MultipleLocator(vstep)

    if logv:
        cbar_kwargs['format'] = LogFormatterMathtext(10, labelOnlyBase=False)
    #
    if cbarscale is not None:
        cbar_kwargs['shrink'] = cbarscale

    if cbarorient is not None:
        cbar_kwargs['orientation'] = cbarorient

    cbar = plt.colorbar(mappable, ax=ax, **cbar_kwargs)

    if not logv:
        cbar.formatter.set_scientific(True)
        cbar.formatter.set_powerlimits((-3, 3))
        cbar.update_ticks()

    cbar.set_label(cbarlabel)


def basic_plot(data, how=None, ax=None, xaxis=None, yaxis=None, projection=None, central_longitude=0.0,
               label=None, *args, **kwargs):
    """
    Plot a single data object using the method specified

    :param CommonData data: The data to plot
    :param string how: The method to use, one of:  "contour", "contourf", "heatmap", "line", "scatter", "scatter2d",
    "comparativescatter", "histogram", "histogram2d" or "taylor"
    :param Axes ax: A matplotlib axes on which to draw the plot
    :param Coord or CommonData xaxis: The data to plot on the x axis
    :param Coord or CommonData yaxis: The data to plot on the y axis
    :param string or cartopy.crs.Projection projection: The projection to use for map plots (default is PlateCaree)
    :param float central_longitude: The central longitude to use for PlateCaree (if no other projection specified)
    :param string label: A label for the data. This is used for the title, colorbar or legend depending on plot type
    :param args: Other plot-specific args
    :param kwargs: Other plot-specific kwargs
    :return APlot and Axes: The APlot instance and the matplotlib Axes on which the plot was drawn
    """
    import cartopy.crs as ccrs
    from cartopy.mpl.geoaxes import GeoAxes
    import matplotlib.pyplot as plt
    from cis.data_io.common_data import CommonData
    from cis.data_io.gridded_data import GriddedData
    from cis.utils import squeeze
    from cis.plotting.genericplot import GenericPlot

    # Remove any extra gridded data dimensions
    if isinstance(data, GriddedData):
        data = squeeze(data)

    if isinstance(xaxis, CommonData):
        if how is not None:
            if how not in ['comparativescatter', 'histogram2d']:
                raise ValueError("Invalid plot type with xaxis as a CommonData object. Either use comparativescatter, "
                                 "histogram2d or use a Coord (or None) for the xaxis argument.")
        else:
            how = 'comparativescatter'
        xaxis_coord = xaxis
    else:
        xaxis_coord = get_axis(data, 'X', xaxis)

    yaxis_coord = get_axis(data, 'Y', yaxis)

    how = how or data._get_default_plot_type(xaxis_coord.standard_name == 'longitude'
                                             and yaxis_coord.standard_name == 'latitude')

    try:
        plt_type = plot_types[how]
    except KeyError:
        raise ValueError("Invalid plot type, must be one of: {}".format(plot_types.keys()))

    if issubclass(plt_type, GenericPlot) and yaxis is not None:
        # If we have a line or scatter plot and the user has specified a y-axis, then this should be the data
        data = yaxis_coord
    else:
        # Otherwise, it's just another kwarg
        kwargs['yaxis'] = yaxis_coord

    # Set a nice default label
    label = get_label(data) if label is None else label

    plot = plot_types[how](data, xaxis=xaxis_coord, label=label, *args, **kwargs)

    subplot_kwargs = {}
    if plot.is_map():
        if projection is None:
            projection = ccrs.PlateCarree(central_longitude=central_longitude)
        elif isinstance(projection, six.string_types):
            projection = projections[projection]()
        plot.mplkwargs['transform'] = ccrs.PlateCarree()
        subplot_kwargs['projection'] = projection
        # Monkey-patch the nasabluemarble method onto the axis
        GeoAxes.bluemarble = drawbluemarble

    if ax is None:
        _, ax = plt.subplots(subplot_kw=subplot_kwargs)

    # Make the plot
    plot(ax)

    # Any post-processing
    if xaxis_coord.standard_name == 'time' and how not in ['comparativescatter', 'histogram2d', 'histogram']:
        set_x_axis_as_time(ax)

    if yaxis_coord.standard_name == 'air_pressure':
        ax.invert_yaxis()

    return plot, ax


def multilayer_plot(data_list, how=None, ax=None, yaxis=None, layer_opts=None, *args, **kwargs):
    """
    Plot multiple data objects using the method specified

    :param list data_list: A list of CommonData objects to plot
    :param string how: The method to use, one of:  "contour", "contourf", "heatmap", "line", "scatter", "scatter2d",
    "comparativescatter", "histogram", "histogram2d" or "taylor"
    :param Axes ax: A matplotlib axes on which to draw the plot
    :param Coord or CommonData xaxis: The data to plot on the x axis
    :param Coord or CommonData yaxis: The data to plot on the y axis
    :param list layer_opts: A list of keyword dictionaries to pass to each layer of the plot.
    :param args: Other plot-specific args to pass to all plots
    :param kwargs: Other plot-specific kwargs to pass to all plots
    :return APlot and Axes: The APlot instance and the matplotlib Axes on which the plot was drawn
    """
    layer_opts = [{} for i in data_list] if layer_opts is None else layer_opts
    if len(layer_opts) != len(data_list):
        raise ValueError("One layer-options keyword dictionary must be supplied for each data item, or none at all.")

    if how in ['comparativescatter', 'histogram2d']:
        if len(data_list) != 2:
            raise ValueError("Exactly two data objects must be provided for comparative plots")
        layer_kwargs = dict(list(kwargs.items()) + list(layer_opts[0].items()))
        plot, ax = basic_plot(data_list[1], how, ax, xaxis=data_list[0], *args, **layer_kwargs)
    elif how == 'taylor':
        plot, ax = taylor_plot(data_list, ax, layer_opts, *args, **kwargs)
    else:
        if not isinstance(yaxis, list):
            yaxis = [yaxis for i in data_list]

        for d, y, opts in zip(data_list, yaxis, layer_opts):
            layer_kwargs = dict(list(kwargs.items()) + list(opts.items()))
            how = layer_kwargs.pop('type', how)
            label = layer_kwargs.pop('label', get_label(d, units=False))
            plot, ax = basic_plot(d, how, ax, yaxis=y, label=label, *args, **layer_kwargs)

        legend = ax.legend(loc="best")
        if legend is not None:
            legend.set_draggable(True)

    return plot, ax


def taylor_plot(data_list, ax=None, layer_opts=None, *args, **kwargs):
    """
    Construct a Taylor diagram from the data list provided. Taylor plots are a bit special!
     Layer_opts are parsed for itemstyle and color which are then combined to be passed to the plotting routines. This
     allows reuse of familiar command line kwargs while maintaining a simple API.

    :param list data_list: List of CommonData objexts
    :param ax: Optional axis - although we don't use a standard axis for this plot so using the default is strongly
    recommended
    :param list layer_opts: A list of dictionaries optionally containing labels, itemstyles and colors for each data object
    :param list args: Optional extra arguments
    :param dict kwargs: Optional extra keyword arguments
    :return: Taylor plot and axes instances
    """
    import matplotlib.pyplot as plt
    from cis.plotting.taylor import ArcCosTransform
    from matplotlib.projections import PolarAxes
    from matplotlib.transforms import IdentityTransform, blended_transform_factory
    import mpl_toolkits.axisartist.floating_axes as floating_axes

    _ = kwargs.pop('central_longitude', None)  # In case the Plotter has added it...

    layer_opts = [{} for i in data_list] if layer_opts is None else layer_opts
    labels = [layer_opt.pop('label', None) for layer_opt in layer_opts]

    # Pull together markers from the layer_opts
    markers = [layer_opt.pop('itemstyle', None) for layer_opt in layer_opts]
    if all(m is None for m in markers):
        # If all markers are None then just set the list to None
        markers = None
    elif any(m is None for m in markers):
        # If not all are None, but some are then we have a problem
        raise ValueError("If any markers are set then a marker must be set for every dataset")

    # Pull together colors from the layer_opts
    colors = [layer_opt.pop('color', None) for layer_opt in layer_opts]
    if all(c is None for c in colors):
        # If all markers are None then just set the list to None
        colors = None
    elif any(c is None for c in colors):
        # If not all are None, but some are then we have a problem
        raise ValueError("If any markers are set then a marker must be set for every dataset")
    kwargs['itemwidth'] = layer_opts[0].pop('itemwidth', None)
    plot = Taylor(data_list, labels, colors, markers, *args, **kwargs)

    if ax is None:
        fig = plt.figure()

        tr = blended_transform_factory(ArcCosTransform(), IdentityTransform()) + PolarAxes.PolarTransform()

        gh = floating_axes.GridHelperCurveLinear(tr, extremes=(plot.extend, 1., 0., plot.gammamax),
                                                 grid_locator1=None,
                                                 grid_locator2=None,
                                                 tick_formatter1=None,
                                                 tick_formatter2=None)
        ax = floating_axes.FloatingSubplot(fig, 1, 1, 1, grid_helper=gh)
        fig.add_subplot(ax)

    ax = plot(ax)

    return plot, ax
