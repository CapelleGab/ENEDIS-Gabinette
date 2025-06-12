"""
Module de calcul des statistiques spécifiques aux employés en 3x8.

author : CAPELLE Gabin
"""

import pandas as pd
from .horaires import get_horaires_effectifs
from config import JOURS_WEEKEND


def est_horaire_3x8(row):
    """
    Détermine si la ligne correspond à un horaire 3x8.
    Les horaires 3x8 sont:
    - Matin: 07:30-15:30
    - Après-midi: 15:30-23:30
    - Nuit: 23:30-07:30

    Ces horaires sont uniquement présents dans les deux premières colonnes (HT, De, à)

    Args:
        row: Ligne du DataFrame

    Returns:
        bool: True si c'est un horaire 3x8, False sinon
    """
    try:
        # Vérifier d'abord si les colonnes requises existent
        if 'HT' not in row or 'De' not in row or 'à' not in row:
            return False

        # Récupérer les valeurs des colonnes HT et De/à
        ht = str(row.get('HT', '')) if pd.notna(row.get('HT', '')) else ''
        debut_1 = str(row.get('De', '')) if pd.notna(row.get('De', '')) else ''
        fin_1 = str(row.get('à', '')) if pd.notna(row.get('à', '')) else ''

        # Si les colonnes sont vides, retourner False
        if not ht or not debut_1 or not fin_1:
            return False

        # Poste du matin (7h30-15h30)
        if '07:30:00' in debut_1 and '15:30:00' in fin_1:
            return True

        # Poste d'après-midi (15h30-23h30)
        if '15:30:00' in debut_1 and '23:30:00' in fin_1:
            return True

        # Poste de nuit (23h30-7h30)
        if '23:30:00' in debut_1 and '07:30:00' in fin_1:
            return True

        return False
    except (KeyError, TypeError, AttributeError):
        # En cas d'erreur, retourner False
        return False


def identifier_type_poste_3x8(row):
    """
    Identifie le type de poste 3x8 (matin, après-midi, nuit).
    Les horaires 3x8 sont:
    - Matin: 07:30-15:30
    - Après-midi: 15:30-23:30
    - Nuit: 23:30-07:30

    Args:
        row: Ligne du DataFrame

    Returns:
        str: 'matin', 'apres-midi', 'nuit' ou None si ce n'est pas un 3x8
    """
    try:
        # Vérifier d'abord si les colonnes requises existent
        if 'HT' not in row or 'De' not in row or 'à' not in row:
            return None

        # Récupérer les valeurs des colonnes HT et De/à
        debut_1 = str(row.get('De', '')) if pd.notna(row.get('De', '')) else ''
        fin_1 = str(row.get('à', '')) if pd.notna(row.get('à', '')) else ''

        # Si les colonnes sont vides, retourner None
        if not debut_1 or not fin_1:
            return None

        # Poste du matin (7h30-15h30)
        if '07:30:00' in debut_1 and '15:30:00' in fin_1:
            return 'matin'

        # Poste d'après-midi (15h30-23h30)
        if '15:30:00' in debut_1 and '23:30:00' in fin_1:
            return 'apres-midi'

        # Poste de nuit (23h30-7h30)
        if '23:30:00' in debut_1 and '07:30:00' in fin_1:
            return 'nuit'

        return None
    except (KeyError, TypeError, AttributeError):
        # En cas d'erreur, retourner None
        return None


def separer_donnees_3x8_et_tip(df_tip):
    """
    Sépare les données entre jours en horaires 3x8 et jours en horaires TIP standard.
    Un employé peut être à la fois en 3x8 certains jours et en TIP standard d'autres jours.

    Args:
        df_tip: DataFrame contenant les données TIP

    Returns:
        tuple: (DataFrame des jours en 3x8, DataFrame des jours en TIP standard)
    """
    if df_tip.empty:
        return pd.DataFrame(), df_tip

    # Créer une copie du DataFrame TIP
    df_tip_copy = df_tip.copy()

    # Identifier les lignes qui correspondent à des horaires 3x8
    df_tip_copy['Est_3x8'] = df_tip_copy.apply(est_horaire_3x8, axis=1)

    # Extraire les lignes qui correspondent à des horaires 3x8
    df_jours_3x8 = df_tip_copy[df_tip_copy['Est_3x8'] == True].copy()

    # Garder uniquement les lignes qui ne correspondent pas à des horaires 3x8 pour le TIP standard
    df_jours_tip_standard = df_tip_copy[df_tip_copy['Est_3x8'] == False].copy()

    # Nettoyer les DataFrames en supprimant la colonne temporaire
    if 'Est_3x8' in df_jours_3x8.columns:
        df_jours_3x8 = df_jours_3x8.drop(columns=['Est_3x8'])

    if 'Est_3x8' in df_jours_tip_standard.columns:
        df_jours_tip_standard = df_jours_tip_standard.drop(columns=['Est_3x8'])

    return df_jours_3x8, df_jours_tip_standard


