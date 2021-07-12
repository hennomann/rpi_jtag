#!/usr/bin/env python3

from high_level_jtag import *
from jtag import read_id

read_IDCODE()

print("Enabling USERMODE1")

TLR_RTI()
prep_shift_ir()
load_instr("USER1")
update_RTI()
prep_shift_dr()
disable_gpios()

# Read device ID
print("Reading flash device ID:")
r=flash_read_id()
print("0x",end="")
for byte in r:
    print("{:02x}".format(byte),end="")
print()
#binstr=""
#for byte in r[2:-1]:
#    binstr += "{:08b}".format(byte)
#print(binstr)
'''
print("Read SPI flash device ID:")
r=read_id()
print("0x",end="")
for byte in r[1:-1]:
    print("{:02x}".format(byte),end="")
print()
binstr=""
for byte in r[1:-1]:
    binstr += "{:08b}".format(byte)
print(binstr)
'''
ref=[0xc2,0x28,0x17]
print("ID should be:")
print("0xc22817")
for byte in ref:
    print("{:08b}".format(byte),end="")
print()
'''
# Left-shift response by one bit to match expectation
print("Discarding first bit of readback and evaluating next 32 bits:")
binstr = binstr[1:1+24]
print(binstr)
r = []
for i in range(3):
    r.append(int(binstr[i*8:i*8+8],2))
print("0x",end="")
for byte in r:
    print("{:02x}".format(byte),end="")
print()
'''
if (r[0]==0xc2 and r[1]==0x28 and r[2]==0x17):
    print("Found correct flash device ID!")
else:
    sys.exit("Wrong flash device ID detected, exiting...")

enable_gpios()

print("Done!")
