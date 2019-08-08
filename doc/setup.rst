Mouse Reach Task Training Rig Setup
===================================


Parts list
**********

3D printed parts:

Raspberry pi 4:

    - power supply
    - raspbian on SD card
    - ethernet cable

Touch sensors (per paw rest and spout):

    - 220 ohm + 270 ohm resistor
    - 2N2222 transistor
    - 1x 1x1 wire socket

Spouts (per spout):

    - 3.2 mm x 1.6 mm x 3M silicon tubing
    - 1.1 x 40 mm (19G) syringe needle, with plastic trimmed to fit into tubing
    - 1x solenoid with a pair of pins soldered to wire ends
    - 1x 1N4001 diode
    - 1x 2N2222 transistor
    - 1x 3.9 KOhm resistor
    - 1x LED with 100 Ohm resistor in series, long wires
    - 2x 2x1 wire sockets
    - 50 ml syringe

Misc:
    - perma-proto pi hat
    - conductive foil tape
    - 100 uF capacitor
    - 2x RIVETS bar thumb screws
    - USB camera
    - Momentary button with ~15 cm wires ending in pair of pins for start button


Raspberry Pi Setup
******************

1. Flash SD card with raspbian lite
2. Connect mouse, keyboard and monitor and boot
3. Set passwords for pi and root users
4. Run raspi-config and enable automatic login as user pi, and set locale to en_US.UTF-8 
5. Get IS to assign static IP to mac address
8. Edit /etc/dhcpcd.conf to show and then restart dhcpcd:

    interface eth0
    static ip_address=<IP address assigned by IS>/23
    #static ip6......
    static routers=172.19.83.254

14. Create /etc/apt/apt.conf.d/80proxy containing:

    Acquire::https {
	Proxy "https://wwwcache.ed.ac.uk:3128";
    }
    Acquire::http {
	Proxy "http://wwwcache.ed.ac.uk:3128";
    }

7. apt-get update and upgrade
9. git clone https://github.com/DuguidLab/reach.git
11. Add to /boot/config.txt:

    dtoverlay=pi3-disable-bt
    dtoverlay=pi3-disable-wifi
    enable_uart=1
    dtparam=eth_led0=14
    dtparam=eth_led1=14
    dtparam=pwr_led_trigger=none
    dtparam=pwr_led_activelow=off
    dtparam=act_led_trigger=none
    dtparam=act_led_activelow=off

12. Add to /etc/rc.local (possibly unneeded):

    echo none > /sys/class/leds/led0/trigger
    echo none > /sys/class/leds/led1/trigger
    echo 0 > /sys/class/leds/led0/brightness
    echo 0 > /sys/class/leds/led1/brightness

15. Add to ~/.zshrc:

    export https_proxy=wwwcache.ed.ac.uk:3128
    export http_proxy=$https_proxy

16. Optionally install zsh ranger vim and any other useful tools
17. Reboot and test connectivity


Rig base
********

1. Make paw rests:
    - Fix a piece of stick from a cotton bud to each of two M6 screws with araldite
    - Solder the end of a wire to the threads of each screw. The other end of each wire should reach the top of the raspberry pi.
    - Solder a pin to the other end of each wire
    - Cover the rests with heat shrink, leaving the screw heads partly exposed 
    - Fix to the rig base with araldite
    - Paint a thick layer on the rests with conductive paint, reaching the heads of each screw.

2. Assemble spouts (for a single spout):
    - Fix syringe holder to wall, fix tubing to syringe, mount syringe into holder
    - Fix other end of tubing to solenoid
    - Fix another length of tubing to solenoid to reach spout area
    - Fix plastic end of 19G syringe needle into end of tubing, angled downward

3. Make start button:
    - Mount button to 3D printed switch box

4. Mount raspberry pi to base and screw into place
5. Fix base to bench


stepper motor driver
    
    1. Power with 3.7V from raspberry pi
    2. Connect RST to SLP to enable driver
    3. Measure Vref, from ground to potentiometer
    4. Turn potentiometer so that Vref == 8 * 0.068 * (motor current rating, this was 1.68 for the first motor)
        - this calculated to around 0.913V so I set to 0.900
