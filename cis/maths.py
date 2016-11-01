# (C) British Crown Copyright 2010 - 2016, Met Office
#
# This file was derived from a related file in the Iris project which is released under the LGPL 3
"""
Basic mathematical and statistical operations.
"""
import math
import operator

import cf_units
import numpy as np

from cis.data_io.ungridded_data import LazyData


def abs(ungridded_data, in_place=False):
    """
    Calculate the absolute values of the data in the LazyData provided.

    Args:

    * ungridded_data:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    Kwargs:

    * in_place:
        Whether to create a new LazyData, or alter the given "ungridded_data".

    Returns:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    """
    return _math_op_common(ungridded_data, np.abs, ungridded_data.units, in_place=in_place)


def _assert_is_ungridded_data(ungridded_data):
    if not isinstance(ungridded_data, LazyData):
        raise TypeError('The "ungridded_data" argument must be an instance of '
                        'cis.data_io.ungridded_data.LazyData.')


def _assert_matching_units(ungridded_data, other, operation_name):
    """
    Check that the units of the ungridded_data and the other item are the same, or if
    the other does not have a unit, skip this test
    """
    if ungridded_data.units != getattr(other, 'units', ungridded_data.units):
        msg = 'Cannot use {!r} with differing units ({} & {})'.format(
            operation_name, ungridded_data.units, other.units)
        raise NotImplementedError(msg)


def add(ungridded_data, other, in_place=False):
    """
    Calculate the sum of two ungridded_datas, or the sum of a ungridded_data and a
    coordinate or scalar value.

    When summing two ungridded_datas, they must both have the same coordinate
    systems & data resolution.

    When adding a coordinate to a ungridded_data, they must both share the same
    number of elements along a shared axis.

    Args:

    * ungridded_data:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.
    * other:
        An instance of :class:`cis.data_io.ungridded_data.LazyData` or :class:`iris.coords.Coord`,
        or a number or :class:`numpy.ndarray`.

    Kwargs:

    * in_place:
        Whether to create a new LazyData, or alter the given "ungridded_data".

    Returns:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    """
    op = operator.iadd if in_place else operator.add
    return _add_subtract_common(op, ungridded_data, other, in_place=in_place)


def subtract(ungridded_data, other, in_place=False):
    """
    Calculate the difference between two ungridded_datas, or the difference between
    a ungridded_data and a coordinate or scalar value.

    When subtracting two ungridded_datas, they must both have the same coordinate
    systems & data resolution.

    When subtracting a coordinate to a ungridded_data, they must both share the
    same number of elements along a shared axis.

    Args:

    * ungridded_data:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.
    * other:
        An instance of :class:`cis.data_io.ungridded_data.LazyData` or :class:`iris.coords.Coord`,
        or a number or :class:`numpy.ndarray`.

    Kwargs:

    * in_place:
        Whether to create a new LazyData, or alter the given "ungridded_data".

    Returns:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    """
    op = operator.isub if in_place else operator.sub
    return _add_subtract_common(op, ungridded_data, other, in_place=in_place)


def _add_subtract_common(operation_function, ungridded_data, other, in_place=False):
    """
    Function which shares common code between addition and subtraction
    of ungridded_datas.

    operation_function   - function which does the operation
                           (e.g. numpy.subtract)
    ungridded_data                 - the ungridded_data whose data is used as the first argument
                           to `operation_function`
    other                - the ungridded_data, coord, ndarray or number whose data is
                           used as the second argument
    in_place             - whether or not to apply the operation in place to
                           `ungridded_data` and `ungridded_data.data`

    """
    _assert_is_ungridded_data(ungridded_data)
    _assert_matching_units(ungridded_data, other, operation_function.__name__)

    new_ungridded_data = _binary_op_common(operation_function, ungridded_data, other, ungridded_data.units, in_place)

    return new_ungridded_data


def multiply(ungridded_data, other, in_place=False):
    """
    Calculate the product of a ungridded_data and another ungridded_data or coordinate.

    Args:

    * ungridded_data:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.
    * other:
        An instance of :class:`cis.data_io.ungridded_data.LazyData` or :class:`iris.coords.Coord`,
        or a number or :class:`numpy.ndarray`.

    Returns:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    """
    _assert_is_ungridded_data(ungridded_data)
    other_unit = getattr(other, 'units', '1')
    new_unit = ungridded_data.units * other_unit
    op = operator.imul if in_place else operator.mul
    return _binary_op_common(op, ungridded_data, other, new_unit, in_place=in_place)


