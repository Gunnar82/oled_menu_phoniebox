import settings
import os

cmd_check_bt_dev = "sudo bluetoothctl connect %s && sudo l2ping %s -c 1" % (settings.MAC_DEV_BT_1, settings.MAC_DEV_BT_1)


def init_output():
    retv = os.system(check_bt_dev)
    if retv == 0:
        enable_dev_bt_1()
    else:
        enable_dev_local()

def enable_dev_bt_1():
    os.system("sudo bluetoothctl connect %s && sudo l2ping %s -c 1 && mpc enable \"%s\" && mpc disable \"%s\"" % (settings.MAC_DEV_BT_1, settings.MAC_DEV_BT_1, settings.ALSA_DEV_BT_1, settings.ALSA_DEV_LOCAL))

def enable_dev_bt_2():
    os.system("sudo bluetoothctl connect %s && sudo l2ping %s -c 1 && mpc enable \"%s\" && mpc disable \"%s\"" % (settings.MAC_DEV_BT_2, settings.MAC_DEV_BT_2, settings.ALSA_DEV_BT_2, settings.ALSA_DEV_LOCAL))


def enable_dev_local():
    os.system("mpc enable \"%s\" && mpc disable \"%s\" && mpc disable \"%s\"" % (settings.ALSA_DEV_LOCAL, settings.ALSA_DEV_BT_1, settings.ALSA_DEV_BT_2))

def check_dev_bt():
    return os.system(cmd_check_bt_dev) == 0