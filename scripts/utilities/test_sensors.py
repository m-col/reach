#!/usr/bin/env python3
"""
Control the two solenoids using the two buttons.
"""


from reach.raspberry import UtilityPi


rpi = UtilityPi()
rpi.test_sensors()

input("Hit enter to finish.\n")

rpi.cleanup()
