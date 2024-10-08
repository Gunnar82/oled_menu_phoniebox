import logging
import sys
import os
import config.loglevel

lvlDEBUG = logging.DEBUG
lvlINFO = logging.INFO
lvlWARN = logging.WARNING
lvlERROR = logging.ERROR


# Globale Variable, um Debug-Module zu verwalten
DEBUG_MODULES = []

def setup_logger(module_name,default_level = config.loglevel.LOGLEVEL):
    if 'INVOCATION_ID' in os.environ:
        level = logging.ERROR
    else:
        # Prüfen, ob das aktuelle Modul im Debug-Level laufen soll
        if module_name in DEBUG_MODULES:
            level = logging.DEBUG
        else:
            level = default_level
    # Grundlegende Konfiguration des Loggings
    logger = logging.getLogger(module_name)
    #logging.basicConfig(
    #    level= level,  # Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    #    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format der Log-Nachrichten
    #    datefmt='%Y-%m-%d %H:%M:%S'
    #)
    logger.setLevel(level)

    # Optional: Konfiguration von Dateihandlern, Konsolenhandlern etc.
    # Beispiel: Log-Nachrichten auch in eine Datei schreiben
    #file_handler = logging.FileHandler('app.log')
    #file_handler.setLevel(logging.INFO)  # Nur INFO und höher in Datei loggen
    #file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # StreamHandler für stdout (Konsole)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)  # Setzt das Level für diesen Handler

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
     # Vermeide doppelte Handler
    if not logger.handlers:
        logger.addHandler(handler)
    else:
        print ("logger vorhanden")
    
    return logger


def configure_debug_modules(modules):
    global DEBUG_MODULES
    DEBUG_MODULES = modules
