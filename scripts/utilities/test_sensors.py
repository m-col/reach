#!/usr/bin/env python3
"""
Print out when touch sensors are touched.
"""

from reach.backends.raspberrypi import Utilities

rpi = Utilities()
rpi.test_sensors()
rpi.cleanup()
