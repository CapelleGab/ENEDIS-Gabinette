"""
Analyse des statistiques PMT (Planning de Maintenance Technique)
Ce script traite les données de planning journalier pour calculer les statistiques
de présence et d'heures travaillées par employé et par équipe.

author : CAPELLE Gabin
"""

import pandas as pd
import numpy as np
from openpyxl import load_workbook
from openpyxl import Workbook


# =============================================================================
# CONFIGURATION
# =============================================================================

ANNEE = '2024'
FICHIER_CSV = f'Planning_journalier_{ANNEE}.csv'
FICHIER_EXCEL = f'Statistiques_PMT_{ANNEE}.xlsx'

# Équipes à analyser
CODES_EQUIPES = ['PV IT ASTREINTE', 'PV B ASTREINTE', 'PV G ASTREINTE', 'PV PE ASTREINTE']

# Jours à exclure de l'analyse
JOURS_WEEKEND = ['Samedi', 'Dimanche']

# Horaires de référence pour le filtrage
HORAIRE_DEBUT_REFERENCE = '07:30:00'
HORAIRE_FIN_REFERENCE = '16:15:00'


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def get_horaire_final(row):
    """
    Détermine le code horaire final selon la priorité :
    1. HTM (Horaire Théorique Modifié) si disponible
    2. HT (Horaire Théorique) sinon
    """
    if pd.notna(row['HTM']) and row['HTM'] not in [' ', '']:
        return row['HTM']
    elif pd.notna(row['HT']) and row['HT'] not in [' ', '']:
        return row['HT']
    else:
        return ''


def get_horaires_effectifs(row):
    """
    Récupère les horaires effectifs selon la priorité :
    1. HTM avec ses colonnes De.2, à.2, De.3, à.3
    2. HT avec ses colonnes De, à, De.1, à.1
    Retourne un dictionnaire avec debut1, fin1, debut2, fin2
    """
    if pd.notna(row['HTM']) and row['HTM'] not in [' ', '']:
        return {
            'debut1': row['De.2'],
            'fin1': row['à.2'], 
            'debut2': row['De.3'],
            'fin2': row['à.3']
        }
    elif pd.notna(row['HT']) and row['HT'] not in [' ', '']:
        return {
            'debut1': row['De'],
            'fin1': row['à'],
            'debut2': row['De.1'], 
            'fin2': row['à.1']
        }
    else:
        return {
            'debut1': None,
            'fin1': None,
            'debut2': None,
            'fin2': None
        }


def verifier_horaire_reference(row):
    """
    Vérifie si l'employé a l'horaire de référence.
    Accepte soit :
    - 07:30:00 à 16:15:00 (horaire continu)
    - 07:30:00 à 12:00:00 + 12:45:00 à 16:15:00 (horaire avec pause)
    Retourne True si au moins une des plages horaires correspond.
    """
    horaires = get_horaires_effectifs(row)
    
    # Vérifier l'horaire continu 07:30:00 à 16:15:00
    if (horaires['debut1'] == HORAIRE_DEBUT_REFERENCE and 
        horaires['fin1'] == HORAIRE_FIN_REFERENCE):
        return True
    
    if (horaires['debut2'] == HORAIRE_DEBUT_REFERENCE and 
        horaires['fin2'] == HORAIRE_FIN_REFERENCE):
        return True
    
    # Vérifier l'horaire avec pause : 07:30:00 à 12:00:00 + 12:45:00 à 16:15:00
    if (horaires['debut1'] == '07:30:00' and horaires['fin1'] == '12:00:00' and
        horaires['debut2'] == '12:45:00' and horaires['fin2'] == '16:15:00'):
        return True
    
    # Vérifier l'inverse (au cas où les colonnes seraient inversées)
    if (horaires['debut2'] == '07:30:00' and horaires['fin2'] == '12:00:00' and
        horaires['debut1'] == '12:45:00' and horaires['fin1'] == '16:15:00'):
        return True
    
    return False


def calculer_heures_travaillees(row):
    """
    Calcule les heures travaillées selon la logique corrigée :
    - Si la valeur existe et est numérique : 8 - valeur
    - Si code d'absence sans valeur : 0 heures travaillées (8h d'absence)
    - Si pas de code ou valeur invalide : 8 heures travaillées (journée complète)
    """
    try:
        # Si on a un code (absence ou autre)
        if pd.notna(row['Code']) and row['Code'] not in ['', ' ']:
            # Si on a une valeur numérique avec le code
            if pd.notna(row['Valeur']) and row['Valeur'] != '':
                valeur = float(row['Valeur'])
                if valeur >= 0:
                    heures_travaillees = 8.0 - valeur
                    return max(0, heures_travaillees)  # Minimum 0 heures
                else:
                    return 8.0  # Valeur négative = journée complète
            else:
                # Code d'absence sans valeur = 8h d'absence = 0h travaillées
                return 0.0
        else:
            # Pas de code = journée complète travaillée
            return 8.0
    except (ValueError, TypeError):
        # Si conversion impossible, considérer comme journée complète
        return 8.0


