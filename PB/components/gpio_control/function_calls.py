import logging
import sys
from subprocess import Popen as function_call

logger = logging.getLogger(__name__)

playout_control = "../../scripts/playout_controls.sh"
rfid_trigger_play = "../../scripts/rfid_trigger_play.sh"

def functionCallShutdown(*args):
    function_call("{command} -c=shutdown".format(command=playout_control), shell=True)


def functionCallVolU(steps=None):
    if steps is None:
        function_call("{command} -c=volumeup".format(command=playout_control), shell=True)
    else:
        function_call("{command} -c=volumeup -v={steps}".format(steps=steps,
            command=playout_control),
                shell=True)


def functionCallVolD(steps=None):
    if steps is None:
        function_call("{command} -c=volumedown".format(command=playout_control), shell=True)
    else:
        function_call("{command} -c=volumedown -v={steps}".format(steps=steps,
            command=playout_control),
                shell=True)


def functionCallVol0(*args):
    function_call("{command} -c=mute".format(command=playout_control), shell=True)


def functionCallPlayerNext(*args):
    function_call("{command} -c=playernext".format(command=playout_control), shell=True)


def functionCallPlayerPrev(*args):
    function_call("{command} -c=playerprev".format(command=playout_control), shell=True)


def functionCallPlayerPauseForce(*args):
    function_call("{command} -c=playerpauseforce".format(command=playout_control), shell=True)


def functionCallPlayerPause(*args):
    function_call("{command} -c=playerpause".format(command=playout_control), shell=True)

def functionCallPlayerLast(*args):
    function_call("{command} -d=\"$(cat /home/pi/RPi-Jukebox-RFID/settings/Latest_Folder_Played)\"".format(command=rfid_trigger_play), shell=True)


def functionCallRecordStart(*args):
    function_call("{command} -c=recordstart".format(command=playout_control), shell=True)


def functionCallRecordStop(*args):
    function_call("{command} -c=recordstop".format(command=playout_control), shell=True)


def functionCallRecordPlayLatest(*args):
    function_call("{command} -c=recordplaylatest".format(command=playout_control), shell=True)


def functionCallToggleWifi(*args):
    function_call("{command} -c=togglewifi".format(command=playout_control), shell=True)


def functionCallPlayerStop(*args):
    function_call("{command} -c=playerstop".format(command=playout_control),
            shell=True)


def functionCallPlayerSeekFwd(*args):
    function_call("{command} -c=playerseek -v=+10".format(command=playout_control), shell=True)


def functionCallPlayerRadioForce(*args):
    function_call("{command} -c=playlistaddplay -d=\"GBRadio\" -v=\"GBRadio\" ".format(command=playout_control), shell=True)


def functionCallPlayerSeekBack(*args):
    function_call("{command} -c=playerseek -v=-10".format(command=playout_control), shell=True)


def getFunctionCall(functionName):
    logger.error('Get FunctionCall: {} {}'.format(functionName, functionName in locals()))
    getattr(sys.modules[__name__], str)
    return locals().get(functionName, None)
