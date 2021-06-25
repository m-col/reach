#!/usr/bin/env python3
"""
Open or close the solenoids individually.
"""

from reach.backends.raspberrypi import Utilities

rpi = Utilities()
rpi.enable_leds()
rpi.toggle_solenoids()
rpi.cleanup()
