=========================
Training Box Construction
=========================

This page describes how to construct a single training box, which looks like
this:

.. image:: /_static/images/training_box.png
    :width: 420pt

The base holds a Raspberry Pi which runs the reach code and operates the
training box hardware.

The circuit design was done in `fritzing <https://fritzing.org/home>`_. The
design file is :download:`here </pi_hat_circuit.fzz>` to be used as reference
during construction.


Parts list
----------

3D printed parts:
"""""""""""""""""

- base
- 2x RIVETS head bars
- LED case per target spout
- button box

Raspberry Pi:
"""""""""""""

- power supply
- SD card flashed with raspbian lite
- ethernet cable

Circuitry:
""""""""""

- Adafrauit Perma-Proto HAT for Pi
- 4x touch sensors (proto-pic part #PPAC0012)
- 100 uF capacitor
- 2x momentary push buttons to fit button box
- 2x small solenoid valves
- 2x 1N4001 diodes
- 2x 2N2222 transistors
- 2x 3.9 KOhm resistor
- 2x 100 Ohm resistors
- 2x white LEDs
- 4x 2x1 wire sockets
- 2x 50 ml syringe
- 3.2 mm x 1.6 mm x 3M silicon tubing
- 2x 1.1 x 40 mm (19G) syringe needle
- conductive foil tape
- plenty of wire

Misc:
"""""

- 2x RIVETS bar thumb screws
- USB camera
- three axis coarse manipulator or something else to mount the spouts
- optic fibres
- superglue
- a box to cover the rig during training
- black paint (optional)


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

3. text
#. text
