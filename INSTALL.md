rspi buster lite installieren
wlan einrichten
ssh einrichten
i2c aktivieren

dtoverlay= je nach dem

apt-get update
apt-get upgrade

sudo apt-get install mc

sudo mcedit /boot/config.txt


sudo mcedit /etc/asound.conf
hifiberry dac2/amp2
pcm.!default {
    type       hw card 0
}

ctl.!default {
    type hw card 0
}


<<EOF



pcm.hifiberry {
          type softvol
          slave.pcm "plughw:0"
          control.name "Master"
          control.card 0
  } 
pcm.!default {
          type plug
          slave.pcm "hifiberry"
  }
EOF



cd; rm buster-install-*; wget https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/master/scripts/installscripts/buster-install-default.sh; chmod +x buster-install-default.sh; ./buster-install-default.sh 

Audiodevice --> AMP2; DAC2 PRO


Radiosender --> GBRadio.m3u TODO


/etc/mpd.conf

hifiberry dac2 amp2
audio_output {
    enabled "True"
    device "hw:0"
    type "alsa"
    name "pcm512x-hifi"
    mixer_type "hardware"
    mixer_control "Digital"
}
____



####
audio_output
    type	"alsa"
    name	"hifiberrydac"
    mixer_control	master
____


Logging ausschalten  bzw tmpfs

### /etc/fstab
tmpfs		/var/log	tmpfs	size=10%	0	0
tmpfs		/tmp		tmpfs	size=5%		0	0

### /etc/samba/smb.conf

log file = /var/log/samba_log.%m

### /etc/lighttpd/lighttp.conf

logeintrag eintfernen oder hashen

#server.errorlog

----





RASPI OLED MENU
https://github.com/techdiem/RasPi-OLED-Menu

von Github aber geändert
--> kopiren nach /home/pi/oledctrl

sudo apt-get install python3-dev python3-pip libfreetype6-dev build-essential libopenjp2-7 libtiff5
sudo apt-get install python3-smbus python3-musicpd

cd oledctrl/

sudo pip3 install -r requirements.txt
sudo cp oled.service /lib/systemd/system/
sudo systemctl daemon-reload

test python3 oled.py
sudo systemctl enable oled.service


___

Bluetooth Ziel und Quelle

sudo apt-get install bluealsa

But add the following line to /etc/default/bluealsa:

LIBASOUND_THREAD_SAFE=0

sudo mcediit /etc/systemd/system/bluealsa-aplay.service
<<EOF
[Unit]
Description=Bluealsa-aplay daemon
Documentation=https://github.com/Arkq/bluez-alsa/
After=bluealsa.service
Requires=bluealsa.service
StopWhenUnneeded=true

[Service]
Type=simple
Environment="LIBASOUND_THREAD_SAFE=0"
ExecStart=/usr/bin/bluealsa-aplay 00:00:00:00:00:00

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable bluealsa-aplay.service
sudo systemctl start bluealsa-aplay.service

sudo mcedit /etc/bluetooth/main.conf


add line "Enable=Source,Sink,Media,Socket" under [general]


# Default device class. Only the major and minor device class bits are
# considered. Defaults to '0x000000'.
Class = 0x200414

# How long to stay in discoverable mode before going back to non-discoverable
# The value is in seconds. Default is 180, i.e. 3 minutes.
# 0 = disable timer, i.e. stay discoverable forever
DiscoverableTimeout = 180

# How long to stay in pairable mode before going back to non-discoverable
# The value is in seconds. Default is 0.
# 0 = disable timer, i.e. stay pairable forever
PairableTimeout = 120

sudo mcedit /etc/asound.conf >> append
set MAC OF BT PARTNER --> /home/pi/oledctrl/settings.py

pcm.btheadphones {
    type plug
    slave.pcm {

        type bluealsa
        device "4A:F5:FF:38:28:D5"
        profile "a2dp"
        delay -20000
    }
    hint {
        show on
    description "btheadphones"

    }
}


#####
/etc/mpd.conf
add-->

#Headphones

audio_output {
        enabled         "False"
        type            "alsa"
        name            "btheadphones"
        device          "btheadphones"  # optional
        mixer_type      "software"      # optional
#       mixer_device    "hw:0"  # optional
#       mixer_control   "Headphones"            # optional
#       mixer_index     "0"             # optional
}




###
/etc/bluetooth $ cat main.conf
[General]
Class = 0x200414
DiscoverableTimeout = 120

[Policy]
AutoEnable=true



######:
/etc/bluetooth $

pi@phoniebox8463:/etc/default $ cat bluealsa
OPTIONS="-p a2dp-source -p a2dp-sink"

LIBASOUND_THREAD_SAFE=0

#######
/etc/default $ cat bluealsa-aplay
OPTIONS="00:00:00:00:00:00"


#######
/etc/systemd/system/bluetooth.target.wants 



 cat bluetooth.service
[Unit]
Description=Bluetooth service
Documentation=man:bluetoothd(8)
ConditionPathIsDirectory=/sys/class/bluetooth

[Service]
Type=dbus
BusName=org.bluez
ExecStart=/usr/lib/bluetooth/bluetoothd --noplugin=sap
NotifyAccess=main
#WatchdogSec=10
#Restart=on-failure
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
LimitNPROC=1
ProtectHome=true
ProtectSystem=full

[Install]
WantedBy=bluetooth.target
Alias=dbus-org.bluez.service


####
 cat bluealsa-aplay.service
[Unit]
Description=Bluealsa audio player
Documentation=https://github.com/Arkq/bluez-alsa/
Wants=bluealsa.service

[Service]
Type=simple
;default to all devices - can be overridden in the EnvironmentFile
Environment="BT_ADDR=00:00:00:00:00:00"
EnvironmentFile=-/etc/default/bluealsa-aplay
ExecStart=/usr/bin/bluealsa-aplay $OPTIONS $BT_ADDR
Restart=on-failure
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
RemoveIPC=true
RestrictAddressFamilies=AF_UNIX
; Also non-privileged can user be used
; this example assumes a user called 'bluealsa-aplay' exists in the group 'audio'
;User=bluealsa-aplay
;Group=audio
;NoNewPrivileges=true

[Install]
WantedBy=bluetooth.target

###
cat bluealsa.service
[Unit]
Description=Bluealsa daemon
Documentation=https://github.com/Arkq/bluez-alsa/
After=dbus-org.bluez.service
Requires=dbus-org.bluez.service

[Service]
Type=dbus
BusName=org.bluealsa
EnvironmentFile=-/etc/default/bluealsa
ExecStart=/usr/bin/bluealsa $OPTIONS
Restart=on-failure
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
RemoveIPC=true
RestrictAddressFamilies=AF_UNIX AF_BLUETOOTH
; Also non-privileged can user be used
; this example assumes a user and group called 'bluealsa' exist
;User=bluealsa
;Group=bluealsa
;NoNewPrivileges=true

[Install]
WantedBy=bluetooth.target

_____


powercontroller shutdown

/lib/systemd/system-shutdown/clean-shutdown << EOF

#!/bin/bash
case "$1" in
  poweroff)
        i2cset -y -f 1 0x77 0x0a 20
        i2cset -y -f 1 0x77 0x05 0
        #i2cset -y -f 1 0x77 0x0e 1
        i2cset -y -f 1 0x77 0x02 0
        i2cset -y -f 1 0x77 0x03 100
        i2cset -y -f 1 0x77 0x04 0
        i2cset -y -f 1 0x77 0x01 2
        i2cset -y -f 1 0x77 0x09 30
        ;;

sudo chmod +x clean-shutdown
sudo systemctl daemon-reload
