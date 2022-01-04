#!/bin/bash
echo "ejecting"
sudo -u pi /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=playerstop
sleep 2
umount /home/pi/RPi-Jukebox-RFID/shared/audiofolders/usb/
umount /media/pb_import/$1
rm /tmp/phoniebox/usb_$1
mpc update
