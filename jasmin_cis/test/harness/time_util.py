__author__ = 'duncan'

from jasmin_cis.time_util import convert_sec_since_to_std_time, convert_std_time_to_datetime
import datetime as dt
from iris.unit import Unit

Caliop_time_unit = Unit('seconds since 1993-01-01', calendar='gregorian')

Caliop_UTC_time_unit = Unit('days since 2010-01-01', calendar='gregorian')

t1a = Caliop_time_unit.num2date(536539236.156000)

t1 = convert_sec_since_to_std_time(536539236.156000, dt.datetime(1993,1,1,0,0,0))

t2 = dt.datetime(2010,1,1) + dt.timedelta(days=0.944782)

t3 = Caliop_UTC_time_unit.num2date(0.944782)

print convert_std_time_to_datetime(t1)
print t1a
print t2
print t3