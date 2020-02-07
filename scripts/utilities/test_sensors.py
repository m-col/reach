#!/usr/bin/env python3
"""
Control the two solenoids using the two buttons.
"""


from reach.backends.raspberrypi import Utilities


rpi = Utilities()
rpi.test_sensors()

input("Hit enter to finish.\n")

rpi.cleanup()
