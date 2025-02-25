
class Settings:
    def __init__(self, sqlite):
        self.__dict__["sqlite"] = sqlite  # Direkt in __dict__ setzen, um __setattr__ zu umgehen
        print (sqlite)
        self.load_settings()  # Einstellungen aus der DB laden

    def load_settings(self):
        """Lädt alle Einstellungen aus der Datenbank und speichert sie als Attribute."""
        for key, value in self.sqlite.load_user_settings():
            self.__dict__[key] = value  # Direkt in __dict__ setzen, um Endlosschleife zu vermeiden

    def __setattr__(self, key, value):
        """Wird aufgerufen, wenn ein Attribut gesetzt wird -> speichert automatisch in DB."""
        self.sqlite.save_user_setting(key, value)  # Speichert direkt in die Datenbank
        self.__dict__[key] = value  # Setzt das Attribut normal

