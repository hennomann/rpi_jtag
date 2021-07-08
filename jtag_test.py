#!/usr/bin/env python3

from time import sleep
from jtag import *

enable_gpios()

'''
# Read IDCODE using GPIOs (bit banging)
prep_shift_dr() # Reset test logic and prepare shifting out data
r = gpio_read(32)
r.reverse()
binstr = ""
for entry in r:
    binstr += "{:1b}".format(entry)
print("IDCODE read from device using GPIO bit banging:\n0x{:08x}".format(int(binstr, 2)))
'''

# Read IDCODE using hardware SPI interface
prep_shift_dr() # Reset test logic and prepare shifting out data
disable_gpios()
r = spi_read(4)
binstr = ""
for byte in r:
    binstr += "{:08b}".format(byte)
binstr = binstr[::-1]
print("IDCODE read from device using SPI interface:\n0x{:08x}".format(int(binstr,2)))

#print("0x",end='')
#for byte in r:
#    print("{:02x}".format(byte),end='')
#print()
