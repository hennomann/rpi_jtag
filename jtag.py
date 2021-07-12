#!/usr/bin/env python3

import sys
from time import sleep
import RPi.GPIO as GPIO
import spidev

##############
# GPIO setup
##############

# GPIO pin mapping to JTAG / SPI interface
#        SPI PIN (connected via ~470R resistor so that GPIO state overrules SPI pin state)
TCK = 5  # SCLK
TMS = 6  # CS
TDI = 13 # MOSI - was 26, but realized that on KILOM1 schematic GPIO26 and GPIO13 are swapped
TDO = 19 # MISO

# Setup GPIO pins (default: enabled, overruling SPI pins)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TCK, GPIO.OUT)
GPIO.setup(TMS, GPIO.OUT)
GPIO.setup(TDI, GPIO.OUT)
GPIO.setup(TDO, GPIO.IN)
GPIO.output(TCK,0)
GPIO.output(TMS,1)
GPIO.output(TDI,1)
gpio_mode = 1

# Enable GPIO pins
def enable_gpios():
    GPIO.setup(TCK, GPIO.OUT)
    GPIO.setup(TMS, GPIO.OUT)
    GPIO.setup(TDI, GPIO.OUT)
    GPIO.output(TCK,0)
    GPIO.output(TMS,1)
    GPIO.output(TDI,1)
    global gpio_mode
    gpio_mode = 1

# Disable GPIO pins
def disable_gpios():
    GPIO.setup(TCK, GPIO.IN)
    GPIO.setup(TMS, GPIO.IN)
    GPIO.setup(TDI, GPIO.IN)
    global gpio_mode
    gpio_mode = 0    
    

###########################
# GPIO bitbanging functions
###########################

# Send TMS '0'
def TMS0():
    GPIO.output(TMS,0)
    GPIO.output(TCK,1)
    GPIO.output(TCK,0)
    GPIO.output(TMS,1)

# Send TMS 1
def TMS1():
    GPIO.output(TMS,1)
    GPIO.output(TCK,1)
    GPIO.output(TCK,0)

# Test-Logic-Reset
def TLR():
    GPIO.output(TMS,1)
    for i in range(5):
        GPIO.output(TCK,1)
        GPIO.output(TCK,0)

# Test-Logic-Reset & move into RTI
def TLR_RTI():
    GPIO.output(TMS,1)
    for i in range(5):
        GPIO.output(TCK,1)
        GPIO.output(TCK,0)
    GPIO.output(TMS,0)
    GPIO.output(TCK,1)
    GPIO.output(TCK,0)
    GPIO.output(TMS,1)

# Send 1 byte using GPIO bitbanging
# For bits[7:1] TMS = 0, for bit[0] TMS = 1 (last bit)
def gpio_send_last_byte(byte):
    enable_gpios()
    GPIO.output(TMS,0)
    for i in range(1,8)[::-1]: # bits[7:1]
        bit = (byte & (0b00000001 << i)) >> i
        GPIO.output(TDI,bit)
        GPIO.output(TCK,1)
        GPIO.output(TCK,0)
    # Last bit (TMS = 1)
    GPIO.output(TMS,1)
    GPIO.output(TDI, byte & 0b00000001)
    GPIO.output(TCK,1)
    GPIO.output(TCK,0)
    GPIO.output(TDI,1)
    
# Read n bits from TDO using GPIO bit banging (shifts in n clk cycles)
def gpio_read(n):
    GPIO.output(TMS,0)
    r = []
    for i in range(n):
        GPIO.output(TCK,1)
        r.append(GPIO.input(TDO))
        GPIO.output(TCK,0)
    return r

############################################
# Move functions assuming start in RTI state
############################################

# Move into SHIFT-DR state
def prep_shift_dr():
    msg = [1,0,0]
    for i in range(3):
        GPIO.output(TMS,msg[i])
        GPIO.output(TCK,1)
        GPIO.output(TCK,0)
    GPIO.output(TMS,1)
        
# Prepare loading of instruction
def prep_shift_ir():
    msg = [1,1,0,0]
    for i in range(4):
        GPIO.output(TMS,msg[i])
        GPIO.output(TCK,1)
        GPIO.output(TCK,0)
    GPIO.output(TMS,1)


####################
# Load instructions
####################

