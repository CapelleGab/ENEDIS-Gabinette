"""
Configuration globale de l'application La Gabinette
"""

import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
SAMPLES_DIR = DATA_DIR / "samples"
LOGS_DIR = BASE_DIR / "logs"

# Créer les répertoires s'ils n'existent pas
for directory in [DATA_DIR, INPUT_DIR, OUTPUT_DIR, SAMPLES_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Configuration CSV
CSV_SEPARATOR = ";"
CSV_ENCODING = "latin1"  # ISO-8859-1

# Colonnes attendues dans le CSV (ordre exact)
EXPECTED_COLUMNS = [
    "UM", "UM (Lib)", "DUM", "DUM (Lib)", "SDUM", "SDUM (Lib)", "FSDUM", "FSDUM (Lib)",
    "Dom.", "Dom.(Lib)", "SDom", "SDom.(Lib)", "Equipe", "Equipe (Lib.)",
    "NNI", "Nom", "Prénom", "Jour", "Désignation jour", "Jour férié",
    "Fin cycle", "Astreinte", "Astr. Occas.", "HT", "De", "à", "De", "à",
    "HTM", "De", "à", "De", "à", "HE", "De", "à", "De", "à",
    "Code", "Désignation code", "Valeur", "Dés. unité", "Heure début", "Heure fin"
]

# Valeurs possibles pour certaines colonnes
VALID_VALUES = {
    "UM (Lib)": ["DR PARIS"],
    "Equipe (Lib.)": ["PV IT ASTREINTE"],
    "Désignation jour": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
    "Jour férié": ["X", ""],
    "Astreinte": ["I", ""],
    "HT": ["J", ""],
    "Code": ["D"],
    "Dés. unité": ["Heure(s)", "Jour(s)"]
}

# Configuration de l'interface utilisateur
UI_CONFIG = {
    "window_title": "La Gabinette",
    "window_size": "1200x800",
    "theme": "cosmo",  # Theme ttkbootstrap
    "font_family": "Segoe UI",
    "font_size": 10
}

# Configuration du logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "pmt_analytics.log",
    "max_bytes": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Configuration des exports
EXPORT_CONFIG = {
    "default_format": "xlsx",
    "supported_formats": ["xlsx", "csv", "json"],
    "date_format": "%d/%m/%Y",
    "time_format": "%H:%M:%S"
}


