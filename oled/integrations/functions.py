import os
import subprocess, re
import datetime
import settings

def get_parent_folder(folder):
    return os.path.dirname(folder)

def has_subfolders(path):
    for file in os.listdir(path):
        d = os.path.join(path, file)
        if os.path.isdir(d):
            return True
    return False


def to_min_sec(seconds):
        mins = int(float(seconds) // 60)
        secs = int(float(seconds) - (mins*60))
        if mins >=60:
            hours = int(float(mins) // 60)
            mins = int(float(mins) - (hours*60))
            return "%d:%2.2d:%2.2d" % (hours,mins,secs)
        else:
            return "%2.2d:%2.2d" % (mins,secs)

def linux_job_remaining(job_name):
        cmd = ['sudo', 'atq', '-q', job_name]
        dtQueue = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()
        regex = re.search('(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', dtQueue)
        if regex:
            dtNow = datetime.datetime.now()
            dtQueue = datetime.datetime.strptime(dtNow.strftime("%d.%m.%Y") + " " + regex.group(5), "%d.%m.%Y %H:%M:%S")

            # subtract 1 day if queued for the next day
            if dtNow > dtQueue:
                dtNow = dtNow - datetime.timedelta(days=1)

            return int(round((dtQueue.timestamp() - dtNow.timestamp()) / 60, 0))
        else:
            return -1


def get_folder_of_livestream(url):
    basefolder = settings.AUDIO_BASEPATH_RADIO

    for folder in os.listdir(basefolder):
        d = os.path.join(basefolder, folder)
        if os.path.isdir(d):
           filename = os.path.join(d,'livestream.txt')
           try:
               with open(filename, 'r') as file:
                    data = file.read().replace('\n', '')
               if data == url:
                   return d
           except:
               pass

    return "n/a"


def get_folder(folder,direction = 1):
    parent = get_parent_folder(folder)
    entrys = []
    for folders in os.listdir(parent):
        d = os.path.join(parent, folders)
        if os.path.isdir(d):
            entrys.append(d)
    entrys.sort()
    pos = entrys.index(folder)
    pos += direction

    if pos < 0:
        pos = 0
    if pos > len(entrys) -1:
        pos = len(entrys) -1
    rel_path = os.path.relpath(entrys[pos],settings.AUDIO_BASEPATH_BASE)
    return rel_path


def restart_oled():
    if settings.DISPLAY_DRIVER == "emulated":
        print ("restarting lightdm service")

        os.system("sudo systemctl restart lightdm")
    else:
        print ("restarting  service")

        os.system("sudo systemctl restart oled")


def get_usb_name():
    for file in os.listdir("/tmp/phoniebox"):
        if file.startswith("usb_"):
            return (file.split("_")[1])

def mountusb():
    usbdev=get_usb_name()
    if (usbdev == "n/a"):
        return -1

    if not os.path.ismount(settings.AUDIO_BASEPATH_USB):
        print (usbdev)
        os.system("unionfs-fuse -orw,cow,allow_other /media/pb_import/tmpfs/=rw:/media/pb_import/%s=ro %s" % (usbdev, settings.AUDIO_BASEPATH_USB))
        os.system("mpc update")
    else:
        print ("already mounted")

def umountusb():
    os.system("/home/pi/RPi-Jukebox-RFID/shared/audiofolders/usb/")

def get_folder_from_file(filename):
    try:
        with open (filename) as f:
            lines = f.readlines()
            f.close()
            if (lines[0].startswith("/")):
                path = settings.AUDIO_BASEPATH_BASE + lines[0].rstrip()
            else:
                path = settings.AUDIO_BASEPATH_BASE + "/" + lines[0].rstrip()
            return (path)
    except:
        return settings.AUDIO_BASEPATH_BASE


def get_battload_color():
    if settings.battloading:
        return settings.COLOR_BLUE
    elif settings.battcapacity == -1:
        return "WHITE"
    elif settings.battcapacity >= 70:
        return settings.COLOR_GREEN
    elif settings.battcapacity >= 30:
        return settings.COLOR_YELLOW
    else:
        return settings.COLOR_RED

