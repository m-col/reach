#!/usr/bin/env python3
"""
Delete the last session in a data file
======================================

This can be used if a small bit of extra time was given at the end of a
training session, but you don't want to include that extra data.
"""


import argparse
import os
import sys

from reach import Mouse


HOME = os.path.expanduser('~')


def parse_args():
    parser = argparse.ArgumentParser(description='Undo last session')

    parser.add_argument(
        '-m', '--mouse_id',
        help='Specify mouse_id',
        default=None,
        type=str
    )

    parser.add_argument(
        '-j', '--json_path',
        help='Path to folder containing training JSONs',
        default=f'{HOME}/CuedBehaviourAnalysis/Data/TrainingJSON',
        type=str
    )

    settings = parser.parse_args()
    if not settings.mouse_id or not settings.json_path:
        raise SystemError('Pass -h to see usage.')

    return settings

def main():
    settings = parse_args()

    mouse = Mouse.init_from_file(
        mouse_id=settings.mouse_id,
        json_path=settings.json_path
    )

    del mouse.training_data[-1]

    print(f"Deleting the last session for mouse ID: {settings.mouse_id}.")
    reply = input(f"Are you sure? [y/N] ").lower()

    if reply == 'y' or reply == 'yes':
        mouse.save_data_to_file(settings.json_path)


if __name__ == '__main__':
    main()
