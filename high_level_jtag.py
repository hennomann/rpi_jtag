#!/usr/bin/env python3

import sys
import math
from time import sleep
import jtag

####################################################
# Read device IDCODE and design USERCODE
####################################################

# Reset test access port
def TAP_RESET():
    jtag.enable_gpios()
    jtag.TLR_RTI()

####################################################
# Read device IDCODE and design USERCODE
####################################################
def read_IDCODE():
    # Read device IDCODE register
    jtag.enable_gpios()
    jtag.TLR_RTI()
    jtag.prep_shift_dr()
    jtag.disable_gpios()
    r = jtag.spi_read(4)
    binstr = ""
    for byte in r:
        binstr += "{:08b}".format(byte)
    binstr = binstr[::-1]
    id_hex = "0x{:08x}".format(int(binstr,2))
    print("IDCODE read from FPGA using SPI interface:\n" + id_hex)
    jtag.enable_gpios()
    return id_hex

# Read USERCODE only
def read_USERCODE():
    # Read USERCODE register
    jtag.enable_gpios()
    jtag.TLR_RTI()
    jtag.prep_shift_ir()
    jtag.load_instr("USERCODE")
    jtag.update_RTI()
    jtag.prep_shift_dr()
    jtag.disable_gpios() # Prepare using the hardware SPI interface
    r = jtag.spi_read(4)
    binstr = ""
    for byte in r:
        binstr += "{:08b}".format(byte)
    binstr = binstr[::-1]
    print("USERCODE read from device using SPI interface:\n0x{:08x}".format(int(binstr,2)))
    jtag.enable_gpios()


####################################################
# Program device via JTAG with bitstream in bitfile
####################################################
def program_device(bitfile):
    jtag.TLR_RTI()
    jtag.prep_shift_ir()
    jtag.load_instr("JPROGRAM")
    jtag.TLR_RTI()
    sleep(0.020) # Necessary wait time in this RTI according to manual (min 10ms)
    jtag.prep_shift_ir()
    jtag.load_instr("CFG_IN")
    jtag.update_RTI()
    jtag.prep_shift_dr()
    jtag.disable_gpios() # Prepare using the hardware SPI interface
    # Open bitfile and read bytes in binary mode:
    with open(bitfile,'rb') as f:
        data_raw = f.read()
    f.close()
    data = list(data_raw)
    pagecount = int((len(data)-1) / 256)
    bytes_last_page = (len(data)-1) % 256
    print("Starting to write bitstream data into FPGA:")
    # Send full pages of 256 bytes except for last page
    for i in range(pagecount):
        print("Writing page {:05d}/{:05d}\r".format(i,pagecount-1), end="")
        jtag.spi_send(data[i*256:i*256+256])
    print()
    # Send all but last byte of last page
    #print("Writing last page")
    if bytes_last_page > 0:
        jtag.spi_send(data[pagecount*256:pagecount*256+bytes_last_page])
    jtag.enable_gpios() # Back to GPIO mode for bitbanging of last byte
    #print("Writing last byte")
    jtag.gpio_send_last_byte(data[-1])
    jtag.update_RTI()
    print("Writing bitstream data finished")
    jtag.prep_shift_ir()
    jtag.load_instr("JSTART")
    jtag.update_RTI()
    jtag.disable_gpios()
    print("Restarting device")
    jtag.spi_read(256)
    jtag.enable_gpios()
    #read_USERCODE()

