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