def calculer_jours_travailles(heures):
    """
    Convertit les heures travaillées en fraction de jour.
    Exemple : 6h = 6/8 = 0.75 jour
    """
    return heures / 8.0


def appliquer_filtres_base(df):
    """
    Applique les filtres de base :
    1. Supprime les week-ends
    2. Supprime les jours fériés
    3. Supprime les jours d'astreinte
    4. Ne garde que les horaires 'J'
    5. NOUVEAU : Ne garde que les horaires 07:30:00 à 16:15:00
    """
    print("Application des filtres de base...")
    
    # 1. Supprimer les week-ends
    df = df[~df['Désignation jour'].isin(JOURS_WEEKEND)].copy()
    print(f"Après suppression week-ends: {len(df)} lignes")
    
    # 2. Supprimer les jours fériés
    df = df[df['Jour férié'] != 'X'].copy()
    print(f"Après suppression jours fériés: {len(df)} lignes")
    
    # 3. Supprimer les jours d'astreinte
    df = df[df['Astreinte'] != 'I'].copy()
    print(f"Après suppression astreintes: {len(df)} lignes")
    
    # 4. Ne garder que les horaires 'J'
    df = df[df['Horaire_Final'] == 'J'].copy()
    print(f"Après filtrage horaires 'J': {len(df)} lignes")
    
    # 5. NOUVEAU : Ne garder que les horaires 07:30:00 à 16:15:00
    df['Horaire_Reference'] = df.apply(verifier_horaire_reference, axis=1)
    df = df[df['Horaire_Reference'] == True].copy()
    print(f"Après filtrage horaires {HORAIRE_DEBUT_REFERENCE}-{HORAIRE_FIN_REFERENCE}: {len(df)} lignes")
    
    return df


def calculer_statistiques_employes_nouvelles(df_filtre):
    """
    Calcule les statistiques pour chaque employé selon la nouvelle logique.
    Sépare les jours complets, partiels et absents.
    """
    # Calculer les heures travaillées pour chaque ligne
    df_filtre['Heures_Travaillees'] = df_filtre.apply(calculer_heures_travaillees, axis=1)
    
    # Calculer les jours travaillés (en fraction)
    df_filtre['Jours_Travailles'] = df_filtre['Heures_Travaillees'].apply(calculer_jours_travailles)
    
    # Identifier les jours partiels : quand il y a un code d'absence avec une valeur
    # Cela signifie que l'employé a travaillé partiellement (8h - valeur)
    df_filtre['Est_Jour_Partiel'] = (
        pd.notna(df_filtre['Code']) & 
        (df_filtre['Code'] != '') & 
        (df_filtre['Code'] != ' ') &
        pd.notna(df_filtre['Valeur']) & 
        (df_filtre['Valeur'] > 0)
    )
    
    # Calculer les statistiques par employé
    stats = df_filtre.groupby(['Gentile', 'Equipe (Lib.)', 'Nom', 'Prénom']).agg(
        # Jours complets (8h exactement)
        Nb_Jours_Complets=('Heures_Travaillees', lambda x: sum(x == 8.0)),
        
        # Jours partiels (heures entre 0 et 8, exclus)
        Nb_Jours_Partiels=('Est_Jour_Partiel', 'sum'),
        
        # Jours absents (0h)
        Nb_Jours_Absents=('Heures_Travaillees', lambda x: sum(x == 0.0)),
        
        # Jours présents = jours complets uniquement (pas les partiels)
        Nb_Jours_Presents=('Heures_Travaillees', lambda x: sum(x == 8.0)),
        
        # Total jours travaillés (en fraction de jours)
        Total_Jours_Travailles=('Jours_Travailles', 'sum'),
        
        # Total heures travaillées
        Total_Heures_Travaillees=('Heures_Travaillees', 'sum'),
        
        # Total heures d'absence
        Total_Heures_Absence=('Heures_Travaillees', lambda x: sum(8.0 - x))
    ).reset_index()
    
    # Calculer le pourcentage de présence sur 365 jours (basé sur les jours complets)
    stats['Presence_Pourcentage_365j'] = (stats['Nb_Jours_Presents'] / 365 * 100).round(2)
    
    # Calculer la moyenne d'heures par jour présent (jours complets + partiels)
    stats['Moyenne_Heures_Par_Jour'] = (
        stats['Total_Heures_Travaillees'] / 
        (stats['Nb_Jours_Presents'] + stats['Nb_Jours_Partiels']).replace(0, 1)
    ).round(2)
    
    return stats


