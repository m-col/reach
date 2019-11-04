#!/usr/bin/env python3
"""
Trigger air puffs upon press of button 1.
"""


from reach.raspberry import UtilityPi


rpi = UtilityPi()
rpi.test_air_puffs()


input("Hit enter to finish.\n")