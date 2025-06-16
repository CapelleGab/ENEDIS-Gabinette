"""
Module de logging pour PMT Analytics.

Author: CAPELLE Gabin
Version: 2.0.0
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class PMTLogger:
    """Gestionnaire de logging pour PMT Analytics."""

    def __init__(self, name: str = "PMTAnalytics"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        """Configure le logger avec les handlers appropriés."""
        if self.logger.handlers:
            return  # Déjà configuré

        self.logger.setLevel(logging.INFO)

        # Format des messages
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler fichier (optionnel)
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            log_file = log_dir / f"pmt_analytics_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception:
            # Si on ne peut pas créer le fichier de log, on continue sans
            pass

    def info(self, message: str):
        """Log un message d'information."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log un avertissement."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log une erreur."""
        self.logger.error(message)

    def debug(self, message: str):
        """Log un message de debug."""
        self.logger.debug(message)

    def success(self, message: str):
        """Log un message de succès."""
        self.logger.info(f"✅ {message}")

    def step(self, message: str):
        """Log une étape de traitement."""
        self.logger.info(f"🔄 {message}")

    def result(self, message: str):
        """Log un résultat."""
        self.logger.info(f"📊 {message}")


# Instance globale du logger
pmt_logger = PMTLogger()

# Fonctions de compatibilité
def get_logger(name: Optional[str] = None) -> PMTLogger:
    """Retourne une instance du logger."""
    if name:
        return PMTLogger(name)
    return pmt_logger
