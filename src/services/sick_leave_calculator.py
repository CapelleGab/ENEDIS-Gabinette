"""
Service de calcul des arrêts maladie pour La Gabinette
"""

from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict
from datetime import datetime, timedelta

from src.models.data_model import PMTRecord
from src.utils.logger import logger


class SickLeaveCalculator:
    """
    Calculateur d'arrêts maladie
    
    Cette classe permet de calculer les statistiques d'arrêts maladie
    à partir des codes 41 (arrêt maladie classique) et 5H (arrêt maladie long).
    """

    def __init__(self):
        self.logger = logger.get_logger("SickLeaveCalculator")
        
        # Codes d'arrêt maladie
        self.CLASSIC_SICK_LEAVE_CODE = "41"
        self.LONG_SICK_LEAVE_CODE = "5H"
        
        # Nombre de jours maximum entre deux arrêts pour considérer qu'ils font partie de la même période
        self.MAX_DAYS_BETWEEN_SICK_LEAVES = 3
    
    def calculate_sick_leave_stats(self, records: List[PMTRecord]) -> Dict[str, Dict[str, Any]]:
        """
        Calcule les statistiques d'arrêt maladie pour tous les employés
        
        Args:
            records: Liste des enregistrements PMT
            
        Returns:
            Dictionnaire avec les statistiques d'arrêt maladie par employé
        """
        self.logger.info("Calcul des statistiques d'arrêt maladie")
        
        # Dictionnaire pour stocker les résultats par employé (NNI)
        sick_leave_stats = {}
        
        # Regrouper les enregistrements par employé
        employees_records = defaultdict(list)
        for record in records:
            if record.nni:
                employees_records[record.nni].append(record)
        
        # Calculer les statistiques pour chaque employé
        for nni, emp_records in employees_records.items():
            # Trier les enregistrements par date
            sorted_records = sorted(emp_records, key=lambda r: datetime.strptime(r.jour, "%d/%m/%Y") if r.jour else datetime.min)
            
            # Calculer les statistiques d'arrêt maladie
            classic_sick_leaves, long_sick_leaves, sick_leave_periods, avg_hours_per_sick_leave = self._calculate_employee_sick_leave(sorted_records)
            
            # Stocker les résultats
            sick_leave_stats[nni] = {
                'classic_sick_leaves': classic_sick_leaves,
                'long_sick_leaves': long_sick_leaves,
                'sick_leave_periods': sick_leave_periods,
                'avg_hours_per_sick_leave': avg_hours_per_sick_leave
            }
        
        self.logger.info(f"Statistiques d'arrêt maladie calculées pour {len(sick_leave_stats)} employés")
        return sick_leave_stats
    
    def _calculate_employee_sick_leave(self, records: List[PMTRecord]) -> Tuple[int, int, int, float]:
        """
        Calcule les statistiques d'arrêt maladie pour un employé
        
        Args:
            records: Liste des enregistrements PMT d'un employé, triés par date
            
        Returns:
            Tuple contenant:
            - Nombre d'arrêts maladie classiques (code 41)
            - Nombre d'arrêts maladie longs (code 5H)
            - Nombre de périodes d'arrêt maladie
            - Moyenne des heures par arrêt maladie
        """
        # Compteurs
        classic_sick_leaves = 0
        long_sick_leaves = 0
        total_sick_leave_hours = 0.0
        
        # Liste pour suivre les périodes d'arrêt maladie
        sick_leave_dates = []
        
        # Parcourir les enregistrements
        for record in records:
            # Vérifier si c'est un arrêt maladie classique (code 41)
            if record.code == self.CLASSIC_SICK_LEAVE_CODE:
                classic_sick_leaves += 1
                if record.valeur is not None:
                    total_sick_leave_hours += record.valeur
                
                # Ajouter la date à la liste des dates d'arrêt maladie
                if record.jour:
                    sick_leave_dates.append(datetime.strptime(record.jour, "%d/%m/%Y"))
            
            # Vérifier si c'est un arrêt maladie long (code 5H)
            elif record.code == self.LONG_SICK_LEAVE_CODE:
                long_sick_leaves += 1
                if record.valeur is not None:
                    total_sick_leave_hours += record.valeur
                
                # Ajouter la date à la liste des dates d'arrêt maladie
                if record.jour:
                    sick_leave_dates.append(datetime.strptime(record.jour, "%d/%m/%Y"))
        
        # Calculer le nombre de périodes d'arrêt maladie
        sick_leave_periods = self._calculate_sick_leave_periods(sick_leave_dates)
        
        # Calculer la moyenne des heures par arrêt maladie
        total_sick_leaves = classic_sick_leaves + long_sick_leaves
        avg_hours_per_sick_leave = total_sick_leave_hours / total_sick_leaves if total_sick_leaves > 0 else 0.0
        
        return classic_sick_leaves, long_sick_leaves, sick_leave_periods, avg_hours_per_sick_leave
    
    def _calculate_sick_leave_periods(self, dates: List[datetime]) -> int:
        """
        Calcule le nombre de périodes d'arrêt maladie
        Une période est définie comme un ensemble de dates consécutives ou séparées par au maximum MAX_DAYS_BETWEEN_SICK_LEAVES jours
        
        Args:
            dates: Liste des dates d'arrêt maladie, triées par ordre chronologique
            
        Returns:
            Nombre de périodes d'arrêt maladie
        """
        if not dates:
            return 0
        
        # Trier les dates par ordre chronologique
        sorted_dates = sorted(dates)
        
        # Initialiser le compteur de périodes
        periods = 1
        
        # Parcourir les dates pour identifier les périodes
        for i in range(1, len(sorted_dates)):
            # Calculer le nombre de jours entre deux dates consécutives
            days_diff = (sorted_dates[i] - sorted_dates[i-1]).days
            
            # Si la différence est supérieure au seuil, c'est une nouvelle période
            if days_diff > self.MAX_DAYS_BETWEEN_SICK_LEAVES:
                periods += 1
        
        return periods 

    def calculate_all_employees_sick_leave(self, records: List[PMTRecord]) -> Dict[str, Dict[str, Any]]:
        """
        Calcule les statistiques d'arrêt maladie pour tous les employés
        
        Args:
            records: Liste des enregistrements PMT
            
        Returns:
            Dictionnaire avec les statistiques d'arrêt maladie par employé
        """
        self.logger.info(f"Calcul des arrêts maladie pour {len(records)} enregistrements")
        result = self.calculate_sick_leave_stats(records)
        self.logger.info(f"Résultat du calcul des arrêts maladie : {len(result)} employés")
        return result 