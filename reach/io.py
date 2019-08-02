#!/usr/bin/env python3
""" Helper functions to handle user input, parameters and file processing """


import argparse, configparser, json, sys, time
from os.path import isfile, join


def parse_args():
    """ Parse command line arguments """

    parser = argparse.ArgumentParser(
            description = 'mouse reach behavioural task sequencer'
            )

    parser.add_argument(
            '-c', '--config',
            help='Select configuration file',
            default='',
            type=str
            )

    parser.add_argument(
            '-g', '--generate_config',
            help='Generate a new configuration file',
            action='store_true'
            )

    parser.add_argument(
            '-n', '--no-data',
            help='Disable data collection',
            action='store_true'
            )

    parser.add_argument(
            '-m', '--mouseID',
            help='Specify mouseID',
            default='',
            type=str
            )

    parser.add_argument(
            '-u', '--utility',
            help='Use a utility. Pass \'list\' to list options',
            default='',
            type=str
            )

    parser.add_argument(
            '-d', '--debug',
            help='Run in debugging mode',
            default='',
            action='store_true'
            )

    args = parser.parse_args()
    return args



def default_config():
    """ Create configuration structure with default values """
    config = configparser.RawConfigParser()

    config.add_section('Settings')
    config.set('Settings', 'duration',      '1800')
    config.set('Settings', 'spout_count',   '1')
    config.set('Settings', 'reward_ms',     '300')
    config.set('Settings', 'cue_ms',        '10000')
    config.set('Settings', 'ITI_min_ms',    '4000')
    config.set('Settings', 'ITI_max_ms',    '6000')
    config.set('Settings', 'shaping',       'False')
    config.set('Settings', 'json_dir',
            '/home/pi/CuedBehaviourAnalysis/Data/TrainingJSON')

    return config



def read_config(config, config_file):
    """ Read parameters from a config file and error if required """
    try:
        config.read(config_file)
    except configparser.MissingSectionHeaderError:
        print("%s is an invalid config file." % config_file)
        sys.exit(1)

    return config



def generate_config(config, config_file):
    """ Write configuration to file  """

    if isfile(config_file):
        print("Config file %s already exists." % config_file)
        confirm = input("Overwrite? (y/N) ")
        if not confirm in ['y', 'Y']:
            sys.exit(1)
            
    with open(config_file, 'w') as new_file:
        config.write(new_file)
    print("A new config file has been generated as %s." % config_file)



def enforce_suffix(suffix, string):
    """ Append suffix to string if not present """
    if not string.endswith(suffix):
        string = string + suffix

    return string



def request_metadata(mouseID, json_dir):
    """ Request metadata from user and load previous metadata """

    if not mouseID:
        mouseID = input("Enter mouse ID: ") or 'Mouse'

        if not mouseID:
            print("Please enter a mouse ID at the prompt or by passing -m <mouseID>")
            print("Alternatively pass -n to ignore data")
            sys.exit(1)

    date = time.strftime('%Y-%m-%d')
    data_file = join(json_dir, mouseID + '.json')
    data = {}

    if isfile(data_file):
        print("Found pre-existing training JSON for %s" % mouseID)
        with open(data_file) as json_file:
            try:
                prev_data = json.load(json_file)
                data['day'] = prev_data[-1]['day'] + 1

                prev_trainer = prev_data[-1]['trainer']
                data['trainer'] = input("Enter trainer (%s): " %
                        prev_trainer) or prev_trainer

                prev_weight = prev_data[-1]['weight']
                data['weight'] = input("Enter weight (%s): " %
                        prev_weight) or prev_weight

                prev_training_box = prev_data[-1]['box']
                data['box'] = input("Enter training box (%s): " %
                        prev_training_box) or prev_training_box
            except:
                print("Something appears to be wrong with %s" % data_file)
                sys.exit(1)

    else:
        print("This will generate a new training JSON for %s" % mouseID)
        data['day'] = 1
        data['trainer'] = input("Enter trainer: ") or 'matt'
        data['weight'] = input("Enter weight: ") or '?'
        data['box'] = input("Enter training box (1): ") or 1

    data['prewatering'] = input("Enter prewatering volume (0): ") or '0'

    return data, mouseID



def write_data(mouseID, json_dir, data):
    """ Write data to JSON file """
    data_file = join(json_dir, mouseID + '.json')

    if data['day'] == 1:
        # creating new JSON
        data = [data]
        with open(data_file, 'w') as output:
            json.dump(data, output, indent=4)

    else:
        # appending to existing data
        with open(data_file) as json_file:
            prev_data = json.load(json_file)

        prev_data.append(data)

        with open(data_file, 'w') as json_file:
            json.dump(prev_data, json_file, indent=4)

    print("Data was saved in:\n     %s" % data_file)
