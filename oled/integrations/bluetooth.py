import settings
import  re
import subprocess
import pexpect
import time


from integrations.functions import run_command

from integrations.logging_config import *

logger = setup_logger(__name__)

bt_dev_1="bt_dev_1"


class BluetoothOutput():

    def __init__(self):

        self.new_devices = []

        self.all_bt_dev = self.get_bt_devices()

        self.selected_bt_mac, self.selected_bt_name = self.read_dev_bt_from_file()


    def read_dev_bt_from_file(self):
        mac = "00:00:00:00:00:00"
        name = "none"
        try:
            with open('/home/pi/oledctrl/oled/config/bt_device') as reader:
                text = reader.read()
                mac, name = text.split(maxsplit=1)
        except Exception as error:
            logger.error(error)

        return mac,name

    def get_bt_dev_status(self):
        print (f"MAC:{self.selected_bt_mac}")
        run_command ("bluetoothctl connect %s" % (self.selected_bt_mac))
        return run_command ("sudo l2ping %s -c 1" % (self.selected_bt_mac))

    def cmd_disconnect(self):
        return run_command("bluetoothctl disconnect")


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
        with open('/home/pi/oledctrl/oled/config/bt_device','w') as bt_conf:
            bt_conf.write(f"{mac} {name}")

        self.selected_bt_mac, self.selected_bt_name = self.read_dev_bt_from_file()

    def find_sink_by_mac(self,mac_address):
        try:
            # Ersetze die ':' in der MAC-Adresse durch '_', da PulseAudio das Format so verwendet
            mac_address = mac_address.replace(":", "_")
            # Führe den Befehl pactl list short sinks aus, um alle Sinks aufzulisten
            result = subprocess.run(
                ["pactl", "list", "short", "sinks"], 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        
            # Gehe durch die Ausgabe und suche nach der MAC-Adresse
            for line in result.stdout.splitlines():
                if mac_address in line:
                    # Der erste Wert in der Zeile ist der Sink-Name
                    sink_name = line.split()[0]
                    return sink_name
        
            # Wenn keine passende Sink gefunden wurde
            return None
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Ausführen von pactl: {e}")
            return None


    def set_default_sink(self,sink_name):
        try:
            # Setze die gefundene Sink als Standard
            subprocess.run(["pactl", "set-default-sink", sink_name], check=True)
            logger.debug(f"Die Bluetooth-Sink {sink_name} wurde als Standard gesetzt.")
        except subprocess.CalledProcessError as e:
            logger.debug(f"Fehler beim Setzen der Standard-Sink: {e}")

    def enable_dev_bt(self):
        sink_name = self.find_sink_by_mac(self.selected_bt_mac)
        if sink_name:
            self.set_default_sink(sink_name)
            return True
        else:
            return False

    def enable_dev_local(self):
        run_command("pactl set-default-sink 0")


    def output_is_bluez(self):
        results = []
        run_command("pactl list short sinks | grep bluez | grep RUNNING", results=results)
        if "bluez_sink" in str(results):
            logger.debug("bluez")
            return True
        else:
            return False

    def send(self, command, pause=0):
        self.process.send(f"{command}\n")
        time.sleep(pause)
        if self.process.expect(["bluetooth", pexpect.EOF]):
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
            logger.error(e)

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
            logger.error(e)
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
            logger.error(e)
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
            logger.error(e)
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
            logger.error(e)
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
            logger.error(e)
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
