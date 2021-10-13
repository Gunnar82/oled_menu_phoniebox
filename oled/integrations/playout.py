import os
import settings

def pc_prev():
    os.system("%s -c=playerprev" % (settings.PLAYOUT_CONTROLS))
def pc_next():
    os.system("%s -c=playernext" % (settings.PLAYOUT_CONTROLS))
def pc_stop():
    os.system("%s -c=playerstop" % (settings.PLAYOUT_CONTROLS))

def pc_play(pos = 0):
    os.system("%s -c=playerplay -v=%d" % (settings.PLAYOUT_CONTROLS, pos))

def pc_mute():
    os.system("%s -c=mute" % (settings.PLAYOUT_CONTROLS))

def pc_play_last_hoerspiel():
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh -d=\"`cat /home/pi/RPi-Jukebox-RFID/settings/Latest_Hörspiele_Folder_Played`\"")

def pc_play_last_radio():
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh -d=\"`cat /home/pi/RPi-Jukebox-RFID/settings/Latest_Radio_Folder_Played`\"")

def pc_play_last_musik():
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh -d=\"`cat /home/pi/RPi-Jukebox-RFID/settings/Latest_Musik_Folder_Played`\"")

def pc_volup():
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=volumeup")

def pc_voldown():
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=volumedown")

def savepos():
    os.system("%s -c=savepos" % (settings.PLAYOUT_CONTROLS))


def pc_playfolder(folder=settings.AUDIO_BASEPATH_RADIO):
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh -d=\"%s\"" % (folder))
