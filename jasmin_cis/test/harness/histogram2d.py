import matplotlib.pyplot as plt
from numpy import arange
from numpy.random import random
from math import ceil, floor

w = 2

#d1 = arange(start=-5, stop=20.6, step=0.5)
d1 = random(30)*50 - 5
print d1

#d2 = arange(start=0,stop=50, step=1)
d2 = random(10)*20
print d2

# GETTING THE TOTAL RANGE
min_v = min(d1.min(), d2.min())
max_v = max(d1.max(), d2.max())
r = ceil(max_v - min_v)
print r

w = None
if w is None:
    w = ceil((max_v-min_v)/10)

# CREATING AN ARRAY OF BIN EDGES
bins = arange(start=min_v,stop=min_v+r+w,step=w)
print bins

plt.hist(d1, bins=bins, histtype="step")
plt.hist(d2, bins=bins, histtype="step")
plt.show()
