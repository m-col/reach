#!/usr/bin/env python3
"""
Run a mock session using the curses interface.
==============================================
"""


import os

from reach import Mouse
from reach.curses import RPiCurses


HOME = os.path.expanduser('~')
config_file = f'{HOME}/reach_config.ini'

mouse = Mouse()

mouse.train(
    config_file=config_file,
    rpi=RPiCurses,
)

mouse.save_data_to_file()