def program_device4k(bitfile):
    read_IDCODE()
    jtag.TLR_RTI()
    jtag.prep_shift_ir()
    jtag.load_instr("JPROGRAM")
    jtag.TLR_RTI()
    sleep(0.020) # Necessary wait time in this RTI according to manual (min 10ms)
    jtag.prep_shift_ir()
    jtag.load_instr("CFG_IN")
    jtag.update_RTI()
    jtag.prep_shift_dr()
    jtag.disable_gpios() # Prepare using the hardware SPI interface
    # Open bitfile and read bytes in binary mode:
    with open(bitfile,'rb') as f:
        data_raw = f.read()
    f.close()
    data = list(data_raw)
    pagecount = int((len(data)-1) / 256)
    bytes_last_page = (len(data)-1) % 256
    sector4kcount = int((len(data)-1) / 4096)
    pagesremaining = int(((len(data)-1) % 4096) / 256)
    print("Starting to write bitstream data")
    # Send full sectors of 4kB
    for i in range(sector4kcount):
        print("Writing sector {:05d}/{:05d}\r".format(i,sector4kcount-1), end="")
        jtag.spi_send(data[i*4096:i*4096+4096])
    print()
    # Send remaining pages
    start_remaining = sector4kcount*4096
    for i in range(pagesremaining):
        print("Writing remaing page {:05d}/{:05d}\r".format(i,pagesremaining-1), end="")
        jtag.spi_send(data[start_remaining+i*256:start_remaining+i*256+256])
    print()
    # Send all but last byte of last page
    print("Writing last page")
    if bytes_last_page > 0:
        jtag.spi_send(data[pagecount*256:pagecount*256+bytes_last_page])
    jtag.enable_gpios() # Back to GPIO mode for bitbanging of last byte
    print("Writing last byte")
    jtag.gpio_send_last_byte(data[-1])
    jtag.update_RTI()
    print("Writing bitstream data finished")
    jtag.prep_shift_ir()
    jtag.load_instr("JSTART")
    jtag.update_RTI()
    jtag.disable_gpios()
    print("Clocking in start sequence")
    jtag.spi_read(256)
    jtag.enable_gpios()
    read_USERCODE()
    print("Done!")


####################################################
# SPI flash access functions
####################################################

def enable_USERMODE1():
    # Enable TAP USERMODE1
    jtag.enable_gpios()
    jtag.TLR_RTI()
    jtag.prep_shift_ir()
    jtag.load_instr("USER1")
    jtag.update_RTI()
    jtag.prep_shift_dr()
    jtag.disable_gpios()

def flash_check_id():
    # Read flash device ID
    print("Reading flash device ID:")
    r=jtag.flash_read_id()
    print("0x",end="")
    for byte in r:
        print("{:02x}".format(byte),end="")
    print()
    # Check ID
    if (r[0]==0xc2 and r[1]==0x28 and r[2]==0x17):
        print("Found correct flash device ID, continuing...")
    else:
        sys.exit("Wrong flash device ID detected, exiting...")

def flash_erase():
    jtag.flash_write_enable()
    print("Starting flash erase:")
    jtag.flash_erase()
    i=0
    cnt = 0
    while True:
        sleep(1)
        r=jtag.flash_status()
        if r==0:
            print("Flash erase finished")
            break
        else:
            print("Still erasing"+"."*cnt+" "*(3-cnt)+"\r",end='')
            i=i+1
            cnt=(cnt+1)%4

def flash_program(data):    
    # Pad data to have a full last page
    pagecount = int(math.ceil(float(len(data))/256.))
    n_pad = pagecount * 256 - len(data)
    data += [0xff]*n_pad
    # Program flash page by page
    print("Starting flash loading:")
    for i in range(pagecount):
        addr = i*256
        print("Writing page {:05d}/{:05d}\r".format(i,pagecount-1), end="")
        jtag.flash_page_program3B(addr, data[addr:addr+256])
        sleep(0.001)
    print()
    print("Programming flash finished")

def flash_verify(data):
    print("Starting flash content verification:")
    pagecount = int(math.ceil(float(len(data))/256.))
    n_pad = pagecount * 256 - len(data)
    data += [0xff]*n_pad
    for i in range(pagecount):
        addr = i*256
        print("Reading page {:05d}/{:05d}\r".format(i,pagecount-1), end="")
        r=jtag.flash_read_page3B(addr)
        if list(r) != data[addr:addr+256]:
            print()
            print()
            print("Found bad flash content on page {:d}".format(i))
            print("Content of flash page:")
            print(list(r))
            print("Content of input bitstream page:")
            print(data[addr:addr+256])
            print()
            sys.exit("Verification failed! Exiting...")
    print()
    print("Flash content verified successfully!")












