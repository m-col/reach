= Construction guide for mouse reach task training rig =


== Parts list ==

Raspberry pi 3
    - power supply
    - raspbian SD card

gertbot motor driver
    - driver source: http://www.gertbot.com

stepper motor
    - (part here)
    - 9V power supply (e.g. xxxxx) 


== Setup ==

=== Circuit ===



=== Raspberry pi ===

1. Set passwords for pi and root users
2. Run 'sudo apt-get update && sudo apt-get upgrade'
3. Clone reach repo into pi home directory
4. Remove "console=serial0,115200 console=tty1" from /boot/cmdline.txt
5. Add to /boot/config.txt:

    dtoverlay=pi3-disable-bt
    enable_uart=1

6. Reboot
