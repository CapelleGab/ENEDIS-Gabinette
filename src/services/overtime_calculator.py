"""
Service de calcul des heures supplémentaires pour La Gabinette
"""

from typing import List, Dict, Any
from collections import defaultdict

from src.models.data_model import PMTRecord
from src.utils.logger import logger


class OvertimeCalculator:
    """Service de calcul des heures supplémentaires"""

    def __init__(self):
        self.logger = logger.get_logger("OvertimeCalculator")
        self.OVERTIME_CODE = "D"  # Code pour les heures supplémentaires
        self.HOURS_PER_DAY = 8.0  # Conversion jour vers heures

    def calculate_employee_overtime(self, records: List[PMTRecord]) -> Dict[str, float]:
        """
        Calcule les heures supplémentaires pour un employé

        Args:
            records: Liste des enregistrements d'un employé

        Returns:
            Dictionnaire avec les heures supplémentaires par employé
        """
        if not records:
            return {}

        # Grouper par employé (NNI)
        employee_records = defaultdict(list)
        for record in records:
            if record.nni:
                employee_records[record.nni].append(record)

        results = {}
        for nni, employee_records_list in employee_records.items():
            total_overtime = self._calculate_overtime_for_employee(employee_records_list)
            results[nni] = total_overtime

        return results

    def calculate_all_employees_overtime(self, records: List[PMTRecord]) -> Dict[str, float]:
        """
        Calcule les heures supplémentaires pour tous les employés

        Args:
            records: Liste de tous les enregistrements

        Returns:
            Dictionnaire avec les heures supplémentaires par employé (NNI -> heures)
        """
        self.logger.info(f"Calcul des heures supplémentaires pour {len(records)} enregistrements")

        if not records:
            return {}

        # Grouper par employé
        employee_records = defaultdict(list)
        for record in records:
            if record.nni:
                employee_records[record.nni].append(record)

        # Calculer pour chaque employé
        results = {}
        for nni, employee_records_list in employee_records.items():
            overtime_hours = self._calculate_overtime_for_employee(employee_records_list)
            results[nni] = overtime_hours

        self.logger.info(f"Heures supplémentaires calculées pour {len(results)} employés")
        return results

    def _calculate_overtime_for_employee(self, records: List[PMTRecord]) -> float:
        """
        Calcule les heures supplémentaires pour un seul employé

        Args:
            records: Enregistrements de l'employé

        Returns:
            Total des heures supplémentaires
        """
        total_overtime = 0.0

        for record in records:
            # Vérifier si c'est un enregistrement d'heures supplémentaires
            if self._is_overtime_record(record):
                overtime_hours = self._calculate_overtime_hours(record)
                total_overtime += overtime_hours

        return total_overtime

    def _is_overtime_record(self, record: PMTRecord) -> bool:
        """
        Vérifie si un enregistrement correspond à des heures supplémentaires

        Args:
            record: Enregistrement à vérifier

        Returns:
            True si c'est un enregistrement d'heures supplémentaires
        """
        # Vérifier le code D et la valeur
        if not (record.code and 
                record.code.strip().upper() == self.OVERTIME_CODE and
                record.valeur is not None and
                record.valeur > 0):
            return False
        
        # Exclure complètement les employés AUTRES
        if self._is_autres_employee(record):
            return False
        
        # Pour les employés ASTREINTES et TIPS, vérifier HT/HTM = "J" et exclure weekends/astreintes
        if self._is_astreinte_employee(record) or self._is_tips_employee(record):
            # Vérifier que c'est un jour "J" (HT ou HTM)
            if not self._is_working_day(record):
                return False
            
            # Exclure les weekends
            if self._is_weekend(record):
                return False
            
            # Exclure les jours d'astreinte
            if self._is_astreinte_day(record):
                return False
        
        # Pour les 3X8, pas de restrictions (tous les jours comptent)
        
        return True

    def _calculate_overtime_hours(self, record: PMTRecord) -> float:
        """
        Calcule les heures supplémentaires pour un enregistrement

        Args:
            record: Enregistrement avec code D

        Returns:
            Nombre d'heures supplémentaires
        """
        if not record.valeur or record.valeur <= 0:
            return 0.0

        # Vérifier l'unité
        unit = (record.des_unite or "").strip().lower()
        
        if "jour" in unit:

            return float(record.valeur) * self.HOURS_PER_DAY
        elif "heure" in unit:
            # Déjà en heures
            return float(record.valeur)
        else:
            # Unité inconnue, traiter comme des heures par défaut
            self.logger.warning(f"Unité inconnue pour heures supplémentaires: '{record.des_unite}', traité comme heures")
            return float(record.valeur)

    def get_overtime_summary(self, records: List[PMTRecord]) -> Dict[str, Any]:
        """
        Génère un résumé des heures supplémentaires

        Args:
            records: Liste des enregistrements

        Returns:
            Résumé des heures supplémentaires
        """
        overtime_by_employee = self.calculate_all_employees_overtime(records)
        
        if not overtime_by_employee:
            return {
                'total_employees_with_overtime': 0,
                'total_overtime_hours': 0.0,
                'average_overtime_per_employee': 0.0,
                'max_overtime': 0.0,
                'min_overtime': 0.0
            }

        # Filtrer les employés avec des heures supplémentaires
        employees_with_overtime = {nni: hours for nni, hours in overtime_by_employee.items() if hours > 0}
        
        total_overtime = sum(employees_with_overtime.values())
        
        return {
            'total_employees_with_overtime': len(employees_with_overtime),
            'total_overtime_hours': total_overtime,
            'average_overtime_per_employee': total_overtime / len(employees_with_overtime) if employees_with_overtime else 0.0,
            'max_overtime': max(employees_with_overtime.values()) if employees_with_overtime else 0.0,
            'min_overtime': min(employees_with_overtime.values()) if employees_with_overtime else 0.0
        }

    def _is_astreinte_employee(self, record: PMTRecord) -> bool:
        """
        Détermine si un employé est dans la catégorie ASTREINTES

        Args:
            record: Enregistrement à vérifier

        Returns:
            True si c'est un employé ASTREINTES
        """
        if not record.equipe_lib:
            return False
            
        equipe = record.equipe_lib.upper()
        astreinte_teams = [
            'PV IT ASTREINTE',
            'PV B ASTREINTE', 
            'PV G ASTREINTE',
            'PV PE ASTREINTE'
        ]
        
        return any(team in equipe for team in astreinte_teams)

    def _is_tips_employee(self, record: PMTRecord) -> bool:
        """
        Détermine si un employé est dans la catégorie TIPS

        Args:
            record: Enregistrement à vérifier

        Returns:
            True si c'est un employé TIPS
        """
        if not record.equipe_lib:
            return False
            
        equipe = record.equipe_lib.upper()
        tips_teams = [
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
        
        return any(team in equipe for team in tips_teams)

    def _is_autres_employee(self, record: PMTRecord) -> bool:
        """
        Détermine si un employé est dans la catégorie AUTRES

        Args:
            record: Enregistrement à vérifier

        Returns:
            True si c'est un employé AUTRES (ni ASTREINTES, ni TIPS)
        """
        # Si c'est ni ASTREINTES ni TIPS, c'est AUTRES
        return not (self._is_astreinte_employee(record) or self._is_tips_employee(record))

    def _is_3x8_employee(self, record: PMTRecord) -> bool:
        """
        Détermine si un employé est dans la catégorie 3X8

        Args:
            record: Enregistrement à vérifier

        Returns:
            True si c'est un employé 3X8
        """
        # D'abord vérifier si c'est un employé TIPS
        if not self._is_tips_employee(record):
            return False
        
        # Ensuite vérifier si les horaires correspondent aux horaires 3x8
        return self._has_3x8_schedule(record)

    def _has_3x8_schedule(self, record: PMTRecord) -> bool:
        """
        Vérifie si un enregistrement a des horaires 3x8

        Args:
            record: Enregistrement à vérifier

        Returns:
            True si les horaires correspondent aux horaires 3x8
        """
        # Horaires 3x8 standards
        three_shift_schedules = [
            ("07:30:00", "15:30:00"),  # Poste du matin
            ("15:30:00", "23:30:00"),  # Poste d'après-midi
            ("23:30:00", "07:30:00")   # Poste de nuit
        ]
        
        # Vérifier les horaires de début et fin
        if record.heure_debut and record.heure_fin:
            debut = record.heure_debut.strip()
            fin = record.heure_fin.strip()
            
            for debut_3x8, fin_3x8 in three_shift_schedules:
                if debut == debut_3x8 and fin == fin_3x8:
                    return True
        
        return False

    def _is_weekend(self, record: PMTRecord) -> bool:
        """
        Vérifie si un enregistrement correspond à un weekend

        Args:
            record: Enregistrement à vérifier

        Returns:
            True si c'est un weekend (Samedi ou Dimanche)
        """
        if not record.designation_jour:
            return False
            
        jour = record.designation_jour.strip().lower()
        return jour in ['samedi', 'dimanche']

    def _is_astreinte_day(self, record: PMTRecord) -> bool:
        """
        Vérifie si un enregistrement correspond à un jour d'astreinte

        Args:
            record: Enregistrement à vérifier

        Returns:
            True si c'est un jour d'astreinte (colonne Astreinte = "I")
        """
        if not record.astreinte:
            return False
            
        return record.astreinte.strip().upper() == "I"

    def _is_working_day(self, record: PMTRecord) -> bool:
        """
        Vérifie si un enregistrement correspond à un jour de travail (HT ou HTM = "J")

        Args:
            record: Enregistrement à vérifier

        Returns:
            True si c'est un jour de travail (HT ou HTM = "J")
        """
        # Si HTM a une valeur non vide, alors HTM doit être "J"
        if record.htm and record.htm.strip():
            return record.htm.strip().upper() == "J"
        
        # Sinon, HT doit être "J"
        if record.ht and record.ht.strip():
            return record.ht.strip().upper() == "J"
            
        # Si ni HT ni HTM ne sont renseignés, ne pas compter
        return False 

    def get_overtime_summary_by_category(self, records: List[PMTRecord], classifications: Dict[str, List[PMTRecord]]) -> Dict[str, Dict[str, Any]]:
        """
        Génère un résumé des heures supplémentaires par catégorie d'employés

        Args:
            records: Liste des enregistrements
            classifications: Classifications des employés par catégorie

        Returns:
            Résumé des heures supplémentaires par catégorie
        """
        from services.employee_classifier import EmployeeClassifier
        classifier = EmployeeClassifier()
        
        # Calculer les heures supplémentaires pour tous les employés
        overtime_by_employee = self.calculate_all_employees_overtime(records)
        
        results = {}
        
        for category, category_records in classifications.items():
            # Filtrer les enregistrements selon les règles métier
            filtered_records = classifier.filter_records_by_business_rules(
                category_records, category
            )
            
            # Obtenir les employés uniques de cette catégorie
            unique_employees = set()
            for record in filtered_records:
                if record.nni:
                    unique_employees.add(record.nni)
            
            if not unique_employees:
                results[category] = {
                    'total_employees': 0,
                    'employees_with_overtime': 0,
                    'total_overtime_hours': 0.0,
                    'average_overtime_all': 0.0,
                    'average_overtime_with_overtime_only': 0.0,
                    'max_overtime': 0.0,
                    'min_overtime': 0.0,
                    'percentage_with_overtime': 0.0
                }
                continue
            
            # Récupérer les heures supplémentaires pour cette catégorie
            category_overtime = []
            employees_with_overtime = []
            
            for nni in unique_employees:
                overtime_hours = overtime_by_employee.get(nni, 0.0)
                category_overtime.append(overtime_hours)
                if overtime_hours > 0:
                    employees_with_overtime.append(overtime_hours)
            
            total_employees = len(unique_employees)
            employees_with_overtime_count = len(employees_with_overtime)
            total_overtime = sum(category_overtime)
            
            # Calculer les moyennes
            avg_overtime_all = total_overtime / total_employees if total_employees > 0 else 0.0
            avg_overtime_with_overtime_only = sum(employees_with_overtime) / employees_with_overtime_count if employees_with_overtime_count > 0 else 0.0
            
            # Calculer les statistiques
            max_overtime = max(category_overtime) if category_overtime else 0.0
            min_overtime_with_overtime = min(employees_with_overtime) if employees_with_overtime else 0.0
            percentage_with_overtime = (employees_with_overtime_count / total_employees * 100) if total_employees > 0 else 0.0
            
            results[category] = {
                'total_employees': total_employees,
                'employees_with_overtime': employees_with_overtime_count,
                'total_overtime_hours': total_overtime,
                'average_overtime_all': avg_overtime_all,
                'average_overtime_with_overtime_only': avg_overtime_with_overtime_only,
                'max_overtime': max_overtime,
                'min_overtime_with_overtime_only': min_overtime_with_overtime,
                'percentage_with_overtime': percentage_with_overtime
            }
        
        return results 