def calculer_moyennes_equipe_nouvelles(df_stats):
    """
    Calcule les moyennes par équipe selon la nouvelle structure.
    """
    return df_stats.groupby('Équipe').agg(
        Nb_Employés=('Nom', 'count'),
        Moy_Jours_Présents_Complets=('Jours_Présents_Complets', 'mean'),
        Moy_Jours_Partiels=('Jours_Partiels', 'mean'),
        Moy_Total_Jours_Travaillés=('Total_Jours_Travaillés', 'mean'),
        Moy_Total_Heures=('Total_Heures_Travaillées', 'mean'),
        Moy_Jours_Complets=('Jours_Complets', 'mean'),
        Moy_Jours_Absents=('Jours_Absents', 'mean'),
        Moy_Heures_Absence=('Total_Heures_Absence', 'mean'),
        Moy_Présence_365j=('Présence_%_365j', 'mean'),
        Moy_Heures_Par_Jour_Présent=('Moyenne_Heures_Par_Jour_Présent', 'mean')
    ).round(2).reset_index()


def analyser_horaires_disponibles(df):
    """
    Analyse les différents horaires présents dans les données pour diagnostic.
    """
    print("\n" + "="*50)
    print("ANALYSE DES HORAIRES DISPONIBLES")
    print("="*50)
    
    # Analyser les horaires HT
    horaires_ht = df[['De', 'à', 'De.1', 'à.1']].drop_duplicates()
    print(f"\nHoraires HT uniques trouvés: {len(horaires_ht)}")
    for _, row in horaires_ht.head(10).iterrows():
        if pd.notna(row['De']) and pd.notna(row['à']):
            print(f"  HT: {row['De']} à {row['à']}", end="")
            if pd.notna(row['De.1']) and pd.notna(row['à.1']):
                print(f" + {row['De.1']} à {row['à.1']}")
            else:
                print()
    
    # Analyser les horaires HTM
    horaires_htm = df[['De.2', 'à.2', 'De.3', 'à.3']].drop_duplicates()
    print(f"\nHoraires HTM uniques trouvés: {len(horaires_htm)}")
    for _, row in horaires_htm.head(10).iterrows():
        if pd.notna(row['De.2']) and pd.notna(row['à.2']):
            print(f"  HTM: {row['De.2']} à {row['à.2']}", end="")
            if pd.notna(row['De.3']) and pd.notna(row['à.3']):
                print(f" + {row['De.3']} à {row['à.3']}")
            else:
                print()


# =============================================================================
# TRAITEMENT PRINCIPAL
# =============================================================================

