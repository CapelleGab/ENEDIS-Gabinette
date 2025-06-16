"""
Module de calcul des statistiques PMT.

Author: CAPELLE Gabin
Version: 2.0.0
"""

import pandas as pd
import logging
from typing import Optional
from dataclasses import dataclass

from .exceptions import CalculationError

logger = logging.getLogger(__name__)


@dataclass
class WorkHoursResult:
    """Résultat du calcul des heures travaillées."""
    hours_worked: float
    is_full_day: bool
    is_partial_day: bool
    is_absent: bool


class WorkHoursCalculator:
    """Calculateur d'heures travaillées."""

    FULL_DAY_HOURS = 8.0
    SPECIAL_CODES = {
        '80TH': FULL_DAY_HOURS
    }

    def calculate_hours_worked(self, row: pd.Series) -> WorkHoursResult:
        """
        Calcule les heures travaillées selon la logique métier.

        Args:
            row: Ligne du DataFrame

        Returns:
            WorkHoursResult avec les détails du calcul
        """
        try:
            code = self._get_clean_code(row)
            value = self._get_numeric_value(row)
            unit = self._get_unit(row)

            # Cas spéciaux par code
            if code in self.SPECIAL_CODES:
                hours = self.SPECIAL_CODES[code]
                return WorkHoursResult(hours, True, False, False)

            # Si on a un code d'absence
            if code:
                if value is not None and value >= 0:
                    hours = self._calculate_hours_with_unit(value, unit)
                    is_absent = hours == 0
                    is_full = hours == self.FULL_DAY_HOURS
                    is_partial = not is_absent and not is_full
                    return WorkHoursResult(hours, is_full, is_partial, is_absent)
                else:
                    # Code sans valeur = absence complète
                    return WorkHoursResult(0.0, False, False, True)

            # Pas de code = journée complète
            return WorkHoursResult(self.FULL_DAY_HOURS, True, False, False)

        except Exception as e:
            logger.warning(f"Erreur calcul heures travaillées: {e}, utilisation valeur par défaut")
            return WorkHoursResult(self.FULL_DAY_HOURS, True, False, False)

    def _get_clean_code(self, row: pd.Series) -> str:
        """Extrait et nettoie le code de la ligne."""
        code = row.get('Code', '')
        if pd.notna(code) and str(code).strip():
            return str(code).strip().upper()
        return ''

    def _get_numeric_value(self, row: pd.Series) -> Optional[float]:
        """Extrait la valeur numérique de la ligne."""
        value = row.get('Valeur')
        if pd.notna(value) and value != '':
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    def _get_unit(self, row: pd.Series) -> str:
        """Extrait l'unité de la ligne."""
        unit = row.get('Dés. unité', '')
        if pd.notna(unit):
            return str(unit).strip().lower()
        return ''

    def _calculate_hours_with_unit(self, value: float, unit: str) -> float:
        """Calcule les heures en fonction de la valeur et de l'unité."""
        if 'jour' in unit:
            # Valeur en jours travaillés
            hours = value * self.FULL_DAY_HOURS
            return min(self.FULL_DAY_HOURS, hours)
        elif 'heure' in unit:
            # Valeur en heures travaillées
            return min(self.FULL_DAY_HOURS, value)
        else:
            # Valeur en heures d'absence (comportement par défaut)
            hours = self.FULL_DAY_HOURS - value
            return max(0, hours)


