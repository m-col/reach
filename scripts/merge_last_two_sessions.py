#!/usr/bin/env python3
"""
Merge two sessions in a training file
=====================================

This example shows how to manipulate previously collected data, in this case merging two
sessions. This can be useful if further training is given to a mouse after a session has
finished, but you want to count them as one session.
"""


import argparse
import os

from reach import Mouse


HOME = os.path.expanduser('~')


# Pass mouse and data_dir as arguments to script
parser = argparse.ArgumentParser(description='Merge two sessions')
parser.add_argument('-m', '--mouse_id', type=str, help='Specify mouse_id')
parser.add_argument('-1', '--session_1', type=int, help='Session to keep everything')
parser.add_argument('-2', '--session_2', type=int, help='Session to take data from')
parser.add_argument(
    '-d', '--data_dir', default=f'{HOME}/reach_data', type=str,
    help='Path to folder containing training JSONs',
)
settings = parser.parse_args()


# Instantiate Mouse from existing data
mouse = Mouse.init_from_file(
    data_dir=settings.data_dir,
    mouse_id=settings.mouse_id,
)
session1 = mouse[settings.session_1]
session2 = mouse[settings.session_2]

# Display some information
print(f"Dates: {session1.data['date']} and {session2.data['date']}")
print(f"Start times: {session1.data['start_time']} and {session2.data['start_time']}")
print(f"End times: {session1.data['end_time']} and {session2.data['end_time']}")
print(f"Notes: '{session1.data['notes']}' and '{session2.data['notes']}'")
print(len(mouse))

# Merge two sessions
session1.data['trials'].extend(session2.data['trials'])
session1.data['resets'].extend(session2.data['resets'])
session1.data['spontaneous_reaches'].extend(session2.data['spontaneous_reaches'])

print("Which notes would you like to keep?")
reply = input("Please type '1', '2', or some new notes: ")
if reply == "2":
    session1.data['notes'] = session2.data['notes']
elif reply != "1":
    session1.data['notes'] = reply

del mouse.data[settings.session_2]
print(len(mouse))

reply = input(f"Are you sure? [y/N] ").lower()
if reply.startswith('y'):
    mouse.save_data_to_file(settings.data_dir)