def calculer_heures_travaillees_avec_unite(row):
    """
    Calcule les heures travaillées en tenant compte de l'unité dans "Dés. unité".

    Args:
        row: Ligne du DataFrame

    Returns:
        float: Nombre d'heures travaillées
    """
    try:
        # Si on a un code (absence ou autre)
        if pd.notna(row.get('Code', '')) and row.get('Code', '') not in ['', ' ']:
            # Cas spécial : code "80TH" = 8 heures travaillées
            if str(row.get('Code', '')).strip().upper() == '80TH':
                return 8.0

            # Si on a une valeur numérique avec le code
            if pd.notna(row.get('Valeur', '')) and row.get('Valeur', '') != '':
                valeur = float(row.get('Valeur', 0))
                if valeur >= 0:
                    # Vérifier l'unité dans la colonne "Dés. unité"
                    unite = str(row.get('Dés. unité', '')).strip().lower() if pd.notna(row.get('Dés. unité', '')) else ''

                    if 'jour' in unite:
                        # Si l'unité est en jours : valeur = nombre de jours travaillés
                        # Exemple: 1 jour travaillé = 8h travaillées
                        heures_travaillees = valeur * 8.0
                        return min(8.0, heures_travaillees)  # Maximum 8 heures par jour
                    elif 'heure' in unite:
                        # Si l'unité est en heures : valeur = nombre d'heures travaillées
                        # Exemple: 6 heures travaillées
                        return min(8.0, valeur)  # Maximum 8 heures par jour
                    else:
                        # Si pas d'unité : valeur = nombre d'heures d'absence (ancien comportement)
                        # Exemple: 2 heures d'absence = 8-2 = 6h travaillées
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


def calculer_statistiques_3x8(df_3x8):
    """
    Calcule les statistiques pour les employés 3x8, incluant le nombre de postes
    du matin, d'après-midi et de nuit.

    Args:
        df_3x8: DataFrame contenant les données des employés 3x8

    Returns:
        pd.DataFrame: DataFrame avec les statistiques 3x8 par employé
    """
    if df_3x8.empty:
        return pd.DataFrame()

    # Commencer avec une copie du DataFrame original
    df_3x8_filtre = df_3x8.copy()

    # Filtrer les jours de weekend (Samedi et Dimanche) si la colonne existe
    if 'Désignation jour' in df_3x8_filtre.columns:
        df_3x8_filtre = df_3x8_filtre[~df_3x8_filtre['Désignation jour'].isin(JOURS_WEEKEND)].copy()

    # Filtrer les jours avec les codes à exclure: "D", "FP", "41", "21", "68", "10" si la colonne existe
    codes_a_exclure = ["D", "FP", "41", "21", "68", "10"]
    if 'Code' in df_3x8_filtre.columns:
        df_3x8_filtre = df_3x8_filtre[~df_3x8_filtre['Code'].isin(codes_a_exclure)].copy()

    # Si après filtrage il ne reste plus de données, retourner un DataFrame vide
    if df_3x8_filtre.empty:
        return pd.DataFrame()

    # Ajouter la colonne du type de poste 3x8
    df_3x8_filtre['Type_Poste'] = df_3x8_filtre.apply(identifier_type_poste_3x8, axis=1)

    # Calculer les heures travaillées avec gestion des unités
    df_3x8_filtre['Heures_Travaillees'] = df_3x8_filtre.apply(calculer_heures_travaillees_avec_unite, axis=1)

    # Calculer la fraction de jour travaillé
    df_3x8_filtre['Fraction_Jour_Travaille'] = df_3x8_filtre['Heures_Travaillees'] / 8.0

    # Calculer les jours d'absences et les jours travaillés
    if 'Code' in df_3x8_filtre.columns and 'Valeur' in df_3x8_filtre.columns:
        # Un jour est considéré comme une absence complète si les heures travaillées = 0
        df_3x8_filtre['Est_Absent_Complet'] = (df_3x8_filtre['Heures_Travaillees'] == 0.0)
    else:
        # Si les colonnes n'existent pas, considérer qu'il n'y a pas d'absence
        df_3x8_filtre['Est_Absent_Complet'] = False

    # Préparer les colonnes pour le groupby
    colonnes_groupby = ['Gentile', 'Equipe (Lib.)', 'Nom', 'Prénom']

    # Ajouter 'UM (Lib)' si elle existe dans le DataFrame
    if 'UM (Lib)' in df_3x8_filtre.columns:
        colonnes_groupby.append('UM (Lib)')

    # Calculer les statistiques par employé
    stats = df_3x8_filtre.groupby(colonnes_groupby).agg(
        # Nombre total de jours (présent + absent)
        Total_Jours=('Jour', 'count'),

        # Somme des fractions de jours travaillés
        Jours_Travailles_Effectifs=('Fraction_Jour_Travaille', 'sum'),

        # Nombre de postes du matin
        Postes_Matin=('Type_Poste', lambda x: (x == 'matin').sum()),

        # Nombre de postes d'après-midi
        Postes_Apres_Midi=('Type_Poste', lambda x: (x == 'apres-midi').sum()),

        # Nombre de postes de nuit
        Postes_Nuit=('Type_Poste', lambda x: (x == 'nuit').sum()),

        # Somme des heures travaillées
        Total_Heures_Travaillées=('Heures_Travaillees', 'sum')
    ).reset_index()

    # Calculer le nombre de jours d'absence partielle
    stats['Jours_Absents_Partiels'] = stats['Total_Jours'] - stats['Jours_Travailles_Effectifs']

    # Calculer le nombre total de jours d'absence (partiels seulement)
    stats['Total_Jours_Absents'] = stats['Jours_Absents_Partiels']

    # Renommer les colonnes pour plus de clarté
    stats = stats.rename(columns={
        'Equipe (Lib.)': 'Équipe',
        'Jours_Travailles_Effectifs': 'Jours_Travaillés'
    })

    # Réorganiser les colonnes
    colonnes_ordre = [
        'Gentile', 'Nom', 'Prénom', 'Équipe',
        'Jours_Travaillés', 'Jours_Absents_Partiels',
        'Total_Jours_Absents', 'Total_Jours',
        'Postes_Matin', 'Postes_Apres_Midi', 'Postes_Nuit',
        'Total_Heures_Travaillées'
    ]

    # S'assurer que toutes les colonnes existent avant de réorganiser
    colonnes_disponibles = [col for col in colonnes_ordre if col in stats.columns]
    stats = stats[colonnes_disponibles]

    return stats


