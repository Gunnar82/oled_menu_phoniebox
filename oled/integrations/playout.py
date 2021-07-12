import os
import settings

def pc_prev():
    os.system("%s -c=playerprev" % (settings.PLAYOUT_CONTROLS))
def pc_next():
    os.system("%s -c=playernext" % (settings.PLAYOUT_CONTROLS))
def pc_stop():
    os.system("%s -c=playerstop" % (settings.PLAYOUT_CONTROLS))

def savepos():
    os.system("%s -c=savepos" % (settings.RESUME_PLAY))