def main():
    """
    Fonction principale du traitement des données PMT avec la nouvelle logique.
    """
    print(f"Traitement des statistiques PMT pour l'année {ANNEE}")
    
    # Chargement des données depuis le fichier CSV
    print("Chargement des données depuis le fichier CSV...")
    try:
        df_originel = pd.read_csv(FICHIER_CSV, encoding='latin1', sep=';', low_memory=False)
        print(f"Données chargées : {len(df_originel)} lignes, {len(df_originel.columns)} colonnes")
    except Exception as e:
        print(f"ERREUR lors du chargement du fichier CSV : {e}")
        return
    
    # Préparation des données
    df_originel['Gentile'] = (df_originel['Nom'] + ' ' + 
                             df_originel['Prénom'] + ' ' + 
                             df_originel['Equipe (Lib.)'])
    
    # Filtrage par équipe
    df_equipe = df_originel[df_originel['Equipe (Lib.)'].isin(CODES_EQUIPES)].copy()
    
    # Corriger le format français (virgule) vers format anglais (point) pour les décimales
    df_equipe['Valeur'] = df_equipe['Valeur'].astype(str).str.replace(',', '.', regex=False)
    
    # Conversion numérique des valeurs
    df_equipe['Valeur'] = pd.to_numeric(df_equipe['Valeur'], errors='coerce')
    
    # Analyse des horaires disponibles (pour diagnostic)
    analyser_horaires_disponibles(df_equipe)
    
    # Détermination de l'horaire final
    df_equipe['Horaire_Final'] = df_equipe.apply(get_horaire_final, axis=1)
    
    # Suppression des doublons
    df_unique = df_equipe.drop_duplicates(subset=['Gentile', 'Jour'], keep='first').copy()
    
    # Application des filtres de base (avec nouveau filtre horaire)
    df_filtre = appliquer_filtres_base(df_unique)
    
    print(f"\nDonnées après filtrage : {len(df_filtre)} lignes")
    
    # Analyse des codes présents
    codes_uniques = df_filtre['Code'].value_counts()
    print(f"\nCodes présents dans les données filtrées :")
    for code, count in codes_uniques.head(10).items(): 
        print(f"  '{code}': {count} occurrences")
    
    # Calcul des statistiques avec la nouvelle logique
    stats_employes = calculer_statistiques_employes_nouvelles(df_filtre)
    
    # Formatage du DataFrame final avec UNIQUEMENT les colonnes demandées
    stats_final = stats_employes[['Nom', 'Prénom', 'Equipe (Lib.)', 
                                 'Nb_Jours_Presents', 'Nb_Jours_Partiels', 'Total_Jours_Travailles',
                                 'Total_Heures_Travaillees', 'Nb_Jours_Complets', 
                                 'Nb_Jours_Absents', 'Total_Heures_Absence', 
                                 'Presence_Pourcentage_365j']].copy()
    
    # Calculer la moyenne d'heures de présence par jour OÙ L'EMPLOYÉ ÉTAIT PRÉSENT
    # (Total heures travaillées / (Jours présents + Jours partiels))
    stats_final['Moyenne_Heures_Par_Jour_Present'] = (
        stats_final['Total_Heures_Travaillees'] / 
        (stats_final['Nb_Jours_Presents'] + stats_final['Nb_Jours_Partiels']).replace(0, 1)
    ).round(2)
    
    # Renommage des colonnes selon vos spécifications exactes
    stats_final.columns = ['Nom', 'Prénom', 'Équipe', 'Jours_Présents_Complets', 
                          'Jours_Partiels', 'Total_Jours_Travaillés', 'Total_Heures_Travaillées', 
                          'Jours_Complets', 'Jours_Absents', 'Total_Heures_Absence', 
                          'Présence_%_365j', 'Moyenne_Heures_Par_Jour_Présent']
    
    # Calcul des moyennes par équipe
    moyennes_equipe = calculer_moyennes_equipe_nouvelles(stats_final)
    
    # Sauvegarde
    print(f"\nSauvegarde dans {FICHIER_EXCEL}...")
    with pd.ExcelWriter(FICHIER_EXCEL, engine='openpyxl') as writer:
        stats_final.to_excel(writer, sheet_name='Statistiques_Employés', index=False)
        moyennes_equipe.to_excel(writer, sheet_name='Moyennes_par_Équipe', index=False)
    
    # Affichage du résumé
    print("\n" + "=" * 70)
    print("RÉSUMÉ DES RÉSULTATS (LOGIQUE CORRIGÉE)")
    print("=" * 70)
    print("LOGIQUE APPLIQUÉE :")
    print("- Tous les codes sont conservés")
    print("- Code avec valeur : 8h - valeur = heures travaillées")
    print("- Code sans valeur : 0h travaillées (8h d'absence)")
    print(f"- Filtrage horaires : {HORAIRE_DEBUT_REFERENCE} à {HORAIRE_FIN_REFERENCE}")
    print(f"\nNombre d'employés analysés: {len(stats_final)}")
    print(f"Moyenne jours présents par employé: {stats_final['Jours_Présents_Complets'].mean():.1f} jours")
    print(f"Moyenne jours partiels par employé: {stats_final['Jours_Partiels'].mean():.1f} jours")
    print(f"Moyenne total jours travaillés par employé: {stats_final['Total_Jours_Travaillés'].mean():.1f} jours")
    print(f"Moyenne heures totales par employé: {stats_final['Total_Heures_Travaillées'].mean():.1f} heures")
    print(f"Moyenne jours complets (8h) par employé: {stats_final['Jours_Complets'].mean():.1f} jours")
    print(f"Moyenne jours absents par employé: {stats_final['Jours_Absents'].mean():.1f} jours")
    print(f"Moyenne heures d'absence par employé: {stats_final['Total_Heures_Absence'].mean():.1f} heures")
    print(f"\nFichier généré: {FICHIER_EXCEL}")


# =============================================================================
# EXÉCUTION
# =============================================================================

if __name__ == "__main__":
    main()
