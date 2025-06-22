from integrations.settingsclass import Settings

class UserSettings(Settings):
    #BluetoothKopfhoerer
    BLUETOOTH_ENABLED=False
    BLUETOOTH_AUTOCONNECT=False
    BLUETOOTH_ADDR = "00:00:00:00:00:00"
    BLUETOOTH_NAME = "n/a"

    #Firewall-Konfiguration
    FW_AUTO_ENABLED=False

    #Wenn keine Eingabe, dann Fenster zurücl - Timeout in Sekunden
    MENU_TIMEOUT=20

    #Start Bildschirm Timeout
    START_TIMEOUT=5

    #abdunkeln Stufe 1 in Sekunden
    CONTRAST_TIMEOUT=40

    #abdunkeln Stufe 2 in Sekunden
    DARK_TIMEOUT=60

    #Renderzeit bei abdungeln Stufe 1
    CONTRAST_RENDERTIME=3

    #Renderzeit bei abdungeln Stufe 2
    DARK_RENDERTIME=2 #sekunden

    #Renderzeit bei Busy-Screen
    BUSY_RENDERTIME=1


    #Helligkeitswerte
    CONTRAST_FULL=245
    CONTRAST_DARK=64
    CONTRAST_BLACK=20


    #Display ausschalten?
    DISABLE_DISPLAY=True

    #Radiostationen aktualisieren
    UPDATE_RADIO=False

    #Zeige Debuginformationen auf Display
    SHOW_DEBUGINFOS=False

    #Schalte das Gerät bei inaktivität aus in min
    IDLE_POWEROFF=30

    #Schalte das Gerät bei inaktivität aus in min
    IDLE_POWEROFF=30

    #X728
    #Herunterfahren wenn Batterie EMERG erreicht hat ?
    X728_OFF_EMERG=True

    #Wert für EMERG in  %
    X728_BATT_EMERG=1

    #Wert für LOW in %
    X728_BATT_LOW=15


    #Online-Test {ping|url}
    ONLINE_TEST="url"