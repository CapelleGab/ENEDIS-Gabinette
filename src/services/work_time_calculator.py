"""
Service de calcul des jours de travail complets et partiels pour La Gabinette
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
from datetime import datetime

from src.models.data_model import PMTRecord
from src.utils.logger import logger


class WorkTimeCalculator:
    """Service de calcul des jours de travail complets et partiels"""

    def __init__(self):
        self.logger = logger.get_logger("WorkTimeCalculator")
        self.FULL_DAY_HOURS = 8.0  # Nombre d'heures pour un jour complet

    def calculate_work_days_for_employee(self, records: List[PMTRecord], category: str) -> Dict[str, Any]:
        """
        Calcule les jours complets et partiels pour un employé selon sa catégorie

        Args:
            records: Liste des enregistrements d'un employé
            category: Catégorie de l'employé (ASTREINTES ou TIPS)

        Returns:
            Dictionnaire avec les statistiques de jours de travail
        """
        if not records or category not in ["ASTREINTES", "TIPS"]:
            return {
                'full_days': 0,
                'partial_days': 0,
                'total_absence_hours': 0.0,
                'average_hours_per_day': 0.0
            }

        # Filtrer les enregistrements selon les règles métier
        filtered_records = self._filter_records_by_category_rules(records, category)

        if not filtered_records:
            return {
                'full_days': 0,
                'partial_days': 0,
                'total_absence_hours': 0.0,
                'average_hours_per_day': 0.0
            }

        # Grouper par jour pour analyser chaque jour
        days_data = defaultdict(list)

        for record in filtered_records:
            if not record.jour or not record.nni:
                continue
            days_data[record.jour].append(record)

        # Analyser chaque jour pour déterminer s'il est complet ou partiel
        full_days = 0
        partial_days = 0
        total_absence_hours = 0.0

        for day_key, day_records in days_data.items():
            day_type, absence_hours = self._analyze_day(day_records)

            if day_type == "full":
                full_days += 1
            elif day_type == "partial":
                partial_days += 1
                total_absence_hours += absence_hours
            # day_type == "excluded" → ne pas compter (jours avec code D)

        total_days = full_days + partial_days
        # Pour les jours complets, on compte 8h de travail effectif
        total_work_hours = full_days * self.FULL_DAY_HOURS + partial_days * (self.FULL_DAY_HOURS - (total_absence_hours / partial_days if partial_days > 0 else 0))
        average_hours_per_day = total_work_hours / total_days if total_days > 0 else 0.0

        return {
            'full_days': full_days,
            'partial_days': partial_days,
            'total_absence_hours': total_absence_hours,
            'average_hours_per_day': average_hours_per_day,
            'total_days': total_days
        }

    def _analyze_day(self, day_records: List[PMTRecord]) -> Tuple[str, float]:
        """
        Analyse un jour pour déterminer s'il est complet ou partiel

        Args:
            day_records: Liste des enregistrements pour un jour donné

        Returns:
            Tuple (type_jour, heures_absence) où type_jour est "full" ou "partial"
        """
        total_absence_hours = 0.0
        has_absence_code = False
        has_overtime_code = False

        for record in day_records:
            # Vérifier s'il y a un code
            if record.code and record.code.strip():
                code = record.code.strip().upper()
                if code == "D":
                    # Code D (heures supplémentaires) = exclure complètement le jour
                    has_overtime_code = True
                else:
                    # Autres codes = codes d'absence
                    has_absence_code = True
                    # Calculer les heures d'absence
                    if record.valeur and record.valeur > 0:
                        absence_hours = self._convert_to_hours(record.valeur, record.des_unite)
                        total_absence_hours += absence_hours

        # Si code D (heures supp) → exclure le jour (ni complet ni partiel)
        if has_overtime_code:
            return "excluded", 0.0
        # Si code d'absence → jour partiel
        elif has_absence_code:
            return "partial", total_absence_hours
        # Si pas de code → jour complet
        else:
            return "full", 0.0

    def calculate_all_employees_work_days(self, records: List[PMTRecord], classifications: Dict[str, List[PMTRecord]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Calcule les jours de travail pour tous les employés ASTREINTES et TIPS uniquement
        Exclut les 3X8, AUTRES et les catégories Agence/DR Paris

        Args:
            records: Liste de tous les enregistrements
            classifications: Classifications des employés par catégorie

        Returns:
            Dictionnaire avec les statistiques par catégorie puis par employé (catégorie -> NNI -> stats)
        """
        self.logger.info(f"Calcul des jours de travail pour {len(records)} enregistrements")

        if not records or not classifications:
            return {}

        results = {}

        # Traiter uniquement ASTREINTES et TIPS (exclure 3X8, AUTRES, Agence, DR Paris)
        for category in ["ASTREINTES", "TIPS"]:
            if category not in classifications:
                continue

            category_records = classifications[category]

            # Grouper par employé
            employee_records = defaultdict(list)
            for record in category_records:
                if record.nni:
                    employee_records[record.nni].append(record)

            # Calculer pour chaque employé de cette catégorie
            category_results = {}
            for nni, employee_records_list in employee_records.items():
                work_stats = self.calculate_work_days_for_employee(employee_records_list, category)
                category_results[nni] = work_stats

            results[category] = category_results

        self.logger.info(f"Jours de travail calculés pour {len(results)} catégories")
        return results

    def _filter_records_by_category_rules(self, records: List[PMTRecord], category: str) -> List[PMTRecord]:
        """
        Filtre les enregistrements selon les règles spécifiques à chaque catégorie

        Args:
            records: Liste des enregistrements à filtrer
            category: Catégorie (ASTREINTES ou TIPS)

        Returns:
            Liste des enregistrements filtrés
        """
        filtered_records = []

        for record in records:
            if self._should_include_record_for_category(record, category):
                filtered_records.append(record)

        self.logger.info(f"Catégorie {category}: {len(filtered_records)} enregistrements retenus sur {len(records)}")
        return filtered_records

    def _should_include_record_for_category(self, record: PMTRecord, category: str) -> bool:
        """
        Détermine si un enregistrement doit être inclus selon les règles de la catégorie

        Args:
            record: Enregistrement à évaluer
            category: Catégorie (ASTREINTES ou TIPS)

        Returns:
            True si l'enregistrement doit être inclus
        """
        # Règles communes pour ASTREINTES et TIPS:
        # - PAS DE WEEKEND
        # - PAS DE JOUR FÉRIÉ
        # - PAS DE FIN DE CYCLE
        # - HT OU HTM = J OU K

        # Vérifier jour férié (marqué par un "X") - pour ASTREINTES et TIPS
        if record.jour_ferie and record.jour_ferie.strip().upper() == "X":
            return False

        # Vérifier fin de cycle (marqué par un "X")
        if record.fin_cycle and record.fin_cycle.strip().upper() == "X":
            return False

        # Vérifier weekend (basé sur designation_jour)
        if record.designation_jour:
            designation = record.designation_jour.strip().upper()
            if "SAMEDI" in designation or "DIMANCHE" in designation:
                return False

        # Vérifier HT/HTM selon la priorité : HTM en priorité, sinon HT
        # Si HTM existe, on l'utilise (on ignore HT)
        # Si HTM vide, on utilise HT
        # Dans tous les cas, la valeur doit être J ou K

        # Exclure complètement les jours avec code D (heures supplémentaires)
        if record.code and record.code.strip() and record.code.strip().upper() == "D":
            return False

        has_absence_code = record.code and record.code.strip() and record.code.strip().upper() != "D"

        if has_absence_code:
            # Si code d'absence, on accepte même sans HT/HTM valide
            return True

        # Priorité à HTM si présent
        if record.htm and record.htm.strip():
            htm_valid = record.htm.strip().upper() in ["J", "K"]
            return htm_valid
        else:
            # Sinon utiliser HT
            ht_valid = record.ht and record.ht.strip().upper() in ["J", "K"]
            return ht_valid

        # Règle spécifique selon la catégorie
        if category == "ASTREINTES":
            # J ASTREINTE = I ou vide (pour les employés déjà classifiés ASTREINTES)
            if not record.astreinte or not record.astreinte.strip():
                return True  # Astreinte vide = OK pour employé ASTREINTES
            return record.astreinte.strip().upper() == "I"

        elif category == "TIPS":
            # J ASTREINTE = NON (ne doit pas être "I")
            if not record.astreinte:
                return True  # Pas d'astreinte = OK pour TIP
            astreinte_value = record.astreinte.strip().upper()
            return astreinte_value != "I"

        return False

    def _convert_to_hours(self, value: float, unit: str) -> float:
        """
        Convertit une valeur vers des heures selon l'unité

        Args:
            value: Valeur à convertir
            unit: Unité de la valeur

        Returns:
            Valeur en heures
        """
        if not unit:
            return value  # Par défaut, traiter comme des heures

        unit_lower = unit.strip().lower()

        if "jour" in unit_lower:
            return value * self.FULL_DAY_HOURS
        elif "heure" in unit_lower:
            return value
        else:
            # Unité inconnue, traiter comme des heures
            self.logger.warning(f"Unité inconnue pour absence: '{unit}', traité comme heures")
            return value

    def get_work_time_summary_by_category(self, records: List[PMTRecord], classifications: Dict[str, List[PMTRecord]]) -> Dict[str, Dict[str, Any]]:
        """
        Génère un résumé des jours de travail par catégorie (ASTREINTES et TIPS uniquement)
        Exclut les 3X8, AUTRES et les catégories Agence/DR Paris

        Args:
            records: Liste des enregistrements
            classifications: Classifications des employés par catégorie

        Returns:
            Résumé des jours de travail par catégorie
        """
        # Calculer les jours de travail pour tous les employés
        work_days_by_category = self.calculate_all_employees_work_days(records, classifications)

        results = {}

        # Ne traiter que ASTREINTES et TIPS
        for category in ["ASTREINTES", "TIPS"]:
            if category not in work_days_by_category:
                results[category] = {
                    'total_employees': 0,
                    'total_full_days': 0,
                    'total_partial_days': 0,
                    'average_full_days_per_employee': 0.0,
                    'average_partial_days_per_employee': 0.0,
                    'percentage_full_days': 0.0,
                    'total_absence_hours': 0.0
                }
                continue

            category_data = work_days_by_category[category]

            if not category_data:
                results[category] = {
                    'total_employees': 0,
                    'total_full_days': 0,
                    'total_partial_days': 0,
                    'average_full_days_per_employee': 0.0,
                    'average_partial_days_per_employee': 0.0,
                    'percentage_full_days': 0.0,
                    'total_absence_hours': 0.0
                }
                continue

            # Agréger les statistiques pour cette catégorie
            total_full_days = 0
            total_partial_days = 0
            total_absence_hours = 0.0

            for nni, stats in category_data.items():
                total_full_days += stats['full_days']
                total_partial_days += stats['partial_days']
                total_absence_hours += stats['total_absence_hours']

            total_days = total_full_days + total_partial_days
            total_employees = len(category_data)

            # Calculer les moyennes
            avg_full_days = total_full_days / total_employees if total_employees > 0 else 0.0
            avg_partial_days = total_partial_days / total_employees if total_employees > 0 else 0.0
            percentage_full_days = (total_full_days / total_days * 100) if total_days > 0 else 0.0

            results[category] = {
                'total_employees': total_employees,
                'total_full_days': total_full_days,
                'total_partial_days': total_partial_days,
                'average_full_days_per_employee': avg_full_days,
                'average_partial_days_per_employee': avg_partial_days,
                'percentage_full_days': percentage_full_days,
                'total_absence_hours': total_absence_hours
            }

        return results

    def get_work_time_summary(self, records: List[PMTRecord], classifications: Dict[str, List[PMTRecord]]) -> Dict[str, Any]:
        """
        Génère un résumé global des jours de travail (ASTREINTES et TIPS uniquement)

        Args:
            records: Liste des enregistrements
            classifications: Classifications des employés par catégorie

        Returns:
            Résumé global des jours de travail
        """
        category_summaries = self.get_work_time_summary_by_category(records, classifications)

        if not category_summaries:
            return {
                'total_employees': 0,
                'total_full_days': 0,
                'total_partial_days': 0,
                'average_full_days_per_employee': 0.0,
                'average_partial_days_per_employee': 0.0,
                'percentage_full_days': 0.0,
                'total_absence_hours': 0.0
            }

        # Agréger toutes les statistiques
        total_employees = sum(summary['total_employees'] for summary in category_summaries.values())
        total_full_days = sum(summary['total_full_days'] for summary in category_summaries.values())
        total_partial_days = sum(summary['total_partial_days'] for summary in category_summaries.values())
        total_absence_hours = sum(summary['total_absence_hours'] for summary in category_summaries.values())
        total_days = total_full_days + total_partial_days

        return {
            'total_employees': total_employees,
            'total_full_days': total_full_days,
            'total_partial_days': total_partial_days,
            'average_full_days_per_employee': total_full_days / total_employees if total_employees > 0 else 0.0,
            'average_partial_days_per_employee': total_partial_days / total_employees if total_employees > 0 else 0.0,
            'percentage_full_days': (total_full_days / total_days * 100) if total_days > 0 else 0.0,
            'total_absence_hours': total_absence_hours
        }
