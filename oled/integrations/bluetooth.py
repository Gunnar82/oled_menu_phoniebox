import settings
import os


enable_local_cmd = "mpc enable \"%s\" && mpc disable \"%s\"" % (settings.ALSA_DEV_LOCAL, settings.ALSA_DEV_BT)
enable_bt_cmd = "sudo bluetoothctl connect %s && sudo l2ping %s -c 1 && mpc enable \"%s\" && mpc disable \"%s\"" % (settings.BT_HF_MAC, settings.BT_HF_MAC,                                                                                                              settings.ALSA_DEV_BT, settings.ALSA_DEV_LOCAL)
check_bt_dev = "sudo bluetoothctl connect %s && sudo l2ping %s -c 1" % (settings.BT_HF_MAC, settings.BT_HF_MAC)


def init_output():
    retv = os.system(check_bt_dev)
    if retv == 0:
        os.system(enable_bt_cmd)
    else:
        os.system(enable_local_cmd)

def enable_dev_bt():
    os.system(enable_bt_cmd)


def enable_dev_alsa():
    os.system(enable_local_cmd)