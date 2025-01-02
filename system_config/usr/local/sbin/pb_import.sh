#!/bin/bash


DATE=`date +"%d-%m-%Y-%H-%M-%S"`
DEVICE=$1
MOUNTPATH="/media/pb_import/$DEVICE"
IMPORTFILE="$MOUNTPATH/PB_import.txt"
EXPORTFILE="$MOUNTPATH/PB_export.txt"

TMPFILEPATH="/tmp/phoniebox"

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
mkdir -p $TMPFILEPATH

mount /dev/$DEVICE $MOUNTPATH -orw

playsound "07" 1

if  [ -f "$EXPORTFILE" ]; then
    touch "$TMPFILEPATH/export_$DEVICE"
    playsound "07" 2

    rsync --delete -rv --size-only $DESTPATH $MOUNTPATH/audio/ --log-file=$MOUNTPATH/export-$DATE.log
    RET=$?
    if [ $RET -eq 0 ] ; then

        playsound "07" 4
        rm "$EXPORTFILE"
	RV=0
    else
        playsound "03" 4
        RV=1
    fi
    umount $MOUNTPATH


elif [ -f "$IMPORTFILE" ]; then
    touch "$TMPFILEPATH/import_$DEVICE"

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
    umount $MOUNTPATH

else
    mount /dev/$DEVICE $MOUNTPATH -oremount,ro
    sleep 1
#    mount -t unionfs -oallow_other,cow,dirs=/media/pb_import/$DEVICE=ro:/media/pb_import/tmpfs/=rw none  /home/pi/RPi-Jukebox-RFID/shared/audiofolders/usb/
    touch $TMPFILEPATH/usb_$DEVICE
    playsound "05" 1
    RV=0
fi


exit $RV
