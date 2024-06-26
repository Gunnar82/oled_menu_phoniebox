import os
import settings
import requests
import urllib.parse

import config.file_folder as cfg_file_folder
import config.online as cfg_online

def pc_prev():
    os.system("%s -c=playerprev" % (cfg_file_folder.PLAYOUT_CONTROLS))
def pc_next():
    os.system("%s -c=playernext" % (cfg_file_folder.PLAYOUT_CONTROLS))
def pc_stop():
    os.system("%s -c=playerstop" % (cfg_file_folder.PLAYOUT_CONTROLS))

def pc_play(pos = 0):
    os.system("%s -c=playerplay -v=%d" % (cfg_file_folder.PLAYOUT_CONTROLS, pos))

def pc_mute():
    os.system("%s -c=mute" % (cfg_file_folder.PLAYOUT_CONTROLS))

def pc_toggle():
    os.system("%s -c=playerpause" % (cfg_file_folder.PLAYOUT_CONTROLS))

def pc_shutdown():
    os.system("%s -c=shutdown" % (cfg_file_folder.PLAYOUT_CONTROLS))

def pc_reboot():
    print("Reboot down system")
    os.system("%s -c=reboot" % (cfg_file_folder.PLAYOUT_CONTROLS))


def pc_seek0():
    print("mpc seek 0")
    os.system("mpc seek 0")

def savepos():
    os.system("%s -c=savepos" % (cfg_file_folder.RESUME_PLAY))

def savepos_online(nowplaying):
    data = {'url' : nowplaying.filename, 'pos' : str(nowplaying._elapsed), 'song' : str(nowplaying._song), 'length' : str(nowplaying._playlistlength)}
    try:
        r = requests.post(cfg_online.ONLINE_SAVEPOS,data=data,timeout=8)

    except Exception as error:
        print (error)

def getpos_online(baseurl,cwd):
    url = baseurl+urllib.parse.quote(cwd)
    data = {'url' : url}
    try:
        r = requests.post("%sgetpos.php" % (cfg_online.ONLINE_SAVEPOS),data=data)
        response = r.content.decode()
        vals = response.split("|")
        vals.append(url)
        return vals

    except:
        return ["ERREXP"]

def add_leading_slash(folder):
    return folder if folder[0] == '/' else '/%s' % (folder)

def checkfolder(playfile):
    try:
        lastfile=add_leading_slash(open(playfile).read().replace("\n",""))
        if not os.path.isdir(cfg_file_folder.AUDIO_BASEPATH_BASE + lastfile):
            return 2
        return 0
    except:
        return 1

def playlast_checked(playfile):
    lastfile=add_leading_slash(open(playfile).read().replace("\n",""))

    pc_playfolder(lastfile)

def pc_volup(step=5):
    os.system("mpc vol  +%d" % (step))
#    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=volumeup -v=%d" % (step))

def pc_voldown(step=5):
    os.system("mpc vol -%d" % (step))
#    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=volumedown -v=%d" % (step))


def pc_playfolder(folder=cfg_file_folder.AUDIO_BASEPATH_RADIO):
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh -d=\"%s\"" % (folder))

def pc_shutdown():
    os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=shutdown")

def pc_enableresume(folder=""):
    if folder != "":
        print("%s -c=enableresume -d=\"%s\"" % (cfg_file_folder.RESUME_PLAY,folder))

def pc_disableresume(folder=""):
    if folder != "":
        os.system("%s -c=disableresume -d=\"%s\"" % (cfg_file_folder.RESUME_PLAY,folder))
