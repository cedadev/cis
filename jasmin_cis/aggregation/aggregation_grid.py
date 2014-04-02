from collections import namedtuple


class AggregationGrid(namedtuple('AggregationGrid', ['start', 'end', 'delta', 'is_time'])):
    """Holds the start and delta values for the aggregation grid.
    is_date indicates whether the limits are date/times - None if unknown
    :ivar start: aggregation start point
    :type start: str
    :ivar delta: aggregation step to take through grid
    :type delta: str
    :ivar is_time: indicates whether the limits apply to a time dimension: None if not known
    :type is_type: bool
    """
    pass
