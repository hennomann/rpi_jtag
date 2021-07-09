#!/usr/bin/env python3

from high_level_jtag import *

#import profile
#profile.run('program_device4k("trixor_bitfile2.bit"); print()')

import timeit

start = timeit.default_timer()

program_device("trixor_bitfile2.bit")

stop = timeit.default_timer()

print('Time: ', stop - start)
