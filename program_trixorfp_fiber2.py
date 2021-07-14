#!/usr/bin/env python3

import sys
import argparse
from high_level_jtag import *
import timeit

start = timeit.default_timer()

parser = argparse.ArgumentParser()
parser.add_argument("bitfile", help="specify path of bitfile to be loaded")
parser.add_argument("-lf","--loadFlash", help="load bitstream into non-volatile configuration flash memory", action="store_true")
parser.add_argument("-nv","--noVerify", help="only load bitstream into flash memory, skip verification", action="store_true")
parser.add_argument("-vo","--verifyOnly", help="only verify flash content with specified bitfile", action="store_true")
args = parser.parse_args()

# Verify communication channel and correct hardware
print("Establishing JTAG connection to device")
idcode = read_IDCODE()
if idcode[3:] == "362e093":
    print("Found expected FPGA IDCODE for module TRIXORFP_FIBER2, continuing...")
else:
    sys.exit("Wrong FPGA IDCODE detected, exiting...")

# Perform tasks specified by arguments

if args.loadFlash or args.verifyOnly:
    print("Configuring device for flash background programming")
    program_device("trixorfp_fiber2_flash_load_20210714.bit")
    # Open bitfile and read bytes in binary mode:
    with open(args.bitfile,'rb') as f:
        data_raw=f.read()
    f.close()
    # Convert binary object to list an discard unneccessary header data
    start_byte = 113
    data = list(data_raw[start_byte:])
else: # no flash option selected -> only configure FPGA with bitstream
    program_device(args.bitfile)

if args.loadFlash:
    print("Starting to load flash with bitfile: " + args.bitfile)
    enable_USERMODE1()
    flash_check_id()
    flash_erase()
    flash_program(data)
    if args.noVerify:
        print("Skipping flash content verification")
    else:
        flash_verify(data)
else:
    if args.verifyOnly:
        flash_verify(data)

# Reset TAP controller
TAP_RESET()

print("Done!")

stop = timeit.default_timer()

print('Time: ', stop - start)
