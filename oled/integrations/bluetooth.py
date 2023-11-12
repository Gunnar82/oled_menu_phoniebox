import settings
import os, re
import subprocess


bt_dev_1="bt_dev_1"


class BluetoothOutput():

    def __init__(self):

        self.selected_bt_mac, self.selected_bt_name = self.read_dev_bt_from_file()
        self.all_bt_dev = self.get_bt_devices()


    def read_dev_bt_from_file(self):
        mac = "00:00:00:00:00:00"
        name = "none"
        try:
            with open('/etc/asound.conf') as reader:
                text = reader.read()
                mac = re.findall("(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})",text)[0]
                name = re.findall("description \"[A-Za-z0-9_\- ]*\"",text)[0].split("\"")[1]

        except Exception as errir:
            print (error)
        finally:
            reader.close()

        return mac,name

    def get_bt_dev_status():
        return True if (os.system(cmd_check_bt_dev = "bluetoothctl connect %s && sudo l2ping %s -c 1" % (self.selected_bt_mac, self.selected_bt_mac))== 0) else False

    def get_bt_devices(self):
        result = subprocess.run("bluetoothctl devices", shell=True, capture_output=True)
        lines = result.stdout.decode().splitlines()
        devices = []
        try:
            for line in lines:
                elems = line.split(' ',2)
                devices.append([elems[1],elems[2]])
        except:
            pass

        return devices


    def init_output(self):

        if self.get_bt_dev_status():
            self.enable_dev_bt()
        else:
            self.enable_dev_local()

    def set_alsa_bluetooth_mac(self,mac,name):

        with open('/etc/asound.conf') as asound:
            asound_content = asound.read()

        asound_new = re.sub("(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})",mac,asound_content)
        asound_new = re.sub("description \"[A-Za-z0-9_\- ]*\"","description \"%s\"" %(name),asound_new)

        os.system ("sudo chown pi /etc/asound.conf")

        with open('/etc/asound.conf','w') as asound:
            asound.write(asound_new)

        os.system ("sudo chown root /etc/asound.conf")

        os.system ("sudo systemctl restart mpd")

        self.selected_bt_mac, self.selected_bt_name = self.read_dev_bt_from_file()



    def enable_dev_bt(self):
        return os.system("bluetoothctl connect %s && sudo l2ping %s -c 1 && mpc enable \"%s\" && mpc disable \"%s\"" % (self.selected_bt_mac, self.selected_bt_mac, bt_dev_1, settings.ALSA_DEV_LOCAL))

    def enable_dev_local(self):
        os.system("mpc enable \"%s\" && mpc disable \"%s\"" % (settings.ALSA_DEV_LOCAL, bt_dev_1))


    def output_status(self,device="hifiberry"):
        result = subprocess.run("mpc outputs | grep %s" % (device), shell=True, capture_output=True)
        message = str(result.stdout)
        if "abled" in message:
            return (message[message.find("is")+3:message.find('\n')-2])
        else:
           print ("unavailable")


    def output_status_local(self):
        return self.output_status(settings.ALSA_DEV_LOCAL)

    def output_status_bt(self):
        return self.output_status(bt_dev_1)
