#!/usr/bin/env python3
"""
Toggle the LEDs.
"""

from reach.backends.raspberrypi import Utilities

rpi = Utilities()
rpi.toggle_spout_leds()
rpi.cleanup()
