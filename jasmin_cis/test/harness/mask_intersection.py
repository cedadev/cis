import numpy.ma as ma
import numpy as np

first_array = ma.array([5,-1,5],mask=[0,1,0])
second_array = ma.array([8,9,-1],mask=[0,0,1])

intersection = ma.mask_or(first_array.mask, second_array.mask)

new_array = ma.array(first_array, mask = intersection)

print intersection
print new_array