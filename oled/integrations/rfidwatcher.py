import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import settings

import config.file_folder as cfg_file_folder

from datetime import datetime

rfid_watcher_changed = False

class MyHandler(FileSystemEventHandler):

    def on_modified(self, event):
        global rfid_watcher_changed
        if event.src_path == cfg_file_folder.LATEST_RFID:
            rfid_watcher_changed = True
        settings.lastinput = datetime.now()

class RfidWatcher:

    def __init__(self, directory="/home/pi/RPi-Jukebox-RFID/settings/", handler=MyHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def start(self):
        global rfid_watcher_changed 
        self.observer.schedule(
            self.handler, self.directory, recursive=False)
        self.observer.start()
        print("\nWatcher Running in {}/\n".format(self.directory))

    def stop():
        self.observer.stop()
        self.observer.join()
        print("\nWatcher Terminated\n")

    def get_state(test=None):
        global rfid_watcher_changed
        if rfid_watcher_changed:
            rfid_watcher_changed = False
            return True
        return False



