"""
Mock Backend
============

This backend is a text-only version backend that does nothing except print messages and
at times sleep to emulate a real raspberry pi backend.

"""


import time

from .. import Backend


class Mock(Backend):
    """
    A mock instance of a raspberry pi and its GPIO pins.
    """

    def wait_to_start(self):
        """
        Print start message and wait for enter key.
        """
        input("Press enter to begin.\n")

    def wait_for_rest(self):
        """
        Print waiting message.
        """
        print("Waiting for rest... ")
        time.sleep(1)

    def start_trial(self, spout_number):
        """
        Inform of cue illumination.
        """
        print("Cue illuminated")

    def dispense_water(self, spout_number):
        """
        Pretend to dispense water from a specified spout.
        """
        time.sleep(0.050)