class StatisticsCalculator:
    """Calculateur de statistiques pour les employés."""

    def __init__(self):
        self.hours_calculator = WorkHoursCalculator()

    def calculate_employee_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule les statistiques pour chaque employé.

        Args:
            df: DataFrame filtré avec les données employés

        Returns:
            DataFrame avec les statistiques par employé
        """
        if df.empty:
            logger.warning("DataFrame vide pour le calcul des statistiques")
            return pd.DataFrame()

        try:
            logger.info(f"Calcul des statistiques pour {df['Gentile'].nunique()} employés")

            # Calculer les heures travaillées
            df_calc = df.copy()
            work_results = df_calc.apply(self.hours_calculator.calculate_hours_worked, axis=1)

            # Extraire les résultats
            df_calc['Heures_Travaillees'] = [r.hours_worked for r in work_results]
            df_calc['Est_Jour_Complet'] = [r.is_full_day for r in work_results]
            df_calc['Est_Jour_Partiel'] = [r.is_partial_day for r in work_results]
            df_calc['Est_Absent'] = [r.is_absent for r in work_results]
            df_calc['Jours_Travailles'] = df_calc['Heures_Travaillees'] / 8.0

            # Grouper par employé
            group_columns = self._get_grouping_columns(df_calc)

            stats = df_calc.groupby(group_columns).agg(
                Nb_Jours_Complets=('Est_Jour_Complet', 'sum'),
                Nb_Jours_Partiels=('Est_Jour_Partiel', 'sum'),
                Nb_Jours_Absents=('Est_Absent', 'sum'),
                Nb_Jours_Presents=('Est_Jour_Complet', 'sum'),  # Seuls les jours complets
                Total_Jours_Travailles=('Jours_Travailles', 'sum'),
                Total_Heures_Travaillees=('Heures_Travaillees', 'sum'),
                Total_Heures_Absence=('Heures_Travaillees', lambda x: sum(8.0 - x))
            ).reset_index()

            # Calculer le pourcentage de présence
            stats['Presence_Pourcentage_365j'] = (
                stats['Nb_Jours_Presents'] / 365 * 100
            ).round(2)

            # Arrondir les valeurs
            stats['Total_Jours_Travailles'] = stats['Total_Jours_Travailles'].round(2)

            logger.info(f"Statistiques calculées pour {len(stats)} employés")
            return stats

        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            raise CalculationError(f"Impossible de calculer les statistiques: {e}")

    def calculate_team_averages(self, df_stats: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule les moyennes par équipe.

        Args:
            df_stats: DataFrame avec les statistiques par employé

        Returns:
            DataFrame avec les moyennes par équipe
        """
        if df_stats.empty:
            logger.warning("Aucune statistique pour calculer les moyennes d'équipe")
            return pd.DataFrame()

        try:
            logger.info("Calcul des moyennes par équipe")

            moyennes = df_stats.groupby('Équipe').agg(
                Nb_Employés=('Nom', 'count'),
                Moy_Jours_Présents_Complets=('Jours_Présents_Complets', 'mean'),
                Moy_Jours_Partiels=('Jours_Partiels', 'mean'),
                Moy_Total_Jours_Travaillés=('Total_Jours_Travaillés', 'mean'),
                Moy_Total_Heures=('Total_Heures_Travaillées', 'mean'),
                Moy_Jours_Complets=('Jours_Complets', 'mean'),
                Moy_Jours_Absents=('Jours_Absents', 'mean'),
                Moy_Heures_Absence=('Total_Heures_Absence', 'mean'),
                Moy_Présence_365j=('Présence_%_365j', 'mean')
            ).reset_index()

            # Arrondir les valeurs
            numeric_columns = moyennes.select_dtypes(include=['float64', 'int64']).columns
            moyennes[numeric_columns] = moyennes[numeric_columns].round(2)

            # Arrondir spécifiquement les jours partiels à 1 décimale
            if 'Moy_Jours_Partiels' in moyennes.columns:
                moyennes['Moy_Jours_Partiels'] = moyennes['Moy_Jours_Partiels'].round(1)

            logger.info(f"Moyennes calculées pour {len(moyennes)} équipes")
            return moyennes

        except Exception as e:
            logger.error(f"Erreur lors du calcul des moyennes: {e}")
            raise CalculationError(f"Impossible de calculer les moyennes: {e}")

    def _get_grouping_columns(self, df: pd.DataFrame) -> list:
        """Détermine les colonnes de groupement disponibles."""
        base_columns = ['Gentile', 'Equipe (Lib.)', 'Nom', 'Prénom']

        # Ajouter 'UM (Lib)' si disponible
        if 'UM (Lib)' in df.columns:
            base_columns.append('UM (Lib)')

        return base_columns


# Instance globale du calculateur
statistics_calculator = StatisticsCalculator()

# Fonctions de compatibilité avec l'ancienne API
def calculer_heures_travaillees(row: pd.Series) -> float:
    """Calcule les heures travaillées (fonction de compatibilité)."""
    calculator = WorkHoursCalculator()
    result = calculator.calculate_hours_worked(row)
    return result.hours_worked

def calculer_jours_travailles(heures: float) -> float:
    """Convertit les heures en fraction de jour (fonction de compatibilité)."""
    return heures / 8.0

def calculer_statistiques_employes(df_filtre: pd.DataFrame) -> pd.DataFrame:
    """Calcule les statistiques employés (fonction de compatibilité)."""
    return statistics_calculator.calculate_employee_statistics(df_filtre)

def calculer_moyennes_equipe(df_stats: pd.DataFrame) -> pd.DataFrame:
    """Calcule les moyennes d'équipe (fonction de compatibilité)."""
    return statistics_calculator.calculate_team_averages(df_stats)
