import time
from datetime import datetime

import settings

import config.file_folder as cfg_file_folder

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from integrations.logging_config import setup_logger

logger = setup_logger(__name__)


latest_played_changed = False

class MyHandler(FileSystemEventHandler):

    def on_modified(self, event):
        logger.debug("event on: %s" %(event.src_path))
        if event.src_path == cfg_file_folder.LATEST_PLAYED_FOLDER:
            logger.debug("event on LatestPlayed")
            try:
                played = open(event.src_path, 'r')
                line = played.readline()
                played.close()
                logger.debug("LastPlayed: %s" %(line))

                if line.startswith("/Musik") or line.startswith("Musik"):
                    outfile = cfg_file_folder.FILE_LAST_MUSIC
                elif line.startswith("/Radio" or line.startswith("Radio")):
                    outfile = cfg_file_folder.FILE_LAST_RADIO
                elif line.startswith("/Hörspiel")or line.startswith("Hörspiel"):
                    outfile = cfg_file_folder.FILE_LAST_HOERBUCH
                else:
                    return

                logger.debug("LastPlayed: outfile: %s" % (outfile))

                with open(outfile,"w") as out:
                    out.write(line)

            except Exception as error:
                logger.error(f"on_modified: {error}")


class LatestPlayed:

    def __init__(self, directory="/home/pi/RPi-Jukebox-RFID/settings/", handler=MyHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def start(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=False)
        self.observer.start()
        logger.info("LatestPlayed Watchdog Running in %s/" % (self.directory))

    def stop():
        self.observer.stop()
        self.observer.join()
        logger.info("LatestPlayed Watcher Terminated")




