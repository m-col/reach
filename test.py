#!/usr/bin/env python3
import RPi.GPIO as GPIO
import threading
from time import sleep, time, strftime

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


##while True:
##    sleep(0.01)
##    GPIO.input(touch)
#
#def func(pin):
#    print(pin)
#
#touch = 25
#
#
##GPIO.setup(touch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
##GPIO.setup(touch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(touch, GPIO.IN)
#
#GPIO.add_event_detect(touch, GPIO.BOTH, callback=func, bouncetime=100)
#
##GPIO.remove_event_detect(touch)
##GPIO.wait_for_edge(touch, GPIO.FALLING)
#
#print("ok")
#sleep(5000)


# stepper motor

LED = 5
GPIO.setup(LED, GPIO.OUT, initial=False)

# dir True is clockwise
motor_dir = 6
GPIO.setup(motor_dir, GPIO.OUT)

# step is pulsed to move
motor_step = 12
GPIO.setup(motor_step, GPIO.OUT)

# step size settings
EN  = 21
MS1 = 20
MS2 = 19
MS3 = 16
GPIO.setup([MS1, MS2, MS3], GPIO.OUT, initial=False)
GPIO.setup(EN, GPIO.OUT, initial=False)

# motor is 400 steps per revolution
spr = 400

pulse_width = 0.020

GPIO.output(motor_dir, True)

for i in range(40):
    GPIO.output(motor_step, True)
    GPIO.output(LED, True)
    sleep(pulse_width)
    GPIO.output(motor_step, False)
    GPIO.output(LED, False)
    sleep(pulse_width)

GPIO.cleanup() 
