"""
Module de chargement et préparation des données PMT.

Author: CAPELLE Gabin
Version: 2.0.0
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass

from config import config
from .exceptions import DataValidationError

logger = logging.getLogger(__name__)


@dataclass
class DataValidationResult:
    """Résultat de validation des données."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class DataLoader:
    """Gestionnaire de chargement et préparation des données PMT."""

    def __init__(self):
        self.config = config

    def load_csv(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Charge les données depuis le fichier CSV.

        Args:
            file_path: Chemin vers le fichier CSV. Si None, utilise le fichier par défaut.

        Returns:
            DataFrame avec les données chargées

        Raises:
            DataValidationError: Si le fichier ne peut pas être chargé ou validé
        """
        csv_path = Path(file_path) if file_path else Path(self.config.files.csv_filename)

        logger.info(f"Chargement du fichier CSV: {csv_path}")

        # Validation du fichier
        self._validate_file(csv_path)

        try:
            # Chargement du CSV
            df = pd.read_csv(
                csv_path,
                encoding=self.config.files.csv_encoding,
                sep=self.config.files.csv_separator,
                low_memory=False
            )

            # Validation des données
            validation_result = self._validate_dataframe(df)
            if not validation_result.is_valid:
                raise DataValidationError(f"Données invalides: {'; '.join(validation_result.errors)}")

            # Log des avertissements
            for warning in validation_result.warnings:
                logger.warning(warning)

            logger.info(f"CSV chargé avec succès: {len(df)} lignes, {len(df.columns)} colonnes")
            return df

        except pd.errors.EmptyDataError:
            raise DataValidationError("Le fichier CSV ne contient aucune donnée")
        except pd.errors.ParserError as e:
            raise DataValidationError(f"Erreur de parsing du CSV: {e}")
        except UnicodeDecodeError as e:
            raise DataValidationError(f"Erreur d'encodage du fichier CSV: {e}")
        except Exception as e:
            raise DataValidationError(f"Erreur inattendue lors du chargement: {e}")

    def prepare_data(self, df: pd.DataFrame, team_filter: List[str]) -> pd.DataFrame:
        """
        Prépare les données pour l'analyse.

        Args:
            df: DataFrame source
            team_filter: Liste des équipes à conserver

        Returns:
            DataFrame préparé
        """
        logger.info(f"Préparation des données pour {len(team_filter)} équipes")

        # Créer une copie pour éviter les modifications du DataFrame original
        df_prepared = df.copy()

        # Créer l'identifiant unique employé
        df_prepared['Gentile'] = (
            df_prepared['Nom'] + ' ' +
            df_prepared['Prénom'] + ' ' +
            df_prepared['Equipe (Lib.)']
        )

        # Filtrage par équipe
        df_filtered = df_prepared[df_prepared['Equipe (Lib.)'].isin(team_filter)].copy()

        if df_filtered.empty:
            logger.warning(f"Aucune donnée trouvée pour les équipes: {team_filter}")
            return df_filtered

        # Normalisation des valeurs numériques
        df_filtered = self._normalize_numeric_values(df_filtered)

        logger.info(f"Données préparées: {len(df_filtered)} lignes pour {df_filtered['Gentile'].nunique()} employés")
        return df_filtered

    def prepare_astreinte_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare les données pour l'analyse des équipes d'astreinte."""
        return self.prepare_data(df, self.config.teams.astreinte_teams)

    def prepare_tip_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare les données pour l'analyse des équipes TIP (hors astreinte)."""
        return self.prepare_data(df, self.config.teams.non_astreinte_teams)

    def prepare_3x8_data(self, df: pd.DataFrame, df_tip: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prépare les données pour l'analyse des équipes en 3x8.

        Sépare les employés 3x8 des employés TIP standard.

        Args:
            df: DataFrame source complet
            df_tip: DataFrame des équipes TIP déjà préparé (optionnel)

        Returns:
            Tuple (df_3x8, df_tip_standard)
        """
        from .calculateurs_3x8 import est_horaire_3x8

        logger.info("Identification des employés 3x8")

        # Préparer les données TIP si nécessaire
        if df_tip is None:
            df_tip = self.prepare_tip_data(df)

        if df_tip.empty:
            logger.warning("Aucune donnée TIP disponible pour l'analyse 3x8")
            return pd.DataFrame(), df_tip

        # Identifier les lignes avec horaires 3x8
        df_tip_copy = df_tip.copy()
        df_tip_copy['Est_3x8'] = df_tip_copy.apply(est_horaire_3x8, axis=1)

        # Identifier les employés qui font du 3x8
        employes_3x8 = df_tip_copy[df_tip_copy['Est_3x8']]['Gentile'].unique()

        # Séparer les données
        df_3x8 = df_tip_copy[df_tip_copy['Gentile'].isin(employes_3x8)].copy()
        df_tip_standard = df_tip_copy[~df_tip_copy['Gentile'].isin(employes_3x8)].copy()

        # Nettoyer les colonnes temporaires
        for df_temp in [df_3x8, df_tip_standard]:
            if 'Est_3x8' in df_temp.columns:
                df_temp.drop(columns=['Est_3x8'], inplace=True)

        logger.info(f"Employés 3x8 identifiés: {len(employes_3x8)}")
        return df_3x8, df_tip_standard

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Supprime les doublons par employé et jour.

        Args:
            df: DataFrame source

        Returns:
            DataFrame sans doublons
        """
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=['Gentile', 'Jour'], keep='first').copy()
        removed_count = initial_count - len(df_clean)

        if removed_count > 0:
            logger.info(f"Doublons supprimés: {removed_count} lignes")

        return df_clean

    def _validate_file(self, file_path: Path) -> None:
        """Valide l'existence et les propriétés du fichier."""
        if not file_path.exists():
            raise DataValidationError(f"Le fichier n'existe pas: {file_path}")

        if not file_path.is_file():
            raise DataValidationError(f"Le chemin n'est pas un fichier: {file_path}")

        if file_path.stat().st_size == 0:
            raise DataValidationError(f"Le fichier est vide: {file_path}")

    def _validate_dataframe(self, df: pd.DataFrame) -> DataValidationResult:
        """Valide le contenu du DataFrame."""
        errors = []
        warnings = []

        # Vérifications de base
        if df.empty:
            errors.append("Le DataFrame est vide")

        if len(df.columns) == 0:
            errors.append("Le DataFrame n'a aucune colonne")

        # Vérifier les colonnes requises
        missing_columns = [
            col for col in self.config.columns.required_csv_columns
            if col not in df.columns
        ]
        if missing_columns:
            errors.append(f"Colonnes manquantes: {missing_columns}")

        # Vérifications d'avertissement
        if len(df) < 100:
            warnings.append(f"Peu de données: seulement {len(df)} lignes")

        # Vérifier la présence d'équipes connues
        if 'Equipe (Lib.)' in df.columns:
            known_teams = set(self.config.teams.all_teams)
            found_teams = set(df['Equipe (Lib.)'].unique())
            unknown_teams = found_teams - known_teams

            if unknown_teams:
                warnings.append(f"Équipes inconnues trouvées: {list(unknown_teams)[:5]}")

        return DataValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _normalize_numeric_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalise les valeurs numériques (format français vers anglais)."""
        if 'Valeur' in df.columns:
            # Convertir les virgules en points pour les décimales
            df['Valeur'] = df['Valeur'].astype(str).str.replace(',', '.', regex=False)
            # Conversion numérique avec gestion des erreurs
            df['Valeur'] = pd.to_numeric(df['Valeur'], errors='coerce')

        return df


# Instance globale du loader
data_loader = DataLoader()

# Fonctions de compatibilité avec l'ancienne API
def charger_donnees_csv(fichier_csv: Optional[str] = None) -> pd.DataFrame:
    """Charge les données depuis le fichier CSV (fonction de compatibilité)."""
    return data_loader.load_csv(fichier_csv)

def preparer_donnees(df: pd.DataFrame) -> pd.DataFrame:
    """Prépare les données pour l'analyse d'astreinte (fonction de compatibilité)."""
    return data_loader.prepare_astreinte_data(df)

def preparer_donnees_tip(df: pd.DataFrame) -> pd.DataFrame:
    """Prépare les données pour l'analyse TIP (fonction de compatibilité)."""
    return data_loader.prepare_tip_data(df)

def preparer_donnees_3x8(df: pd.DataFrame, df_equipe_tip: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Prépare les données pour l'analyse 3x8 (fonction de compatibilité)."""
    return data_loader.prepare_3x8_data(df, df_equipe_tip)

def supprimer_doublons(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les doublons (fonction de compatibilité)."""
    return data_loader.remove_duplicates(df)
