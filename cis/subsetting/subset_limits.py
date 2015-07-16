from collections import namedtuple


class SubsetLimits(namedtuple('SubsetLimits', ['start', 'end', 'is_time'])):
    """Holds the start and end values for subsetting limits.
    is_date indicates whether the limits are date/times - None if unknown
    :ivar start: subsetting limit start
    :type start: str
    :ivar end: subsetting limit end
    :type end: str
    :ivar is_time: indicates whether the limits apply to a time dimension: None if not known
    :type is_type: bool
    """
    pass
