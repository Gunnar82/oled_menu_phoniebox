""" Playlist menu """
import config.symbols as symbols
import qrcode
import importlib

from luma.core.render import canvas
from ui.listbase import ListBase
from integrations.functions import *
from integrations.webrequest import WebRequest
import config.online as cfg_online
import config.file_folder as cfg_file_folder
import config.services as cfg_services


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

    def __init__(self, windowmanager,loop,usersettings, title,musicmanager):
        super().__init__(windowmanager, loop, usersettings, title)
        self.usersettings = usersettings
        self.refresh_values()
        self.musicmanager=musicmanager

        self.handle_left_key = False
        self.processing = False
        self.totalsize = 0

        # QR-Code generieren
        self.menu.append(["pixel ausrichten","function"])    # 0
        self.menu.append(["","bool","","UPDATE_RADIO"])      # 1
        self.menu.append(["","bool","","DISABLE_DISPLAY"])      # 1
        self.menu.append(["","bool","","SHOW_DEBUGINFOS"])      # 1


        self.menu.append(["","bool","","BLUETOOTH_ENABLED"]) # 2
        self.menu.append(["","bool","","BLUETOOTH_AUTOCONNECT"]) # 3
        self.menu.append(["Firewall","h"])                       # 4
        self.menu.append(["","bool","","FW_AUTO_ENABLED"])  # 5
        self.menu.append(["","func","",self.toggle_firewall,self.generate_fw_status])  # 5


        self.menu.append(["","int","","CONTRAST_FULL"])
        self.menu.append(["","int","","CONTRAST_DARK"])
        self.menu.append(["","int","","CONTRAST_BLACK"])

        self.menu.append(["","int","","MENU_TIMEOUT"])
        self.menu.append(["","int","","CONTRAST_TIMEOUT"])
        self.menu.append(["","int","","DARK_TIMEOUT"])

        if "x728" in settings.INPUTS:
            self.menu.append(["Firewall","h"])
            self.menu.append(["","bool","","X728_OFF_EMERG"])
            self.menu.append(["","int","","X728_BATT_EMERG"])
            self.menu.append(["","int","","X728_BATT_LOW"])
            self.menu.append(["","c"])


        self.menu.append(["WLAN: aus","cmd","","sudo ip link set wlan0 down"])                            # Eintrag 8
        self.menu.append(["WLAN: an","cmd","","sudo ip link set wlan0 up"])                             # Eintrag 9

        self.menu.append(["sudo pip3 install -r requirements.txt", "cmd"])
        self.menu.append(["git pull","cmd"])

        self.menu.append(["Lösche Radiosender","func","",self.musicmanager.delete_radiostations])                   # Eintrag 6

        self.menu.append(["WLAN QR anzeigen","func","",""])                     # Eintrag 18

#        self.menu.append(["Lösche Online-Status Online"])          # Eintrag 5


#        self.menu.append(["","c"])                                     # Eintrag 13
#        self.menu.append(["beenden"])                              # Eintrag 14
#        self.menu.append(["starten"])                              # Eintrag 15
#        self.menu.append(["deaktivieren"])                         # Eintrag 16
#        self.menu.append(["aktivieren"])                           # Eintrag 17

#        self.menu.append(["ssid"])                                 # Eintrag 19
#        self.menu.append(["psk"])                                  # Eintrag 20
#        self.menu.append([""])                                     # Eintrag 21
#        self.menu.append([""])                                     # Eintrag 29

#        self.menu.append(["Dienste neustarten:", "h"])             # Eintrag 36

