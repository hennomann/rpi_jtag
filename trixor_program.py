#!/usr/bin/env python3

from high_level_jtag import *

print("Configuring device for flash background programming")
program_device("um1_flash_connect_tdo_bit_shift.bit")

print("Enabling USERMODE1")
enable_USERMODE1()

flash_check_id()

flash_erase()

# Open bitfile and read bytes in binary mode:
with open('um1_flash_connect_tdo_bit_shift.bit','rb') as f:
    data_raw=f.read()
f.close()
# Convert binary object to list an discard unneccessary header data
start_byte = 113
data = list(data_raw[start_byte:])

flash_program(data)

flash_verify(data)

print("Done!")
