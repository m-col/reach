#!/usr/bin/env python3
"""
Control the two solenoids using the two buttons.
"""


from reach.raspberry import UtilityPi


rpi = UtilityPi()
rpi.hold_open_solenoid()


input("Hit enter to finish.")
