=========================
Training Box Construction
=========================

THIS IS A WORK IN PROGRESS

This page describes how to construct a single training box, which looks like
this:

#.. image:: /_static/training_box.jpg
#    :width: 420pt

The base holds a Raspberry Pi which runs the reach code and operates the
training box hardware.


Parts list
----------

For best touch sensor performance, the mice should be electrically contiguous
with a much larger mass of conductive material. The capacittive touch sensors
work well with the human finger but may become more erratic when a mouse is
interacting them. I found this is largely improved by building the training
boxes on a metal table and line conductive tape from where the mice sit to the
table.

3D printed parts:
`````````````````
- base with RIVETS head posts
- 2x RIVETS head bars
- spout mount with LED case lid
- spritzer mounter
- button box with lid

Raspberry Pi:
`````````````
- raspberry pi 4
- SD card flashed with raspbian lite
- power supply
- ethernet cable

Circuitry:
``````````
- prototyping board
- 4x touch sensors (proto-pic part #PPAC0012)
- 100 uF capacitor
- 3x momentary push buttons to fit button box (part number?)
- 2x small solenoid valves (part number?)
- 2x 1N4001 diodes
- 2x 2N2222 transistors
- 2x 3.9 KOhm resistor
- 2x 100 Ohm resistors
- 2x white LEDs (UPDATE)
- 4x 2x1 wire sockets (UPDATE)
- 2x 60 ml syringe
- 3.2 mm x 1.6 mm x 3M silicon tubing (UPDATE)
- 2x 1.1 x 40 mm (19G) syringe needle
- conductive tape (RS part 458-7416)
- plenty of wire

PuffAdder
`````````
Based on: http://raimondolab.com/2013/11/29/puffadder-picospritzer/
Part supplier: https://www.festo.com/cat/en-gb_gb/products

Festo Pressure Switch, R 1/8 0bar to 4 bar

- Festo Precision Pressure Regulator LRP-1/4-4 (Festo part 159501)
- Festo Precision Gauge MAP-40-4-1/8-EN (Festo part 162842)
- Solenoid Valve MHE2-M1H-3/2G-M7 (Festo part 196130)
- KMYZ-4-24-2.5-B (plug in cable for valve – not essential) (Festo part 193691)
- QSL-1/4-6 Festo Push-in/threaded L-fitting (Festo part 153047)
- QS-1/4-4 Festo Push-in fitting (Festo part 190644)
- 2x QSM-M7-4-I Festo Push-in fitting (Festo part 153319)
- 4mm OD Festo Plastic tubing (Festo part 159662)

Misc:
`````
- cable clips (RS part 475-198)
- 2x RIVETS bar thumb screws
- USB camera (RS part 125-4274)
- IR LEDs (led1.de part 58008450050) with 12V power supply (RS part 121-7157)
- three axis coarse manipulator or something else to mount the spouts
- optic fibres
- superglue
- a box to cover the rig during training (RS part 303-4781)


Steps
-----

#. Download this git repository onto the Raspberry Pi.
#. Add these lines to /boot/config.txt to disable LEDs:

 .. code-block::

    dtparam=eth_led0=14
    dtparam=eth_led1=14
    dtparam=pwr_led_trigger=none
    dtparam=pwr_led_activelow=off
    dtparam=act_led_trigger=none
    dtparam=act_led_activelow=off

3. Fix the base to the table with cable clips.
#. Fix the syringes to be higher than the base and attach around 1 metre of 
