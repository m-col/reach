#!/usr/bin/env python3
"""
Dispense a fixed volume (by time) of water from the spouts.
"""

from reach.backends.raspberrypi import Utilities

rpi = Utilities(reward_duration=0.070)
rpi.enabled_leds()
rpi.dispense_reward_volume()
rpi.cleanup()
