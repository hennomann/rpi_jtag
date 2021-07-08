#!/usr/bin/env python3
import os
import sys
import math
import struct
import RPi.GPIO as GPIO
import spidev

from time import sleep

device = spidev.SpiDev()
device.open(0,0)
device.max_speed_hz = 10000000
device.mode = 0

device.bits_per_word = 8

msg = [0x5A]

device.xfer2(msg)
