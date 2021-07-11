#!/usr/bin/env python3

from high_level_jtag import *
from jtag import spi_send
from time import sleep

#read_IDCODE()

print("Enabling USERMODE1")

TLR_RTI()
prep_shift_ir()
load_instr("USER1")
update_RTI()
prep_shift_dr()
disable_gpios()

spi_send([0x55])

enable_gpios()

print("Done")
