#!/usr/bin/env python3
"""
Open or close the solenoids individually.
"""

from reach.backends.raspberrypi import Utilities

rpi = Utilities()
rpi.toggle_solenoids()
rpi.cleanup()