# JTAG instructions dictionary (needed LSB first -> reversed)
INSTR = { "JPROGRAM" : "001011"[::-1],
          "CFG_IN"   : "000101"[::-1],
          "JSTART"   : "001100"[::-1],
          "USERCODE" : "001000"[::-1],
          "USER1"    : "000010"[::-1],
         }

# Load instruction
def load_instr(instr_str):
    GPIO.output(TMS,0)
    msg = INSTR[instr_str]
    for i in range(5):
        GPIO.output(TDI,int(msg[i]))
        GPIO.output(TCK,1)
        GPIO.output(TCK,0)
    GPIO.output(TMS,1)
    GPIO.output(TDI,int(msg[5]))
    GPIO.output(TCK,1)
    GPIO.output(TCK,0)

# Update DR/IR and move to RTI state
def update_RTI():
    TMS1()
    TMS0()

    
##################################
# Hardware SPI interface functions
##################################
    
# Open SPI connection
def spi_open():
    try:
        spi_device = spidev.SpiDev()
        spi_device.open(0,0)
        spi_device.max_speed_hz = 10000000
        spi_device.mode = 0
    except Exception as e:
        print("Failed to open SPI connection")
        print(e.message, e.args)
        return
    return spi_device

# Open SPI device
device = spi_open()

# Send list of bytes via SPI
def spi_send(data):
    if gpio_mode == 1:
        raise NameError("GPIO mode needs to be disabled to use SPI interface, exiting...")
    device.xfer2(data)

# Read n bytes
def spi_read(n):
    if gpio_mode == 1:
        raise NameError("GPIO mode needs to be disabled to use SPI interface, exiting...")
    msg = [0x00]*n
    r = device.xfer2(msg)
    return r

##################################
# SPI flash functions (USERMODE1)
##################################

# Enter 4-byte address mode
def flash_enter_4b_am():
    msg = [0xb7]
    device.xfer2(msg)

# Exit 4-byte address mode
def flash_exit_4b_am():
    msg = [0xe9]
    device.xfer2(msg)

# Read flash status register
def flash_status():
    msg = [0x05,0x00,0x00]
    r = device.xfer2(msg)
    return r[2]

def flash_flag_status():
    msg = [0x70,0x00,0x00]
    r = device.xfer2(msg)
    #print(hex(r[1]))
    return r[2:]

# Read flash ID register
def flash_read_id():
    msg = [0x9f,0x00,0x00,0x00,0x00,0x00]
    r = device.xfer2(msg)
    return r[2:-1]

# Flash write enable command
def flash_write_enable():
    msg = [0x06]
    device.xfer2(msg)

# Flash erase command
def flash_erase():
    msg = [0x60]
    device.xfer2(msg)

# Flash 1 byte write operation (commands without payload)
def flash_write(cmd):
    msg = [0x00]
    msg[0] = cmd
    device.xfer2(msg)

# Flash 1 byte write operation (commands without payload)
def flash_page_program(addr,data):
    write_enable()
    msg = [0x02]
    msg += [((addr & 0xff000000) >> 24)]
    msg += [((addr & 0xff0000) >> 16)]
    msg += [((addr & 0xff00) >> 8)]
    msg += [(addr & 0xff)]
    for byte in data:
        msg += [byte]
    device.xfer2(msg)
    sleep(0.001)    

# Read back 1 page (256 bytes) from flash memory
def flash_read_page(addr):
    msg = [0x03]
    msg += [((addr & 0xff000000) >> 24)]
    msg += [((addr & 0xff0000) >> 16)]
    msg += [((addr & 0xff00) >> 8)]
    msg += [(addr & 0xff)]
    for i in range(256):
        msg += [0x00]
    r = device.xfer3(msg)
    return r[5:]

# Flash 1 byte write operation (commands without payload)
def flash_page_program3B(addr,data):
    write_enable()
    msg = [0x02]
    msg += [((addr & 0xff0000) >> 16)]
    msg += [((addr & 0xff00) >> 8)]
    msg += [(addr & 0xff)]
    for byte in data:
        msg += [byte]
    device.xfer2(msg)
    sleep(0.001)

# Read back 1 page (256 bytes) from flash memory
def flash_read_page3B(addr):
    msg = [0x03]
    msg += [((addr & 0xff0000) >> 16)]
    msg += [((addr & 0xff00) >> 8)]
    msg += [(addr & 0xff)]
    for i in range(256):
        msg += [0x00]
    r = device.xfer3(msg)
    return r[4:]