def divide(ungridded_data, other, in_place=False):
    """
    Calculate the division of a ungridded_data by a ungridded_data or coordinate.

    Args:

    * ungridded_data:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.
    * other:
        An instance of :class:`cis.data_io.ungridded_data.LazyData` or :class:`iris.coords.Coord`,
        or a number or :class:`numpy.ndarray`.

    Returns:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    """
    _assert_is_ungridded_data(ungridded_data)
    other_unit = getattr(other, 'units', '1')
    new_unit = ungridded_data.units / other_unit
    try:
        op = operator.idiv if in_place else operator.div
    except AttributeError:
        op = operator.itruediv if in_place else operator.truediv
    return _binary_op_common(op, ungridded_data, other, new_unit, in_place=in_place)


def exponentiate(ungridded_data, exponent, in_place=False):
    """
    Returns the result of the given ungridded_data to the power of a scalar.

    Args:

    * ungridded_data:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.
    * exponent:
        The integer or floating point exponent.

        .. note:: When applied to the ungridded_data's unit, the exponent must
            result in a unit that can be described using only integer
            powers of the basic units.

            e.g. Unit('meter^-2 kilogram second^-1')

    Kwargs:

    * in_place:
        Whether to create a new LazyData, or alter the given "ungridded_data".

    Returns:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    """
    _assert_is_ungridded_data(ungridded_data)

    def power(data, out=None):
        return np.power(data, exponent, out)

    return _math_op_common(ungridded_data, power, ungridded_data.units ** exponent, in_place=in_place)


def exp(ungridded_data, in_place=False):
    """
    Calculate the exponential (exp(x)) of the ungridded_data.

    Args:

    * ungridded_data:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    .. note::

        Taking an exponential will return a ungridded_data with dimensionless units.

    Kwargs:

    * in_place:
        Whether to create a new LazyData, or alter the given "ungridded_data".

    Returns:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    """
    return _math_op_common(ungridded_data, np.exp, cf_units.Unit('1'), in_place=in_place)


def log(ungridded_data, in_place=False):
    """
    Calculate the natural logarithm (base-e logarithm) of the ungridded_data.

    Args:

    * ungridded_data:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    Kwargs:

    * in_place:
        Whether to create a new LazyData, or alter the given "ungridded_data".

    Returns:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    """
    return _math_op_common(ungridded_data, np.log, ungridded_data.units.log(math.e), in_place=in_place)


def log2(ungridded_data, in_place=False):
    """
    Calculate the base-2 logarithm of the ungridded_data.

    Args:

    * ungridded_data:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    Kwargs:

    * in_place:
        Whether to create a new LazyData, or alter the given "ungridded_data".

    Returns:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    """
    return _math_op_common(ungridded_data, np.log2, ungridded_data.units.log(2), in_place=in_place)


def log10(ungridded_data, in_place=False):
    """
    Calculate the base-10 logarithm of the ungridded_data.

    Args:

    * ungridded_data:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    Kwargs:

    * in_place:
        Whether to create a new LazyData, or alter the given "ungridded_data".

    Returns:
        An instance of :class:`cis.data_io.ungridded_data.LazyData`.

    """
    return _math_op_common(ungridded_data, np.log10, ungridded_data.units.log(10), in_place=in_place)


def _binary_op_common(operation_function, ungridded_data, other, new_unit, in_place=False):
    """
    Function which shares common code between binary operations.

    operation_function   - function which does the operation
                           (e.g. numpy.divide)
    ungridded_data                 - the ungridded_data whose data is used as the first argument
                           to `operation_function`
    other                - the ungridded_data, coord, ndarray or number whose data is
                           used as the second argument
    new_unit             - unit for the resulting quantity
    in_place             - whether or not to apply the operation in place to
                           `ungridded_data` and `ungridded_data.data`
    """
    _assert_is_ungridded_data(ungridded_data)

    if isinstance(other, LazyData):
        other = other.data

    def unary_func(x):
        ret = operation_function(x, other)
        if ret is NotImplemented:
            # explicitly raise the TypeError, so it gets raised even if, for
            # example, `cis.maths.multiply(ungridded_data, other)` is called
            # directly instead of `ungridded_data * other`
            raise TypeError('cannot %s %r and %r objects' %
                            (operation_function.__name__, type(x).__name__,
                             type(other).__name__))
        return ret
    return _math_op_common(ungridded_data, unary_func, new_unit, in_place)


def _math_op_common(ungridded_data, operation_function, new_unit, in_place=False):
    _assert_is_ungridded_data(ungridded_data)
    if in_place:
        new_ungridded_data = ungridded_data
        try:
            operation_function(new_ungridded_data._my_data, out=new_ungridded_data._my_data)
        except TypeError:
            # Non ufunc function
            operation_function(new_ungridded_data.data)
    else:
        new_ungridded_data = ungridded_data.copy(data=operation_function(ungridded_data._my_data))
    new_ungridded_data.units = new_unit
    new_ungridded_data.add_history('Performed {op} operation'.format(op=operation_function.__name__))
    return new_ungridded_data
