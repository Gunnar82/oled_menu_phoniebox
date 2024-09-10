import logging
import sys

import config.loglevel



def setup_logger(level = config.loglevel.LOGLEVEL):
    # Grundlegende Konfiguration des Loggings
    logging.basicConfig(
        level= level,  # Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format der Log-Nachrichten
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Optional: Konfiguration von Dateihandlern, Konsolenhandlern etc.
    # Beispiel: Log-Nachrichten auch in eine Datei schreiben
    #file_handler = logging.FileHandler('app.log')
    #file_handler.setLevel(logging.INFO)  # Nur INFO und höher in Datei loggen
    #file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # StreamHandler für stdout (Konsole)
    stdout_handler = logging.StreamHandler(sys.stderr)
    stdout_handler.setLevel(level)  # Setzt das Level für diesen Handler

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stdout_handler.setFormatter(formatter)
    # Zum root logger hinzufügen
