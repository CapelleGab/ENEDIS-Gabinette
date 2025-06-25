"""
Point d'entrée principal de l'application La Gabinette
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.main_window import MainWindow
from src.utils.logger import logger
from src.config.settings import UI_CONFIG


def main():
    """Fonction principale de l'application"""
    try:
        # Initialiser le logger
        app_logger = logger.get_logger("Main")
        app_logger.info("=" * 50)
        app_logger.info("DÉMARRAGE DE LA GABINETTE")
        app_logger.info("=" * 50)

        # Créer et lancer l'interface utilisateur
        app = MainWindow()
        app.run()

        app_logger.info("Application fermée normalement")

    except Exception as e:
        error_msg = f"Erreur critique lors du démarrage de l'application: {str(e)}"
        print(error_msg)

        # Essayer de logger l'erreur si possible
        try:
            logger.critical(error_msg)
        except:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()
