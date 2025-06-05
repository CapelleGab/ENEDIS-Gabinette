"""
Configuration du projet PMT Analytics
Centralise tous les paramètres et constantes du projet.

author : CAPELLE Gabin
"""

# =============================================================================
# CONFIGURATION GÉNÉRALE
# =============================================================================

ANNEE = '2024'

# =============================================================================
# FICHIERS
# =============================================================================

FICHIER_CSV = f'Planning_journalier_{ANNEE}.csv'
FICHIER_EXCEL = f'Statistiques_PMT_{ANNEE}.xlsx'

# =============================================================================
# ÉQUIPES À ANALYSER
# =============================================================================

CODES_EQUIPES_ASTREINTE = [
    'PV IT ASTREINTE', 
    'PV B ASTREINTE', 
    'PV G ASTREINTE', 
    'PV PE ASTREINTE'
]

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

# =============================================================================
# FILTRES
# =============================================================================

# Jours à exclure de l'analyse
JOURS_WEEKEND = ['Samedi', 'Dimanche']

# Horaires de référence pour le filtrage
HORAIRE_DEBUT_REFERENCE = '07:30:00'
HORAIRE_FIN_REFERENCE = '16:15:00'

# =============================================================================
# PARAMÈTRES DE LECTURE CSV
# =============================================================================

CSV_ENCODING = 'latin1'
CSV_SEPARATOR = ';'

# =============================================================================
# COLONNES EXCEL DE SORTIE
# =============================================================================

COLONNES_FINALES = [
    'Nom', 'Prénom', 'Équipe', 'Jours_Présents_Complets', 
    'Jours_Partiels', 'Total_Jours_Travaillés', 'Total_Heures_Travaillées', 
    'Jours_Complets', 'Jours_Absents', 'Total_Heures_Absence', 
    'Présence_%_365j',
    # Nouvelle colonne pour heures supplémentaires hors astreinte
    'Heures_Supp',
    # Nouvelles colonnes pour arrêts maladie (simplifiées)
    'Nb_Périodes_Arrêts', 'Nb_Jours_Arrêts_41', 'Nb_Jours_Arrêts_5H',
    'Moy_Heures_Par_Arrêt_Maladie'
]

NOMS_FEUILLES = {
    'statistiques': 'ASTREINTE_STATS',
    'moyennes': 'ASTREINTE_EQUIPES_MOYENNES',
    'tip_statistiques': 'TIP_STATS',
    'tip_moyennes': 'TIP_EQUIPES_MOYENNES',
    '3x8_statistiques': '3x8_STATS',
    '3x8_moyennes': '3x8_EQUIPES_MOYENNES',
    'arrets_maladie': 'TOUS'
} 