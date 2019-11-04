#!/usr/bin/env python3
"""
Run a training session.
=======================

argparse is used to provide extra information about the Session before
beginning training.

"""


import argparse
import os
import sys

from reach import Mouse


HOME = os.path.expanduser('~')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run reach training session'
    )

    parser.add_argument(
        '-c', '--config_file',
        help='Select training configuration file',
        default=f'{HOME}/reach_config.ini',
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
        default=f'{HOME}/CuedBehaviourAnalysis/Data/TrainingJSON',
        type=str
    )

    settings = parser.parse_args()
    if settings.config_file == 'None':
        settings.config_file = None

    return settings


settings = parse_args()


# add any necessary data
data = {}
for key in ['trainer', 'weight', 'training_box']:
    if getattr(settings, key):
        data.update({key: getattr(settings, key)})


if settings.mouse_id:
    # Instantiate mouse from training JSON
    mouse = Mouse.init_from_file(
        mouse_id=settings.mouse_id,
        json_path=settings.json_path
    )

else:
    # Instantiate anonymous mouse
    mouse = Mouse()


# Begin the training session
mouse.train(
    config_file=settings.config_file,
    data=data,
    save_notes=True if settings.mouse_id else False,
)


# Ignore this session's data if we pass 'rm' into the notes
notes = mouse.training_data[-1].data['notes']
if notes == 'rm':
    print('Not saving new training data.')
elif: settings.mouse_id is not None:
    mouse.save_data_to_file(settings.json_path)


# Print remaining water that mouse requires
reward_count = mouse.training_data[-1].reward_count
print(f'\n1000 uL - {reward_count} * 6 uL = {1000 - reward_count * 6} uL')
