#!/usr/bin/python3
#
# Python commands for interactive testing of the circuitry
#
# Start a python interpreter in the root reach directory and send it
# command from here
#


## Stepper motor control using gertbot ##
import gertbot

BOARD = 3
CHANNEL = 0
MODE  = 24
FREQ = 900.0
STEPS = 200

gertbot.open_uart(0)
gertbot.set_mode(BOARD, CHANNEL, MODE)
gertbot.freq_stepper(BOARD, CHANNEL, FREQ)

gertbot.move_stepper(BOARD, CHANNEL, STEPS)
gertbot.move_stepper(BOARD, CHANNEL, -STEPS)

gertbot.stop_all()


## Solenoid ##
import RPi.GPIO as GPIO
from time import sleep

pin = 16
reward_ms = 1000
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT, initial=False)

def test():
    GPIO.output(pin, True)
    sleep(reward_ms / 1000)
    GPIO.output(pin, False)


