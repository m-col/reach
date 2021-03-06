#!/usr/bin/env python3
"""
Move the two spout linear actuators.
"""

from reach.backends.raspberrypi import Utilities

rpi = Utilities()
rpi.step_actuators()
rpi.cleanup()
