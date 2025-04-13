
class Settings:
    def __init__(self, sqlite):
        try:
            self.__dict__["sqlite"] = sqlite  # Direkt in __dict__ setzen, um __setattr__ zu umgehen
            self.load_settings()  # Einstellungen aus der DB laden
        except Exception as error:
            print (error)

    def load_settings(self):
        """Lädt alle Einstellungen aus der Datenbank und speichert sie als Attribute."""
        try:
            for key, value in self.sqlite.load_user_settings():
                self.__dict__[key] = value  # Direkt in __dict__ setzen, um Endlosschleife zu vermeiden
        except Exception as error:
            print (error)

    def __setattr__(self, key, value):
        """Wird aufgerufen, wenn ein Attribut gesetzt wird -> speichert automatisch in DB."""
        try:
            self.sqlite.save_user_setting(key, value)  # Speichert direkt in die Datenbank
            self.__dict__[key] = value  # Setzt das Attribut normal
        except Exception as error:
            print (error)

    def get_setting(self, key):
        """Wird aufgerufen, wenn ein Attribut gesetzt wird -> speichert automatisch in DB."""
        try:
            return self.__dict__[key]  # Direkt in __dict__ setzen, um Endlosschleife zu vermeiden
        except Exception as error:
            print (error)

