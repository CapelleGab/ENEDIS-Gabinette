"""
Fonctions utilitaires communes pour La Gabinette
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

def validate_date_format(date_string: str, format_string: str = "%d/%m/%Y") -> bool:
    """
    Valide le format d'une date

    Args:
        date_string: La chaîne de date à valider
        format_string: Le format attendu

    Returns:
        True si la date est valide, False sinon
    """
    try:
        datetime.strptime(date_string, format_string)
        return True
    except ValueError:
        return False


def validate_time_format(time_string: str, format_string: str = "%H:%M:%S") -> bool:
    """
    Valide le format d'une heure

    Args:
        time_string: La chaîne d'heure à valider
        format_string: Le format attendu

    Returns:
        True si l'heure est valide, False sinon
    """
    try:
        datetime.strptime(time_string, format_string)
        return True
    except ValueError:
        return False


def clean_string(value: Any) -> str:
    """
    Nettoie une chaîne de caractères

    Args:
        value: La valeur à nettoyer

    Returns:
        La chaîne nettoyée
    """
    if value is None:
        return ""

    # Convertir en string et supprimer les espaces en début/fin
    cleaned = str(value).strip()

    # Remplacer les espaces multiples par un seul espace
    cleaned = re.sub(r'\s+', ' ', cleaned)

    return cleaned


def safe_convert_to_int(value: Any) -> Optional[int]:
    """
    Convertit une valeur en entier de manière sécurisée

    Args:
        value: La valeur à convertir

    Returns:
        L'entier ou None si la conversion échoue
    """
    try:
        if value is None or value == "":
            return None
        return int(float(str(value)))
    except (ValueError, TypeError):
        return None


def safe_convert_to_float(value: Any) -> Optional[float]:
    """
    Convertit une valeur en float de manière sécurisée
    Supporte le format français avec virgule comme séparateur décimal

    Args:
        value: La valeur à convertir

    Returns:
        Le float ou None si la conversion échoue
    """
    try:
        if value is None or value == "":
            return None
        
        # Convertir en string et nettoyer
        str_value = str(value).strip()
        
        # Remplacer la virgule par un point pour le format français
        str_value = str_value.replace(',', '.')
        
        return float(str_value)
    except (ValueError, TypeError):
        return None


def format_file_size(size_bytes: int) -> str:
    """
    Formate une taille de fichier en unités lisibles

    Args:
        size_bytes: La taille en bytes

    Returns:
        La taille formatée (ex: "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Récupère les informations d'un fichier

    Args:
        file_path: Le chemin vers le fichier

    Returns:
        Dictionnaire avec les informations du fichier
    """
    path = Path(file_path)

    if not path.exists():
        return {"exists": False}

    stat = path.stat()

    return {
        "exists": True,
        "name": path.name,
        "size": stat.st_size,
        "size_formatted": format_file_size(stat.st_size),
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "extension": path.suffix.lower(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir()
    }


def create_backup_filename(original_path: Union[str, Path]) -> Path:
    """
    Crée un nom de fichier de sauvegarde avec timestamp

    Args:
        original_path: Le chemin du fichier original

    Returns:
        Le chemin du fichier de sauvegarde
    """
    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
    return path.parent / backup_name


def validate_csv_structure(headers: List[str], expected_headers: List[str]) -> Dict[str, Any]:
    """
    Valide la structure d'un CSV par rapport aux en-têtes attendus

    Args:
        headers: Les en-têtes trouvés dans le fichier
        expected_headers: Les en-têtes attendus

    Returns:
        Dictionnaire avec le résultat de la validation
    """
    result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "missing_columns": [],
        "extra_columns": [],
        "column_count": len(headers)
    }

    # Nettoyer les en-têtes
    clean_headers = [clean_string(h) for h in headers]
    clean_expected = [clean_string(h) for h in expected_headers]

    # Vérifier les colonnes manquantes
    missing = [col for col in clean_expected if col not in clean_headers]
    if missing:
        result["missing_columns"] = missing
        result["errors"].append(f"Colonnes manquantes: {', '.join(missing)}")
        result["is_valid"] = False

    # Vérifier les colonnes supplémentaires
    extra = [col for col in clean_headers if col not in clean_expected]
    if extra:
        result["extra_columns"] = extra
        result["warnings"].append(f"Colonnes supplémentaires: {', '.join(extra)}")

    # Vérifier l'ordre des colonnes
    if clean_headers != clean_expected and not missing:
        result["warnings"].append("L'ordre des colonnes ne correspond pas à l'ordre attendu")

    # Log la validation si le logger est disponible
    try:
        from utils.logger import logger
        logger.info(f"Validation CSV: {result}")
    except:
        pass

    return result
