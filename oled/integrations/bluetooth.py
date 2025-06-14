import settings
import  re
import subprocess
import time
import pexpect


from integrations.functions import run_command as run_cmd

from integrations.logging_config import *
from integrations.playout import *


logger = setup_logger(__name__)

bt_dev_1="bt_dev_1"


class BluetoothOutput():

    def __init__(self,user_settings):

        """Initialisiert den BluetoothHandler und bereitet das Gerät vor."""
        self.nearby_devices = []
        self.paurable_devices = []
        self.new_devices = []
        self.user_settings = user_settings

        #self.all_bt_dev = self.get_paired_devices()

        self.bluetoothctl = None
        self.connected_devices = []
        self.pairable_devices = []
        self.start_bluetoothctl()


        self.selected_bt_mac = self.user_settings.BLUETOOTH_ADDR
        self.selected_bt_name = self.user_settings.BLUETOOTH_NAME


    def enable_bluez(self):
        logger.debug(f"verbinde zu {self.selected_bt_mac}")
        self.connect_device(self.selected_bt_mac)

        if self.output_is_bluez(running="SUSPENDED"):
            logger.debug("bluz-sink vorhanden")
            return self.enable_dev_bt()
        return False

    def set_alsa_bluetooth_mac(self,mac,name):
        self.user_settings.BLUETOOTH_ADDR = mac
        self.user_settings.BLUETOOTH_NAME = name

        self.selected_bt_mac = self.user_settings.BLUETOOTH_ADDR
        self.selected_bt_name = self.user_settings.BLUETOOTH_NAME


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
            logger.debug(f"Fehler beim Ausführen von pactl: {e}")
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
        run_cmd("pactl set-default-sink 0")


    def output_is_bluez(self, running="RUNNING"):
        results = []
        run_command(f"pactl list short sinks | grep bluez | grep {running}", results=results)
        logger.debug(str(results))
        if "bluez_sink" in str(results):
            logger.debug("bluez")
            return True
        else:
            return False


    def connect_default_bt_device(self,mac = None):
        logger.debug(f"BT: connect_default_device {self.selected_bt_name}")
        if mac is None:
            return self.connect(self.selected_bt_mac)
        else:
            return self.connect(mac)

    def disconnect_default_bt_device(self):
        logger.debug(f"BT: disconnect_default_device {self.selected_bt_name}")
        return self.disconnect(self.selected_bt_mac)

    def disconnect_all_connected_devices(self):
        for device in self.get_connected_devices():
            logger.debug (f"disconnect: {device}")
            self.disconnect()

    def start_bluetoothctl(self):
        """Startet den bluetoothctl-Prozess und überprüft die Ausgabe."""
        logger.debug("start_bluetoothctl startet")
        try:
            if not self.bluetoothctl:
                self.bluetoothctl = pexpect.spawn('bluetoothctl', echo=False)
                # Warten auf den Start und die Anmeldung des Agenten
                index = self.bluetoothctl.expect([r'Agent registered', r'#'], timeout=5)
                if index == 0:
                    logger.debug("Agent erfolgreich registriert.")
                elif index == 1:
                    logger.debug("Bluetoothctl ist bereit.")
            
                # Verbundene Geräte abrufen
                self.connected_devices = self.get_connected_devices()
                logger.debug("bluetoothctl erfolgreich gestartet.")
        except pexpect.exceptions.TIMEOUT:
            logger.debug("Fehler: Timeout beim Start von bluetoothctl.")
            if self.bluetoothctl:
                logger.debug(f"Letzte Ausgabe von bluetoothctl: {self.bluetoothctl.before.decode('utf-8')}")
            self.bluetoothctl = None
        except pexpect.exceptions.ExceptionPexpect as e:
            logger.debug(f"Pexpect-Fehler beim Start von bluetoothctl: {e}")
            if self.bluetoothctl:
                logger.debug(f"Letzte Ausgabe von bluetoothctl: {self.bluetoothctl.before.decode('utf-8')}")
            self.bluetoothctl = None
        except Exception as e:
            logger.debug(f"Allgemeiner Fehler beim Start von bluetoothctl: {e}")
            if self.bluetoothctl:
                logger.debug(f"Letzte Ausgabe von bluetoothctl: {self.bluetoothctl.before.decode('utf-8')}")
            self.bluetoothctl = None

    def stop_bluetoothctl(self):
        """Beendet den bluetoothctl-Prozess."""
        logger.debug("stop_bluetoothctl startet")
        if self.bluetoothctl:
            try:
                self.bluetoothctl.sendline('exit')
                self.bluetoothctl.close()
                self.bluetoothctl = None
                logger.debug("bluetoothctl beendet.")
            except (pexpect.exceptions.ExceptionPexpect, pexpect.exceptions.TIMEOUT):
                logger.debug("Fehler: bluetoothctl konnte nicht beendet werden.")

    def run_command(self, command, timeout=5):
        """Führt einen Befehl in bluetoothctl aus und gibt die Ausgabe zurück."""
        logger.debug("run_command startet")
        if self.bluetoothctl:
            try:
                logger.debug(f"Befehl wird ausgeführt: {command}")
                self.bluetoothctl.sendline(command)
                self.bluetoothctl.expect('#', timeout=timeout)
                return self.bluetoothctl.before.decode('utf-8')
            except (pexpect.exceptions.ExceptionPexpect, pexpect.exceptions.TIMEOUT):
                logger.debug(f"Fehler: Der Befehl '{command}' konnte nicht ausgeführt werden.")
                return ""
        return ""

    def get_pairable_devices(self):
        """Listet alle in Reichweite befindlichen Bluetooth-Geräte als Array mit [MAC-Adresse, Name] auf, die nicht gepairt sind."""
        logger.debug("get_pairable_devices startet")
        try:
            paired = {device[0] for device in self.paired_devices()}
            self.run_command('scan on', timeout=10)
            time.sleep(10)
            output = self.run_command('devices', timeout=10)
            self.run_command('scan off')
            devices = re.findall(r'Device ([0-9A-F:]{17}) (.+)', output)
            logger.debug(f"Gefundene Geräte: {devices}")
            self.pairable_devices = [[mac, name.strip("\r")] for mac, name in devices if mac not in paired]
            return self.pairable_devices
        except Exception as e:
            logger.debug(f"Fehler beim Scannen nach Geräten: {e}")
            self.pairable_devices = []
            return []

    def pair(self, mac_address,timeout=10):
        """Pairt ein Gerät mit der angegebenen MAC-Adresse."""
        logger.debug("pair startet")
        try:
            output = self.run_command(f'pair {mac_address}')
            if 'Pairing successful' in output or 'AlreadyExists' in output:
                logger.debug(f"Pairing erfolgreich: {mac_address}")
                return True
            else:
                logger.debug(f"Fehler beim Pairen des Geräts {mac_address}: {output}")
                return False
        except Exception as e:
            logger.debug(f"Fehler beim Pairen des Geräts {mac_address}: {e}")
            return False

    def trust(self, mac_address,timeout=10):
        """Vertraut einem Gerät mit der angegebenen MAC-Adresse."""
        logger.debug("trust startet")
        try:
            output = self.run_command(f'trust {mac_address}')
            if 'trusted' in output:
                logger.debug(f"Gerät vertraut: {mac_address}")
                return True
            else:
                logger.debug(f"Fehler beim Vertrauen des Geräts {mac_address}: {output}")
                return False
        except Exception as e:
            logger.debug(f"Fehler beim Vertrauen des Geräts {mac_address}: {e}")
            return False

    def connect(self, mac_address):
        """Verbindet sich mit einem Gerät mit der angegebenen MAC-Adresse."""
        logger.debug("connect startet")
        try:
            output = self.run_command(f'connect {mac_address}',timeout=10)
            if 'Connection successful' in output:
                self.connected_devices.append(mac_address)
                logger.debug(f"Verbindung erfolgreich: {mac_address}")
                return True
            else:
                logger.debug(f"Fehler beim Verbinden mit dem Gerät {mac_address}: {output}")
                return False
        except Exception as e:
            logger.debug(f"Fehler beim Verbinden mit dem Gerät {mac_address}: {e}")
            return False

    def disconnect(self, mac_address=None):
        """Trennt die Verbindung zu einem Gerät mit der angegebenen MAC-Adresse. Falls keine MAC-Adresse angegeben ist, werden alle Geräte getrennt."""
        logger.debug("disconnect startet")
        try:
            if mac_address:
                output = self.run_command(f'disconnect {mac_address}')
                if 'Successful disconnected' in output:
                    if mac_address in self.connected_devices:
                        self.connected_devices.remove(mac_address)
                    logger.debug(f"Verbindung getrennt: {mac_address}")
                    return True
                else:
                    logger.debug(f"Fehler beim Trennen der Verbindung zum Gerät {mac_address}: {output}")
                    return False
            else:
                success = True
                for device in self.connected_devices[:]:
                    output = self.run_command(f'disconnect {device}')
                    if 'Successful disconnected' in output:
                        self.connected_devices.remove(device)
                        logger.debug(f"Verbindung getrennt: {device}")
                    else:
                        logger.debug(f"Fehler beim Trennen der Verbindung zum Gerät {device}: {output}")
                        success = False
                return success
        except Exception as e:
            logger.debug(f"Fehler beim Trennen der Verbindung: {e}")
            return False

    def paired_devices(self):
        """Listet alle gepairten Geräte als Array mit [MAC-Adresse, Name] auf."""
        logger.debug("paired_devices startet")
        try:
            output = self.run_command('paired-devices')
            devices = re.findall(r'Device ([0-9A-F:]{17}) (.+)', output)
            logger.debug(f"Gepairte Geräte: {devices}")
            return [[mac, name.strip("\r")] for mac, name in devices]
        except Exception as e:
            logger.debug(f"Fehler beim Abrufen der gepairten Geräte: {e}")
            return []

    def get_connected_devices(self):
        """Listet alle aktuell verbundenen Geräte auf."""
        logger.debug("get_connected_devices startet")
        try:
            output = self.run_command('info')
            devices = re.findall(r'Device ([0-9A-F:]{17})', output)
            self.connected_devices = devices
            logger.debug(f"Verbunden Geräte: {devices}")
            return devices
        except Exception as e:
            logger.debug(f"Fehler beim Abrufen der verbundenen Geräte: {e}")
            self.connected_devices = []
            return []

