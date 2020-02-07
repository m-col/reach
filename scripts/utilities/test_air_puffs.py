#!/usr/bin/env python3
"""
Trigger air puffs upon press of button 1.
"""


from reach.backends.raspberrypi import Utilities


rpi = Utilities()
rpi.test_air_puffs()

input("Hit enter to finish.\n")

rpi.cleanup()
