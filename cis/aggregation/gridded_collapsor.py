import logging
import iris.cube


class GriddedCollapsor(object):

    def __init__(self, data, coords):
        """
        Set up the collapse of a GriddedData set over the given Coords
        :param GriddedData data:
        :param list coords: of Coord instances
        """
        self.data = data
        self.coords = coords

    @staticmethod
    def _partially_collapse_multidimensional_coord(coord, dims_to_collapse, kernel=iris.analysis.MEAN):
        import operator
        from functools import reduce
        import numpy as np

        # First calculate our new shape and dims
        dims_to_collapse = sorted(dims_to_collapse)
        end_size = reduce(operator.mul, (coord.shape[dim] for dim in dims_to_collapse))
        untouched_dims = list(set(range(coord.ndim)) - set(dims_to_collapse))
        untouched_shape = [coord.shape[dim] for dim in untouched_dims]
        new_shape = untouched_shape + [end_size]
        dims = untouched_dims + dims_to_collapse

        # Then reshape the data so that the dimensions being aggregated
        # over are grouped 'at the end' (i.e. axis=-1).
        unrolled_data = np.transpose(coord.points, dims).reshape(new_shape)

        new_points = kernel.aggregate(unrolled_data, axis=-1)
        new_coord = coord.copy(points=new_points)
        return new_coord

    @staticmethod
    def _calc_new_dims(coord_dims, dims_to_collapse):
        """
            Calculate the new dimensions for the coordinate.
        :param coord_dims: the original dimensions
        :param dims_to_collapse: The dimensions which are being collapsed over
        :return: The new coordinates which the coord will take on the collapsed cube
        """
        new_dims = []
        # For each original dimension subtract one for every collapsed coordinate which came before it.
        # TODO: There must be a cleaner way to do this...
        for d in coord_dims:
            new_d = d
            for dc in dims_to_collapse:
                if d > dc:
                    new_d -= 1
            # If the dimension is one being collapsed then we don't include it in the new dimensions
            if d not in dims_to_collapse:
                new_dims.append(new_d)

        return new_dims

    @staticmethod
    def _update_aux_factories(data, *args, **kwargs):
        from cis.utils import listify
        d_list = listify(data)
        for d in d_list:
            for factory in d.aux_factories:
                factory.update(*args, **kwargs)

    def _gridded_full_collapse(self, kernel):
        from copy import deepcopy
        from cis.exceptions import ClassNotFoundError
        ag_args = {}

        dims_to_collapse = set()
        for coord in self.coords:
            dims_to_collapse.update(self.data.coord_dims(coord))

        coords_for_partial_collapse = []

        # Collapse any coords that span the dimension(s) being collapsed
        for coord in self.data.aux_coords:
            coord_dims = self.data.coord_dims(coord)
            # If a coordinate has any of the dimensions we wan't to collapse AND has some dimensions we don't...
            if set(dims_to_collapse).intersection(coord_dims) and \
                    set(coord_dims).difference(dims_to_collapse):
                # ... add it to our list of partial coordinates to collapse.
                coords_for_partial_collapse.append((coord, coord_dims))

        if isinstance(kernel, iris.analysis.WeightedAggregator) and \
                        'latitude' in [c.standard_name for c in self.coords]:
            # If this is a list we can calculate weights using the first item (all variables should be on
            # same grid)
            data_for_weights = self.data[0] if isinstance(self.data, list) else self.data
            # Weights to correctly calculate areas.
            ag_args['weights'] = iris.analysis.cartography.area_weights(data_for_weights)
        elif not isinstance(kernel, iris.analysis.Aggregator):
            raise ClassNotFoundError('Error - unexpected aggregator type.')

        # Before we remove the coordinates which need to be partially collapsed we take a copy of the data. We need
        #  this so that the aggregation doesn't have any side effects on the input data. This is particularly important
        #  when using a MultiKernel for which this routine gets called multiple times.
        data_for_collapse = deepcopy(self.data)

        for coord, _ in coords_for_partial_collapse:
            data_for_collapse.remove_coord(coord)

        # Having set-up the collapse we can now just defer to the Cube.collapse method for much of the leg-work
        new_data = iris.cube.Cube.collapsed(data_for_collapse, self.coords, kernel, **ag_args)

        for coord, old_dims in coords_for_partial_collapse:
            collapsed_coord = GriddedCollapsor._partially_collapse_multidimensional_coord(coord, dims_to_collapse)
            new_dims = GriddedCollapsor._calc_new_dims(old_dims, dims_to_collapse)

            new_data.add_aux_coord(collapsed_coord, new_dims)
            # If the coordinate we had to collapse manually was a dependency in an aux factory (which is quite likely)
            #  then we need to put it back in and fix the factory, this will update any missing dependencies.
            self._update_aux_factories(new_data, None, collapsed_coord)

        return new_data

    def __call__(self, kernel):
        from cis.data_io.gridded_data import GriddedDataList
        from cis.aggregation.collapse_kernels import MultiKernel

        # Make sure all coordinate have bounds - important for weighting and aggregating
        # Only try and guess bounds on Dim Coords
        for coord in self.data.coords(dim_coords=True):
            if not coord.has_bounds() and len(coord.points) > 1:
                coord.guess_bounds()
                logging.warning("Creating guessed bounds as none exist in file")
                new_coord_number = self.data.coord_dims(coord)
                self.data.remove_coord(coord.name())
                self.data.add_dim_coord(coord, new_coord_number)

        output = GriddedDataList([])
        if isinstance(kernel, MultiKernel):
            for sub_kernel in kernel.sub_kernels:
                sub_kernel_out = self._gridded_full_collapse(sub_kernel)
                output.append_or_extend(sub_kernel_out)
        else:
            output.append_or_extend(self._gridded_full_collapse(kernel))
        return output

