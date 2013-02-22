import matplotlib.pyplot as plt


class Contour_Plot(object):
    #'contour' : PlotType(1, 2, plot_contour),
    def plot(self, data_item, *args, **kwargs):
        '''
        Plots a contour plot
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        from mpl_toolkits.basemap import Basemap
        basemap = Basemap()
        #kwargs["latlon"] = True
        return basemap.contour(data_item["x"], data_item["y"], data_item["data"])#, *args, **kwargs)

    def set_axis_label(self, axis, options, data):
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if options[axislabel] is None:
            #if self.__is_map():
                options[axislabel] = "Longitude" if axis == "x" else "Latitude"
                '''
                else:
                    try:
                        name = data[0].coord(axis=axis).name()
                    except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                        name = data[0].name()

                    try:
                        units = data[0].coord(axis=axis).units
                    except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                        units = data[0].units

                    # in general, display both name and units in brackets
                    options[axislabel] = name + self.__format_units(units)
                    '''

        return options

    def create_legend(self, datafiles):
        pass

    def add_color_bar(self, logv, vmin, vmax, v_range, orientation, units):
        from plot import format_units
        # nformat = "%e"
        # nformat = "%.3f"
        # nformat = "%.3e"
        nformat = "%.3g"

        if not logv:
            try:
                step = v_range.get("vstep", (vmax-vmin) / 5)
            except AttributeError:
                step = (vmax-vmin) / 5
            ticks = []
            tick = vmin
            while tick <= vmax:
                ticks.append(tick)
                tick = tick + step
        else:
            ticks = None

        cbar = plt.colorbar(orientation = orientation, ticks = ticks, format = nformat)

        cbar.set_label(format_units(units))