def calculer_moyennes_equipe_3x8(stats_3x8):
    """
    Calcule les moyennes par équipe pour les employés 3x8.

    Args:
        stats_3x8: DataFrame avec les statistiques 3x8 par employé

    Returns:
        pd.DataFrame: DataFrame avec les moyennes par équipe
    """
    if stats_3x8.empty:
        return pd.DataFrame()

    # Calculer les moyennes par équipe
    moyennes = stats_3x8.groupby('Équipe').agg(
        Nb_Employés=('Nom', 'count'),
        Moy_Jours_Travaillés=('Jours_Travaillés', 'mean'),
        Moy_Jours_Absents_Partiels=('Jours_Absents_Partiels', 'mean'),
        Moy_Total_Jours_Absents=('Total_Jours_Absents', 'mean'),
        Moy_Total_Jours=('Total_Jours', 'mean'),
        Moy_Postes_Matin=('Postes_Matin', 'mean'),
        Moy_Postes_Apres_Midi=('Postes_Apres_Midi', 'mean'),
        Moy_Postes_Nuit=('Postes_Nuit', 'mean'),
        Moy_Heures_Travaillées=('Total_Heures_Travaillées', 'mean')
    ).reset_index()

    # Calculer également les totaux par équipe
    totaux = stats_3x8.groupby('Équipe').agg(
        Total_Postes_Matin=('Postes_Matin', 'sum'),
        Total_Postes_Apres_Midi=('Postes_Apres_Midi', 'sum'),
        Total_Postes_Nuit=('Postes_Nuit', 'sum'),
        Total_Heures=('Total_Heures_Travaillées', 'sum')
    ).reset_index()

    # Fusionner les moyennes et les totaux
    moyennes = pd.merge(moyennes, totaux, on='Équipe', how='left')

    # Arrondir les colonnes numériques à 2 décimales
    colonnes_moyennes = [
        'Moy_Jours_Travaillés', 'Moy_Jours_Absents_Partiels',
        'Moy_Total_Jours_Absents', 'Moy_Total_Jours',
        'Moy_Postes_Matin', 'Moy_Postes_Apres_Midi', 'Moy_Postes_Nuit',
        'Moy_Heures_Travaillées'
    ]
    moyennes[colonnes_moyennes] = moyennes[colonnes_moyennes].round(2)

    # Réorganiser les colonnes
    colonnes_ordre = [
        'Équipe', 'Nb_Employés',
        'Moy_Jours_Travaillés', 'Moy_Jours_Absents_Partiels',
        'Moy_Total_Jours_Absents', 'Moy_Total_Jours',
        'Moy_Postes_Matin', 'Moy_Postes_Apres_Midi', 'Moy_Postes_Nuit',
        'Moy_Heures_Travaillées',
        'Total_Postes_Matin', 'Total_Postes_Apres_Midi', 'Total_Postes_Nuit',
        'Total_Heures'
    ]

    # S'assurer que toutes les colonnes existent
    colonnes_disponibles = [col for col in colonnes_ordre if col in moyennes.columns]
    moyennes = moyennes[colonnes_disponibles]

    return moyennes
