#!/usr/bin/env python3
"""
Run a training session
"""


import argparse
import os

from reach import Mouse


home = os.path.expanduser('~')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run reach training session'
    )

    parser.add_argument(
        '-c', '--config_file',
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
        '-b', '--training_box',
        help='Specify training box',
        default=None,
        type=int
    )

    parser.add_argument(
        '-w', '--weight',
        help='Specify mouse weight',
        default=None,
        type=str
    )

    parser.add_argument(
        '-t', '--trainer',
        help='Specify trainer',
        default=None,
        type=str
    )

    parser.add_argument(
        '-j', '--json_path',
        help='Path to folder containing training JSONs',
        default=f'{home}/CuedBehaviourAnalysis/Data/TrainingJSON',
        type=str
    )

    settings =  parser.parse_args()
    if settings.config_file == 'None':
        settings.config_file = None

    return settings


settings = parse_args()


# add any necessary metadata
metadata = {}
for key in ['trainer', 'weight', 'training_box']:
    if getattr(settings, key):
        metadata.update({key: getattr(settings, key)})


if settings.mouse_id is None:
    # Instantiate anonymous mouse
    mouse = Mouse()

else:
    # Instantiate mouse from training JSON
    mouse = Mouse.init_from_file(
        mouse_id=settings.mouse_id,
        json_path=settings.json_path
    )


# Begin the training session
mouse.train(
    config_file=settings.config_file,
    metadata=metadata
)

mouse.save_data_to_file(settings.json_path)
