#!/bin/bash


DATE=`date +"%d/%m/%Y %H:%M:%S"`
DEVICE=$1
MOUNTPATH="/media/pb_import/$DEVICE/"
IMPORTFILE="$MOUNTPATH/PB_import.txt"
EXPORTFILE="$MOUNTPATH/PB_export.txt"

DESTPATH="/home/pi/RPi-Jukebox-RFID/shared/audiofolders/"




mkdir -p $MOUNTPATH
mount /dev/$DEVICE $MOUNTPATH

sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-07.mp3

if  [ -f "$EXPORTFILE" ]; then
    sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-07.mp3
    sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-07.mp3
    rsync -r $DESTPATH $MOUNTPATH

        sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-07.mp3
        sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-07.mp3
        sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-07.mp3
        sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-07.mp3
        RV=0


elif [ -f "$IMPORTFILE" ]; then
    sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-07.mp3

    rsync -ru --size-only $MOUNTPATH $DESTPATH
    RET=$?
    if [ $RET -eq 0 ] ; then
	chown -R pi.pi $DESTPATH
	sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-07.mp3
	sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-07.mp3
	sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-07.mp3
	RV=0
    else
	sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-03.mp3
	sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-03.mp3
	sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-03.mp3
	RV=1
    fi
else
    sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-05.mp3
    RV=2
fi


umount $MOUNTPATH
exit $RV
