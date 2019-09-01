#!/usr/bin/env python3
"""

Run training session
====================

"""


import argparse
import os

from reach import Mouse, Session


home = os.path.expanduser('~')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run reach training session'
    )

    parser.add_argument(
        '-c', '--config',
        help='Select training configuration file',
        default=f'{home}/reach_config.ini',
        type=str
    )

    parser.add_argument(
        '-m', '--mouse_id',
        help='Specify mouse_id',
        default='',
        type=str
    )

    parser.add_argument(
        '-j', '--json_dir',
        help='Path to folder containing training JSONs',
        default=f'{home}/CuedBehaviourAnalysis/Data/TrainingJSON',
        type=str
    )

    parser.add_argument(
        '-M', '--merge',
        help='Merge data with last entry in training JSON',
        action='store_true'
    )

    settings =  parser.parse_args()
    return settings.config, settings.mouse_id, settings.json_dir, settings.merge


config_file, mouse_id, json_dir, merge = parse_args()


if os.path.isdir(json_dir):
    json_path = os.path.join(json_dir, f'{mouse_id}.json')
else:
    json_path = json_dir


mouse = Mouse.init_from_file(
    mouse_id=mouse_id,
    json_path=json_path
)

mouse.train(config_file)
