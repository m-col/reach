#!/usr/bin/env python3
"""
Move the two spout linear actuators.
"""


from reach.raspberry import UtilityPi


rpi = UtilityPi()
rpi.test_actuators()

input("Hit enter to finish.\n")

rpi.cleanup()
