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
        default=None,
        type=str
    )

    parser.add_argument(
        '-j', '--json_dir',
        help='Path to folder containing training JSONs',
        default=f'{home}/CuedBehaviourAnalysis/Data/TrainingJSON',
        type=str
    )

    settings =  parser.parse_args()
    if settings.config == 'None':
        settings.config = None

    return settings.config, settings.mouse_id, settings.json_dir


config_file, mouse_id, json_dir = parse_args()


if os.path.isdir(json_dir):
    json_path = os.path.join(json_dir, f'{mouse_id}.json')
else:
    json_path = json_dir


mouse = Mouse.init_from_file(
    mouse_id=mouse_id,
    json_path=json_path
)
mouse.train(config_file)
mouse.save_data_to_file(json_path)
