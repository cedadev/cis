from collections import namedtuple


class SubsetLimits(namedtuple('SubsetLimits', ['start', 'end', 'is_time'])):
    """Holds the start and end values for subsetting limits.
    is_date indicates whether the limits are date/times - None if unknown
    """
    pass
