import settings
import  re
import subprocess
import time
import bluetooth as bt

from integrations.functions import run_command

from integrations.logging_config import *

logger = setup_logger(__name__)

bt_dev_1="bt_dev_1"


class BluetoothOutput():

    def __init__(self):

        """Initialisiert den BluetoothHandler und bereitet das Gerät vor."""
        self.nearby_devices = []
        self.paired_devices = []

        self.new_devices = []

        #self.all_bt_dev = self.get_paired_devices()

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

    def enable_bluez(self):
        logger.debug(f"verbinde zu {self.selected_bt_mac}")
        self.connect_device(self.selected_bt_mac)

        if self.output_is_bluez(running="SUSPENDED"):
            logger.debug("bluz-sink vorhanden")
            return self.enable_dev_bt()
        return False

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
        logger.debug(f"enable_dev_bt: {self.selected_bt_mac} ")
        sink_name = self.find_sink_by_mac(self.selected_bt_mac)
        if sink_name:
            self.set_default_sink(sink_name)
            return True
        else:
            return False

    def enable_dev_local(self):
        run_command("pactl set-default-sink 0")


    def output_is_bluez(self, running="RUNNING"):
        results = []
        run_command(f"pactl list short sinks | grep bluez | grep {running}", results=results)
        print (results)
        if "bluez_sink" in str(results):
            logger.debug("bluez")
            return True
        else:
            return False

    def discover_devices(self):
        """
        Scanne nach verfügbaren Bluetooth-Geräten in der Nähe und speichere sie in der Instanz.
        """
        try:
            print("Scanne nach Bluetooth-Geräten...")
            self.nearby_devices = bt.discover_devices(lookup_names=True)
            
            if self.nearby_devices:
                print("Gefundene Bluetooth-Geräte:")
                for addr, name in self.nearby_devices:
                    print(f"Adresse: {addr}, Name: {name}")
            else:
                print("Keine Bluetooth-Geräte gefunden.")
        
        except bt.BluetoothError as e:
            print(f"Fehler beim Scannen nach Bluetooth-Geräten: {str(e)}")
        return self.nearby_devices


    def get_paired_devices(self):
        """
        Hole die Liste der bereits gekoppelten Geräte über den 'bluetoothctl' Befehl.
        """
        print("Hole die Liste der bereits gekoppelten Bluetooth-Geräte...")
        
        try:
            output = subprocess.check_output("bluetoothctl paired-devices", shell=True).decode("utf-8")
            paired_devices = []
            for line in output.splitlines():
                if "Device" in line:
                    parts = line.split(" ")
                    address = parts[1]
                    name = bt.lookup_name(address)
                    paired_devices.append((address, name))
            
            self.paired_devices = paired_devices
            if self.paired_devices:
                print("Bereits gekoppelte Geräte:")
                for addr, name in self.paired_devices:
                    print(f"Adresse: {addr}, Name: {name}")
            else:
                print("Keine bereits gekoppelten Geräte gefunden.")
        
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Abrufen der gekoppelten Geräte: {e}")

    def pair_device(self, device_addr):
        """
        Versuche, ein Gerät zu koppeln, indem die Adresse übergeben wird.
        Dies erfolgt durch den Aufruf von bluetoothctl.
        """
        try:
            print(f"Versuche, mit Gerät {device_addr} zu koppeln...")

            # Scanne nach Geräten, um sicherzustellen, dass das Gerät sichtbar ist
            subprocess.run("bluetoothctl --timeout 10 scan on", shell=True, check=True)
             # Warten, um sicherzustellen, dass die Geräte sichtbar sind

            # Versuch, das Gerät zu koppeln
            subprocess.run(f"bluetoothctl pair {device_addr}", shell=True, check=True)
            print(f"Erfolgreich gekoppelt mit {device_addr}")
        
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Koppeln mit {device_addr}: {e}")
        except Exception as e:
            print(f"Unbekannter Fehler beim Koppeln mit {device_addr}: {str(e)}")

    def connect_device(self, device_addr):
        """
        Versuche, eine Verbindung mit einem Bluetooth-Gerät herzustellen.
        """
        try:
            print(f"Versuche, mit Gerät {device_addr} zu verbinden...")
            subprocess.run(f"bluetoothctl connect {device_addr}", shell=True, check=True)
            print(f"Erfolgreich verbunden mit {device_addr}")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Verbinden mit {device_addr}: {e}")

    def disconnect_device(self, device_addr):
        """
        Trenne die Verbindung zu einem Bluetooth-Gerät.
        """
        try:
            print(f"Trenne Verbindung zu Gerät {device_addr}...")
            subprocess.run(f"bluetoothctl disconnect {device_addr}", shell=True, check=True)
            print(f"Erfolgreich die Verbindung zu {device_addr} getrennt.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Trennen der Verbindung mit {device_addr}: {e}")

    def remove_device(self, device_addr):
        """
        Entferne (entkopple) ein Bluetooth-Gerät.
        """
        try:
            print(f"Versuche, das Gerät {device_addr} zu entfernen...")
            subprocess.run(f"bluetoothctl remove {device_addr}", shell=True, check=True)
            print(f"Erfolgreich entfernt {device_addr}")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Entfernen des Geräts {device_addr}: {e}")

    def show_device_options(self):
        """
        Zeigt die Optionen für verfügbare Geräte an und ermöglicht die Auswahl eines Geräts.
        """
        all_devices = self.paired_devices + self.nearby_devices
        if all_devices:
            print("Wähle ein Gerät aus:")
            for index, (addr, name) in enumerate(all_devices, 1):
                print(f"{index}. {name} - {addr}")
            try:
                selected_index = int(input("Gib die Nummer des Geräts ein: ")) - 1
                selected_device = all_devices[selected_index]
                return selected_device[0]
            except (ValueError, IndexError):
                print("Ungültige Auswahl.")
        else:
            print("Keine Geräte zum Auswählen.")
        return None

