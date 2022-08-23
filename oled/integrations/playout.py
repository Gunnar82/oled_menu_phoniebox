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


def checkfolder(playfile):
    try:
        lastfile=open(playfile).read().replace("\n","")
        if not os.path.isdir(settings.AUDIO_BASEPATH_BASE + lastfile):
            return 2
        return 0
    except:
        return 1

def playlast_checked(playfile):
    lastfile=open(playfile).read().replace("\n","")

    pc_playfolder(lastfile)

def pc_volup(step=1):
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=volumeup -v=%d" % (step))

def pc_voldown(step=1):
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=volumedown -v=%d" % (step))

def savepos():
    os.system("%s -c=savepos" % (settings.PLAYOUT_CONTROLS))


def pc_playfolder(folder=settings.AUDIO_BASEPATH_RADIO):
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh -d=\"%s\"" % (folder))

def pc_shutdown():
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=shutdown")
