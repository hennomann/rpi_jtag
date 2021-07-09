#!/usr/bin/env python3

from time import sleep
from jtag import *

####################################################
# Read device IDCODE and design USERCODE
####################################################
def read_IDCODE():
    # Read device IDCODE register
    enable_gpios()
    TLR_RTI()
    prep_shift_dr()
    disable_gpios()
    r = spi_read(4)
    binstr = ""
    for byte in r:
        binstr += "{:08b}".format(byte)
    binstr = binstr[::-1]
    print("IDCODE read from device using SPI interface:\n0x{:08x}".format(int(binstr,2)))
    enable_gpios()

# Read USERCODE only
def read_USERCODE():
    # Read USERCODE register
    enable_gpios()
    TLR_RTI()
    prep_shift_ir()
    load_instr("USERCODE")
    update_RTI()
    prep_shift_dr()
    disable_gpios() # Prepare using the hardware SPI interface
    r = spi_read(4)
    binstr = ""
    for byte in r:
        binstr += "{:08b}".format(byte)
    binstr = binstr[::-1]
    print("USERCODE read from device using SPI interface:\n0x{:08x}".format(int(binstr,2)))
    enable_gpios()


####################################################
# Program device via JTAG with bitstream in bitfile
####################################################
def program_device(bitfile):
    read_IDCODE()
    TLR_RTI()
    prep_shift_ir()
    load_instr("JPROGRAM")
    TLR_RTI()
    sleep(0.020) # Necessary wait time in this RTI according to manual (min 10ms)
    prep_shift_ir()
    load_instr("CFG_IN")
    update_RTI()
    prep_shift_dr()
    disable_gpios() # Prepare using the hardware SPI interface
    # Open bitfile and read bytes in binary mode:
    with open(bitfile,'rb') as f:
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
    update_RTI()
    print("Writing bitstream data finished")
    prep_shift_ir()
    load_instr("JSTART")
    update_RTI()
    disable_gpios()
    print("Clocking in start sequence")
    spi_read(256)
    enable_gpios()
    read_IDCODE()
    read_USERCODE()
    print("Done!")

