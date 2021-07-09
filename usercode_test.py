#!/usr/bin/env python3

from time import sleep
from jtag import *

# Read IDCODE using hardware SPI interface
TLR_RTI()
#prep_shift_dr() # Prepare shifting in/out data
TMS1()
TMS0()
TMS0()
disable_gpios()
r = spi_read(4)
binstr = ""
for byte in r:
    binstr += "{:08b}".format(byte)
binstr = binstr[::-1]
print("IDCODE read from device using SPI interface:\n0x{:08x}".format(int(binstr,2)))

# Read USERCODE register
enable_gpios()
TLR_RTI()
prep_shift_ir()
print("Loading instruction USERCODE")
load_instr("USERCODE")
TMS1()
TMS0()
prep_shift_dr()


disable_gpios() # Prepare using the hardware SPI interface

r = spi_read(4)
binstr = ""
for byte in r:
    binstr += "{:08b}".format(byte)
binstr = binstr[::-1]
print("USERCODE read from device using SPI interface:\n0x{:08x}".format(int(binstr,2)))

enable_gpios()


'''
# 32 bit GPIO bitbang read
r = gpio_read(32)
r.reverse()
binstr = ""
for entry in r:
    binstr += "{:1b}".format(entry)
print("USERCODE read from device using GPIO bit banging:\n0x{:08x}".format(int(binstr, 2)))
disable_gpios()
'''
