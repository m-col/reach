#!/usr/bin/env python3
"""
Delete the last session in a data file
======================================

This example shows how to manipulate previously collected data, in this case deleting
the last session. This can be useful if extra time is given to a mouse, as an additional
'session', but the data is not wanted.
"""


import argparse
import os

from reach import Mouse


HOME = os.path.expanduser('~')


# Pass mouse and data_dir as arguments to script
parser = argparse.ArgumentParser(description='Undo last session')
parser.add_argument(
    '-m', '--mouse_id',
    default=None, type=str
    help='Specify mouse_id',
)
parser.add_argument(
    '-d', '--data_dir',
    default=f'{HOME}/reach_data', type=str
    help='Path to folder containing training JSONs',
)
settings = parser.parse_args()


# Instantiate Mouse from existing data
mouse = Mouse.init_from_file(
    data_dir=settings.data_dir,
    mouse_id=settings.mouse_id,
)


# Delete last session and save to file
del mouse.training_data[-1]

print(f"Deleting the last session for mouse ID: {settings.mouse_id}.")
reply = input(f"Are you sure? [y/N] ").lower()

if reply.startswith('y'):
    mouse.save_data_to_file(settings.data_dir)
