""" Playlist menu """
import config.symbols as symbols
import qrcode
import importlib

from luma.core.render import canvas
from ui.listbase import ListBase
from integrations.playout import *  # Wenn notwendig, ansonsten spezifisch importieren
from integrations.functions import *
from integrations.webrequest import WebRequest
import config.online as cfg_online
import config.file_folder as cfg_file_folder
import config.services as cfg_services
import config.user_settings


from integrations.logging_config import *

logger = setup_logger(__name__)


class SystemMenu(ListBase):

    qr_width = settings.DISPLAY_HEIGHT if settings.DISPLAY_HEIGHT < settings.DISPLAY_WIDTH else settings.DISPLAY_WIDTH
    timeout = False
    busysymbol = symbols.SYMBOL_ZAHNRAD
    pixeltest = False

    def create_qr(self):

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=12,
            border=1,
        )

    
        ssid = self.hostapd_ssid.split('=',1)[1]
        psk = self.hostapd_psk.split('=',1)[1]
        wifi_format = f"WIFI:T:WPA;S:{ssid};P:{psk};H:false;;"
        qr.add_data(wifi_format)
        qr.make(fit=True)
        img = None
        img = qr.make_image(fill='black', back_color='white')
        return img.resize((self.qr_width,self.qr_width))

    def refresh_values(self):
        self.firewall_status = str(get_firewall_state())
        self.hostapd_status = get_hostapd_file_status()
        self.hostapd_ssid = get_hostapd_ssid()
        self.hostapd_psk = get_hostapd_psk()
        self.firewall_status = str(get_firewall_state())

    def __init__(self, windowmanager,loop,title):
        super().__init__(windowmanager, loop, title)
        self.refresh_values()

        self.handle_left_key = False
        self.processing = False
        self.totalsize = 0

        # QR-Code generieren
        self.menu.append("pixel ausrichten")             # Eitnrag 0
        self.menu.append("PLACEHOLDER UPDATE_RADIO 2")             # Eitnrag 1

        self.menu.append(["Lösche Online-Ordner"])                 # Eintrag 2
        self.menu.append(["Lösche Online-Status Online"])          # Eintrag 3

        self.menu.append(["Lösche Hörspielstatus"])                # Eintrag 4
        self.menu.append(["Lösche Musikstatus"])                   # Eintrag 5
        self.menu.append(["Lösche Radiostatus"])                   # Eintrag 6

        self.menu.append(["Update OLED"])                          # Eintrag 7

        self.menu.append(["WLAN: aus"])                            # Eintrag 8
        self.menu.append(["WLAN: an"])                             # Eintrag 9

        self.menu.append(["PLACEHOLDER AUTO_ENABLE 1"])            # Eintrag 10
        self.menu.append(["PLACEHOLDER AUTO_ENABLE 2"])            # Eintrag 11
        self.menu.append([""])                                     # Eintrag 12

        self.menu.append(["PLACEHOLDER FIREWALL_STATUS 1"])        # Eintrag 13
        self.menu.append(["PLACEHOLDER FIREWALL_STATUS 2"])        # Eintrag 14
        self.menu.append(["","c"])                                     # Eintrag 15

        self.menu.append(["PLACEHOLDER BLUETOOTH_AUTOCONNECT 1"])  # Eintrag 16
        self.menu.append(["PLACEHOLDER BLUETOOTH_AUTOCONNECT 2"])  # Eintrag 17
        self.menu.append(["","c"])                                     # Eintrag 18

        self.menu.append([""])                                     # Eintrag 19

        self.menu.append(["beenden"])                              # Eintrag 20
        self.menu.append(["starten"])                              # Eintrag 21
        self.menu.append(["deaktivieren"])                         # Eintrag 22
        self.menu.append(["aktivieren"])                           # Eintrag 23

        self.menu.append(["WLAN QR anzeigen"])                     # Eintrag 24
        self.menu.append(["ssid"])                                 # Eintrag 25
        self.menu.append(["psk"])                                  # Eintrag 26
        self.menu.append([""])                                     # Eintrag 27
        self.menu.append(["PLACEHOLDER CONTRAST_FULL"])            # Eintrag 28
        self.menu.append(["PLACEHOLDER CONTRAST_DARK"])            # Eintrag 29
        self.menu.append(["PLACEHOLDER CONTRASST_BLACK"])          # Eintrag 30
        self.menu.append([""])                                     # Eintrag 31
        self.menu.append(["PLACEHOLDER MENU_TIMEOUT"])             # Eintrag 32
        self.menu.append(["PLACEHOLDER CONTRAST_TIMEOUT"])         # Eintrag 33
        self.menu.append(["PLACEHOLDER DARK_TIMEOUT"])             # Eintrag 34
        self.menu.append([""])                                     # Eintrag 35

        self.menu.append(["Dienste neustarten:", "h"])             # Eintrag 36

        for srv in cfg_services.RESTART_LIST:
            self.menu.append(srv)

    def activate(self):
        self.cmd = ""
        self.showqr = False

    def deactivate(self):
        self.showqr = False
        self.qrimage = None

    def exec_command(self):
        logger.debug(f"cmd: {self.cmd}")
        try:
            self.processing = True
            if self.position == 3:
                try:
                    url = f"{cfg_online.ONLINE_SAVEPOS}deletepos.php?confirm=true"

                    logger.debug(f"Verzeichnis-URL: {url}")
                    self.append_busytext(self.menu[self.position][0])

                    response = WebRequest(url).get_response_text().splitlines()
                    logger.debug(f"response: {response}")
                    self.append_busytext("")
                    for line in response:
                        if line.startswith('DELOK'): self.append_busytext(line,reuse_last=True)
                        else: self.append_busyerror(line)
                except Exception as error:
                    logger.debug(f"exec_command: {error}")
                    self.append_busyerror(error)
            elif self.position == 14:
                if "deny" not in self.firewall_status: enable_firewall()
                else: disable_firewall()
            else:
                self.append_busytext(self.menu[self.position][0])
                self.append_busytext(str(self.cmd).replace('\n',''))
                result = []
                if run_command(self.cmd,results=result) == True:
                    self.append_busytext("Erfolgreich!")
                else:
                    text = check_results_list(result)

                    logger.debug(f"exec_command: FAILED: {text}")
                    self.append_busyerror(str(text))
        except Exception as error:
            self.append_busyerror(error)
        finally:
            self.append_busytext("Abgeschlossen!")
            time.sleep(2)
            importlib.reload(config.user_settings)

            self.refresh_values()
            self.processing = False
            self.set_window_busy(False,wait=5)


    def push_handler(self,button = '*'):
        if self.showqr:
            self.showqr = False
            self.timeout = True
            self.contrasthandle = True

            return

        if self.pixeltest:
            self.pixeltest = False

            return

        self.cmd = ""

        self.set_window_busy()
        self.append_busytext()

        if self.position == 0 and not self.pixeltest:
            self.pixeltest = True
        if self.position == 1:
            self.cmd = self.set_option("UPDATE_RADIO",not config.user_settings.UPDATE_RADIO,cfg_file_folder.FILE_USER_SETTINGS)

        elif self.position == 2:
            delete_local_online_folder()

        elif self.position >= 4 and self.position <= 6:
            if self.position == 4:
                what = cfg_file_folder.FILE_LAST_HOERBUCH
            elif self.position == 5:
                what = cfg_file_folder.FILE_LAST_MUSIC
            elif self.position == 6:
                what = cfg_file_folder.FILE_LAST_RADIO
            self.cmd = f"sudo rm {what}"


        elif self.position == 7:

            self.cmd = ["git pull", "sudo pip3 install -r requirements.txt", "sudo systemctl restart oled"]

        elif self.position == 8:
            self.cmd = "sudo ip link set wlan0 down"

        elif self.position == 9:
            self.cmd = "sudo ip link set wlan0 up"

        elif self.position == 11:
            self.cmd = self.set_option("AUTO_ENABLED",not config.user_settings.AUTO_ENABLED,cfg_file_folder.FILE_USER_SETTINGS)

        elif self.position == 17:
            self.cmd = self.set_option("BLUETOOTH_AUTOCONNECT",not config.user_settings.BLUETOOTH_AUTOCONNECT,cfg_file_folder.FILE_USER_SETTINGS)

        elif self.position == 20:
            self.cmd = "sudo systemctl stop hostapd"

        elif self.position == 21:
            self.cmd = "sudo systemctl start hostapd"

        elif self.position == 22:
            self.cmd = "echo \"disabled\" > /home/pi/oledctrl/oled/config/hotspot"

        elif self.position == 23:
            self.cmd = "echo \"enabled\" > /home/pi/oledctrl/oled/config/hotspot"
        elif self.position == 24:
            self.showqr = True
            self.timeout = False
            self.contrasthandle = False

            self.qrimage = self.create_qr()

        elif self.position == 25:
            self.cmd = "sudo sed -i \"s/^ssid=.*/ssid=pb_`tr -dc 'A-Za-z0-9' </dev/urandom | head -c 7`/\" \"/etc/hostapd/hostapd.conf\""

        elif self.position == 26:
            self.cmd = "sudo sed -i \"s/^wpa_passphrase=.*/wpa_passphrase=`tr -dc 'A-Za-z0-9' </dev/urandom | head -c 10`/\" \"/etc/hostapd/hostapd.conf\""

        elif self.position >= 28 and self.position <= 30:
            logger.debug(f"Started CONTRAST Setting {self.menu[self.position]}")
            if self.position == 28: startpos = config.user_settings.CONTRAST_FULL
            elif self.position == 29: startpos = config.user_settings.CONTRAST_DARK
            elif self.position == 30: startpos = config.user_settings.CONTRAST_BLACK

            value = self.windowmanager.getValue(vmin=1,vmax=255,vstep=3,startpos=startpos)
            logger.debug(f"got value: {value}")

            if self.position == 28: self.cmd = self.set_option("CONTRAST_FULL",value,cfg_file_folder.FILE_USER_SETTINGS)
            elif self.position == 29: self.cmd = self.set_option("CONTRAST_DARK",value,cfg_file_folder.FILE_USER_SETTINGS)
            else: self.cmd = self.set_option("CONTRAST_BLACK",value,cfg_file_folder.FILE_USER_SETTINGS)

        elif self.position >= 32 and self.position <= 34:
            logger.debug(f"Started CONTRAST Setting {self.menu[self.position]}")
            if self.position == 32:
                startpos = config.user_settings.MENU_TIMEOUT
                vmin = 5
                vmax = 100
            elif self.position == 33:
                startpos = config.user_settings.CONTRAST_TIMEOUT
                vmin = 5
                vmax = config.user_settings.DARK_TIMEOUT - 1
            elif self.position == 34:
                vmin = config.user_settings.CONTRAST_TIMEOUT + 1
                vmax = 300
                startpos = config.user_settings.DARK_TIMEOUT

            value = self.windowmanager.getValue(vmin=vmin,vmax=vmax,startpos=startpos, unit="sec")
            logger.debug(f"got value: {value}")

            if self.position == 32: self.cmd = self.set_option("MENU_TIMEOUT",value,cfg_file_folder.FILE_USER_SETTINGS)
            elif self.position == 33: self.cmd = self.set_option("CONTRAST_TIMEOUT",value,cfg_file_folder.FILE_USER_SETTINGS)
            else:
               value = max(value, config.user_settings.CONTRAST_TIMEOUT + 1)
               self.cmd = self.set_option("DARK_TIMEOUT",value,cfg_file_folder.FILE_USER_SETTINGS)

        elif self.position > 36:
            self.cmd = "sudo systemctl restart %s" % (self.menu[self.position][0])

        logger.debug(f"cmd: {self.cmd}")
        self.loop.run_in_executor(None,self.exec_command)


    def set_option(self,option,value,filename):
        command = f"grep -q '{option}=' {filename} && sed -i 's/{option}=[^ ]*/{option}={value}/g' {filename} || {{ echo '\n{option}={value}\n' >> {filename}; }}"
        logger.debug(f"set_option: {command}")
        return command


    def render(self):
        if self.pixeltest:
            try:
                with canvas(self.device) as draw:
                    outer_x1, outer_y1 = 0, 0
                    outer_x2, outer_y2 = settings.DISPLAY_WIDTH, settings.DISPLAY_HEIGHT

                    draw.rectangle([outer_x1, outer_y1, outer_x2, outer_y2], outline="blue", fill="blue")

                    # Inneres Rechteck (gelb, innerhalb der blauen Umrandung)
                    inner_x1 = outer_x1 + 10  # Offset von 2 Pixeln für die Wandstärke
                    inner_y1 = outer_y1 + 10
                    inner_x2 = outer_x2 - 10
                    inner_y2 = outer_y2 - 10
                    draw.rectangle([inner_x1, inner_y1, inner_x2, inner_y2], outline="yellow", fill="yellow")
            except:
                self.pixetest = False

        elif not self.showqr:
            try:
                self.menu[1]  = ["Radio ist %s - setze auf %s" % ("EIN" if config.user_settings.UPDATE_RADIO else "AUS","EIN" if not config.user_settings.UPDATE_RADIO else "AUS")]

                self.menu[10] = ["Firewall AUTO_ENABLED ist %s" % ("EIN" if config.user_settings.AUTO_ENABLED else "AUS"),"h"]
                self.menu[11]  = ["setze auf %s" % ("EIN" if not config.user_settings.AUTO_ENABLED else "AUS")]

                self.menu[13] = ["Firewall Status: %s " % ("AUS" if "deny" not in self.firewall_status else "EIN"),"h"]
                self.menu[14]  = ["setze auf %s" % ("AUS" if "deny" in self.firewall_status else "EIN")]

                self.menu[16] = ["Bluetooth_Autoconnect ist %s" % ("EIN" if config.user_settings.BLUETOOTH_AUTOCONNECT else "AUS"),"h"]
                self.menu[17]  = ["setze auf %s" % ("EIN" if not config.user_settings.BLUETOOTH_AUTOCONNECT else "AUS")]

                self.menu[28] = ["CONTRAST_FULL: %d" % (config.user_settings.CONTRAST_FULL)]
                self.menu[29] = ["CONTRAST_DARK: %d" % (config.user_settings.CONTRAST_DARK)]
                self.menu[30] = ["CONTRAST_BLACK: %d" % (config.user_settings.CONTRAST_BLACK)]

                self.menu[32] = ["MENU_TIMEOUT: %d" % (config.user_settings.MENU_TIMEOUT)]
                self.menu[33] = ["CONTAST_TIMEOUT: %d" % (config.user_settings.CONTRAST_TIMEOUT)]
                self.menu[34] = ["DARK_TIMEOUT: %d" % (config.user_settings.DARK_TIMEOUT)]

                if not self.hostapd_status is None: self.menu[19] = [f"hostapd (aktiviert: {self.hostapd_status}):", "h"]
                if not self.hostapd_ssid is None: self.menu[25] = [self.hostapd_ssid]
                if not self.hostapd_psk is None: self.menu[26] = [self.hostapd_psk]

                super().render()
            except:
                pass
        else:
            try:
                with canvas(self.device) as draw:
                    draw.bitmap(((settings.DISPLAY_WIDTH - self.qr_width) // 2,0), self.qrimage)
            except:
                self.showqr = False
