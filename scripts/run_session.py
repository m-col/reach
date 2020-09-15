#!/usr/bin/env python3
"""
Run a training session
======================

This script shows an example of how a training session can be run.
"""


import functools

from reach import Mouse
from reach.session import print_results
from reach.backends.raspberrypi import RaspberryPi


# Basic settings
mouse_id = 'Mouse1'
training_box = 1
weight = '21.0'
trainer = 'matt'
data_dir = '/home/pi/reach_data'


# Instantiate Mouse from existing data
mouse = Mouse.init_from_file(
    data_dir=data_dir,
    mouse_id=mouse_id,
)

# Additional metadata
metadata = {
    'trainer': trainer,
    'weight': weight,
    'training_box': training_box,
}

# Begin the training session
mouse.train(
    RaspberryPi(reward_duration=0.070),  # raspberry pi backend
    additional_data=metadata,
    duration=1800,
    intertrial_interval=(4000, 6000),
    hook=functools.partial(mouse.save_data_to_file, '/tmp'),
)

# Collect some extra notes
notes = input('Add any training notes:\n')
if notes:
    mouse[-1].add_data({'notes': notes})

# Ignore this session's data if we pass 'rm' into the notes
if notes == 'rm':
    print('Not saving new training data.')

else:
    trials = mouse[-1].data['trials']
    if trials and 'outcome' in trials[0]:
        mouse.save_data_to_file(data_dir)
    else:
        confirm = input('There were no new trials. Still save data? [Y/n]')
        if confirm != 'n':
            mouse.save_data_to_file(data_dir)

print_results(mouse[-1])

# Print remaining water that mouse requires
reward_count = mouse[-1].reward_count
print(f'1000 uL - {reward_count} * 6 uL = {1000 - reward_count * 6} uL')
