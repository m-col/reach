#!/usr/bin/env python3
"""
Run a mock session
==================
"""


from reach import Mouse
from reach.backends.mock import Mock
from reach.session import print_results


# Basic settings
mouse_id = 'Mouse1'
training_box = 1
weight = '21.0'
trainer = 'matt'
data_dir = '/home/mcol/reach_data'


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
    Mock(),
    additional_data=metadata,
    duration=30,
    intertrial_interval=(400, 600),
)

# Collect some extra notes
notes = input('Add any training notes:\n')
if notes:
    mouse[-1].add_data({'notes': notes})

# Ignore this session's data if we pass 'rm' into the notes
if notes == 'rm':
    print('Not saving new training data.')

else:
    if len(mouse[-1].data['trials']) == 0:
        confirm = input('There were no new trials. Still save data? [Y/n]')
        if confirm != 'n':
            mouse.save_data_to_file(data_dir)
    else:
        mouse.save_data_to_file(data_dir)

# Print remaining water that mouse requires
reward_count = mouse[-1].reward_count
print_results(mouse[-1])
print(f'1000 uL - {reward_count} * 6 uL = {1000 - reward_count * 6} uL')
