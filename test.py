#!/usr/bin/env python3
import RPi.GPIO as GPIO
import threading
from time import sleep, time, strftime

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#while True:
#    sleep(0.01)
#    GPIO.input(touch)

def func(pin):
    print(pin)

touch = 25

#GPIO.setup(touch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(touch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch, GPIO.IN)

GPIO.add_event_detect(touch, GPIO.BOTH, callback=func, bouncetime=100)

#GPIO.remove_event_detect(touch)
#GPIO.wait_for_edge(touch, GPIO.FALLING)

print("ok")
sleep(5000)

