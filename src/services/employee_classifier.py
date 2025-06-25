"""
Service de classification des employés pour La Gabinette
"""

from typing import List, Dict, Set, Any
from collections import defaultdict
import pandas as pd

from src.models.data_model import PMTRecord
from src.utils.logger import logger


class EmployeeClassifier:
    """Service de classification des employés par catégorie"""

    # Codes d'équipes pour les astreintes
    CODES_EQUIPES_ASTREINTE = [
        'PV IT ASTREINTE',
        'PV B ASTREINTE', 
        'PV G ASTREINTE',
        'PV PE ASTREINTE'
    ]

    # Codes d'équipes TIP (TIP)
    CODES_EQUIPES_HORS_ASTREINTE = [
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

    def __init__(self):
        self.logger = logger.get_logger("EmployeeClassifier")

    def classify_employees(self, records: List[PMTRecord]) -> Dict[str, List[PMTRecord]]:
        """
        Classifie tous les employés en 4 catégories

        Args:
            records: Liste des enregistrements PMT

        Returns:
            Dictionnaire avec les 4 catégories d'employés
        """
        self.logger.info(f"Classification de {len(records)} enregistrements")

        # Grouper les enregistrements par employé (NNI)
        employees_records = self._group_by_employee(records)
        
        # Classifier chaque employé
        classifications = {
            'ASTREINTES': [],
            'TIPS': [],
            '3X8': [],
            'AUTRES': []
        }

        for nni, employee_records in employees_records.items():
            category = self._classify_single_employee(employee_records)
            classifications[category].extend(employee_records)

        # Log des statistiques
        for category, records_list in classifications.items():
            unique_employees = len(set(record.nni for record in records_list))
            self.logger.info(f"{category}: {unique_employees} employés, {len(records_list)} enregistrements")

        return classifications

    def _group_by_employee(self, records: List[PMTRecord]) -> Dict[str, List[PMTRecord]]:
        """
        Groupe les enregistrements par employé (NNI)

        Args:
            records: Liste des enregistrements

        Returns:
            Dictionnaire groupé par NNI
        """
        employees = defaultdict(list)
        for record in records:
            if record.nni:  # S'assurer que le NNI existe
                employees[record.nni].append(record)
        
        self.logger.info(f"Groupement terminé: {len(employees)} employés uniques")
        return dict(employees)

    def _classify_single_employee(self, employee_records: List[PMTRecord]) -> str:
        """
        Classifie un seul employé basé sur ses enregistrements

        Args:
            employee_records: Liste des enregistrements d'un employé

        Returns:
            Catégorie de l'employé ('ASTREINTES', 'TIPS', '3X8', 'AUTRES')
        """
        if not employee_records:
            return 'AUTRES'

        # Prendre le premier enregistrement pour les informations générales
        first_record = employee_records[0]
        equipe_lib = first_record.equipe_lib or ''

        # 1. Vérifier si c'est un astreigneur
        if self._is_astreinte_employee(equipe_lib):
            return 'ASTREINTES'

        # 2. Vérifier si c'est un employé TIP (TIP)
        if self._is_tip_employee(equipe_lib):
            # 3. Vérifier si c'est un employé 3x8 (sous-catégorie de TIP)
            if self._is_3x8_employee(employee_records):
                return '3X8'
            else:
                return 'TIPS'

        # 4. Vérifier si c'est un autre employé de DR PARIS
        if self._is_dr_paris_employee(first_record):
            return 'AUTRES'

        # Par défaut, ne pas inclure (mais on retourne AUTRES pour éviter les erreurs)
        return 'AUTRES'

    def _is_astreinte_employee(self, equipe_lib: str) -> bool:
        """
        Vérifie si un employé est astreigneur

        Args:
            equipe_lib: Libellé de l'équipe

        Returns:
            True si astreigneur
        """
        return equipe_lib in self.CODES_EQUIPES_ASTREINTE

    def _is_tip_employee(self, equipe_lib: str) -> bool:
        """
        Vérifie si un employé est TIP (TIP)

        Args:
            equipe_lib: Libellé de l'équipe

        Returns:
            True si TIP
        """
        return equipe_lib in self.CODES_EQUIPES_HORS_ASTREINTE

    def _is_3x8_employee(self, employee_records: List[PMTRecord]) -> bool:
        """
        Vérifie si un employé TIP travaille en 3x8

        Args:
            employee_records: Enregistrements de l'employé

        Returns:
            True si 3x8
        """
        # Vérifier si au moins un enregistrement a des horaires 3x8
        for record in employee_records:
            if self._est_horaire_3x8(record):
                return True
        return False

    def _est_horaire_3x8(self, record: PMTRecord) -> bool:
        """
        Détecte si un enregistrement correspond à des horaires 3x8

        Args:
            record: Enregistrement PMT

        Returns:
            True si horaires 3x8
        """
        # Vérifier toutes les paires d'horaires possibles
        time_pairs = [
            (getattr(record, 'ht_de_1', '') or '', getattr(record, 'ht_a_1', '') or ''),
            (getattr(record, 'ht_de_2', '') or '', getattr(record, 'ht_a_2', '') or ''),
            (getattr(record, 'htm_de_1', '') or '', getattr(record, 'htm_a_1', '') or ''),
            (getattr(record, 'htm_de_2', '') or '', getattr(record, 'htm_a_2', '') or ''),
            (getattr(record, 'he_de_1', '') or '', getattr(record, 'he_a_1', '') or ''),
            (getattr(record, 'he_de_2', '') or '', getattr(record, 'he_a_2', '') or ''),
            (getattr(record, 'heure_debut', '') or '', getattr(record, 'heure_fin', '') or '')
        ]

        for debut, fin in time_pairs:
            if debut and fin:
                # Poste du matin (7h30-15h30)
                if '07:30:00' in debut and '15:30:00' in fin:
                    return True
                    
                # Poste d'après-midi (15h30-23h30) 
                if '15:30:00' in debut and '23:30:00' in fin:
                    return True
                    
                # Poste de nuit (23h30-7h30)
                if '23:30:00' in debut and '07:30:00' in fin:
                    return True
                    
        return False

    def _is_dr_paris_employee(self, record: PMTRecord) -> bool:
        """
        Vérifie si un employé appartient à DR PARIS

        Args:
            record: Enregistrement PMT

        Returns:
            True si DR PARIS
        """
        um_lib = getattr(record, 'um_lib', '') or ''
        return um_lib == 'DR PARIS'

    def filter_records_by_business_rules(self, records: List[PMTRecord], category: str) -> List[PMTRecord]:
        """
        Filtre les enregistrements selon les règles métier de chaque catégorie

        Args:
            records: Liste des enregistrements
            category: Catégorie ('ASTREINTES', 'TIPS', '3X8', 'AUTRES')

        Returns:
            Liste filtrée des enregistrements
        """
        filtered_records = []

        for record in records:
            if self._should_include_record(record, category):
                filtered_records.append(record)

        self.logger.info(f"Filtrage {category}: {len(filtered_records)}/{len(records)} enregistrements conservés")
        return filtered_records

    def _should_include_record(self, record: PMTRecord, category: str) -> bool:
        """
        Détermine si un enregistrement doit être inclus selon les règles métier

        Args:
            record: Enregistrement PMT
            category: Catégorie

        Returns:
            True si l'enregistrement doit être inclus
        """
        # Récupérer les valeurs nécessaires
        astreinte = getattr(record, 'astreinte', '') or ''
        jour_ferie = getattr(record, 'jour_ferie', '') or ''
        designation_jour = getattr(record, 'designation_jour', '') or ''
        ht = getattr(record, 'ht', '') or ''

        if category == 'ASTREINTES':
            # ✅ Inclut les jours d'astreinte (colonne 'Astreinte' = 'I')
            # ❌ Exclut les weekends (Samedi/Dimanche)
            # ❌ Exclut les jours fériés (colonne 'Jour férié' = 'X')
            # 📋 Horaires acceptés : 'J' OU n'importe quel code si 'Astreinte' = 'I'
            
            # Exclure les jours fériés
            if jour_ferie == 'X':
                return False
                
            # Exclure les weekends sauf si en astreinte
            if designation_jour in ['Samedi', 'Dimanche'] and astreinte != 'I':
                return False
                
            # Accepter si HT = 'J' ou si en astreinte
            return ht == 'J' or astreinte == 'I'

        elif category == 'TIPS':
            # ❌ Exclut les jours d'astreinte (colonne 'Astreinte' = 'I')
            # ❌ Exclut les jours fériés (colonne 'Jour férié' = 'X')
            # 📋 Horaires acceptés : Uniquement 'J'
            
            if astreinte == 'I':
                return False
            if jour_ferie == 'X':
                return False
            return ht == 'J'

        elif category == '3X8':
            # ✅ Inclut les weekends et jours fériés (service continu)
            # ❌ Exclut uniquement les jours d'astreinte (colonne 'Astreinte' = 'I')
            # 📋 Horaires acceptés : Tous les horaires 3x8 détectés
            
            if astreinte == 'I':
                return False
            return self._est_horaire_3x8(record)

        elif category == 'AUTRES':
            # ❌ Exclut les jours d'astreinte (colonne 'Astreinte' = 'I')
            # ❌ Exclut les jours fériés (colonne 'Jour férié' = 'X')
            
            if astreinte == 'I':
                return False
            if jour_ferie == 'X':
                return False
            return True

        return False

    def get_classification_summary(self, classifications: Dict[str, List[PMTRecord]]) -> Dict[str, Any]:
        """
        Génère un résumé des classifications

        Args:
            classifications: Résultat de la classification

        Returns:
            Résumé des statistiques
        """
        summary = {}
        
        for category, records in classifications.items():
            # Compter les employés uniques
            unique_employees = set(record.nni for record in records if record.nni)
            
            # Statistiques par agence (basé sur Equipe Lib)
            agences = defaultdict(int)
            for record in records:
                equipe_lib = getattr(record, 'equipe_lib', '') or ''
                if 'IT' in equipe_lib:
                    agences['Italie'] += 1
                elif 'G' in equipe_lib:
                    agences['Grenelle'] += 1
                elif 'B' in equipe_lib:
                    agences['Batignolles'] += 1
                elif 'PE' in equipe_lib:
                    agences['Paris Est'] += 1
                else:
                    agences['Autres'] += 1
            
            summary[category] = {
                'nombre_employes': len(unique_employees),
                'nombre_enregistrements': len(records),
                'repartition_agences': dict(agences)
            }
        
        return summary 