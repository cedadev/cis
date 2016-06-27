from abc import ABCMeta, abstractmethod


def aggregate(aggregator, data, kernel, **kwargs):
    """

    :param Aggregator aggregator: The aggregator class to instantiate
    :param CommonData or CommonDataList data: The data to aggregate
    :param cis.collocation.col_framework.Kernel or iris.Analysis.Aggregator kernel:
    :param kwargs:
    :return:
    """
    from cis import __version__

    aggregator = aggregator(data, kwargs)
    data = aggregator.aggregate(kernel)

    # TODO Tidy up output of grid in the history
    history = "Aggregated using CIS version " + __version__ + \
              "\n variables: " + str(getattr(data, "var_name", "Unknown")) + \
              "\n from files: " + str(getattr(data, "filenames", "Unknown")) + \
              "\n using new grid: " + str(kwargs) + \
              "\n with kernel: " + kernel + "."
    data.add_history(history)

    return data


class Aggregator(object):
    """
    Class which provides a method for performing collocation. This just defines the interface which
    the subclasses must implement.
    """
    __metaclass__ = ABCMeta

    def __init__(self, data, grid):
        self.data = data
        self._grid = grid

    @abstractmethod
    def aggregate(self, kernel):
        pass

    def get_grid(self, coord):
        from cis.utils import guess_coord_axis
        grid = None
        guessed_axis = guess_coord_axis(coord)
        if coord.name() in self._grid:
            grid = self._grid.pop(coord.name())
        elif hasattr(coord, 'var_name') and coord.var_name in self._grid:
            grid = self._grid.pop(coord.var_name)
        elif coord.standard_name in self._grid:
            grid = self._grid.pop(coord.standard_name)
        elif coord.long_name in self._grid:
            grid = self._grid.pop(coord.long_name)
        elif guessed_axis is not None:
            if guessed_axis in self._grid:
                grid = self._grid.pop(guessed_axis)
            elif guessed_axis.lower() in self._grid:
                grid = self._grid.pop(guessed_axis.lower())

        return grid, guessed_axis
