= Construction guide for mouse reach task training rig =


== Parts list ==

3D printed parts:
    - reach task base
    - 2x RIVETS head bars
    - spout rail and carriage
    - 50 ml syringe holder (1 per spout)
    - small button box

Raspberry pi 3:
    - power supply
    - raspbian on SD card
    - ethernet cable

Touch sensors (per sensor):
    - 220 ohm + 270 ohm resistor
    - 2N2222 transistor
    - 1x 1x1 wire socket
One set is needed per paw rest and per spout.

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
    - conductive paint for paw rest spouts
    - 100 uF capacitor
    - 2x RIVETS bar thumb screws
    - USB camera
    - Momentary button with ~50 cm wires ending in pair of pins for start button


== Setup ==

=== Raspberry pi ===

1. Install raspbian with desktop (for easier wifi control)
2. Connect to mouse, keyboard and monitor
3. Set passwords for pi and root users
4. Run raspi-config and enable automatic login as user pi, and set locale to en\_US.UTF-8 
5. Get IS to assign static IP to mac address
6. To connect to eduroam, add this to /etc/wpa\_supplicant/wpa_supplicant.conf and reboot (not needed?):

    network={
	ssid="eduroam"
	scan\_ssid=1
	key\_mgmt=WPA-EAP
	eap=PEAP
	identity="<uun>@ed.ac.uk"
	password="<password>"
	phase1="peaplabel=0"
	phase2="auth=MSCHAPV2"
    }

7. apt-get update and upgrade
8. Edit /etc/dhcpcd.conf to show:

    interface eth0
    static ip\_address=<IP address assigned by IS>/23
    #static ip6......
    static routers=172.19.83.254

9. Clone reach repo into pi home directory
10. Remove "console=serial0,115200 console=tty1" from /boot/cmdline.txt (needed for gertbot)
11. Add to /boot/config.txt:

    dtoverlay=pi3-disable-bt
    dtoverlay=pi3-disable-wifi
    enable\_uart=1

12. Add to /etc/rc.local:

    echo none > /sys/class/leds/led0/trigger
    echo none > /sys/class/leds/led1/trigger
    echo 0 > /sys/class/leds/led0/brightness
    echo 0 > /sys/class/leds/led1/brightness

13. Remove "NOPASSWD:" from /etc/sudoers.d/010\_pi-nopasswd
14. Create /etc/apt/apt.conf.d/80proxy containing:

    Acquire::https {
	Proxy "https://wwwcache.ed.ac.uk:3128";
    }
    Acquire::http {
	Proxy "http://wwwcache.ed.ac.uk:3128";
    }

15. Add to ~/.zshrc:

    export https\_proxy=wwwcache.ed.ac.uk:3128
    export http\_proxy=$https_proxy

16. Optionally install zsh ranger vim and any other useful tools
17. Reboot and test connectivity

The raspberry pi can now be remoted into using the IP address assigned by IS, so the monitor, keyboard and mouse are no longer required.


=== Base ===

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


=== Pi-hat circuitry ===

1. Solder stick of sockets to pi-hat
2. Use fritzing file as guide to solder components to pi-hat
3. Mount pi-hat to raspberry pi
4. Plug paw rest sensor pins, spout solenoid, LED and touch sensor pins, and start button pins

