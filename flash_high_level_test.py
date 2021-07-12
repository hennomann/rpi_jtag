#!/usr/bin/env python3

from high_level_jtag import *

print("Enabling USERMODE1")
enable_USERMODE1()

flash_check_id()

flash_erase()

# Open bitfile and read bytes in binary mode:
with open(bitfile,'rb') as f:
    data_raw=f.read()
f.close()
# Convert binary object to list an discard unneccessary header data
start_byte = 113
data = list(data_raw[start_byte:])
# Pad data to have a full last page
pagecount = int(math.ceil(float(len(data))/256.))
n_pad = pagecount * 256 - len(data)
data += [0xff]*n_pad

print()

print("Done!")
