from cis.plotting.comparativescatter import ComparativeScatter
import numpy


class Histogram2D(ComparativeScatter):

    def __call__(self):
        """
        Plots a 2d histogram.
        """
        from cis.utils import apply_intersection_mask_to_two_arrays

        first_data_item, second_data_item = apply_intersection_mask_to_two_arrays(self.x, self.y)

        first_data_item = first_data_item.compressed()
        second_data_item = second_data_item.compressed()

        # Use Numpy histogram generator instead of hist2d to allow log scales to be properly plotted
        histogram2ddata, x, y = numpy.histogram2d(first_data_item, second_data_item)
        histogram2ddata = numpy.ma.masked_equal(histogram2ddata, 0)
        result = self.ax.pcolor(x, y, histogram2ddata.T, *self.mplargs, **self.mplkwargs)

        self._plot_xy_line()

        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

        # TODO: Decide whether to draw this or not...
        # self.ax.get_figure().colorbar(result)
