import time
from datetime import datetime

import settings

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from integrations.logging import *

latest_played_changed = False

class MyHandler(FileSystemEventHandler):

    def on_modified(self, event):
        log(lDEBUG2,"event on: %s" %(event.src_path))
        if event.src_path == file_folder.LATEST_PLAYED_FOLDER:
            log(lDEBUG,"event on LatestPlayed")
            try:
                played = open(event.src_path, 'r')
                line = played.readline()
                played.close()
                log(lDEBUG,"LastPlayed: %s" %(line))

                if line.startswith("/Musik") or line.startswith("Musik"):
                    outfile = file_folder.FILE_LAST_MUSIC
                elif line.startswith("/Radio" or line.startswith("Radio")):
                    outfile = file_folder.FILE_LAST_RADIO
                elif line.startswith("/Hörspiel")or line.startswith("Hörspiel"):
                    outfile = file_folder.FILE_LAST_HOERBUCH

                log(lDEBUG,"LastPlayed: outfile: %s" % (outfile))

                out = open(outfile,"w")
                out.write(line)
                out.close()

            except:
                log(lERROR,"Error on Latest_Played handling")


class LatestPlayed:

    def __init__(self, directory="/home/pi/RPi-Jukebox-RFID/settings/", handler=MyHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def start(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=False)
        self.observer.start()
        log(lINFO,"LatestPlayed Watchdog Running in %s/" % (self.directory))

    def stop():
        self.observer.stop()
        self.observer.join()
        log(lINFO,"LatestPlayed Watcher Terminated")




