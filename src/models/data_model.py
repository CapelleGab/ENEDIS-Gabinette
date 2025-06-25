"""
Modèles de données pour La Gabinette
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from src.utils.helpers import clean_string, safe_convert_to_int, safe_convert_to_float


class ValidationStatus(Enum):
    """Statuts de validation"""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationResult:
    """Résultat de validation"""
    status: ValidationStatus
    message: str
    field_name: Optional[str] = None
    row_number: Optional[int] = None


@dataclass
class FileInfo:
    """Informations sur un fichier"""
    path: str
    name: str
    size: int
    size_formatted: str
    modified: datetime
    extension: str
    exists: bool = True


@dataclass
class PMTRecord:
    """
    Modèle représentant un enregistrement PMT
    Correspond à une ligne du fichier CSV
    """
    # Identifiants organisationnels
    um: str = ""
    um_lib: str = ""
    dum: str = ""
    dum_lib: str = ""
    sdum: str = ""
    sdum_lib: str = ""
    fsdum: str = ""
    fsdum_lib: str = ""

    # Domaines
    dom: str = ""
    dom_lib: str = ""
    sdom: str = ""
    sdom_lib: str = ""

    # Équipe et personnel
    equipe: str = ""
    equipe_lib: str = ""
    nni: str = ""
    nom: str = ""
    prenom: str = ""

    # Informations temporelles
    jour: str = ""
    designation_jour: str = ""
    jour_ferie: str = ""
    fin_cycle: str = ""

    # Astreintes
    astreinte: str = ""
    astr_occas: str = ""

    # Heures de travail
    ht: str = ""
    ht_de_1: str = ""
    ht_a_1: str = ""
    ht_de_2: str = ""
    ht_a_2: str = ""

    # Heures supplémentaires matin
    htm: str = ""
    htm_de_1: str = ""
    htm_a_1: str = ""
    htm_de_2: str = ""
    htm_a_2: str = ""

    # Heures supplémentaires
    he: str = ""
    he_de_1: str = ""
    he_a_1: str = ""
    he_de_2: str = ""
    he_a_2: str = ""

    # Codes et valeurs
    code: str = ""
    designation_code: str = ""
    valeur: Optional[float] = None
    des_unite: str = ""
    heure_debut: str = ""
    heure_fin: str = ""

    # Métadonnées
    row_number: int = 0
    validation_results: List[ValidationResult] = field(default_factory=list)

    @classmethod
    def from_csv_row(cls, row_data: Dict[str, Any], row_number: int = 0) -> 'PMTRecord':
        """
        Crée un PMTRecord à partir d'une ligne CSV

        Args:
            row_data: Dictionnaire contenant les données de la ligne
            row_number: Numéro de ligne

        Returns:
            Instance de PMTRecord
        """
        # Mapping des colonnes CSV vers les attributs du modèle
        column_mapping = {
            "UM": "um",
            "UM (Lib)": "um_lib",
            "DUM": "dum",
            "DUM (Lib)": "dum_lib",
            "SDUM": "sdum",
            "SDUM (Lib)": "sdum_lib",
            "FSDUM": "fsdum",
            "FSDUM (Lib)": "fsdum_lib",
            "Dom.": "dom",
            "Dom.(Lib)": "dom_lib",
            "SDom": "sdom",
            "SDom.(Lib)": "sdom_lib",
            "Equipe": "equipe",
            "Equipe (Lib.)": "equipe_lib",
            "NNI": "nni",
            "Nom": "nom",
            "Prénom": "prenom",
            "Jour": "jour",
            "Désignation jour": "designation_jour",
            "Jour férié": "jour_ferie",
            "Fin cycle": "fin_cycle",
            "Astreinte": "astreinte",
            "Astr. Occas.": "astr_occas",
            "HT": "ht",
            "HTM": "htm",
            "HE": "he",
            "Code": "code",
            "Désignation code": "designation_code",
            "Valeur": "valeur",
            "Dés. unité": "des_unite",
            "Heure début": "heure_debut",
            "Heure fin": "heure_fin"
        }

        # Créer l'instance avec les valeurs par défaut
        record = cls(row_number=row_number)

        # Mapper les colonnes De/à pour les heures
        time_columns = ["De", "à"]
        time_counters = {"ht": 0, "htm": 0, "he": 0}

        for csv_column, value in row_data.items():
            cleaned_value = clean_string(value)

            # Mapping direct
            if csv_column in column_mapping:
                attr_name = column_mapping[csv_column]
                if attr_name == "valeur":
                    setattr(record, attr_name, safe_convert_to_float(cleaned_value))
                else:
                    setattr(record, attr_name, cleaned_value)

            # Gestion spéciale pour les colonnes De/à
            elif csv_column in time_columns:
                # Logique pour mapper les colonnes De/à aux bons attributs
                # Cette partie nécessiterait une logique plus complexe basée sur la position
                pass

        return record

    def validate(self) -> List[ValidationResult]:
        """
        Valide l'enregistrement selon les règles métier

        Returns:
            Liste des résultats de validation
        """
        results = []

        # Validation des champs obligatoires
        required_fields = ["um_lib", "equipe_lib", "nom", "prenom", "jour"]
        for field_name in required_fields:
            value = getattr(self, field_name)
            if not value or value.strip() == "":
                results.append(ValidationResult(
                    status=ValidationStatus.ERROR,
                    message=f"Le champ {field_name} est obligatoire",
                    field_name=field_name,
                    row_number=self.row_number
                ))

        # Validation du format de date
        if self.jour:
            from utils.helpers import validate_date_format
            if not validate_date_format(self.jour):
                results.append(ValidationResult(
                    status=ValidationStatus.ERROR,
                    message=f"Format de date invalide: {self.jour}",
                    field_name="jour",
                    row_number=self.row_number
                ))

        # Validation des heures
        time_fields = ["heure_debut", "heure_fin", "ht_de_1", "ht_a_1", "ht_de_2", "ht_a_2",
                      "htm_de_1", "htm_a_1", "htm_de_2", "htm_a_2",
                      "he_de_1", "he_a_1", "he_de_2", "he_a_2"]

        for field_name in time_fields:
            value = getattr(self, field_name)
            if value and value.strip():
                from utils.helpers import validate_time_format
                if not validate_time_format(value):
                    results.append(ValidationResult(
                        status=ValidationStatus.WARNING,
                        message=f"Format d'heure potentiellement invalide: {value}",
                        field_name=field_name,
                        row_number=self.row_number
                    ))

        # Validation des valeurs énumérées
        from config.settings import VALID_VALUES
        for field_name, valid_values in VALID_VALUES.items():
            if field_name == "UM (Lib)" and self.um_lib:
                if self.um_lib not in valid_values:
                    results.append(ValidationResult(
                        status=ValidationStatus.WARNING,
                        message=f"Valeur inattendue pour UM (Lib): {self.um_lib}",
                        field_name="um_lib",
                        row_number=self.row_number
                    ))

        self.validation_results = results
        return results

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'enregistrement en dictionnaire

        Returns:
            Dictionnaire représentant l'enregistrement
        """
        return {
            "um": self.um,
            "um_lib": self.um_lib,
            "dum": self.dum,
            "dum_lib": self.dum_lib,
            "sdum": self.sdum,
            "sdum_lib": self.sdum_lib,
            "fsdum": self.fsdum,
            "fsdum_lib": self.fsdum_lib,
            "dom": self.dom,
            "dom_lib": self.dom_lib,
            "sdom": self.sdom,
            "sdom_lib": self.sdom_lib,
            "equipe": self.equipe,
            "equipe_lib": self.equipe_lib,
            "nni": self.nni,
            "nom": self.nom,
            "prenom": self.prenom,
            "jour": self.jour,
            "designation_jour": self.designation_jour,
            "jour_ferie": self.jour_ferie,
            "fin_cycle": self.fin_cycle,
            "astreinte": self.astreinte,
            "astr_occas": self.astr_occas,
            "ht": self.ht,
            "ht_de_1": self.ht_de_1,
            "ht_a_1": self.ht_a_1,
            "ht_de_2": self.ht_de_2,
            "ht_a_2": self.ht_a_2,
            "htm": self.htm,
            "htm_de_1": self.htm_de_1,
            "htm_a_1": self.htm_a_1,
            "htm_de_2": self.htm_de_2,
            "htm_a_2": self.htm_a_2,
            "he": self.he,
            "he_de_1": self.he_de_1,
            "he_a_1": self.he_a_1,
            "he_de_2": self.he_de_2,
            "he_a_2": self.he_a_2,
            "code": self.code,
            "designation_code": self.designation_code,
            "valeur": self.valeur,
            "des_unite": self.des_unite,
            "heure_debut": self.heure_debut,
            "heure_fin": self.heure_fin,
            "row_number": self.row_number
        }


@dataclass
class ProcessingResult:
    """Résultat du traitement d'un fichier"""
    success: bool
    file_info: FileInfo
    records_processed: int = 0
    records_valid: int = 0
    records_with_warnings: int = 0
    records_with_errors: int = 0
    validation_results: List[ValidationResult] = field(default_factory=list)
    processing_time: float = 0.0
    error_message: Optional[str] = None
 