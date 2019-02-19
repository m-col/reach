#!/usr/bin/python3

#################################################################
#  stepper.py - Stepper motor control using Gertbot and Python  #
#  Based on Gertbot example code at http://www.gertbot.com/     #
#################################################################

# Use the Gertbot drivers
import gertbot as gb

# Using curses to repond to single keyboard keys
import curses

# This is for the development environment:
BOARD = 0           # which board we talk to
STEPPER_A = 0       # channel for first stepper motor
STEPPER_B = 2       # channel for second stepper motor
MODE  = 24          # stepper control, gray code
FREQ = 900.0        # frequency

# Main program

# Get the curses screen
screen = curses.initscr()

# Open serial port to talk to Gertbot
gb.open_uart(0)

# Setup the channels for stepper motors
gb.set_mode(BOARD,STEPPER_A,MODE)
gb.set_mode(BOARD,STEPPER_B,MODE)
gb.freq_stepper(BOARD,STEPPER_A,FREQ)
gb.freq_stepper(BOARD,STEPPER_B,FREQ)

# Tell user what to expect
screen.addstr("Stepper motor control with Gertbot and python\n")
screen.addstr("\n")
screen.addstr("Press U to go up, D to go down, Q to quit\n")
screen.addstr("\n")

run = 1
while run==1 :
    key = screen.getch() # Key?

    if key==ord('q') :
        run = 0 # stop running

    if key==ord('u') :
        gb.move_stepper(BOARD,STEPPER_A,200) # 200 steps, or one revolution
        gb.move_stepper(BOARD,STEPPER_B,200) # 200 steps, or one revolution

    if key==ord('d') :
        gb.move_stepper(BOARD,STEPPER_A,-200)
        # 200 steps, or one revolution
        gb.move_stepper(BOARD,STEPPER_B,-200)
        # 200 steps, or one revolution

# on exit stop everything
gb.emergency_stop()

# Set terminal behaviour normal again
curses.endwin()
