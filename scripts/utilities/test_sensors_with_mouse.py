#!/usr/bin/env python3
"""
Print touch sensor events, and allow for dispensing water upon press of buttons 1 and 2.
"""


from reach.backends.raspberrypi import Utilities


rpi = Utilities()
rpi.test_reward_volume()
rpi.test_sensors()

input("Hit enter to finish.\n")

rpi.cleanup()
