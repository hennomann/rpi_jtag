#!/usr/bin/env python3

import sys
from time import sleep
import RPi.GPIO as GPIO
import spidev

# GPIO pin mapping to JTAG interface
TCK = 5
TMS = 6
TDI = 26
TDO = 19

# JTAG instructions dictionary (needed LSB first -> reversed)
INSTR = { "JPROGRAM" : "001011"[::-1],
          "CFG_IN" : "000101"[::-1],
          "JSTART" : "001100"[::-1],
         }

# Setup GPIO pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TCK, GPIO.IN)  # TCK
GPIO.setup(TMS, GPIO.IN)  # TMS 
GPIO.setup(TDI, GPIO.IN) # TDI
GPIO.setup(TDO, GPIO.IN) # TDO
gpio_mode = 0

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
    

##################################
# Hardware SPI interface functions
##################################
    
# Open SPI connection
def spi_open():
    try:
        spi_device = spidev.SpiDev()
        spi_device.open(0,0)
        spi_device.max_speed_hz = 1000000
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

