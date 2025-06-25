"""
Service de traitement des fichiers CSV pour La Gabinette
"""

import csv
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Iterator
import pandas as pd

from src.config.settings import (
    CSV_SEPARATOR, CSV_ENCODING, EXPECTED_COLUMNS, INPUT_DIR, OUTPUT_DIR
)
from src.models.data_model import PMTRecord, ProcessingResult, FileInfo, ValidationResult, ValidationStatus
from src.services.employee_classifier import EmployeeClassifier
from src.utils.logger import logger
from src.utils.helpers import get_file_info, validate_csv_structure, create_backup_filename


class CSVProcessor:
    """Service de traitement des fichiers CSV PMT"""

    def __init__(self):
        self.logger = logger.get_logger("CSVProcessor")
        self.classifier = EmployeeClassifier()
        self._current_file_path: Optional[Path] = None
        self._records: List[PMTRecord] = []
        self._processing_result: Optional[ProcessingResult] = None
        self._classifications: Optional[Dict[str, List[PMTRecord]]] = None

    def load_file(self, file_path: str) -> ProcessingResult:
        """
        Charge et traite un fichier CSV

        Args:
            file_path: Chemin vers le fichier CSV

        Returns:
            Résultat du traitement
        """
        start_time = time.time()
        self.logger.info(f"Début du traitement du fichier: {file_path}")

        try:
            # Vérifier l'existence du fichier
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

            # Obtenir les informations du fichier
            file_info_dict = get_file_info(path)
            file_info = FileInfo(
                path=str(path),
                name=file_info_dict["name"],
                size=file_info_dict["size"],
                size_formatted=file_info_dict["size_formatted"],
                modified=file_info_dict["modified"],
                extension=file_info_dict["extension"]
            )

            # Valider la structure du fichier
            validation_result = self._validate_file_structure(path)
            if not validation_result["is_valid"]:
                return ProcessingResult(
                    success=False,
                    file_info=file_info,
                    error_message=f"Structure de fichier invalide: {'; '.join(validation_result['errors'])}",
                    processing_time=time.time() - start_time
                )

            # Traiter le fichier
            records, validation_results = self._process_csv_file(path)

            # Calculer les statistiques
            records_valid = sum(1 for r in records if not any(v.status == ValidationStatus.ERROR for v in r.validation_results))
            records_with_warnings = sum(1 for r in records if any(v.status == ValidationStatus.WARNING for v in r.validation_results))
            records_with_errors = sum(1 for r in records if any(v.status == ValidationStatus.ERROR for v in r.validation_results))

            # Créer le résultat
            result = ProcessingResult(
                success=True,
                file_info=file_info,
                records_processed=len(records),
                records_valid=records_valid,
                records_with_warnings=records_with_warnings,
                records_with_errors=records_with_errors,
                validation_results=validation_results,
                processing_time=time.time() - start_time
            )

            # Sauvegarder l'état
            self._current_file_path = path
            self._records = records
            self._processing_result = result

            self.logger.info(f"Traitement terminé: {len(records)} enregistrements traités en {result.processing_time:.2f}s")
            return result

        except Exception as e:
            error_msg = f"Erreur lors du traitement du fichier: {str(e)}"
            self.logger.error(error_msg)

            return ProcessingResult(
                success=False,
                file_info=FileInfo(
                    path=file_path,
                    name=Path(file_path).name,
                    size=0,
                    size_formatted="0 B",
                    modified=None,
                    extension=Path(file_path).suffix,
                    exists=False
                ),
                error_message=error_msg,
                processing_time=time.time() - start_time
            )

    def _validate_file_structure(self, file_path: Path) -> Dict[str, Any]:
        """
        Valide la structure du fichier CSV

        Args:
            file_path: Chemin vers le fichier

        Returns:
            Résultat de la validation
        """
        try:
            # Lire seulement la première ligne pour vérifier les en-têtes
            with open(file_path, 'r', encoding=CSV_ENCODING) as file:
                reader = csv.reader(file, delimiter=CSV_SEPARATOR)
                headers = next(reader, [])

            return validate_csv_structure(headers, EXPECTED_COLUMNS)

        except Exception as e:
            self.logger.error(f"Erreur lors de la validation de la structure: {str(e)}")
            return {
                "is_valid": False,
                "errors": [f"Impossible de lire le fichier: {str(e)}"],
                "warnings": [],
                "missing_columns": [],
                "extra_columns": [],
                "column_count": 0
            }

    def _process_csv_file(self, file_path: Path) -> Tuple[List[PMTRecord], List[ValidationResult]]:
        """
        Traite le contenu du fichier CSV

        Args:
            file_path: Chemin vers le fichier

        Returns:
            Tuple contenant la liste des enregistrements et les résultats de validation
        """
        records = []
        all_validation_results = []

        try:
            # Utiliser pandas pour une lecture plus robuste
            df = pd.read_csv(
                file_path,
                sep=CSV_SEPARATOR,
                encoding=CSV_ENCODING,
                dtype=str,  # Tout lire comme string pour éviter les conversions automatiques
                na_filter=False  # Éviter la conversion des valeurs vides en NaN
            )

            self.logger.info(f"Fichier lu avec pandas: {len(df)} lignes, {len(df.columns)} colonnes")

            # Traiter chaque ligne
            for index, row in df.iterrows():
                row_number = index + 2  # +2 car index commence à 0 et on compte l'en-tête

                try:
                    # Créer l'enregistrement PMT
                    record = self._create_pmt_record(row.to_dict(), row_number)

                    # Valider l'enregistrement
                    validation_results = record.validate()
                    all_validation_results.extend(validation_results)

                    records.append(record)

                except Exception as e:
                    error_msg = f"Erreur lors du traitement de la ligne {row_number}: {str(e)}"
                    self.logger.error(error_msg)

                    all_validation_results.append(ValidationResult(
                        status=ValidationStatus.ERROR,
                        message=error_msg,
                        row_number=row_number
                    ))

            return records, all_validation_results

        except Exception as e:
            error_msg = f"Erreur lors de la lecture du fichier CSV: {str(e)}"
            self.logger.error(error_msg)
            raise

    def _create_pmt_record(self, row_data: Dict[str, Any], row_number: int) -> PMTRecord:
        """
        Crée un enregistrement PMT à partir des données d'une ligne

        Args:
            row_data: Données de la ligne
            row_number: Numéro de ligne

        Returns:
            Enregistrement PMT
        """
        # Utiliser la méthode from_csv_row du modèle
        record = PMTRecord.from_csv_row(row_data, row_number)

        # Traitement spécial pour les colonnes De/à qui se répètent
        # Cette logique doit être adaptée selon la structure exacte du CSV
        de_a_columns = []
        for col_name, value in row_data.items():
            if col_name in ["De", "à"]:
                de_a_columns.append((col_name, value))

        # Mapper les colonnes De/à aux bons champs selon leur position
        # Cette partie nécessite une logique spécifique basée sur l'ordre des colonnes
        self._map_time_columns(record, de_a_columns)

        return record

    def _map_time_columns(self, record: PMTRecord, de_a_columns: List[Tuple[str, str]]) -> None:
        """
        Mappe les colonnes De/à aux bons attributs de l'enregistrement

        Args:
            record: L'enregistrement PMT à modifier
            de_a_columns: Liste des colonnes De/à avec leurs valeurs
        """
        # Cette logique doit être adaptée selon la structure exacte du CSV
        # Pour l'instant, on fait un mapping simple basé sur l'ordre

        if len(de_a_columns) >= 8:  # 4 paires De/à pour HT, HTM, HE
            # HT: première paire
            if len(de_a_columns) >= 2:
                record.ht_de_1 = de_a_columns[0][1] if de_a_columns[0][0] == "De" else ""
                record.ht_a_1 = de_a_columns[1][1] if de_a_columns[1][0] == "à" else ""

            # HT: deuxième paire
            if len(de_a_columns) >= 4:
                record.ht_de_2 = de_a_columns[2][1] if de_a_columns[2][0] == "De" else ""
                record.ht_a_2 = de_a_columns[3][1] if de_a_columns[3][0] == "à" else ""

            # HTM: première paire
            if len(de_a_columns) >= 6:
                record.htm_de_1 = de_a_columns[4][1] if de_a_columns[4][0] == "De" else ""
                record.htm_a_1 = de_a_columns[5][1] if de_a_columns[5][0] == "à" else ""

            # HTM: deuxième paire
            if len(de_a_columns) >= 8:
                record.htm_de_2 = de_a_columns[6][1] if de_a_columns[6][0] == "De" else ""
                record.htm_a_2 = de_a_columns[7][1] if de_a_columns[7][0] == "à" else ""

            # HE: première paire
            if len(de_a_columns) >= 10:
                record.he_de_1 = de_a_columns[8][1] if de_a_columns[8][0] == "De" else ""
                record.he_a_1 = de_a_columns[9][1] if de_a_columns[9][0] == "à" else ""

            # HE: deuxième paire
            if len(de_a_columns) >= 12:
                record.he_de_2 = de_a_columns[10][1] if de_a_columns[10][0] == "De" else ""
                record.he_a_2 = de_a_columns[11][1] if de_a_columns[11][0] == "à" else ""

    def get_records(self) -> List[PMTRecord]:
        """
        Retourne la liste des enregistrements traités

        Returns:
            Liste des enregistrements PMT
        """
        return self._records.copy()

    def get_processing_result(self) -> Optional[ProcessingResult]:
        """
        Retourne le résultat du dernier traitement

        Returns:
            Résultat du traitement ou None
        """
        return self._processing_result

    def filter_records(self, **filters) -> List[PMTRecord]:
        """
        Filtre les enregistrements selon les critères donnés

        Args:
            **filters: Critères de filtrage

        Returns:
            Liste des enregistrements filtrés
        """
        filtered_records = self._records.copy()

        for field_name, filter_value in filters.items():
            if hasattr(PMTRecord, field_name) and filter_value is not None:
                filtered_records = [
                    record for record in filtered_records
                    if getattr(record, field_name, "") == filter_value
                ]

        self.logger.info(f"Filtrage appliqué: {len(filtered_records)} enregistrements correspondent aux critères")
        return filtered_records

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Calcule des statistiques de résumé sur les données

        Returns:
            Dictionnaire avec les statistiques
        """
        if not self._records:
            return {}

        stats = {
            "total_records": len(self._records),
            "unique_employees": len(set((r.nom, r.prenom) for r in self._records if r.nom and r.prenom)),
            "unique_teams": len(set(r.equipe_lib for r in self._records if r.equipe_lib)),
            "date_range": self._get_date_range(),
            "validation_summary": self._get_validation_summary()
        }

        return stats

    def _get_date_range(self) -> Dict[str, str]:
        """Calcule la plage de dates des enregistrements"""
        dates = [r.jour for r in self._records if r.jour]
        if not dates:
            return {"min_date": "", "max_date": ""}

        return {
            "min_date": min(dates),
            "max_date": max(dates)
        }

    def _get_validation_summary(self) -> Dict[str, int]:
        """Calcule un résumé des validations"""
        total_errors = sum(
            len([v for v in r.validation_results if v.status == ValidationStatus.ERROR])
            for r in self._records
        )
        total_warnings = sum(
            len([v for v in r.validation_results if v.status == ValidationStatus.WARNING])
            for r in self._records
        )

        return {
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "records_with_errors": len([r for r in self._records if any(v.status == ValidationStatus.ERROR for v in r.validation_results)]),
            "records_with_warnings": len([r for r in self._records if any(v.status == ValidationStatus.WARNING for v in r.validation_results)])
        }

    def classify_employees(self) -> Dict[str, List[PMTRecord]]:
        """
        Classifie les employés en 4 catégories

        Returns:
            Dictionnaire avec les classifications
        """
        if not self._records:
            self.logger.warning("Aucun enregistrement à classifier")
            return {'ASTREINTES': [], 'TIPS': [], '3X8': [], 'AUTRES': []}

        self.logger.info("Classification des employés en cours...")
        self._classifications = self.classifier.classify_employees(self._records)
        
        return self._classifications

    def get_classifications(self) -> Optional[Dict[str, List[PMTRecord]]]:
        """
        Retourne les classifications existantes ou les calcule si nécessaire

        Returns:
            Classifications des employés
        """
        if self._classifications is None:
            return self.classify_employees()
        return self._classifications

    def get_classification_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé des classifications

        Returns:
            Résumé des classifications
        """
        if self._classifications is None:
            self.classify_employees()
        
        return self.classifier.get_classification_summary(self._classifications)
 