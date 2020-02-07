#!/usr/bin/env python3
"""
Control the two solenoids using the two buttons.
"""


from reach.backends.raspberrypi import Utilities


rpi = Utilities()
rpi.hold_open_solenoid()

input("Hit enter to finish.\n")

rpi.cleanup()
