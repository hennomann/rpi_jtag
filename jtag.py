#!/usr/bin/env python3

import sys
from time import sleep
import RPi.GPIO as GPIO
import spidev

# Setup GPIO pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)  # TCK
GPIO.setup(6, GPIO.IN)  # TMS 
GPIO.setup(26, GPIO.IN) # TDI
GPIO.setup(19, GPIO.IN) # TDO
gpio_mode = 0

# Enable GPIO pins
def enable_gpios():
    GPIO.setup(5, GPIO.OUT)
    GPIO.setup(6, GPIO.OUT)
    GPIO.setup(26, GPIO.OUT)
    GPIO.output(5,0)
    GPIO.output(6,1)
    GPIO.output(26,1)
    global gpio_mode
    gpio_mode = 1

# Disable GPIO pins
def disable_gpios():
    GPIO.setup(5, GPIO.IN)
    GPIO.setup(6, GPIO.IN)
    GPIO.setup(26, GPIO.IN)
    global gpio_mode
    gpio_mode = 0

# Test-Logic-Reset
def TLR():
    GPIO.output(6,1)
    for i in range(5):
        GPIO.output(5,1)
        GPIO.output(5,0)

# Prepare loading of instruction
def prep_shift_dr():
    TLR()
    # -> RTI -> SEL-IR -> SHIFT-IR
    msg = [0,1,0,0]
    for i in range(4):
        GPIO.output(6,msg[i])
        GPIO.output(5,1)
        GPIO.output(5,0)
    GPIO.output(6,1)
        
# Prepare loading of instruction
def prep_instr():
    TLR()
    # -> RTI -> SEL-IR -> SHIFT-IR
    msg = [0,1,1,0,0]
    for i in range(5):
        GPIO.output(6,msg[i])
        GPIO.output(5,1)
        GPIO.output(5,0)
    GPIO.output(6,1)

def gpio_shift(n):
    GPIO.output(6,0)
    for i in range(n):
        GPIO.output(5,1)
        GPIO.output(5,0)

def gpio_read(n):
    GPIO.output(6,0)
    r = []
    for i in range(n):
        GPIO.output(5,1)
        r.append(GPIO.input(19))
        GPIO.output(5,0)
    return r

# Load IDCODE instruction
def load_IDCODE_instr():
    GPIO.output(6,0)
    msg = [0,0,1,0,0,1]
    msg.reverse()
    for i in range(5):
        GPIO.output(5,0)
        GPIO.output(26,msg[i])
        GPIO.output(5,1)
    GPIO.output(5,0)
    GPIO.output(6,1)
    GPIO.output(26,msg[5])
    GPIO.output(5,1)
    GPIO.output(6,0)

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

# Read n bytes
def spi_read(n):
    if gpio_mode == 1:
        raise NameError("GPIO mode needs to be disabled to use SPI interface, exiting...")
    msg = [0x00]*n
    r = device.xfer2(msg)
    return r

