"""
Run a mock ungridded-ungridded bix colocate and time it as a function of input dataset size
"""
from timeit import Timer
import gc
import memory_profiler
from jasmin_cis.test.util.mock import *
from jasmin_cis.col_implementations import SepConstraintKdtree, mean, GeneralUngriddedColocator, jasmin_cis


def colocate(sample_point_count, data_point_count):
    sample_points = make_lat_lon_time_fly_round_the_world_ungridded_data(sample_point_count)
    data_list = make_lat_lon_time_fly_round_the_world_ungridded_data(data_point_count)

    constraint = SepConstraintKdtree('10')
    kernel = mean()
    col = GeneralUngriddedColocator()
    output = col.colocate(sample_points, data_list, constraint, kernel)
    del output

sample_data_counts= [
    (200000, 10)

]

for sample_point_count, data_point_count in sample_data_counts:
    jasmin_cis.utils.dictionary = []
    gc.collect()
    colocate(sample_point_count, data_point_count)

    print("{}, {}".format("sample_point_count", "data_point_count"))
    print("{}, {}".format(sample_point_count, data_point_count))
    print("{}, {}".format("Memory MB", "what"))
    #print timer.timeit(1)
    for key, value in jasmin_cis.utils.dictionary:
        print("{}, {}".format(value/(1024 * 1024.0), key))
