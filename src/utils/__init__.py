"""
Package utils pour le projet Statistiques PMT.

author : CAPELLE Gabin
"""

# Imports pour faciliter l'utilisation du package
from .data_loader import charger_donnees_csv, preparer_donnees, supprimer_doublons
from .horaires import get_horaire_final, verifier_horaire_reference, analyser_horaires_disponibles
from .filtres import appliquer_filtres_base
from .calculateurs import calculer_statistiques_employes, calculer_moyennes_equipe
from .formatters import formater_donnees_finales, analyser_codes_presence
from .excel_writer import sauvegarder_excel


__all__ = [
    'charger_donnees_csv',
    'preparer_donnees', 
    'supprimer_doublons',
    'get_horaire_final',
    'verifier_horaire_reference',
    'analyser_horaires_disponibles',
    'appliquer_filtres_base',
    'calculer_statistiques_employes',
    'calculer_moyennes_equipe',
    'formater_donnees_finales',
    'analyser_codes_presence',
    'sauvegarder_excel'
] 