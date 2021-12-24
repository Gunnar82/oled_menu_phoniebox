#!/bin/bash


DATE=`date +"%d-%m-%Y-%H-%M-%S"`
DEVICE=$1
MOUNTPATH="/media/pb_import/$DEVICE"
IMPORTFILE="$MOUNTPATH/PB_import.txt"
EXPORTFILE="$MOUNTPATH/PB_export.txt"

DESTPATH="/home/pi/RPi-Jukebox-RFID/shared/audiofolders/"

SOUNDPATH="/home/pi/oledctrl/audio/"
PLAYOUTCONTROLS="/home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh"

function playsound ()
{
	file=$1
	count=$2

	$PLAYOUTCONTROLS -c=playerstop
	while [ $count -gt 0 ]
	do
		sudo /usr/bin/mpg123 /home/pi/oledctrl/audio/beep-$file.mp3
		count=$[$count-1]
	done
}



mkdir -p $MOUNTPATH
mount /dev/$DEVICE $MOUNTPATH

playsound "07" 1

if  [ -f "$EXPORTFILE" ]; then
    playsound "07" 2
    rsync --delete -rv --size-only $DESTPATH $MOUNTPATH/audio/ --log-file=$MOUNTPATH/export-$DATE.log

        playsound "07" 4
	RV=0


elif [ -f "$IMPORTFILE" ]; then
    playsound "07" 1

    rsync -ruv --size-only $MOUNTPATH/audio/ $DESTPATH --log-file=$MOUNTPATH/import-$DATE.log
    RET=$?
    if [ $RET -eq 0 ] ; then
	chown -R pi.pi $DESTPATH
	playsound "07" 3
	RV=0
    else
	playsound "03" 3
	RV=1
    fi
else
    playsound "05" 1
    RV=2
fi


umount $MOUNTPATH
exit $RV
