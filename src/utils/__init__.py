"""
Package utils pour le projet Statistiques PMT.

author : CAPELLE Gabin
"""

# Imports pour faciliter l'utilisation du package
from .data_loader import charger_donnees_csv, preparer_donnees, preparer_donnees_tip, preparer_donnees_3x8, supprimer_doublons
from .horaires import get_horaire_final, verifier_horaire_reference, analyser_horaires_disponibles
from .filtres import appliquer_filtres_base, appliquer_filtres_astreinte
from .calculateurs import calculer_statistiques_employes, calculer_moyennes_equipe
from .calculateurs_3x8 import est_horaire_3x8, identifier_type_poste_3x8, calculer_statistiques_3x8, calculer_moyennes_equipe_3x8, calculer_heures_travaillees_avec_unite
from .calculateurs_supplementaires import (
    enrichir_stats_astreinte_avec_heures_supp,
    enrichir_stats_3x8_avec_heures_supp_service_continu,
    enrichir_stats_avec_arrets_maladie,
    enrichir_moyennes_avec_nouvelles_stats,
    enrichir_stats_avec_heures_supplementaires_hors_astreinte,
    calculer_statistiques_arrets_maladie_tous_employes
)
from .formatters import formater_donnees_finales, analyser_codes_presence
from .excel_writer import sauvegarder_excel
from .remover import supprimer_astreinte_insuffisants, supprimer_tip_insuffisants, supprimer_3x8_insuffisants


__all__ = [
    'charger_donnees_csv',
    'preparer_donnees',
    'preparer_donnees_tip',
    'preparer_donnees_3x8',
    'supprimer_doublons',
    'get_horaire_final',
    'verifier_horaire_reference',
    'analyser_horaires_disponibles',
    'appliquer_filtres_base',
    'appliquer_filtres_astreinte',
    'calculer_statistiques_employes',
    'calculer_moyennes_equipe',
    'est_horaire_3x8',
    'identifier_type_poste_3x8',
    'calculer_statistiques_3x8',
    'calculer_moyennes_equipe_3x8',
    'calculer_heures_travaillees_avec_unite',
    'enrichir_stats_astreinte_avec_heures_supp',
    'enrichir_stats_3x8_avec_heures_supp_service_continu',
    'enrichir_stats_avec_arrets_maladie',
    'enrichir_moyennes_avec_nouvelles_stats',
    'enrichir_stats_avec_heures_supplementaires_hors_astreinte',
    'calculer_statistiques_arrets_maladie_tous_employes',
    'formater_donnees_finales',
    'analyser_codes_presence',
    'sauvegarder_excel',
    'supprimer_astreinte_insuffisants',
    'supprimer_tip_insuffisants',
    'supprimer_3x8_insuffisants'
] 