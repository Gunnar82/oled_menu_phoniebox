import settings
import os, re
import subprocess
import pexpect
import time

bt_dev_1="bt_dev_1"


class BluetoothOutput():

    def __init__(self):

        self.new_devices = []

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
        devices = []
        try:
            for device in self.get_paired_devices():
                devices.append([device['mac_address',device['name']]])
        except:
            print (err)

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
        os.system ("sudo systemctl restart phoniebox-bt-buttons.service")
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

    def send(self, command, pause=0):
        self.process.send(f"{command}\n")
        time.sleep(pause)
        if self.process.expect(["]", pexpect.EOF]):
            raise Exception(f"failed after {command}")

    def get_output(self, *args, **kwargs):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.send(*args, **kwargs)
        return self.process.before.split("\r\n")


    def start_bluetoothctl(self):
        self.process = pexpect.spawnu("bluetoothctl", echo=False)


    def stop_bluetoothctl(self):
        pass
        #self.process = pexpect.spawnu("bluetoothctl", echo=False)

    def start_scan(self):
        """Start bluetooth scanning process."""
        try:
            self.send("scan on")
        except Exception as e:
            print (e)


    def stop_scan(self):
        """Start bluetooth scanning process."""
        try:
            self.send("scan off")
        except Exception as e:
            print (e)

    def get_available_devices(self):
        """Return a list of tuples of paired and discoverable devices."""
        available_devices = []
        try:
            out = self.get_output("devices")
        except Exception as e:
            print(e)
        else:
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    available_devices.append(device)
        return available_devices

    def get_paired_devices(self):
        """Return a list of tuples of paired devices."""
        paired_devices = []
        try:
            out = self.get_output("paired-devices")
        except Exception as e:
            print (e)
        else:
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    paired_devices.append(device)
        return paired_devices

    def get_discoverable_devices(self):
        """Filter paired devices out of available."""
        available = self.get_available_devices()
        paired = self.get_paired_devices()
        return [d for d in available if d not in paired]

    def parse_device_info(self, info_string):
        """Parse a string corresponding to a device."""
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        if not any(keyword in info_string for keyword in block_list):
            try:
                device_position = info_string.index("Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(" ", 2)
                    device = {
                        "mac_address": attribute_list[1],
                        "name": attribute_list[2],
                    }
        return device

    def pair(self, mac_address):
        """Try to pair with a device by mac address."""
        try:
            self.send(f"pair {mac_address}", 4)
        except Exception as e:
            print (e)
            return False
        else:
            res = self.process.expect(
                ["Failed to pair", "Pairing successful", pexpect.EOF]
            )
            return res == 1

    def trust(self, mac_address):
        try:
            self.send(f"trust {mac_address}", 4)
        except Exception as e:
            print (e)
            return False
        else:
            res = self.process.expect(
                ["Failed to trust", "Pairing successful", pexpect.EOF]
            )
            return res == 1

    def connect(self, mac_address):
        """Try to connect to a device by mac address."""
        try:
            self.send(f"connect {mac_address}", 2)
        except Exception as e:
            print (e)
            return False
        else:
            res = self.process.expect(
                ["Failed to connect", "Connection successful", pexpect.EOF]
            )
            return res == 1

    def disconnect(self, mac_address=""):
        """Try to disconnect to a device by mac address."""
        try:
            self.send(f"disconnect {mac_address}", 2)
        except Exception as e:
            print (e)
            return False
        else:
            res = self.process.expect(
                ["Failed to disconnect", "Successful disconnected", pexpect.EOF]
            )
            return res == 1

    def remove(self, mac_address):
        """Remove paired device by mac address, return success of the operation."""
        try:
            self.send(f"remove {mac_address}", 3)
        except Exception as e:
            print(e)
            return False
        else:
            res = self.process.expect(
                ["not available", "Device has been removed", pexpect.EOF]
            )
            return res == 1
