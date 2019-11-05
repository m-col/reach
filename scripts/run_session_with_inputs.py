#!/usr/bin/env python3
"""
Run a training session, prefilling metadata with yesterday's entries
====================================================================

Pass the path to the folder containing training JSONs followed by the mouse ID
to start a training session. Extra information will be pre-filled from
yesterday's data and prompt the trainer to confirm or fill in updated
information.

Usage:
    ./run_session_with_inputs.py ~/TrainingJSONs Mouse123

Alternatively to not handle any data, using an anonymous mouse:
    ./run_session_with_inputs.py

"""


import os
import sys

from reach import Mouse


HOME = os.path.expanduser('~')
KEYS = ['trainer', 'weight', 'training_box', 'json_path']


def get_known_mouse(mouse_id, json_path):
    mouse = Mouse.init_from_file(
        mouse_id=mouse_id,
        json_path=json_path,
    )

    # get yesterday's metadata if it exists
    data = {}
    if len(mouse) > 1:
        for key in KEYS:
            if hasattr(mouse[-1], key):
                data.update({key: getattr(mouse[-1], key)})

    else:
        data['json_path'] = json_path

    # prompt for updated information
    for key in KEYS:
        if key in data:
            value = data[key]
            data[key] = input(f'Enter {key} [{value}]: ') or value
        else:
            data[key] = input(f'Enter {key}: ')

        if data[key] is None:
            return SystemError(f'Required metadata item: {key}')

    return mouse, data


def main():
    mouse_id = None
    if len(sys.argv) >= 2:
        json_path = sys.argv[2]
        mouse_id = sys.argv[2]

    config_file = f'{HOME}/reach_config.ini'
    config_file = input(f'Enter config_file [{config_file}]: ') or config_file

    if mouse_id:
        mouse, data = get_known_mouse(mouse_id, json_path)
        mouse.train(
            config_file=config_file,
            data=data,
            save_notes=True,
        )
        mouse.save_data_to_file(json_path)

    else:
        Mouse().train(
            config_file=config_file,
            save_notes=False,
        )


if __name__ == '__main__':
    main()
