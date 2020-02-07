#!/usr/bin/env python3
"""
Control the two solenoids using the two buttons.
"""


from reach.backends.raspberrypi import Utilities


rpi = Utilities()
rpi.toggle_spout_leds()

input("Hit enter to finish.\n")

rpi.cleanup()
