"""
Configuration du projet Statistiques PMT
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

CODES_EQUIPES = [
    'PV IT ASTREINTE', 
    'PV B ASTREINTE', 
    'PV G ASTREINTE', 
    'PV PE ASTREINTE'
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
    'Présence_%_365j', 'Moyenne_Heures_Par_Jour_Présent'
]

NOMS_FEUILLES = {
    'statistiques': 'Statistiques_Employés',
    'moyennes': 'Moyennes_par_Équipe'
} 