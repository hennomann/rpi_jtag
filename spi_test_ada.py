#!/usr/bin/env python3
import os
import sys
import math
import struct
import RPi.GPIO as GPIO
#import spidev
import Adafruit_PureIO.spi 

from time import sleep

spi = Adafruit_PureIO.spi.SPI("/dev/spidev0.0",max_speed_hz=10000000,bits_per_word=8)

#spi.SPI.writebytes("HALLO",max_speed_hz=10000000,bits_per_word=8)
val = 0xA
bytes = val.to_bytes(length=1,byteorder="little")
spi.writebytes( bytes )


#device = spidev.SpiDev()
#device.open(0,0)
#device.max_speed_hz = 10000000
#device.mode = 0

#device.bits_per_word = 8

#msg = [0x5A]

#device.xfer2(msg)