#        for srv in cfg_services.RESTART_LIST:
#            self.menu.append(srv)

    def activate(self):
        self.cmd = ""
        self.showqr = False
        self.generate_menu()

    def deactivate(self):
        self.showqr = False
        self.qrimage = None

    def exec_command(self):
        logger.debug(f"cmd: {self.cmd}")
        try:
            self.append_busytext(str(self.cmd).replace('\n',''))
            result = []
            if run_command(self.cmd,results=result) == True:
                self.append_busydebug(str(result))
                self.append_busytext("Erfolgreich!")
            else:
                text = check_results_list(result)

                logger.debug(f"exec_command: FAILED: {text}")
                self.append_busyerror(str(text))
        except Exception as error:
            self.append_busyerror(error)


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
        elif self.position >=1:
            entry = self.menu[self.position]
            if entry[1] == "bool":
                setattr(self.usersettings,entry[3],not getattr(self.usersettings,entry[3]))

            elif entry[1] == "int":
                value = self.windowmanager.getValue(vmin=1,vmax=255,vstep=1,startpos=getattr(self.usersettings,entry[3]))
                setattr(self.usersettings,entry[3],value)

            elif entry[1] == "cmd":
                self.cmd = entry[0]
                self.loop.run_in_executor(None,self.exec_command)
            elif entry[1] == "func":
                try:
                    function = entry[3]
                    if callable(function):
                        self.append_busytext(function.__name__)
                        function()
                    else:
                        self.append_busyerror("nicht ausführbar")
                except Exception as error:
                    self.append_busyerror(error)


        self.generate_menu()

        self.append_busytext("Abgeschlossen!")
        time.sleep(2)
        self.refresh_values()
        self.processing = False
        self.set_window_busy(False,wait=5)


        return

        if self.position == 20:
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

            value = self.windowmanager.getValue(vmin=vmin,vmax=vmax,startpos=startpos, unit="sec")
            logger.debug(f"got value: {value}")

        elif self.position > 36:
            self.cmd = "sudo systemctl restart %s" % (self.menu[self.position][0])

        logger.debug(f"cmd: {self.cmd}")


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

                #self.menu[28] = ["CONTRAST_FULL: %d" % (self.usersettings.CONTRAST_FULL)]
                #self.menu[29] = ["CONTRAST_DARK: %d" % (self.usersettings.CONTRAST_DARK)]
                #self.menu[30] = ["CONTRAST_BLACK: %d" % (self.usersettings.CONTRAST_BLACK)]

                #self.menu[32] = ["MENU_TIMEOUT: %d" % (self.usersettings.MENU_TIMEOUT)]
                #self.menu[33] = ["CONTAST_TIMEOUT: %d" % (self.usersettings.CONTRAST_TIMEOUT)]
                #self.menu[34] = ["DARK_TIMEOUT: %d" % (self.usersettings.DARK_TIMEOUT)]

                #if not self.hostapd_status is None: self.menu[19] = [f"hostapd (aktiviert: {self.hostapd_status}):", "h"]
                #if not self.hostapd_ssid is None: self.menu[25] = [self.hostapd_ssid]
                #if not self.hostapd_psk is None: self.menu[26] = [self.hostapd_psk]

                super().render()
        else:
            try:
                with canvas(self.device) as draw:
                    draw.bitmap(((settings.DISPLAY_WIDTH - self.qr_width) // 2,0), self.qrimage)
            except:
                self.showqr = False

    def generate_menu(self):
        try:
            for idx, entry in enumerate(self.menu):
                try:
                    if len(entry) > 4:
                        if callable(entry[4]):
                            funktion = entry[4]
                            self.menu[idx][0] = funktion()
                except Exception as error:
                    print (error)

                if entry[1] == "bool":
                    self.menu[idx][0] = self.generate_bool_text(entry[3])

                elif entry[1] == "int":
                    self.menu[idx][0] = self.generate_int_text(entry[3])
        except Exception as error:
            print (f"render rr: {error}")

    def toggle_firewall(self):
        if "deny" not in self.firewall_status: enable_firewall()
        else: disable_firewall()



    def generate_bool_text(self,key):
        value = getattr(self.usersettings,key)

        return ("%s is %s > %s" % (key, value, not value ))

    def generate_int_text(self,key):
        value = getattr(self.usersettings,key)

        return ("%s is %d" % (key, value ))

    def generate_fw_status(self):
        if "deny" not in self.firewall_status:
            return "Firewall ist AUS > EIN"
        else: 
            return "Firewall ist EIN > AUS"

