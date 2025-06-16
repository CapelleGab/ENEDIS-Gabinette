"""
Configuration du projet PMT Analytics.
Centralise tous les paramètres et constantes du projet.

Author: CAPELLE Gabin
Version: 2.0.0
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
from pathlib import Path


class WeekDays(Enum):
    """Énumération des jours de la semaine."""
    MONDAY = "Lundi"
    TUESDAY = "Mardi"
    WEDNESDAY = "Mercredi"
    THURSDAY = "Jeudi"
    FRIDAY = "Vendredi"
    SATURDAY = "Samedi"
    SUNDAY = "Dimanche"


class SheetNames(Enum):
    """Noms des feuilles Excel de sortie."""
    ASTREINTE_STATS = 'ASTREINTE_STATS'
    ASTREINTE_MOYENNES = 'ASTREINTE_EQUIPES_MOYENNES'
    TIP_STATS = 'TIP_STATS'
    TIP_MOYENNES = 'TIP_EQUIPES_MOYENNES'
    STATS_3X8 = '3x8_STATS'
    MOYENNES_3X8 = '3x8_EQUIPES_MOYENNES'
    AUTRES = 'AUTRES'


@dataclass(frozen=True)
class FileConfig:
    """Configuration des fichiers."""
    year: str = '2024'
    csv_encoding: str = 'latin1'
    csv_separator: str = ';'

    @property
    def csv_filename(self) -> str:
        """Nom du fichier CSV par défaut."""
        return f'Planning_journalier_{self.year}.csv'

    @property
    def excel_filename(self) -> str:
        """Nom du fichier Excel de sortie."""
        return f'Statistiques_PMT_{self.year}.xlsx'


@dataclass(frozen=True)
class TimeConfig:
    """Configuration des horaires."""
    reference_start: str = '07:30:00'
    reference_end: str = '16:15:00'
    standard_work_hours: float = 8.0

    @property
    def weekend_days(self) -> List[str]:
        """Jours de weekend à exclure."""
        return [WeekDays.SATURDAY.value, WeekDays.SUNDAY.value]


@dataclass(frozen=True)
class TeamConfig:
    """Configuration des équipes."""

    @property
    def astreinte_teams(self) -> List[str]:
        """Équipes d'astreinte."""
        return [
            'PV IT ASTREINTE',
            'PV B ASTREINTE',
            'PV G ASTREINTE',
            'PV PE ASTREINTE'
        ]

    @property
    def non_astreinte_teams(self) -> List[str]:
        """Équipes hors astreinte (TIP)."""
        return [
            'PV B SANS ASTREINTE',
            'PV B TERRAIN',
            'PV IT SANS ASTREINTE',
            'PF IT TERRAIN',
            'PV G SANS ASTREINTE',
            'PV G CLI/TRAVAUX',
            'PV G POLE RIP',
            'PV PE SANS ASTREINTE',
            'PF PE TERRAIN'
        ]

    @property
    def all_teams(self) -> List[str]:
        """Toutes les équipes."""
        return self.astreinte_teams + self.non_astreinte_teams


@dataclass(frozen=True)
class ColumnConfig:
    """Configuration des colonnes de sortie."""

    @property
    def final_columns(self) -> List[str]:
        """Colonnes finales pour l'export Excel."""
        return [
            'Nom', 'Prénom', 'Équipe', 'Jours_Présents_Complets',
            'Jours_Partiels', 'Total_Jours_Travaillés', 'Total_Heures_Travaillées',
            'Jours_Complets', 'Jours_Absents', 'Total_Heures_Absence',
            'Présence_%_365j',
            'Heures_Supp',
            'Nb_Périodes_Arrêts', 'Nb_Jours_Arrêts_41', 'Nb_Jours_Arrêts_5H',
            'Moy_Heures_Par_Arrêt_Maladie'
        ]

    @property
    def required_csv_columns(self) -> List[str]:
        """Colonnes requises dans le fichier CSV d'entrée."""
        return ['Nom', 'Prénom', 'Equipe (Lib.)', 'Jour', 'Valeur']

    @property
    def sheet_names_mapping(self) -> Dict[str, str]:
        """Mapping des noms de feuilles."""
        return {
            'statistiques': SheetNames.ASTREINTE_STATS.value,
            'moyennes': SheetNames.ASTREINTE_MOYENNES.value,
            'tip_statistiques': SheetNames.TIP_STATS.value,
            'tip_moyennes': SheetNames.TIP_MOYENNES.value,
            '3x8_statistiques': SheetNames.STATS_3X8.value,
            '3x8_moyennes': SheetNames.MOYENNES_3X8.value,
            'arrets_maladie': SheetNames.AUTRES.value
        }


class AppConfig:
    """Configuration principale de l'application."""

    def __init__(self):
        self.files = FileConfig()
        self.time = TimeConfig()
        self.teams = TeamConfig()
        self.columns = ColumnConfig()

    @property
    def version(self) -> str:
        """Version de l'application."""
        return "2.0.0"

    @property
    def app_name(self) -> str:
        """Nom de l'application."""
        return "PMT Analytics"


# Instance globale de configuration
config = AppConfig()

# Rétrocompatibilité avec l'ancienne API
ANNEE = config.files.year
FICHIER_CSV = config.files.csv_filename
FICHIER_EXCEL = config.files.excel_filename
CODES_EQUIPES_ASTREINTE = config.teams.astreinte_teams
CODES_EQUIPES_HORS_ASTREINTE = config.teams.non_astreinte_teams
JOURS_WEEKEND = config.time.weekend_days
HORAIRE_DEBUT_REFERENCE = config.time.reference_start
HORAIRE_FIN_REFERENCE = config.time.reference_end
CSV_ENCODING = config.files.csv_encoding
CSV_SEPARATOR = config.files.csv_separator
COLONNES_FINALES = config.columns.final_columns
NOMS_FEUILLES = config.columns.sheet_names_mapping
