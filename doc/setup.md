= Construction guide for mouse reach task training rig =


== Parts list ==

Raspberry pi 3
    - power supply
    - raspbian on SD card
    - ethernet cable

gertbot motor driver
    - driver source: http://www.gertbot.com

stepper motor
    - (part here)
    - 9V power supply (e.g. xxxxx) 


== Setup ==

=== Circuit ===

==== Stepper motor ====

- Red and black wires: 100 Ohm resistor in series
- 4 wires from motor plug directly into gertbot:
(photo)

- Power cable wires need exposing and plug directly into gertbot:
(photo)

	________.__.              
	gertbot | O|--1- 
		| O|--2-
	    	| O|--3- power - black and white
	    	| O|--4-
	    	| O|--5-
	    	| O|--6- power - ground
	    	| O|--7-
	    	| O|--8-
	    	| O|--9-
	    	| O|-10-
	    	| O|-11-
	    	| O|-12-
	--------'--'


=== Everything else ===

Pin numbering in the python code and here uses the BOARD scheme. Pinout:
                           .___.              
                       --1-|O O|--2-
                       --3-|O O|--4
                       --5-|O O|--6-
                       --7-|O O|--8-
                      _--9-|O.O|-10-
                       -11-|O O|-12-
                       -13-|O O|-14-_
                       -15-|O O|-16-
         3.3V power-----17-|O O|-18-----Start button
    left paw sensor-----19-|O.O|-20---_ ground
   right paw sensor-----21-|O O|-22-----cue LED
       spout sensor-----23-|O O|-24-----solenoid control
                      _-25-|O O|-26-
                       -27-|O O|-28-
                       -29-|O.O|-30-_
                       -31-|O O|-32-
		       -33-|O O|-34-_
		       -35-|O O|-36-
		       -37-|O O|-38-
                       -39-|O O|-40-
                           '---'


=== Raspberry pi ===

1. Install raspbian with desktop (for easier wifi control)
1. Connect to mouse, keyboard and monitor
1. Set passwords for pi and root users
6. Run raspi-config and enable automatic login as user pi, and set locale to en_US.UTF-8 
3. Get IS to assign static IP to mac address
2. To connect to eduroam, add this to /etc/wpa_supplicant/wpa_supplicant.conf and reboot (not needed?):

    network={
	ssid="eduroam"
	scan_ssid=1
	key_mgmt=WPA-EAP
	eap=PEAP
	identity="<uun>@ed.ac.uk"
	password="<password>"
	phase1="peaplabel=0"
	phase2="auth=MSCHAPV2"
    }

2. apt-get update and upgrade
5. Edit /etc/dhcpcd.conf to show:

    interface eth0
    static ip_address=<IP address assigned by IS>/23
    #static ip6......
    static routers=172.19.83.254

3. Clone reach repo into pi home directory
4. Remove "console=serial0,115200 console=tty1" from /boot/cmdline.txt (needed for gertbot)
5. Add to /boot/config.txt:

    dtoverlay=pi3-disable-bt
    dtoverlay=pi3-disable-wifi
    enable_uart=1

5. Add to /etc/rc.local:

    echo none > /sys/class/leds/led0/trigger
    echo none > /sys/class/leds/led1/trigger
    echo 0 > /sys/class/leds/led0/brightness
    echo 0 > /sys/class/leds/led1/brightness

6. Remove "NOPASSWD:" from /etc/sudoers.d/010_pi-nopasswd
6. Create /etc/apt/apt.conf.d/80proxy containing:

    Acquire::https {
	Proxy "https://wwwcache.ed.ac.uk:3128";
    }
    Acquire::http {
	Proxy "http://wwwcache.ed.ac.uk:3128";
    }

6. Add to ~/.zshrc:

    export https_proxy=wwwcache.ed.ac.uk:3128
    export http_proxy=$https_proxy

6. Optionally install zsh ranger vim and any other useful tools
6. Reboot and test connectivity

The raspberry pi can now be remoted into using the IP address assigned by IS, so the monitor, keyboard and mouse are no longer required.
