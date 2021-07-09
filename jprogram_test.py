#!/usr/bin/env python3

from time import sleep
from jtag import *

# Read IDCODE using hardware SPI interface
TLR_RTI()
prep_shift_dr() # Reset test logic and prepare shifting out data
disable_gpios()
r = spi_read(4)
binstr = ""
for byte in r:
    binstr += "{:08b}".format(byte)
binstr = binstr[::-1]
print("IDCODE read from device using SPI interface:\n0x{:08x}".format(int(binstr,2)))

# Load bitstream into FPGA via JTAG interface
enable_gpios()
TLR_RTI()
prep_shift_ir()
print("Loading instruction JPROGRAM")
load_instr("JPROGRAM")
TLR_RTI()
sleep(0.020) # Necessary wait time in this RTI according to manual (min 10ms)
prep_shift_ir()
print("Loading instruction CFG_IN")
load_instr("CFG_IN")
TMS1()
TMS1()
TMS0()
TMS0()

disable_gpios() # Prepare using the hardware SPI interface

# Open bitfile and read bytes in binary mode:
print("Parsing bitfile")
with open('trixor_bitfile2.bit','rb') as f:
    data_raw = f.read()
f.close()
data = list(data_raw)

pagecount = int((len(data)-1) / 256)
bytes_last_page = (len(data)-1) % 256

print("Starting to write bitstream data")
# Send full pages of 256 bytes except for last page
for i in range(pagecount):
    print("Writing page {:05d}/{:05d}\r".format(i,pagecount-1), end="")
    spi_send(data[i*256:i*256+256])
print()

# Send all but last byte of last page
print("Writing last page")
if bytes_last_page > 0:
    spi_send(data[pagecount*256:pagecount*256+bytes_last_page])

enable_gpios() # Back to GPIO mode for bitbanging of last byte

print("Writing last byte")
gpio_send_last_byte(data[-1])

TMS1()
TMS0()

print("Writing bitstream data finished")

TMS1()
TMS1()
TMS0()
TMS0()

print("Loading instruction JSTART")
load_instr("JSTART")

TMS1()

disable_gpios()

print("Clocking in start sequence")
spi_read(256)

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

print("Done!")

