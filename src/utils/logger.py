"""
Système de logging centralisé pour La Gabinette
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from src.config.settings import LOGGING_CONFIG


class Logger:
    """Gestionnaire de logging centralisé"""

    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self) -> None:
        """Configure le logger principal"""
        self._logger = logging.getLogger("PMTAnalytics")
        self._logger.setLevel(getattr(logging, LOGGING_CONFIG["level"]))

        # Éviter la duplication des handlers
        if not self._logger.handlers:
            # Handler pour fichier avec rotation
            file_handler = logging.handlers.RotatingFileHandler(
                LOGGING_CONFIG["file"],
                maxBytes=LOGGING_CONFIG["max_bytes"],
                backupCount=LOGGING_CONFIG["backup_count"],
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)

            # Handler pour console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # Formatter
            formatter = logging.Formatter(LOGGING_CONFIG["format"])
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Ajouter les handlers
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

    def get_logger(self, name: str = None) -> logging.Logger:
        """Retourne un logger avec le nom spécifié"""
        if name:
            return logging.getLogger(f"PMTAnalytics.{name}")
        return self._logger

    def debug(self, message: str) -> None:
        """Log un message de debug"""
        self._logger.debug(message)

    def info(self, message: str) -> None:
        """Log un message d'information"""
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log un message d'avertissement"""
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log un message d'erreur"""
        self._logger.error(message)

    def critical(self, message: str) -> None:
        """Log un message critique"""
        self._logger.critical(message)


# Instance globale du logger
logger = Logger()
 